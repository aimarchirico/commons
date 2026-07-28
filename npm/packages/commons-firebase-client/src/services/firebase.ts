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

/**
 * Binds the native auth instance and Google provider. Ignores the web config,
 * which the native SDK reads from the bundled `google-services` file instead.
 */
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

/** Returns the auth instance bound by `configureFirebaseAuth`. */
export const getAuth: FirebaseAuthClient['getAuth'] = () => auth;

/** Always throws: native sign-in goes through the Google Sign-In SDK. */
export const signInWithPopup: FirebaseAuthClient['signInWithPopup'] = () => {
  throw new Error('signInWithPopup is not supported on native');
};

/** Signs in with a credential minted by the Google Sign-In SDK. */
export const signInWithCredential: FirebaseAuthClient['signInWithCredential'] =
  (authInstance, credential) =>
    mobileAuth.signInWithCredential(
      authInstance as unknown as NativeAuth,
      credential as Parameters<typeof mobileAuth.signInWithCredential>[1],
    );

/** Signs in with an email and password, used for the dev-only bypass. */
export const signInWithEmailAndPassword: FirebaseAuthClient['signInWithEmailAndPassword'] =
  (authInstance, email, password) =>
    mobileAuth.signInWithEmailAndPassword(
      authInstance as unknown as NativeAuth,
      email,
      password,
    );

/** Clears the native session. */
export const signOut: FirebaseAuthClient['signOut'] = authInstance =>
  mobileAuth.signOut(authInstance as unknown as NativeAuth);

/**
 * Subscribes to sign-in state changes.
 *
 * @returns The unsubscribe handle, which callers must invoke on teardown.
 */
export const onAuthStateChanged: FirebaseAuthClient['onAuthStateChanged'] = (
  authInstance,
  callback,
) =>
  mobileAuth.onAuthStateChanged(
    authInstance as unknown as NativeAuth,
    callback,
  );

/** Returns a fresh ID token for the signed-in user, for backend calls. */
export const getIdToken: FirebaseAuthClient['getIdToken'] = (user: AuthUser) =>
  mobileAuth.getIdToken(
    user as unknown as Parameters<typeof mobileAuth.getIdToken>[0],
  );
