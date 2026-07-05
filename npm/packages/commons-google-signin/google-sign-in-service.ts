import {Platform} from 'react-native';
import {
  getAuth,
  googleProvider,
  signInWithPopup,
  signOut as firebaseSignOut,
  getIdToken,
  signInWithEmailAndPassword,
} from '@aimarchirico/commons-firebase';
import {GoogleOneTapSignIn} from '@react-native-google-signin/google-signin';

export interface GoogleSignInResult {
  type: 'success' | 'cancelled' | 'error' | 'noSavedCredentialFound';
  data?: {
    idToken?: string;
    accessToken?: string;
    user?: {
      id?: string;
      email?: string | null;
      name?: string | null;
      photo?: string | null;
    };
  };
  error?: string;
}

/**
 * Optional email/password credentials used to bypass the Google flow during
 * development. The host app supplies these (e.g. from its build config); the
 * service itself is agnostic to where they come from.
 */
export interface DevCredentials {
  email: string;
  password: string;
}

export interface SignInOptions {
  devCredentials?: DevCredentials;
}

export class GoogleSignInService {
  static async configure(
    config: Parameters<typeof GoogleOneTapSignIn.configure>[0],
  ) {
    if (Platform.OS === 'web') {
      return;
    } else {
      GoogleOneTapSignIn.configure(config);
    }
  }

  static async checkPlayServices() {
    if (Platform.OS === 'web') {
      return true;
    } else {
      return GoogleOneTapSignIn.checkPlayServices();
    }
  }

  static async signIn(options?: SignInOptions): Promise<GoogleSignInResult> {
    try {
      const devCredentials = options?.devCredentials;

      if (devCredentials) {
        const auth = getAuth();
        const result = await signInWithEmailAndPassword(
          auth,
          devCredentials.email,
          devCredentials.password,
        );
        const idToken = await getIdToken(result.user);
        return {
          type: 'success',
          data: {
            idToken,
            user: {
              id: result.user.uid,
              email: result.user.email,
              name: result.user.displayName,
              photo: result.user.photoURL,
            },
          },
        };
      }

      if (Platform.OS === 'web') {
        const auth = getAuth();
        const result = await signInWithPopup(auth, googleProvider);
        const idToken = await getIdToken(result.user);
        return {
          type: 'success',
          data: {
            idToken,
            user: {
              id: result.user.uid,
              email: result.user.email,
              name: result.user.displayName,
              photo: result.user.photoURL,
            },
          },
        };
      } else {
        const signInResponse = await GoogleOneTapSignIn.signIn();
        if (signInResponse.type === 'success') {
          return {
            type: 'success',
            data: {
              idToken: signInResponse.data.idToken,
              user: signInResponse.data.user,
            },
          };
        } else {
          return {type: signInResponse.type};
        }
      }
    } catch (error: unknown) {
      console.error('Google Sign In error:', error);
      const firebaseError = error as {code?: string; message?: string};
      if (
        Platform.OS === 'web' &&
        (firebaseError.code === 'auth/popup-closed-by-user' ||
          firebaseError.code === 'auth/cancelled-popup-request')
      ) {
        return {type: 'cancelled'};
      }
      return {
        type: 'error',
        error: firebaseError.message || 'Sign in failed',
      };
    }
  }

  static async createAccount(): Promise<GoogleSignInResult> {
    if (Platform.OS === 'web') {
      return this.signIn();
    } else {
      try {
        const createResponse = await GoogleOneTapSignIn.createAccount();
        if (createResponse.type === 'success') {
          return {
            type: 'success',
            data: {
              idToken: createResponse.data.idToken,
              user: createResponse.data.user,
            },
          };
        } else {
          return {type: createResponse.type};
        }
      } catch (error: unknown) {
        console.error('Mobile Google Create Account error:', error);
        return {
          type: 'error',
          error:
            (error as {message?: string}).message || 'Account creation failed',
        };
      }
    }
  }

  static async signOut(): Promise<void> {
    try {
      if (Platform.OS === 'web') {
        const auth = getAuth();
        await firebaseSignOut(auth);
      } else {
        await GoogleOneTapSignIn.signOut();
      }
    } catch (error) {
      console.error('Sign out error:', error);
      throw error;
    }
  }

  static async revokeAccess(): Promise<void> {
    try {
      if (Platform.OS === 'web') {
        await this.signOut();
      } else {
        await GoogleOneTapSignIn.revokeAccess('');
      }
    } catch (error) {
      console.error('Revoke access error:', error);
      throw error;
    }
  }
}
