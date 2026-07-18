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

export const signInWithGooglePopup = async (): Promise<GoogleSignInResult> => {
  const result = await signInWithPopup(getAuth(), googleProvider);
  return toResult(result.user, await getIdToken(result.user));
};
