import { rest } from 'msw';

export const handlers = [
  // Mock API endpoints
  rest.get('/api/v1/events', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        {
          id: '1',
          type: 'pull_request',
          action: 'opened',
          title: 'Test PR',
          url: 'https://github.com/test/repo/pull/1',
          created_at: '2025-05-06T04:30:00Z'
        }
      ])
    );
  }),
  
  rest.get('/api/v1/status', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        status: 'healthy',
        version: '1.0.0',
        uptime: 3600
      })
    );
  }),
  
  rest.post('/api/v1/settings', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        success: true,
        message: 'Settings updated successfully'
      })
    );
  })
];

