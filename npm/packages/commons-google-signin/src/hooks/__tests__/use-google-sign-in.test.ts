import {beforeEach, describe, expect, it, vi} from 'vitest';
import {renderHook} from '@testing-library/react';

const {
  configure,
  checkPlayServices,
  signIn,
  createAccount,
  signOut,
  revokeAccess,
  getAuth,
  signInWithCredential,
  firebaseSignOut,
  credential,
} = vi.hoisted(() => ({
  configure: vi.fn(),
  checkPlayServices: vi.fn(),
  signIn: vi.fn(),
  createAccount: vi.fn(),
  signOut: vi.fn(),
  revokeAccess: vi.fn(),
  getAuth: vi.fn(),
  signInWithCredential: vi.fn(),
  firebaseSignOut: vi.fn(),
  credential: vi.fn(),
}));

vi.mock('../../services/google-sign-in-service', () => ({
  GoogleSignInService: {
    configure,
    checkPlayServices,
    signIn,
    createAccount,
    signOut,
    revokeAccess,
  },
}));

vi.mock('@aimarchirico/commons-firebase-client', () => ({
  getAuth,
  signInWithCredential,
  signOut: firebaseSignOut,
  GoogleAuthProvider: {credential},
}));

describe('useGoogleSignIn', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getAuth.mockReturnValue({currentUser: null});
    credential.mockImplementation((idToken: string) => ({idToken}));
  });

  it('signIn configures, checks play services, and signs into firebase on success', async () => {
    checkPlayServices.mockResolvedValue(true);
    signIn.mockResolvedValue({
      type: 'success',
      data: {idToken: 'tok', user: {id: '1'}},
    });

    const {useGoogleSignIn} = await import('../use-google-sign-in');
    const {result} = renderHook(() => useGoogleSignIn());

    const data = await result.current.signIn();

    expect(configure).toHaveBeenCalledWith({webClientId: 'autoDetect'});
    expect(checkPlayServices).toHaveBeenCalled();
    expect(signInWithCredential).toHaveBeenCalledWith(
      {currentUser: null},
      {idToken: 'tok'},
    );
    expect(data).toEqual({idToken: 'tok', user: {id: '1'}});
  });

  it('signIn passes a custom webClientId and devCredentials through', async () => {
    checkPlayServices.mockResolvedValue(true);
    signIn.mockResolvedValue({type: 'cancelled'});

    const {useGoogleSignIn} = await import('../use-google-sign-in');
    const {result} = renderHook(() =>
      useGoogleSignIn({
        webClientId: 'custom',
        devCredentials: {email: 'a@b.com', password: 'pw'},
      }),
    );

    await result.current.signIn();

    expect(configure).toHaveBeenCalledWith({webClientId: 'custom'});
    expect(signIn).toHaveBeenCalledWith({
      devCredentials: {email: 'a@b.com', password: 'pw'},
    });
  });

  it('signIn falls back to createAccount when there is no saved credential', async () => {
    checkPlayServices.mockResolvedValue(true);
    signIn.mockResolvedValue({type: 'noSavedCredentialFound'});
    createAccount.mockResolvedValue({
      type: 'success',
      data: {idToken: 'new-tok', user: {id: '2'}},
    });

    const {useGoogleSignIn} = await import('../use-google-sign-in');
    const {result} = renderHook(() => useGoogleSignIn());

    const data = await result.current.signIn();

    expect(createAccount).toHaveBeenCalled();
    expect(signInWithCredential).toHaveBeenCalledWith(
      {currentUser: null},
      {idToken: 'new-tok'},
    );
    expect(data).toEqual({idToken: 'new-tok', user: {id: '2'}});
  });

  it('signIn returns undefined when the result is cancelled', async () => {
    checkPlayServices.mockResolvedValue(true);
    signIn.mockResolvedValue({type: 'cancelled'});

    const {useGoogleSignIn} = await import('../use-google-sign-in');
    const {result} = renderHook(() => useGoogleSignIn());

    await expect(result.current.signIn()).resolves.toBeUndefined();
    expect(signInWithCredential).not.toHaveBeenCalled();
  });

  it('signIn rethrows when the underlying flow throws', async () => {
    checkPlayServices.mockRejectedValue(new Error('boom'));

    const {useGoogleSignIn} = await import('../use-google-sign-in');
    const {result} = renderHook(() => useGoogleSignIn());

    await expect(result.current.signIn()).rejects.toThrow('boom');
  });

  it('signOut signs out of firebase and the Google SDK', async () => {
    const {useGoogleSignIn} = await import('../use-google-sign-in');
    const {result} = renderHook(() => useGoogleSignIn());

    await result.current.signOut();

    expect(firebaseSignOut).toHaveBeenCalledWith({currentUser: null});
    expect(signOut).toHaveBeenCalled();
  });

  it('signOut rethrows when the underlying flow throws', async () => {
    firebaseSignOut.mockRejectedValue(new Error('sign out failed'));

    const {useGoogleSignIn} = await import('../use-google-sign-in');
    const {result} = renderHook(() => useGoogleSignIn());

    await expect(result.current.signOut()).rejects.toThrow('sign out failed');
  });

  it('deleteAccount revokes access and deletes the current user', async () => {
    const deleteFn = vi.fn().mockResolvedValue(undefined);
    getAuth.mockReturnValue({currentUser: {delete: deleteFn}});

    const {useGoogleSignIn} = await import('../use-google-sign-in');
    const {result} = renderHook(() => useGoogleSignIn());

    await result.current.deleteAccount();

    expect(revokeAccess).toHaveBeenCalled();
    expect(deleteFn).toHaveBeenCalled();
  });

  it('deleteAccount does nothing when there is no current user', async () => {
    getAuth.mockReturnValue({currentUser: null});

    const {useGoogleSignIn} = await import('../use-google-sign-in');
    const {result} = renderHook(() => useGoogleSignIn());

    await expect(result.current.deleteAccount()).resolves.toBeUndefined();
    expect(revokeAccess).toHaveBeenCalled();
  });

  it('deleteAccount rethrows when the underlying flow throws', async () => {
    revokeAccess.mockRejectedValue(new Error('revoke failed'));

    const {useGoogleSignIn} = await import('../use-google-sign-in');
    const {result} = renderHook(() => useGoogleSignIn());

    await expect(result.current.deleteAccount()).rejects.toThrow(
      'revoke failed',
    );
  });
});
