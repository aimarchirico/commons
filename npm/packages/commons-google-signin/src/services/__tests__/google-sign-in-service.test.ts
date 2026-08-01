import {beforeEach, describe, expect, it, vi} from 'vitest';

const {
  signIn,
  createAccount,
  configure,
  checkPlayServices,
  signOut,
  revokeAccess,
  signInWithDevCredentials,
} = vi.hoisted(() => ({
  signIn: vi.fn(),
  createAccount: vi.fn(),
  configure: vi.fn(),
  checkPlayServices: vi.fn(),
  signOut: vi.fn(),
  revokeAccess: vi.fn(),
  signInWithDevCredentials: vi.fn(),
}));

vi.mock('react-native-nitro-google-signin', () => ({
  GoogleOneTapSignIn: {
    configure,
    checkPlayServices,
    signIn,
    createAccount,
    signOut,
    revokeAccess,
  },
  isSuccessResponse: (response: {type: string}) => response.type === 'success',
  isNoSavedCredentialFoundResponse: (response: {type: string}) =>
    response.type === 'noSavedCredentialFound',
}));

vi.mock('../firebase-sign-in', () => ({signInWithDevCredentials}));

describe('GoogleSignInService (native)', () => {
  beforeEach(() => vi.clearAllMocks());

  it('configure delegates to GoogleOneTapSignIn.configure', async () => {
    const {GoogleSignInService} = await import('../google-sign-in-service');
    await GoogleSignInService.configure({webClientId: 'auto'});
    expect(configure).toHaveBeenCalledWith({webClientId: 'auto'});
  });

  it('checkPlayServices resolves true after checking', async () => {
    checkPlayServices.mockResolvedValue(undefined);
    const {GoogleSignInService} = await import('../google-sign-in-service');
    await expect(GoogleSignInService.checkPlayServices()).resolves.toBe(true);
  });

  it('signIn uses the dev credentials bypass when given', async () => {
    signInWithDevCredentials.mockResolvedValue({type: 'success', data: {}});
    const {GoogleSignInService} = await import('../google-sign-in-service');
    const result = await GoogleSignInService.signIn({
      devCredentials: {email: 'a@b.com', password: 'pw'},
    });
    expect(signInWithDevCredentials).toHaveBeenCalledWith({
      email: 'a@b.com',
      password: 'pw',
    });
    expect(result).toEqual({type: 'success', data: {}});
  });

  it('signIn maps a successful response', async () => {
    signIn.mockResolvedValue({
      type: 'success',
      data: {idToken: 'tok', user: {id: '1'}},
    });
    const {GoogleSignInService} = await import('../google-sign-in-service');
    const result = await GoogleSignInService.signIn();
    expect(result).toEqual({
      type: 'success',
      data: {idToken: 'tok', user: {id: '1'}},
    });
  });

  it('signIn maps a no-saved-credential response', async () => {
    signIn.mockResolvedValue({type: 'noSavedCredentialFound'});
    const {GoogleSignInService} = await import('../google-sign-in-service');
    const result = await GoogleSignInService.signIn();
    expect(result).toEqual({type: 'noSavedCredentialFound'});
  });

  it('signIn maps a cancelled response', async () => {
    signIn.mockResolvedValue({type: 'cancelled'});
    const {GoogleSignInService} = await import('../google-sign-in-service');
    const result = await GoogleSignInService.signIn();
    expect(result).toEqual({type: 'cancelled'});
  });

  it('signIn reports an error result when the SDK throws', async () => {
    signIn.mockRejectedValue(new Error('boom'));
    const {GoogleSignInService} = await import('../google-sign-in-service');
    const result = await GoogleSignInService.signIn();
    expect(result).toEqual({type: 'error', error: 'boom'});
  });

  it('signIn falls back to a generic error message', async () => {
    signIn.mockRejectedValue({});
    const {GoogleSignInService} = await import('../google-sign-in-service');
    const result = await GoogleSignInService.signIn();
    expect(result).toEqual({type: 'error', error: 'Sign in failed'});
  });

  it('createAccount maps a successful response', async () => {
    createAccount.mockResolvedValue({
      type: 'success',
      data: {idToken: 'tok', user: {id: '1'}},
    });
    const {GoogleSignInService} = await import('../google-sign-in-service');
    const result = await GoogleSignInService.createAccount();
    expect(result.type).toBe('success');
  });

  it('createAccount reports an error result when the SDK throws', async () => {
    createAccount.mockRejectedValue(new Error('nope'));
    const {GoogleSignInService} = await import('../google-sign-in-service');
    const result = await GoogleSignInService.createAccount();
    expect(result).toEqual({type: 'error', error: 'nope'});
  });

  it('signOut delegates to GoogleOneTapSignIn.signOut', async () => {
    const {GoogleSignInService} = await import('../google-sign-in-service');
    await GoogleSignInService.signOut();
    expect(signOut).toHaveBeenCalled();
  });

  it('revokeAccess delegates to GoogleOneTapSignIn.revokeAccess', async () => {
    const {GoogleSignInService} = await import('../google-sign-in-service');
    await GoogleSignInService.revokeAccess();
    expect(revokeAccess).toHaveBeenCalledWith('');
  });
});
