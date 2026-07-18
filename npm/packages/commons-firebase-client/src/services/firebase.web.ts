import {initializeApp} from 'firebase/app';
import * as webAuth from 'firebase/auth';

import type {
  AuthUser,
  FirebaseAuthClient,
  GoogleAuthProviderStatic,
} from '../types/firebase';

type WebAuth = ReturnType<typeof webAuth.getAuth>;

let auth: WebAuth;
let configured = false;

export let googleProvider: FirebaseAuthClient['googleProvider'];
export let GoogleAuthProvider: GoogleAuthProviderStatic;

export const configureFirebaseAuth: FirebaseAuthClient['configureFirebaseAuth'] =
  webConfig => {
    if (configured) {
      return;
    }
    const app = initializeApp(webConfig);
    auth = webAuth.getAuth(app);
    const provider = new webAuth.GoogleAuthProvider();
    provider.addScope('email');
    provider.addScope('profile');
    googleProvider = provider;
    GoogleAuthProvider =
      webAuth.GoogleAuthProvider as unknown as GoogleAuthProviderStatic;
    configured = true;
  };

export const getAuth: FirebaseAuthClient['getAuth'] = () => auth;

export const signInWithPopup: FirebaseAuthClient['signInWithPopup'] = (
  authInstance,
  provider,
) =>
  webAuth.signInWithPopup(
    authInstance as unknown as WebAuth,
    provider as webAuth.AuthProvider,
  );

export const signInWithCredential: FirebaseAuthClient['signInWithCredential'] =
  (authInstance, credential) =>
    webAuth.signInWithCredential(
      authInstance as unknown as WebAuth,
      credential as webAuth.AuthCredential,
    );

export const signInWithEmailAndPassword: FirebaseAuthClient['signInWithEmailAndPassword'] =
  (authInstance, email, password) =>
    webAuth.signInWithEmailAndPassword(
      authInstance as unknown as WebAuth,
      email,
      password,
    );

export const signOut: FirebaseAuthClient['signOut'] = authInstance =>
  webAuth.signOut(authInstance as unknown as WebAuth);

export const onAuthStateChanged: FirebaseAuthClient['onAuthStateChanged'] = (
  authInstance,
  callback,
) => webAuth.onAuthStateChanged(authInstance as unknown as WebAuth, callback);

export const getIdToken: FirebaseAuthClient['getIdToken'] = (user: AuthUser) =>
  webAuth.getIdToken(user as unknown as webAuth.User);
