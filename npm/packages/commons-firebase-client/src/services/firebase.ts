import * as mobileAuth from '@react-native-firebase/auth';

import type {
  AuthUser,
  FirebaseAuthClient,
  GoogleAuthProviderStatic,
} from '../types/firebase';

type NativeAuth = ReturnType<typeof mobileAuth.getAuth>;

let auth: NativeAuth;
let configured = false;

export let googleProvider: FirebaseAuthClient['googleProvider'];
export let GoogleAuthProvider: GoogleAuthProviderStatic;

export const configureFirebaseAuth: FirebaseAuthClient['configureFirebaseAuth'] =
  () => {
    if (configured) {
      return;
    }
    auth = mobileAuth.getAuth();
    GoogleAuthProvider =
      mobileAuth.GoogleAuthProvider as unknown as GoogleAuthProviderStatic;
    configured = true;
  };

export const getAuth: FirebaseAuthClient['getAuth'] = () => auth;

export const signInWithPopup: FirebaseAuthClient['signInWithPopup'] = () => {
  throw new Error('signInWithPopup is not supported on native');
};

export const signInWithCredential: FirebaseAuthClient['signInWithCredential'] =
  (authInstance, credential) =>
    mobileAuth.signInWithCredential(
      authInstance as unknown as NativeAuth,
      credential as Parameters<typeof mobileAuth.signInWithCredential>[1],
    );

export const signInWithEmailAndPassword: FirebaseAuthClient['signInWithEmailAndPassword'] =
  (authInstance, email, password) =>
    mobileAuth.signInWithEmailAndPassword(
      authInstance as unknown as NativeAuth,
      email,
      password,
    );

export const signOut: FirebaseAuthClient['signOut'] = authInstance =>
  mobileAuth.signOut(authInstance as unknown as NativeAuth);

export const onAuthStateChanged: FirebaseAuthClient['onAuthStateChanged'] = (
  authInstance,
  callback,
) =>
  mobileAuth.onAuthStateChanged(
    authInstance as unknown as NativeAuth,
    callback,
  );

export const getIdToken: FirebaseAuthClient['getIdToken'] = (user: AuthUser) =>
  mobileAuth.getIdToken(
    user as unknown as Parameters<typeof mobileAuth.getIdToken>[0],
  );
