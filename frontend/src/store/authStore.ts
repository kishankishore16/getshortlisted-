import { create } from 'zustand';
import { authApi, type User } from '@/services/api';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (fullName: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  loadUser: () => Promise<void>;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  isLoading: false,

  setLoading: (loading: boolean) => set({ isLoading: loading }),

  login: async (email: string, password: string) => {
    set({ isLoading: true });
    try {
      const response = await authApi.login({ email, password });
      const { access_token, user } = response.data;
      localStorage.setItem('token', access_token);
      if (user) {
        set({ user, token: access_token, isAuthenticated: true, isLoading: false });
      } else {
        const meRes = await authApi.getMe();
        set({ user: meRes.data, token: access_token, isAuthenticated: true, isLoading: false });
      }
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  register: async (fullName: string, email: string, password: string) => {
    set({ isLoading: true });
    try {
      const response = await authApi.register({ full_name: fullName, email, password });
      const { access_token, user } = response.data;
      localStorage.setItem('token', access_token);
      if (user) {
        set({ user, token: access_token, isAuthenticated: true, isLoading: false });
      } else {
        const meRes = await authApi.getMe();
        set({ user: meRes.data, token: access_token, isAuthenticated: true, isLoading: false });
      }
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    set({ user: null, token: null, isAuthenticated: false });
  },

  loadUser: async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      set({ isAuthenticated: false, isLoading: false });
      return;
    }
    set({ isLoading: true });
    try {
      const response = await authApi.getMe();
      set({ user: response.data, isAuthenticated: true, isLoading: false });
    } catch {
      localStorage.removeItem('token');
      set({ user: null, token: null, isAuthenticated: false, isLoading: false });
    }
  },
}));
