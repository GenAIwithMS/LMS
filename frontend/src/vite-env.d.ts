/// <reference types="vite/client" />

// Settings read from frontend/.env (see .env.example)
interface ImportMetaEnv {
  readonly VITE_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
