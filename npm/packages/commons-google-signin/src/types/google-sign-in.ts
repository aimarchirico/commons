import type {OneTapConfigureParams} from 'react-native-nitro-google-signin';

/** The outcome of a Google sign-in, sign-up, or Firebase-credential exchange attempt. */
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

/** Dev-only email/password credentials used to bypass the Google sign-in flow. */
export interface DevCredentials {
  email: string;
  password: string;
}

/** Options accepted by {@link GoogleSignInService.signIn}. */
export interface SignInOptions {
  devCredentials?: DevCredentials;
}

/** The Google sign-in operations a platform-specific implementation must provide. */
export interface GoogleSignInService {
  configure(config: OneTapConfigureParams): Promise<void>;
  checkPlayServices(): Promise<boolean>;
  signIn(options?: SignInOptions): Promise<GoogleSignInResult>;
  createAccount(): Promise<GoogleSignInResult>;
  signOut(): Promise<void>;
  revokeAccess(): Promise<void>;
}
