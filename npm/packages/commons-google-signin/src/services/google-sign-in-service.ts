import {
  GoogleOneTapSignIn,
  isNoSavedCredentialFoundResponse,
  isSuccessResponse,
} from 'react-native-nitro-google-signin';

import {signInWithDevCredentials} from './firebase-sign-in';
import type {
  GoogleSignInResult,
  GoogleSignInService as GoogleSignInServiceContract,
  SignInOptions,
} from '../types/google-sign-in';

const toResult = (
  response: Awaited<ReturnType<typeof GoogleOneTapSignIn.signIn>>,
): GoogleSignInResult => {
  if (isSuccessResponse(response)) {
    return {
      type: 'success',
      data: {
        idToken: response.data.idToken,
        user: response.data.user,
      },
    };
  }
  if (isNoSavedCredentialFoundResponse(response)) {
    return {type: 'noSavedCredentialFound'};
  }
  return {type: 'cancelled'};
};

export const GoogleSignInService: GoogleSignInServiceContract = {
  async configure(config) {
    GoogleOneTapSignIn.configure(config);
  },
  async checkPlayServices() {
    await GoogleOneTapSignIn.checkPlayServices();
    return true;
  },
  async signIn(options?: SignInOptions) {
    try {
      if (options?.devCredentials) {
        return await signInWithDevCredentials(options.devCredentials);
      }
      return toResult(await GoogleOneTapSignIn.signIn());
    } catch (error) {
      console.error('Google Sign In error:', error);
      return {
        type: 'error',
        error: (error as {message?: string}).message || 'Sign in failed',
      };
    }
  },
  async createAccount() {
    try {
      return toResult(await GoogleOneTapSignIn.createAccount());
    } catch (error) {
      console.error('Google Create Account error:', error);
      return {
        type: 'error',
        error:
          (error as {message?: string}).message || 'Account creation failed',
      };
    }
  },
  async signOut() {
    await GoogleOneTapSignIn.signOut();
  },
  async revokeAccess() {
    await GoogleOneTapSignIn.revokeAccess('');
  },
};
