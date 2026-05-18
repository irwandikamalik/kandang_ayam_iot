import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {

  state: () => ({
    isDark:       
      localStorage.getItem('theme')
      !== 'light',

    isOnline: false,

    serverClock: '',
    uptime: ''
  }),

  actions: {

    toggleTheme() {

      this.isDark = !this.isDark

      document.body.classList.toggle(
        'light-mode',
        !this.isDark
      )
    }

  }

})