import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test('should load the dashboard', async ({ page }) => {
    await page.goto('/');
    
    // Check that the dashboard title is visible
    await expect(page.locator('h1')).toHaveText('PR-Agent Dashboard');
    
    // Check that the navigation tabs are visible
    await expect(page.getByRole('tab', { name: 'Home' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'Event Triggers' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'GitHub Workflows' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'AI Assistant' })).toBeVisible();
  });

  test('should switch tabs', async ({ page }) => {
    await page.goto('/');
    
    // Click on the Event Triggers tab
    await page.getByRole('tab', { name: 'Event Triggers' }).click();
    
    // Check that the Event Triggers content is visible
    await expect(page.locator('.card-header').filter({ hasText: 'Event Triggers' })).toBeVisible();
    
    // Click on the GitHub Workflows tab
    await page.getByRole('tab', { name: 'GitHub Workflows' }).click();
    
    // Check that the GitHub Workflows content is visible
    await expect(page.locator('.card-header').filter({ hasText: 'GitHub Workflows' })).toBeVisible();
  });

  test('should open and close settings dialog', async ({ page }) => {
    await page.goto('/');
    
    // Click on the Settings button
    await page.locator('button').filter({ hasText: 'Settings' }).click();
    
    // Check that the settings dialog is visible
    await expect(page.locator('.settings-dialog-content')).toBeVisible();
    
    // Close the dialog by clicking the X button
    await page.locator('.settings-dialog-close').click();
    
    // Check that the dialog is no longer visible
    await expect(page.locator('.settings-dialog-content')).not.toBeVisible();
  });

  test('should toggle theme', async ({ page }) => {
    await page.goto('/');
    
    // Get the initial theme
    const initialTheme = await page.evaluate(() => 
      document.documentElement.getAttribute('data-theme') || 'light'
    );
    
    // Click on the Theme button
    await page.locator('button').filter({ hasText: 'Theme' }).click();
    
    // Check that the theme has changed
    const newTheme = await page.evaluate(() => 
      document.documentElement.getAttribute('data-theme') || 'light'
    );
    
    expect(newTheme).not.toEqual(initialTheme);
  });
});

