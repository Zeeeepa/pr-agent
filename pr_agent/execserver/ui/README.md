# PR-Agent Dashboard UI

This directory contains the UI components for the PR-Agent Dashboard.

## Overview

The PR-Agent Dashboard UI is built with:
- React 18
- TypeScript
- Vite
- React Router
- Axios for API requests
- Bootstrap 5 for styling

## Development

To start the development server:

```bash
npm run dev
```

This will start the Vite development server on port 3000 with hot module replacement.

## Building

To build the UI for production:

```bash
npm run build
```

Or use the provided build script:

```bash
./build.sh
```

This will:
1. Install dependencies
2. Build the application
3. Copy the build output to the static directory

## Project Structure

- `src/` - Source code
  - `components/` - React components
  - `contexts/` - React context providers
  - `utils/` - Utility functions
- `static/` - Static assets and fallback HTML
- `dist/` - Build output (generated)

## API Integration

The UI communicates with the backend API at `/api/v1/` endpoints. The API client is configured in `src/contexts/ApiContext.tsx`.

## Features

- Dashboard with system status and recent events
- Event triggers management
- GitHub workflows integration
- AI assistant chat interface
- Settings management with validation

