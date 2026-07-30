/** The Firebase web app config passed to `configureFirebaseAuth` on web. */
export interface FirebaseWebConfig {
  apiKey: string;
  authDomain: string;
  projectId: string;
  storageBucket: string;
  appId: string;
}

/** A signed-in Firebase user, normalised across the native and web SDKs. */
export interface AuthUser {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL: string | null;
  delete(): Promise<void>;
}

/** A bound Firebase auth instance, as returned by `getAuth`. */
export interface Auth {
  currentUser: AuthUser | null;
}

/** The result of a successful sign-in call. */
export interface UserCredential {
  user: AuthUser;
}

/** Unregisters a listener passed to `onAuthStateChanged`. */
export type Unsubscribe = () => void;

/**
 * The Google provider constructor/namespace. The provider instances and
 * credentials it produces are opaque tokens that are only ever handed back to
 * the sign-in functions, so they are typed `unknown` rather than `any`.
 */
export interface GoogleAuthProviderStatic {
  credential(idToken: string | null, accessToken?: string): unknown;
}

/**
 * The complete surface every platform implementation must provide. Each export
 * in `firebase.ts` / `firebase.web.ts` is annotated with the matching member
 * type, e.g. `export const getAuth: FirebaseAuthClient['getAuth'] = ...`.
 */
export interface FirebaseAuthClient {
  configureFirebaseAuth(webConfig: FirebaseWebConfig): void;
  getAuth(): Auth;
  googleProvider: unknown;
  GoogleAuthProvider: GoogleAuthProviderStatic;
  signInWithPopup(auth: Auth, provider: unknown): Promise<UserCredential>;
  signInWithCredential(
    auth: Auth,
    credential: unknown,
  ): Promise<UserCredential>;
  signInWithEmailAndPassword(
    auth: Auth,
    email: string,
    password: string,
  ): Promise<UserCredential>;
  signOut(auth: Auth): Promise<void>;
  onAuthStateChanged(
    auth: Auth,
    callback: (user: AuthUser | null) => void,
  ): Unsubscribe;
  getIdToken(user: AuthUser): Promise<string>;
}
