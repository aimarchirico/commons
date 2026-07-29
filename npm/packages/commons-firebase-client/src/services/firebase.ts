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

/**
 * Returns the auth instance bound by `configureFirebaseAuth`.
 *
 * @returns The bound native auth instance.
 */
export const getAuth: FirebaseAuthClient['getAuth'] = () => auth;

/**
 * Always throws: native sign-in goes through the Google Sign-In SDK.
 *
 * @returns Never returns; always throws.
 */
export const signInWithPopup: FirebaseAuthClient['signInWithPopup'] = () => {
  throw new Error('signInWithPopup is not supported on native');
};

/**
 * Signs in with a credential minted by the Google Sign-In SDK.
 *
 * @param authInstance - The auth instance to sign in against.
 * @param credential - The credential minted by the Google Sign-In SDK.
 * @returns The resulting user credential.
 */
export const signInWithCredential: FirebaseAuthClient['signInWithCredential'] =
  (authInstance, credential) =>
    mobileAuth.signInWithCredential(
      authInstance as unknown as NativeAuth,
      credential as Parameters<typeof mobileAuth.signInWithCredential>[1],
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
    mobileAuth.signInWithEmailAndPassword(
      authInstance as unknown as NativeAuth,
      email,
      password,
    );

/**
 * Clears the native session.
 *
 * @param authInstance - The auth instance to sign out.
 * @returns Resolves once the session is cleared.
 */
export const signOut: FirebaseAuthClient['signOut'] = authInstance =>
  mobileAuth.signOut(authInstance as unknown as NativeAuth);

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
) =>
  mobileAuth.onAuthStateChanged(
    authInstance as unknown as NativeAuth,
    callback,
  );

/**
 * Returns a fresh ID token for the signed-in user, for backend calls.
 *
 * @param user - The signed-in user to mint a token for.
 * @returns The user's fresh ID token.
 */
export const getIdToken: FirebaseAuthClient['getIdToken'] = (user: AuthUser) =>
  mobileAuth.getIdToken(
    user as unknown as Parameters<typeof mobileAuth.getIdToken>[0],
  );
