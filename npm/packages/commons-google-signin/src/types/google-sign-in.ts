import type {OneTapConfigureParams} from 'react-native-nitro-google-signin';

/**
 * Result returned by a Google sign-in operation.
 */
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
 * Dev-only credentials for bypassing the Google sign-in flow.
 */
export interface DevCredentials {
  email: string;
  password: string;
}

/**
 * Options passed to the sign-in request.
 */
export interface SignInOptions {
  devCredentials?: DevCredentials;
}

/**
 * Service contract for Google Sign-In operations.
 */
export interface GoogleSignInService {
  configure(config: OneTapConfigureParams): Promise<void>;
  checkPlayServices(): Promise<boolean>;
  signIn(options?: SignInOptions): Promise<GoogleSignInResult>;
  createAccount(): Promise<GoogleSignInResult>;
  signOut(): Promise<void>;
  revokeAccess(): Promise<void>;
}
