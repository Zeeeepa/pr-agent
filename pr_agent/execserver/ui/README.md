# PR-Agent UI

This is the frontend UI for the PR-Agent application, built with React, TypeScript, and Vite.

## Development

### Prerequisites

- Node.js (v16 or later)
- npm (v7 or later)

### Setup

1. Install dependencies:

```bash
npm install
```

2. Start the development server:

```bash
npm run dev
```

This will start the development server at http://localhost:3000.

## Building for Production

To build the application for production:

```bash
# Using npm
npm run build

# Or using the build script
./build.sh
```

The build output will be placed in the `static` directory, which is served by the FastAPI backend.

## Project Structure

- `src/` - Source code for the React application
  - `App.tsx` - Main application component
  - `main.tsx` - Entry point
  - `index.css` - Global styles
- `static/` - Build output directory (served by FastAPI)
- `vite.config.ts` - Vite configuration
- `tsconfig.json` - TypeScript configuration
- `build.sh` - Build script for production

## API Integration

The frontend communicates with the backend API at `/api/v1/`. In development mode, API requests are proxied to the backend server running at http://localhost:8000.

## Troubleshooting

If you encounter issues with the frontend not loading properly:

1. Make sure the React application is built (`npm run build`)
2. Check that the build output is in the `static` directory
3. Verify that the FastAPI server is properly serving the static files
4. Check the browser console for any errors

