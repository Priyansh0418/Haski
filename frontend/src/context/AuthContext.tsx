import { createContext, useState, useEffect } from "react";
import type { ReactNode } from "react";
import * as api from "../lib/api";

interface User {
  username?: string;
  email?: string;
}

interface AuthContextType {
  token: string | null;
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, username: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export { AuthContext };
export type { AuthContextType };

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize from localStorage on mount
  useEffect(() => {
    const storedToken = api.getToken();
    const storedUser = localStorage.getItem("auth_user");
    if (storedToken) {
      setToken(storedToken);
      if (storedUser) setUser(JSON.parse(storedUser));
    }
    setIsLoading(false);
  }, []);

  // Update localStorage and API client when token changes
  useEffect(() => {
    if (token) {
      api.setToken(token);
      localStorage.setItem("auth_user", JSON.stringify(user));
    } else {
      api.clearToken();
      localStorage.removeItem("auth_user");
    }
  }, [token, user]);

  const login = async (email: string, password: string) => {
    const response = await api.login(email, password);
    const { access_token } = response;
    setToken(access_token);
    setUser({ email });
  };

  const signup = async (email: string, username: string, password: string) => {
    const response = await api.signup(email, username, password);
    const { access_token } = response;
    setToken(access_token);
    setUser({ email, username });
  };

  const logout = () => {
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        login,
        signup,
        logout,
        isAuthenticated: !!token,
        isLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
