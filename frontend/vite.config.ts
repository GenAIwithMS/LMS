import { defineConfig, loadEnv, Plugin } from 'vite'
import react from '@vitejs/plugin-react'

// Where the backend runs, as an origin like "http://localhost:5000" (or "" for the same site)
const getApiOrigin = (apiUrl: string | undefined): string => {
  if (!apiUrl || apiUrl.startsWith('/')) {
    return ''
  }
  try {
    return new URL(apiUrl).origin
  } catch (error) {
    return ''
  }
}

// Content-Security-Policy for the built site. It tells the browser to run only
// our own script files, so a script injected into the page (XSS) can't run,
// and the page may only talk to our own site and the backend.
// Only added to "npm run build": the dev server needs inline scripts for hot reload.
const contentSecurityPolicy = (apiOrigin: string): Plugin => {
  let connectSources = "'self'"
  if (apiOrigin) {
    connectSources = "'self' " + apiOrigin
  }

  const policy = [
    "default-src 'self'",
    "script-src 'self'",
    "style-src 'self' 'unsafe-inline'",   // React sets some inline styles (style={{...}})
    "img-src 'self' data: blob:",
    "font-src 'self' data:",
    "connect-src " + connectSources,
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
  ].join('; ')

  return {
    name: 'content-security-policy',
    apply: 'build',
    transformIndexHtml(html) {
      return html.replace(
        '<meta charset="UTF-8" />',
        '<meta charset="UTF-8" />\n    <meta http-equiv="Content-Security-Policy" content="' + policy + '" />'
      )
    },
  }
}

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiOrigin = getApiOrigin(env.VITE_API_URL || 'http://localhost:5000/api')

  return {
    plugins: [react(), contentSecurityPolicy(apiOrigin)],
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: 'http://localhost:5000',
          changeOrigin: true,
        }
      }
    }
  }
})
