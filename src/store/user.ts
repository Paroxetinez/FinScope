import { defineStore } from 'pinia';

interface UserInfo {
  id: number;
  username: string;
  email: string;
}

interface UserState {
  userInfo: UserInfo | null;
  token: string | null;
  isLoading: boolean;
}

export const useUserStore = defineStore({
  id: 'user',
  
  state: (): UserState => ({
    userInfo: null,
    token: null,
    isLoading: false
  }),

  getters: {
    isLoggedIn: (state: UserState): boolean => {
      return !!(state.token && state.userInfo?.id);
    }
  },

  actions: {
    setUserInfo(userInfo: UserInfo) {
      this.userInfo = userInfo;
      localStorage.setItem('userInfo', JSON.stringify(userInfo));
    },

    setToken(token: string) {
      this.token = token;
      localStorage.setItem('token', token);
    },

    clearUserInfo() {
      this.userInfo = null;
      this.token = null;
      localStorage.removeItem('userInfo');
      localStorage.removeItem('token');
      localStorage.removeItem('userid');
    },

    async initUserState() {
      try {
        const token = localStorage.getItem('token');
        const userInfo = localStorage.getItem('userInfo');
        
        if (token && userInfo) {
          this.token = token;
          this.userInfo = JSON.parse(userInfo);
          return true;
        }
        return false;
      } catch (error) {
        console.error('Failed to initialize user state:', error);
        return false;
      }
    }
  },

  persist: true
});