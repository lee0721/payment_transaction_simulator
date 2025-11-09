/// <reference types="vite/client" />

declare const __API_BASE__: string;

declare global {
  interface Window {
    __API_BASE__?: string;
  }
}
