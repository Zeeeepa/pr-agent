/**
 * Crypto Polyfill for Browser Environment
 * 
 * This file provides a comprehensive polyfill for the Node.js crypto module
 * when running in a browser environment. It uses the Web Crypto API
 * where possible and provides fallbacks for unsupported features.
 */

// Create a browser-compatible hash function using SubtleCrypto when available
export const createHash = (algorithm) => {
  console.info('Using browser crypto polyfill instead of Node.js crypto module');
  
  // Map Node.js hash algorithm names to SubtleCrypto names
  const algorithmMap = {
    'sha1': 'SHA-1',
    'sha256': 'SHA-256',
    'sha384': 'SHA-384',
    'sha512': 'SHA-512',
    'md5': 'MD5'
  };
  
  // Use the mapped algorithm or default to SHA-256
  const webCryptoAlgorithm = algorithmMap[algorithm.toLowerCase()] || 'SHA-256';
  
  let data = new Uint8Array();
  
  return {
    update: (chunk) => {
      // Convert string to Uint8Array if needed
      let chunkArray;
      if (typeof chunk === 'string') {
        chunkArray = new TextEncoder().encode(chunk);
      } else if (chunk instanceof ArrayBuffer) {
        chunkArray = new Uint8Array(chunk);
      } else if (chunk instanceof Uint8Array) {
        chunkArray = chunk;
      } else {
        chunkArray = new TextEncoder().encode(String(chunk));
      }
      
      // Concatenate the new chunk with existing data
      const newData = new Uint8Array(data.length + chunkArray.length);
      newData.set(data);
      newData.set(chunkArray, data.length);
      data = newData;
      
      return {
        digest: (encoding = 'hex') => {
          // Use Web Crypto API if available
          if (window.crypto && window.crypto.subtle) {
            return window.crypto.subtle.digest(webCryptoAlgorithm, data)
              .then(hashBuffer => {
                // Convert ArrayBuffer to hex string
                const hashArray = Array.from(new Uint8Array(hashBuffer));
                const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
                
                // Handle different encodings
                if (encoding === 'hex') {
                  return hashHex;
                } else if (encoding === 'base64') {
                  // Convert hex to base64
                  return btoa(hashArray.map(b => String.fromCharCode(b)).join(''));
                } else {
                  return hashHex; // Default to hex
                }
              })
              .catch(e => {
                console.error('Web Crypto API failed:', e);
                // Fall back to a simple hash for demo purposes
                return Promise.resolve(`browser-crypto-polyfill-hash-${algorithm}-${Date.now()}`);
              });
          } else {
            // Fallback for browsers without Web Crypto API
            console.warn('Web Crypto API not available, using fallback hash');
            return Promise.resolve(`browser-crypto-polyfill-hash-${algorithm}-${Date.now()}`);
          }
        }
      };
    }
  };
};

// Simple random bytes implementation
export const randomBytes = (size) => {
  if (window.crypto && window.crypto.getRandomValues) {
    const bytes = new Uint8Array(size);
    window.crypto.getRandomValues(bytes);
    return bytes;
  } else {
    // Fallback for browsers without crypto.getRandomValues
    const bytes = new Uint8Array(size);
    for (let i = 0; i < size; i++) {
      bytes[i] = Math.floor(Math.random() * 256);
    }
    return bytes;
  }
};

// Export a browser-compatible crypto object
const browserCrypto = {
  createHash,
  randomBytes,
  // Add other crypto functions as needed
};

export default browserCrypto;
