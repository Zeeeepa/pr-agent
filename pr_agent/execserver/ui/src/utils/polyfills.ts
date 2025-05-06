// Import crypto polyfill
import browserCrypto from '../../static/js/cryptoPolyfill';

// Add crypto to window if it doesn't exist
if (typeof window !== 'undefined' && !window.crypto) {
  (window as any).crypto = browserCrypto;
}

// Add global to window if it doesn't exist
if (typeof window !== 'undefined' && !window.global) {
  (window as any).global = window;
}

// Add process to window if it doesn't exist
if (typeof window !== 'undefined' && !window.process) {
  (window as any).process = { env: {} };
}

export default {};

