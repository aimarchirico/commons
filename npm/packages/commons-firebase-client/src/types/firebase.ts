export interface FirebaseWebConfig {
  apiKey: string;
  authDomain: string;
  projectId: string;
  storageBucket: string;
  appId: string;
}

export interface AuthUser {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL: string | null;
  delete(): Promise<void>;
}

export interface Auth {
  currentUser: AuthUser | null;
}

export interface UserCredential {
  user: AuthUser;
}

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
