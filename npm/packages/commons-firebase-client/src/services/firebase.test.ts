import {beforeEach, describe, expect, it, vi} from 'vitest';

const {
  getAuthMock,
  FakeGoogleAuthProvider,
  signInWithCredential,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  getIdToken,
} = vi.hoisted(() => ({
  getAuthMock: vi.fn(() => ({currentUser: null})),
  FakeGoogleAuthProvider: class FakeGoogleAuthProvider {},
  signInWithCredential: vi.fn(),
  signInWithEmailAndPassword: vi.fn(),
  signOut: vi.fn(),
  onAuthStateChanged: vi.fn(),
  getIdToken: vi.fn(),
}));

vi.mock('@react-native-firebase/auth', () => ({
  getAuth: getAuthMock,
  GoogleAuthProvider: FakeGoogleAuthProvider,
  signInWithCredential,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  getIdToken,
}));

describe('firebase (native)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.resetModules();
  });

  it('configures the native auth instance once', async () => {
    const mod = await import('./firebase');
    mod.configureFirebaseAuth({
      apiKey: 'key',
      authDomain: 'example.firebaseapp.com',
      projectId: 'example',
      storageBucket: 'example.appspot.com',
      appId: '1:2:ios:3',
    });
    mod.configureFirebaseAuth({
      apiKey: 'key',
      authDomain: 'example.firebaseapp.com',
      projectId: 'example',
      storageBucket: 'example.appspot.com',
      appId: '1:2:ios:3',
    });

    expect(getAuthMock).toHaveBeenCalledTimes(1);
    expect(mod.getAuth()).toEqual({currentUser: null});
    expect(mod.GoogleAuthProvider).toBe(FakeGoogleAuthProvider);
  });

  it('signInWithPopup is not supported on native', async () => {
    const mod = await import('./firebase');
    expect(() => mod.signInWithPopup({currentUser: null}, {})).toThrow(
      'signInWithPopup is not supported on native',
    );
  });

  it('delegates every other auth operation to the native SDK', async () => {
    const mod = await import('./firebase');
    mod.configureFirebaseAuth({
      apiKey: 'key',
      authDomain: 'example.firebaseapp.com',
      projectId: 'example',
      storageBucket: 'example.appspot.com',
      appId: '1:2:ios:3',
    });
    const auth = mod.getAuth();
    const credential = {};
    const user = {uid: '1'} as never;

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
