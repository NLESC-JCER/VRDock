import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import basicSsl from '@vitejs/plugin-basic-ssl'

console.log(process.env)

// https://vitejs.dev/config/
export default defineConfig({
  base: process.env.NODE_ENV == 'development' ? '' : process.env.APPLICATION_ENDPOINT,
  plugins: [vue(),basicSsl()],
  assetsInclude: ['**/*.obj'],
})
