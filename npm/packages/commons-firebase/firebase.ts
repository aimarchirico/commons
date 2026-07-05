import {Platform} from 'react-native';

import {initializeApp} from 'firebase/app';
import * as webAuth from 'firebase/auth';
import * as mobileAuth from '@react-native-firebase/auth';

export interface FirebaseWebConfig {
  apiKey: string;
  authDomain: string;
  projectId: string;
  storageBucket: string;
  appId: string;
}

/* eslint-disable @typescript-eslint/no-explicit-any --
   Firebase web vs mobile APIs have incompatible signatures;
   a shared typed wrapper is not feasible here. */
let firebaseAuth: any;
export let googleProvider: any;
export let GoogleAuthProvider: any;
let firebaseSignInWithPopup: any;
let firebaseSignInWithCredential: any;
let firebaseSignOut: any;
let firebaseOnAuthStateChanged: any;
let firebaseGetIdToken: any;
let firebaseSignInWithEmailAndPassword: any;
/* eslint-enable @typescript-eslint/no-explicit-any */

let configured = false;

/**
 * Initialise the platform-appropriate Firebase Auth backend.
 *
 * Must be called exactly once during app startup, before any other export of
 * this module is used. The host app owns the web config (api key, project id,
 * etc.); on native the config is read from the bundled google-services files by
 * @react-native-firebase, so `webConfig` is only consumed on web.
 */
export function configureFirebaseAuth(webConfig: FirebaseWebConfig) {
  if (configured) {
    return;
  }

  if (Platform.OS === 'web') {
    const app = initializeApp(webConfig);
    firebaseAuth = webAuth.getAuth(app);
    const provider = new webAuth.GoogleAuthProvider();
    provider.addScope('email');
    provider.addScope('profile');
    googleProvider = provider;
    GoogleAuthProvider = webAuth.GoogleAuthProvider;
    firebaseSignInWithPopup = webAuth.signInWithPopup;
    firebaseSignInWithCredential = webAuth.signInWithCredential;
    firebaseSignOut = webAuth.signOut;
    firebaseOnAuthStateChanged = webAuth.onAuthStateChanged;
    firebaseGetIdToken = webAuth.getIdToken;
    firebaseSignInWithEmailAndPassword = webAuth.signInWithEmailAndPassword;
  } else {
    firebaseAuth = mobileAuth.getAuth();
    GoogleAuthProvider = mobileAuth.GoogleAuthProvider;
    firebaseSignInWithCredential = mobileAuth.signInWithCredential;
    firebaseSignOut = mobileAuth.signOut;
    firebaseOnAuthStateChanged = mobileAuth.onAuthStateChanged;
    firebaseGetIdToken = mobileAuth.getIdToken;
    firebaseSignInWithEmailAndPassword = mobileAuth.signInWithEmailAndPassword;
  }

  configured = true;
}

/* eslint-disable @typescript-eslint/no-explicit-any -- forwarding wrappers over the untyped bindings above. */
export const getAuth = () => firebaseAuth;
export const signInWithPopup = (...args: any[]) =>
  firebaseSignInWithPopup(...args);
export const signInWithCredential = (...args: any[]) =>
  firebaseSignInWithCredential(...args);
export const signOut = (...args: any[]) => firebaseSignOut(...args);
export const onAuthStateChanged = (...args: any[]) =>
  firebaseOnAuthStateChanged(...args);
export const getIdToken = (...args: any[]) => firebaseGetIdToken(...args);
export const signInWithEmailAndPassword = (...args: any[]) =>
  firebaseSignInWithEmailAndPassword(...args);
/* eslint-enable @typescript-eslint/no-explicit-any */
