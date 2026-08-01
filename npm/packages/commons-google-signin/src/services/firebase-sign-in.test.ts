import {beforeEach, describe, expect, it, vi} from 'vitest';

const {
  getAuth,
  getIdToken,
  googleProvider,
  signInWithEmailAndPassword,
  signInWithPopup,
} = vi.hoisted(() => ({
  getAuth: vi.fn(() => ({currentUser: null})),
  getIdToken: vi.fn(async () => 'fresh-token'),
  googleProvider: {provider: true},
  signInWithEmailAndPassword: vi.fn(),
  signInWithPopup: vi.fn(),
}));

vi.mock('@aimarchirico/commons-firebase-client', () => ({
  getAuth,
  getIdToken,
  googleProvider,
  signInWithEmailAndPassword,
  signInWithPopup,
}));

const user = {
  uid: 'uid-1',
  email: 'a@b.com',
  displayName: 'A B',
  photoURL: 'https://example.com/a.png',
};

describe('signInWithDevCredentials', () => {
  beforeEach(() => vi.clearAllMocks());

  it('signs in with the dev credentials and returns a success result', async () => {
    getAuth.mockReturnValue({currentUser: null});
    getIdToken.mockResolvedValue('fresh-token');
    signInWithEmailAndPassword.mockResolvedValue({user});

    const {signInWithDevCredentials} = await import('./firebase-sign-in');
    const result = await signInWithDevCredentials({
      email: 'a@b.com',
      password: 'pw',
    });

    expect(signInWithEmailAndPassword).toHaveBeenCalledWith(
      {currentUser: null},
      'a@b.com',
      'pw',
    );
    expect(result).toEqual({
      type: 'success',
      data: {
        idToken: 'fresh-token',
        user: {
          id: 'uid-1',
          email: 'a@b.com',
          name: 'A B',
          photo: 'https://example.com/a.png',
        },
      },
    });
  });
});

describe('signInWithGooglePopup', () => {
  beforeEach(() => vi.clearAllMocks());

  it('runs the popup flow and returns a success result', async () => {
    getAuth.mockReturnValue({currentUser: null});
    getIdToken.mockResolvedValue('fresh-token');
    signInWithPopup.mockResolvedValue({user});

    const {signInWithGooglePopup} = await import('./firebase-sign-in');
    const result = await signInWithGooglePopup();

    expect(signInWithPopup).toHaveBeenCalledWith(
      {currentUser: null},
      googleProvider,
    );
    expect(result.type).toBe('success');
    expect(result.data?.idToken).toBe('fresh-token');
  });
});
