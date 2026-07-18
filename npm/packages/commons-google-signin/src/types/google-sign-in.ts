import type {OneTapConfigureParams} from 'react-native-nitro-google-signin';

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

export interface DevCredentials {
  email: string;
  password: string;
}

export interface SignInOptions {
  devCredentials?: DevCredentials;
}

export interface GoogleSignInService {
  configure(config: OneTapConfigureParams): Promise<void>;
  checkPlayServices(): Promise<boolean>;
  signIn(options?: SignInOptions): Promise<GoogleSignInResult>;
  createAccount(): Promise<GoogleSignInResult>;
  signOut(): Promise<void>;
  revokeAccess(): Promise<void>;
}
