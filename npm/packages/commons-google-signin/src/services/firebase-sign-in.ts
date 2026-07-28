import {
  getAuth,
  getIdToken,
  googleProvider,
  signInWithEmailAndPassword,
  signInWithPopup,
  type AuthUser,
} from '@aimarchirico/commons-firebase-client';

import type {DevCredentials, GoogleSignInResult} from '../types/google-sign-in';

const toResult = (user: AuthUser, idToken: string): GoogleSignInResult => ({
  type: 'success',
  data: {
    idToken,
    user: {
      id: user.uid,
      email: user.email,
      name: user.displayName,
      photo: user.photoURL,
    },
  },
});

/**
 * Signs in with the dev-only email and password bypass of the Google flow.
 *
 * @param devCredentials The email and password to authenticate with.
 * @returns The signed-in user and a fresh ID token.
 */
export const signInWithDevCredentials = async (
  devCredentials: DevCredentials,
): Promise<GoogleSignInResult> => {
  const result = await signInWithEmailAndPassword(
    getAuth(),
    devCredentials.email,
    devCredentials.password,
  );
  return toResult(result.user, await getIdToken(result.user));
};

/**
 * Runs the Google popup flow, the sign-in entry point on web.
 *
 * @returns The signed-in user and a fresh ID token.
 */
export const signInWithGooglePopup = async (): Promise<GoogleSignInResult> => {
  const result = await signInWithPopup(getAuth(), googleProvider);
  return toResult(result.user, await getIdToken(result.user));
};
