import {
  getAuth,
  signOut as firebaseSignOut,
} from '@aimarchirico/commons-firebase-client';

import {
  signInWithDevCredentials,
  signInWithGooglePopup,
} from './firebase-sign-in';
import type {
  GoogleSignInResult,
  GoogleSignInService as GoogleSignInServiceContract,
  SignInOptions,
} from '../types/google-sign-in';

const signIn = async (options?: SignInOptions): Promise<GoogleSignInResult> => {
  try {
    if (options?.devCredentials) {
      return await signInWithDevCredentials(options.devCredentials);
    }
    return await signInWithGooglePopup();
  } catch (error) {
    const firebaseError = error as {code?: string; message?: string};
    if (
      firebaseError.code === 'auth/popup-closed-by-user' ||
      firebaseError.code === 'auth/cancelled-popup-request'
    ) {
      return {type: 'cancelled'};
    }
    console.error('Google Sign In error:', error);
    return {
      type: 'error',
      error: firebaseError.message || 'Sign in failed',
    };
  }
};

const signOut = async (): Promise<void> => {
  await firebaseSignOut(getAuth());
};

export const GoogleSignInService: GoogleSignInServiceContract = {
  async configure() {},
  async checkPlayServices() {
    return true;
  },
  signIn,
  createAccount: () => signIn(),
  signOut,
  revokeAccess: () => signOut(),
};
