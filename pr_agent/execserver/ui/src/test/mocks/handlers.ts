import { rest } from 'msw';

// Define handlers for mocking API responses
export const handlers = [
  // Mock the settings endpoint
  rest.get('/api/v1/settings', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        GITHUB_TOKEN: '********',
        SUPABASE_URL: 'https://example.supabase.co',
        SUPABASE_ANON_KEY: '********',
      })
    );
  }),

  // Mock the database status endpoint
  rest.get('/api/v1/database/status', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        status: 'connected',
      })
    );
  }),

  // Mock the events endpoint
  rest.get('/api/v1/events', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        {
          id: '1',
          event_type: 'pull_request',
          repository: 'owner/repo',
          created_at: '2023-01-01T12:00:00Z',
          processed: true,
        },
        {
          id: '2',
          event_type: 'push',
          repository: 'owner/repo',
          created_at: '2023-01-01T11:00:00Z',
          processed: false,
        },
      ])
    );
  }),

  // Mock the triggers endpoint
  rest.get('/api/v1/triggers', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        {
          id: '1',
          name: 'PR Review Trigger',
          project_id: 'project1',
          enabled: true,
          conditions: [
            {
              event_type: 'pull_request',
              condition: { action: 'opened' },
            },
          ],
          actions: [
            {
              action_type: 'pr_comment',
              config: { message: 'PR received for review' },
            },
          ],
        },
      ])
    );
  }),

  // Mock the workflows endpoint
  rest.get('/api/v1/workflows', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        {
          id: '1',
          name: 'CI',
          path: '.github/workflows/ci.yml',
          state: 'active',
        },
      ])
    );
  }),

  // Mock the validate settings endpoint
  rest.post('/api/v1/settings/validate', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        valid: true,
        message: 'Settings validated successfully',
      })
    );
  }),

  // Mock the save settings endpoint
  rest.post('/api/v1/settings', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        status: 'success',
        message: 'Settings saved successfully',
      })
    );
  }),
];

