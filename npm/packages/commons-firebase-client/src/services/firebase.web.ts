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

/**
 * Initialises the web app from the given config and builds the Google provider
 * with the `email` and `profile` scopes. Repeat calls are ignored.
 *
 * @param webConfig - The Firebase web app config.
 */
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

/**
 * Returns the auth instance built by `configureFirebaseAuth`.
 *
 * @returns The bound web auth instance.
 */
export const getAuth: FirebaseAuthClient['getAuth'] = () => auth;

/**
 * Runs the Google sign-in popup flow, the entry point on web.
 *
 * @param authInstance - The auth instance to sign in against.
 * @param provider - The Google auth provider to run the popup flow for.
 * @returns The resulting user credential.
 */
export const signInWithPopup: FirebaseAuthClient['signInWithPopup'] = (
  authInstance,
  provider,
) =>
  webAuth.signInWithPopup(
    authInstance as unknown as WebAuth,
    provider as webAuth.AuthProvider,
  );

/**
 * Signs in with an already-minted credential.
 *
 * @param authInstance - The auth instance to sign in against.
 * @param credential - The already-minted credential.
 * @returns The resulting user credential.
 */
export const signInWithCredential: FirebaseAuthClient['signInWithCredential'] =
  (authInstance, credential) =>
    webAuth.signInWithCredential(
      authInstance as unknown as WebAuth,
      credential as webAuth.AuthCredential,
    );

/**
 * Signs in with an email and password, used for the dev-only bypass.
 *
 * @param authInstance - The auth instance to sign in against.
 * @param email - The account email.
 * @param password - The account password.
 * @returns The resulting user credential.
 */
export const signInWithEmailAndPassword: FirebaseAuthClient['signInWithEmailAndPassword'] =
  (authInstance, email, password) =>
    webAuth.signInWithEmailAndPassword(
      authInstance as unknown as WebAuth,
      email,
      password,
    );

/**
 * Clears the web session.
 *
 * @param authInstance - The auth instance to sign out.
 * @returns Resolves once the session is cleared.
 */
export const signOut: FirebaseAuthClient['signOut'] = authInstance =>
  webAuth.signOut(authInstance as unknown as WebAuth);

/**
 * Subscribes to sign-in state changes.
 *
 * @param authInstance - The auth instance to observe.
 * @param callback - Invoked with the signed-in user, or `null` when signed out.
 * @returns The unsubscribe handle, which callers must invoke on teardown.
 */
export const onAuthStateChanged: FirebaseAuthClient['onAuthStateChanged'] = (
  authInstance,
  callback,
) => webAuth.onAuthStateChanged(authInstance as unknown as WebAuth, callback);

/**
 * Returns a fresh ID token for the signed-in user, for backend calls.
 *
 * @param user - The signed-in user to mint a token for.
 * @returns The user's fresh ID token.
 */
export const getIdToken: FirebaseAuthClient['getIdToken'] = (user: AuthUser) =>
  webAuth.getIdToken(user as unknown as webAuth.User);
