import {beforeEach, describe, expect, it, vi} from 'vitest';

const {getAuth, firebaseSignOut, signInWithDevCredentials, signInWithGooglePopup} =
  vi.hoisted(() => ({
    getAuth: vi.fn(() => ({currentUser: null})),
    firebaseSignOut: vi.fn(),
    signInWithDevCredentials: vi.fn(),
    signInWithGooglePopup: vi.fn(),
  }));

vi.mock('@aimarchirico/commons-firebase-client', () => ({
  getAuth,
  signOut: firebaseSignOut,
}));

vi.mock('./firebase-sign-in', () => ({
  signInWithDevCredentials,
  signInWithGooglePopup,
}));

describe('GoogleSignInService (web)', () => {
  beforeEach(() => vi.clearAllMocks());

  it('configure and checkPlayServices are no-ops that resolve true', async () => {
    const {GoogleSignInService} = await import('./google-sign-in-service.web');
    await expect(GoogleSignInService.configure()).resolves.toBeUndefined();
    await expect(GoogleSignInService.checkPlayServices()).resolves.toBe(true);
  });

  it('signIn uses the dev credentials bypass when given', async () => {
    signInWithDevCredentials.mockResolvedValue({type: 'success', data: {}});
    const {GoogleSignInService} = await import('./google-sign-in-service.web');
    const result = await GoogleSignInService.signIn({
      devCredentials: {email: 'a@b.com', password: 'pw'},
    });
    expect(signInWithDevCredentials).toHaveBeenCalledWith({
      email: 'a@b.com',
      password: 'pw',
    });
    expect(result).toEqual({type: 'success', data: {}});
  });

  it('signIn otherwise runs the Google popup flow', async () => {
    signInWithGooglePopup.mockResolvedValue({type: 'success', data: {}});
    const {GoogleSignInService} = await import('./google-sign-in-service.web');
    const result = await GoogleSignInService.signIn();
    expect(signInWithGooglePopup).toHaveBeenCalled();
    expect(result).toEqual({type: 'success', data: {}});
  });

  it('signIn maps a cancelled-popup error to a cancelled result', async () => {
    signInWithGooglePopup.mockRejectedValue({code: 'auth/popup-closed-by-user'});
    const {GoogleSignInService} = await import('./google-sign-in-service.web');
    const result = await GoogleSignInService.signIn();
    expect(result).toEqual({type: 'cancelled'});
  });

  it('signIn maps a cancelled-popup-request error to a cancelled result', async () => {
    signInWithGooglePopup.mockRejectedValue({
      code: 'auth/cancelled-popup-request',
    });
    const {GoogleSignInService} = await import('./google-sign-in-service.web');
    const result = await GoogleSignInService.signIn();
    expect(result).toEqual({type: 'cancelled'});
  });

  it('signIn maps any other error to an error result', async () => {
    signInWithGooglePopup.mockRejectedValue(new Error('boom'));
    const {GoogleSignInService} = await import('./google-sign-in-service.web');
    const result = await GoogleSignInService.signIn();
    expect(result).toEqual({type: 'error', error: 'boom'});
  });

  it('signIn falls back to a generic error message', async () => {
    signInWithGooglePopup.mockRejectedValue({});
    const {GoogleSignInService} = await import('./google-sign-in-service.web');
    const result = await GoogleSignInService.signIn();
    expect(result).toEqual({type: 'error', error: 'Sign in failed'});
  });

  it('createAccount delegates to signIn', async () => {
    signInWithGooglePopup.mockResolvedValue({type: 'success', data: {}});
    const {GoogleSignInService} = await import('./google-sign-in-service.web');
    const result = await GoogleSignInService.createAccount();
    expect(result).toEqual({type: 'success', data: {}});
  });

  it('signOut clears the Firebase session', async () => {
    getAuth.mockReturnValue({currentUser: null});
    const {GoogleSignInService} = await import('./google-sign-in-service.web');
    await GoogleSignInService.signOut();
    expect(firebaseSignOut).toHaveBeenCalledWith({currentUser: null});
  });

  it('revokeAccess delegates to signOut', async () => {
    getAuth.mockReturnValue({currentUser: null});
    const {GoogleSignInService} = await import('./google-sign-in-service.web');
    await GoogleSignInService.revokeAccess();
    expect(firebaseSignOut).toHaveBeenCalledWith({currentUser: null});
  });
});
