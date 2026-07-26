import fs from 'fs';
import os from 'os';
import path from 'path';

const ENDPOINT = 'https://api.expo.dev/graphql';

export type Keystore = {
  id: string;
  keystore: string;
  keystorePassword: string;
  keyAlias: string;
  keyPassword?: string | null;
};

export type BuildCredentials = {
  id: string;
  name: string;
  isDefault: boolean;
  androidKeystore?: Keystore | null;
};

export type AppCredentials = {
  id: string;
  applicationIdentifier: string;
  androidAppBuildCredentialsList: BuildCredentials[];
};

export type App = {
  id: string;
  fullName: string;
  ownerAccount: {id: string};
  androidAppCredentials: AppCredentials[];
};

const KEYSTORE_FIELDS =
  'id keystore keystorePassword keyAlias keyPassword md5CertificateFingerprint';

/**
 * Authenticate as `EXPO_TOKEN` when set, falling back to the local `eas login`
 * session so the command works on a developer machine without minting a token.
 */
const authHeader = (): Record<string, string> => {
  const token = process.env.EXPO_TOKEN;
  if (token) return {authorization: `Bearer ${token}`};

  const statePath = path.join(os.homedir(), '.expo', 'state.json');
  if (fs.existsSync(statePath)) {
    const state = JSON.parse(fs.readFileSync(statePath, 'utf8')) as {
      auth?: {sessionSecret?: string};
    };
    if (state.auth?.sessionSecret) {
      return {'expo-session': state.auth.sessionSecret};
    }
  }
  throw new Error(
    'No Expo credentials. Set EXPO_TOKEN, or run "npx eas-cli login" on this machine.',
  );
};

const request = async <T>(
  query: string,
  variables: Record<string, unknown>,
): Promise<T> => {
  const response = await fetch(ENDPOINT, {
    method: 'POST',
    headers: {'content-type': 'application/json', ...authHeader()},
    body: JSON.stringify({query, variables}),
  });
  const text = await response.text();
  let payload: {data?: T; errors?: {message: string}[]};
  try {
    payload = JSON.parse(text) as typeof payload;
  } catch {
    throw new Error(`Expo API returned ${response.status}: ${text}`);
  }
  if (payload.errors?.length) {
    throw new Error(
      `Expo API error: ${payload.errors.map(error => error.message).join('; ')}`,
    );
  }
  if (!payload.data) throw new Error('Expo API returned no data.');
  return payload.data;
};

export const resolveApp = async (appId: string): Promise<App> => {
  const data = await request<{app: {byId: App | null}}>(
    `query($appId: String!) {
      app {
        byId(appId: $appId) {
          id
          fullName
          ownerAccount { id }
          androidAppCredentials {
            id
            applicationIdentifier
            androidAppBuildCredentialsList {
              id
              name
              isDefault
              androidKeystore { ${KEYSTORE_FIELDS} }
            }
          }
        }
      }
    }`,
    {appId},
  );
  const app = data.app.byId;
  if (!app) {
    throw new Error(
      `No EAS project with id ${appId}, or this account cannot see it.`,
    );
  }
  return app;
};

export const createKeystore = async (
  accountId: string,
  input: {
    base64EncodedKeystore: string;
    keystorePassword: string;
    keyAlias: string;
    keyPassword: string;
  },
): Promise<Keystore> => {
  const data = await request<{
    androidKeystore: {createAndroidKeystore: Keystore};
  }>(
    `mutation($androidKeystoreInput: AndroidKeystoreInput!, $accountId: ID!) {
      androidKeystore {
        createAndroidKeystore(
          androidKeystoreInput: $androidKeystoreInput
          accountId: $accountId
        ) { ${KEYSTORE_FIELDS} }
      }
    }`,
    {androidKeystoreInput: input, accountId},
  );
  return data.androidKeystore.createAndroidKeystore;
};

export const createAppCredentials = async (
  appId: string,
  applicationIdentifier: string,
): Promise<AppCredentials> => {
  const data = await request<{
    androidAppCredentials: {createAndroidAppCredentials: AppCredentials};
  }>(
    `mutation($appId: ID!, $applicationIdentifier: String!) {
      androidAppCredentials {
        createAndroidAppCredentials(
          androidAppCredentialsInput: {}
          appId: $appId
          applicationIdentifier: $applicationIdentifier
        ) {
          id
          applicationIdentifier
          androidAppBuildCredentialsList { id name isDefault }
        }
      }
    }`,
    {appId, applicationIdentifier},
  );
  return data.androidAppCredentials.createAndroidAppCredentials;
};

export const createBuildCredentials = async (
  appCredentialsId: string,
  input: {name: string; isDefault: boolean; keystoreId: string},
): Promise<BuildCredentials> => {
  const data = await request<{
    androidAppBuildCredentials: {
      createAndroidAppBuildCredentials: BuildCredentials;
    };
  }>(
    `mutation(
      $androidAppBuildCredentialsInput: AndroidAppBuildCredentialsInput!
      $androidAppCredentialsId: ID!
    ) {
      androidAppBuildCredentials {
        createAndroidAppBuildCredentials(
          androidAppBuildCredentialsInput: $androidAppBuildCredentialsInput
          androidAppCredentialsId: $androidAppCredentialsId
        ) {
          id
          name
          isDefault
          androidKeystore { ${KEYSTORE_FIELDS} }
        }
      }
    }`,
    {
      androidAppBuildCredentialsInput: input,
      androidAppCredentialsId: appCredentialsId,
    },
  );
  return data.androidAppBuildCredentials.createAndroidAppBuildCredentials;
};
