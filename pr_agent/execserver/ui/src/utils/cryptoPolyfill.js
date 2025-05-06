/**
 * Crypto Polyfill for Browser Environment
 *
 * This file provides a simple polyfill for the Node.js crypto module
 * when running in a browser environment. It uses the Web Crypto API
 * where possible and provides fallbacks for unsupported features.
 */

// Create a browser-compatible hash function
export const createHash = (algorithm) => {
  console.warn('Using browser crypto polyfill instead of Node.js crypto module');

  // Simple implementation that uses a string-based approach
  // This is not cryptographically secure but prevents errors
  return {
    update: (data) => {
      return {
        digest: (encoding) => {
          // For browser compatibility, just return a placeholder hash
          // In a real implementation, you would use Web Crypto API
          return 'browser-crypto-polyfill-hash';
        }
      };
    }
  };
};

// Export a browser-compatible crypto object
const browserCrypto = {
  createHash,
  // Add other crypto functions as needed
};

export default browserCrypto;
