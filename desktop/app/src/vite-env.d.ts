/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_EOS_BRIDGE_HTTP?: string;
  readonly VITE_EOS_BRIDGE_WS?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
