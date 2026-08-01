import {beforeEach, describe, expect, it, vi} from 'vitest';

const {
  initializeApp,
  getAuthMock,
  addScope,
  FakeGoogleAuthProvider,
  signInWithPopup,
  signInWithCredential,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  getIdToken,
} = vi.hoisted(() => {
  const addScope = vi.fn();
  class FakeGoogleAuthProvider {
    addScope = addScope;
  }
  return {
    initializeApp: vi.fn(() => ({app: true})),
    getAuthMock: vi.fn(() => ({currentUser: null})),
    addScope,
    FakeGoogleAuthProvider,
    signInWithPopup: vi.fn(),
    signInWithCredential: vi.fn(),
    signInWithEmailAndPassword: vi.fn(),
    signOut: vi.fn(),
    onAuthStateChanged: vi.fn(),
    getIdToken: vi.fn(),
  };
});

vi.mock('firebase/app', () => ({initializeApp}));
vi.mock('firebase/auth', () => ({
  getAuth: getAuthMock,
  GoogleAuthProvider: FakeGoogleAuthProvider,
  signInWithPopup,
  signInWithCredential,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  getIdToken,
}));

const webConfig = {
  apiKey: 'key',
  authDomain: 'example.firebaseapp.com',
  projectId: 'example',
  storageBucket: 'example.appspot.com',
  appId: '1:2:web:3',
};

describe('firebase.web', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.resetModules();
  });

  it('configures the app and Google provider once', async () => {
    const mod = await import('../firebase.web');
    mod.configureFirebaseAuth(webConfig);
    mod.configureFirebaseAuth(webConfig);

    expect(initializeApp).toHaveBeenCalledTimes(1);
    expect(addScope).toHaveBeenCalledWith('email');
    expect(addScope).toHaveBeenCalledWith('profile');
    expect(mod.getAuth()).toEqual({currentUser: null});
    expect(mod.googleProvider).toBeInstanceOf(FakeGoogleAuthProvider);
    expect(mod.GoogleAuthProvider).toBe(FakeGoogleAuthProvider);
  });

  it('delegates every auth operation to the web SDK', async () => {
    const mod = await import('../firebase.web');
    mod.configureFirebaseAuth(webConfig);
    const auth = mod.getAuth();
    const provider = {};
    const credential = {};
    const user = {uid: '1'} as never;

    await mod.signInWithPopup(auth, provider);
    expect(signInWithPopup).toHaveBeenCalledWith(auth, provider);

    await mod.signInWithCredential(auth, credential);
    expect(signInWithCredential).toHaveBeenCalledWith(auth, credential);

    await mod.signInWithEmailAndPassword(auth, 'a@b.com', 'pw');
    expect(signInWithEmailAndPassword).toHaveBeenCalledWith(
      auth,
      'a@b.com',
      'pw',
    );

    await mod.signOut(auth);
    expect(signOut).toHaveBeenCalledWith(auth);

    const callback = vi.fn();
    mod.onAuthStateChanged(auth, callback);
    expect(onAuthStateChanged).toHaveBeenCalledWith(auth, callback);

    await mod.getIdToken(user);
    expect(getIdToken).toHaveBeenCalledWith(user);
  });
});
