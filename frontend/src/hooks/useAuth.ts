import { useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';

export function useAuth() {
  const store = useAuthStore();

  useEffect(() => {
    if (store.token && !store.user) {
      store.loadUser();
    }
  }, [store.token, store.user, store.loadUser]);

  return store;
}
