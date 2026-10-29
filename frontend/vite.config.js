import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    // A simulated browser, so components can render inside the tests.
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
    // Tests read the API address from here instead of a .env file.
    env: { VITE_API_BASE_URL: 'http://api.test' },
  },
})
