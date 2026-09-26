import { type Locator, type Page } from "@playwright/test";
import { BasePage } from "./BasePage";

export class IndexPage extends BasePage {
    readonly username: Locator;
    readonly password: Locator;
    readonly loginBtn: Locator;

    constructor(page: Page) {
        super(page);

        const loginForm = page.getByRole('form', { name: 'login form' });
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

        await this.page.waitForURL('/profile', { timeout: 3000, });
    }
}
