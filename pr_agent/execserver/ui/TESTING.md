# PR Review Automator UI Testing Guide

This document provides an overview of the testing approach for the PR Review Automator UI.

## Testing Levels

### Unit Tests

Unit tests focus on testing individual UI components in isolation.

- **Framework**: Vitest + React Testing Library
- **Location**: `src/components/__tests__/*.test.tsx`
- **Run Command**: `npm test` or `npm run test:watch` for watch mode

#### Writing Unit Tests

1. Import the component and testing utilities:
   ```tsx
   import { render, screen } from '../../test/test-utils';
   import MyComponent from '../MyComponent';
   ```

2. Create test cases:
   ```tsx
   describe('MyComponent', () => {
     it('renders correctly', () => {
       render(<MyComponent />);
       expect(screen.getByText('Expected Text')).toBeInTheDocument();
     });
   });
   ```

3. Test user interactions:
   ```tsx
   it('handles click events', async () => {
     const { user } = render(<MyComponent />);
     await user.click(screen.getByRole('button'));
     expect(screen.getByText('Clicked')).toBeInTheDocument();
   });
   ```

### Integration Tests

Integration tests verify that components work together correctly and that the UI interacts properly with the backend.

- **Framework**: Vitest + React Testing Library + MSW
- **Location**: `src/components/__tests__/*.test.tsx` (with integration focus)
- **Run Command**: `npm test`

#### Writing Integration Tests

1. Import the components and testing utilities:
   ```tsx
   import { render, screen, waitFor } from '../../test/test-utils';
   import { server } from '../../test/mocks/server';
   import { rest } from 'msw';
   import MyComponent from '../MyComponent';
   ```

2. Override API responses for specific tests:
   ```tsx
   it('handles API errors', async () => {
     // Override the default handler for a specific endpoint
     server.use(
       rest.get('/api/data', (req, res, ctx) => {
         return res(ctx.status(500));
       })
     );
     
     render(<MyComponent />);
     
     await waitFor(() => {
       expect(screen.getByText('Error loading data')).toBeInTheDocument();
     });
   });
   ```

### End-to-End Tests

End-to-end tests validate complete user workflows and ensure the application works as expected from a user's perspective.

- **Framework**: Playwright
- **Location**: `e2e/*.spec.ts`
- **Run Command**: `npm run test:e2e` or `npm run test:e2e:ui` for UI mode

#### Writing E2E Tests

1. Create a test file:
   ```ts
   import { test, expect } from '@playwright/test';

   test('user can log in', async ({ page }) => {
     await page.goto('/');
     await page.fill('input[name="username"]', 'testuser');
     await page.fill('input[name="password"]', 'password');
     await page.click('button[type="submit"]');
     await expect(page.locator('h1')).toHaveText('Dashboard');
   });
   ```

### Visual Regression Tests

Visual regression tests ensure the UI appearance remains consistent and detect unintended visual changes.

- **Framework**: Storybook + Chromatic
- **Location**: `src/components/*.stories.tsx`
- **Run Command**: `npm run storybook` for development, `npm run chromatic` for visual testing

#### Writing Storybook Stories

1. Create a story file:
   ```tsx
   import type { Meta, StoryObj } from '@storybook/react';
   import MyComponent from './MyComponent';

   const meta: Meta<typeof MyComponent> = {
     title: 'Components/MyComponent',
     component: MyComponent,
     parameters: {
       layout: 'centered',
     },
     tags: ['autodocs'],
   };

   export default meta;
   type Story = StoryObj<typeof MyComponent>;

   export const Default: Story = {
     args: {
       // Component props
     },
   };
   ```

## Test Utilities

### Mock Service Worker (MSW)

MSW is used to mock API responses for testing. The configuration is in:

- `src/test/mocks/handlers.ts` - API response handlers
- `src/test/mocks/server.ts` - MSW server setup

To add a new API mock:

1. Add a handler to `handlers.ts`:
   ```ts
   rest.get('/api/new-endpoint', (req, res, ctx) => {
     return res(
       ctx.status(200),
       ctx.json({
         // Response data
       })
     );
   }),
   ```

### Custom Render Function

A custom render function is provided in `src/test/test-utils.tsx` that wraps components with necessary providers and sets up user-event.

Usage:
```tsx
const { user } = render(<MyComponent />);
await user.click(screen.getByRole('button'));
```

## CI/CD Integration

Tests are automatically run in GitHub Actions on pull requests and pushes to the main branch. The workflow is defined in `.github/workflows/ui-tests.yml`.

The workflow includes:
- Unit and integration tests with coverage reporting
- End-to-end tests with Playwright
- Visual regression tests with Storybook and Chromatic

## Best Practices

1. **Test Component Behavior, Not Implementation**: Focus on what the component does, not how it does it.

2. **Use Role-Based Queries**: Prefer queries like `getByRole` over `getByTestId` for better accessibility testing.

3. **Test User Interactions**: Ensure components respond correctly to user actions.

4. **Mock External Dependencies**: Use MSW to mock API calls and other external dependencies.

5. **Keep Tests Isolated**: Each test should be independent and not rely on the state from other tests.

6. **Test Edge Cases**: Include tests for error states, loading states, and boundary conditions.

7. **Maintain Visual Tests**: Update visual snapshots when intentional UI changes are made.

## Troubleshooting

### Tests Failing in CI but Passing Locally

- Check for environment-specific issues (timezone, locale, etc.)
- Ensure all dependencies are properly installed in CI
- Check for race conditions or timing issues

### Visual Tests Failing

- Review the visual differences in Chromatic
- Update snapshots if the changes are intentional
- Fix the component if the changes are unintentional

