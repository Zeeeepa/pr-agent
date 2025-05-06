# PR-Agent UI

This directory contains the UI components for the PR-Agent dashboard.

## Directory Structure

```
ui/
├── src/                  # React source code
│   ├── components/       # UI components
│   ├── App.tsx           # Main application component
│   ├── main.tsx          # Entry point
│   └── ...
├── static/               # Static files served by FastAPI
│   ├── index.html        # HTML entry point
│   ├── js/               # JavaScript files
│   └── ...
├── package.json          # NPM dependencies
├── vite.config.ts        # Vite configuration
└── build.sh              # Build script
```

## Development

### Prerequisites

- Node.js (v14 or later)
- npm or yarn

### Setup

1. Install dependencies:

```bash
cd pr_agent/execserver/ui
npm install
```

2. Start the development server:

```bash
npm run dev
```

This will start a development server at http://localhost:3000 with hot reloading.

## Building for Production

To build the UI for production:

```bash
cd pr_agent/execserver/ui
./build.sh
```

This script will:
1. Install dependencies
2. Build the React application
3. Copy the build files to the `static` directory

## Integration with FastAPI

The UI is served by the FastAPI application in `pr_agent/execserver/app.py`. The FastAPI app:

1. Mounts the `static` directory to serve static files
2. Provides an API endpoint for the UI to communicate with
3. Serves the React application for all non-API routes

## Troubleshooting

If the UI is not rendering:

1. Check that the React application has been built and the files are in the `static` directory
2. Verify that the FastAPI app is correctly serving the static files
3. Check the browser console for any JavaScript errors
4. Ensure that the API endpoints are accessible from the UI

