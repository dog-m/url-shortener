import { type Locator, type Page } from "@playwright/test";

export class IndexPage {
    page: Page;
    username: Locator;
    password: Locator;
    loginBtn: Locator;

    constructor(page: Page) {
        this.page = page;

        let loginForm = page.getByRole('form', { name: 'login form' });
        this.username = loginForm.locator('input[name="username"]');
        this.password = loginForm.locator('input[name="password"]');
        this.loginBtn = loginForm.locator('button[type="submit"]');
    }

    async goto() {
        await this.page.goto('', { timeout: 1000, });  // main page
    }

    async singInAsAdmin() {
        await this.username.fill('admin@url-shortener.internal');
        await this.password.fill('admin');
        await this.loginBtn.click();

        await this.page.waitForURL('/profile', { timeout: 5000, });
    }
}
