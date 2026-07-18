import {GoogleSignInService} from '../services/google-sign-in-service';
import type {DevCredentials} from '../types/google-sign-in';
import {
  getAuth,
  signInWithCredential,
  signOut as firebaseSignOut,
  GoogleAuthProvider,
} from '@aimarchirico/commons-firebase-client';

export interface UseGoogleSignInOptions {
  /** Overrides the Google web client id. Defaults to 'autoDetect'. */
  webClientId?: string;
  /** Dev-only email/password bypass of the Google flow. */
  devCredentials?: DevCredentials;
}

export const useGoogleSignIn = (options?: UseGoogleSignInOptions) => {
  const signIn = async () => {
    try {
      await GoogleSignInService.configure({
        webClientId: options?.webClientId ?? 'autoDetect',
      });

      await GoogleSignInService.checkPlayServices();

      const signInResult = await GoogleSignInService.signIn({
        devCredentials: options?.devCredentials,
      });
      if (signInResult.type === 'success' && signInResult.data?.idToken) {
        console.log('Google Sign In successful:', signInResult);
        const googleCredential = GoogleAuthProvider.credential(
          signInResult.data.idToken,
        );
        await signInWithCredential(getAuth(), googleCredential);
        return signInResult.data;
      } else if (signInResult.type === 'noSavedCredentialFound') {
        const createResponse = await GoogleSignInService.createAccount();
        if (createResponse.type === 'success' && createResponse.data?.idToken) {
          console.log('Account created successfully:', createResponse);
          const googleCredential = GoogleAuthProvider.credential(
            createResponse.data.idToken,
          );
          await signInWithCredential(getAuth(), googleCredential);
          return createResponse.data;
        }
      }
    } catch (error) {
      console.error('Google Sign In failed:', error);
      throw error;
    }
  };

  const signOut = async (): Promise<void> => {
    try {
      const auth = getAuth();
      await firebaseSignOut(auth);
      await GoogleSignInService.signOut();
    } catch (error) {
      console.error('Sign out error:', error);
      throw error;
    }
  };

  const deleteAccount = async (): Promise<void> => {
    try {
      await GoogleSignInService.revokeAccess();

      const auth = getAuth();
      const currentUser = auth.currentUser;
      if (currentUser) {
        await currentUser.delete();
      }
    } catch (error) {
      console.error('Delete account error:', error);
      throw error;
    }
  };

  return {
    signIn,
    signOut,
    deleteAccount,
  };
};
