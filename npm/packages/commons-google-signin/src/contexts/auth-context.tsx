import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from 'react';
import {
  getAuth,
  onAuthStateChanged,
  getIdToken as firebaseGetIdToken,
} from '@aimarchirico/commons-firebase-client';

interface User {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL: string | null;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  getIdToken: () => Promise<string | null>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Tracks the Firebase sign-in state and publishes it to the tree below.
 *
 * @param props.children The subtree that consumes the auth context.
 * @returns The provider wrapping `children`.
 */
export const AuthProvider = ({children}: {children: ReactNode}) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const auth = getAuth();
    const unsubscribe = onAuthStateChanged(
      auth,
      (
        firebaseUser: {
          uid: string;
          email: string | null;
          displayName: string | null;
          photoURL: string | null;
        } | null,
      ) => {
        if (firebaseUser) {
          setUser({
            uid: firebaseUser.uid,
            email: firebaseUser.email,
            displayName: firebaseUser.displayName,
            photoURL: firebaseUser.photoURL,
          });
        } else {
          setUser(null);
        }
        setLoading(false);
      },
    );

    return unsubscribe;
  }, []);

  const getIdToken = async (): Promise<string | null> => {
    const auth = getAuth();
    const currentUser = auth.currentUser;
    if (currentUser) {
      return await firebaseGetIdToken(currentUser);
    }
    return null;
  };

  return (
    <AuthContext.Provider value={{user, loading, getIdToken}}>
      {children}
    </AuthContext.Provider>
  );
};

/**
 * Reads the auth context.
 *
 * @returns The current user, the loading flag, and the ID token getter.
 * @throws If called outside an {@link AuthProvider}.
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
