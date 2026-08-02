import {beforeEach, describe, expect, it, vi} from 'vitest';
import {renderHook, waitFor} from '@testing-library/react';

const {getAuth, onAuthStateChanged, getIdToken} = vi.hoisted(() => ({
  getAuth: vi.fn(),
  onAuthStateChanged: vi.fn(),
  getIdToken: vi.fn(),
}));

vi.mock('@aimarchirico/commons-firebase-client', () => ({
  getAuth,
  onAuthStateChanged,
  getIdToken,
}));

describe('AuthProvider / useAuth', () => {
  beforeEach(() => vi.clearAllMocks());

  it('throws when useAuth is called outside an AuthProvider', async () => {
    const {useAuth} = await import('../auth-context');
    expect(() => renderHook(() => useAuth())).toThrow(
      'useAuth must be used within an AuthProvider',
    );
  });

  it('starts loading with no user, then reflects a signed-in user', async () => {
    let authCallback: (user: unknown) => void = () => {};
    onAuthStateChanged.mockImplementation((_auth, callback) => {
      authCallback = callback;
      return vi.fn();
    });
    getAuth.mockReturnValue({});

    const {AuthProvider, useAuth} = await import('../auth-context');
    const {result} = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    expect(result.current.loading).toBe(true);
    expect(result.current.user).toBeNull();

    authCallback({
      uid: '1',
      email: 'a@b.com',
      displayName: 'A',
      photoURL: null,
    });

    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.user).toEqual({
      uid: '1',
      email: 'a@b.com',
      displayName: 'A',
      photoURL: null,
    });
  });

  it('clears the user when the auth state becomes signed-out', async () => {
    let authCallback: (user: unknown) => void = () => {};
    onAuthStateChanged.mockImplementation((_auth, callback) => {
      authCallback = callback;
      return vi.fn();
    });
    getAuth.mockReturnValue({});

    const {AuthProvider, useAuth} = await import('../auth-context');
    const {result} = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    authCallback(null);

    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.user).toBeNull();
  });

  it('getIdToken returns null when there is no current user', async () => {
    onAuthStateChanged.mockImplementation(() => vi.fn());
    getAuth.mockReturnValue({currentUser: null});

    const {AuthProvider, useAuth} = await import('../auth-context');
    const {result} = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    await expect(result.current.getIdToken()).resolves.toBeNull();
    expect(getIdToken).not.toHaveBeenCalled();
  });

  it('getIdToken delegates to firebase getIdToken when a user is signed in', async () => {
    const currentUser = {uid: '1'};
    onAuthStateChanged.mockImplementation(() => vi.fn());
    getAuth.mockReturnValue({currentUser});
    getIdToken.mockResolvedValue('token-123');

    const {AuthProvider, useAuth} = await import('../auth-context');
    const {result} = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    await expect(result.current.getIdToken()).resolves.toBe('token-123');
    expect(getIdToken).toHaveBeenCalledWith(currentUser);
  });
});
