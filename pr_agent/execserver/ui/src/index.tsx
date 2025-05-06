import React from 'react';
import ReactDOM from 'react-dom/client';

const App = () => {
  return (
    <div>
      <h1>PR Agent UI</h1>
      <p>This is a placeholder for the PR Agent UI.</p>
    </div>
  );
};

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
