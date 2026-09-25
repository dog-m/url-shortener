import { test as base, expect } from '@playwright/test';
import { IndexPage } from '../models/IndexPage';


// inspired by: https://playwright.dev/docs/test-fixtures

const test = base.extend<{ indexPage: IndexPage }>({

    indexPage: async ({ page }, use) => {
        const pom = new IndexPage(page);
        await pom.goto();
        await use(pom);
    },

});


test.describe('index', () => {
    test.use({
        storageState: undefined,
        locale: 'en-US',  // todo: unused
    });


    test('has title', async ({ indexPage }) => {
        await expect(indexPage.page).toHaveTitle('URL Shortener service', { timeout: 100 });
    });


    test('login form is accessible', async ({ indexPage }) => {
        await expect(indexPage.username).toBeVisible();
        await expect(indexPage.password).toBeVisible();
        await expect(indexPage.loginBtn).toBeVisible();
    });


    test('sign-in as admin', async ({ indexPage }) => {
        await indexPage.singInAsAdmin();
        await expect(indexPage.page).toHaveTitle('Profile / URL Shortener service', { timeout: 100 });
    });
});

