import { test, expect } from '@playwright/test';

test('has title', async ({ page }) => {
  await page.goto('');  // main page

  await expect(page).toHaveTitle('URL Shortener service');
});

test('login form is accessible', async ({ page }) => {
  await page.goto('');  // main page

  let loginForm = page.getByRole('form', { name: 'login form' });

  await expect(loginForm.locator('input[name="username"]')).toBeVisible();
  await expect(loginForm.locator('input[name="password"]')).toBeVisible();
  await expect(loginForm.locator('input[type="submit"]')).toBeVisible();
});
