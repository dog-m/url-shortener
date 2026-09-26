import { type Page, type Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';


export interface UserInfoPatch {
    name?: string;
    email?: string;
    password?: string;
}


export class UserProfilePage extends BasePage {
    readonly name: Locator;
    readonly email: Locator;
    readonly password: Locator;
    readonly updateBtn: Locator;
    readonly logoutBtn: Locator;
    readonly errorMsg: Locator;
    readonly greeting: Locator;

    constructor(page: Page) {
        super(page);

        this.name      = page.locator('#name');
        this.email     = page.locator('#email');
        this.password  = page.locator('#password');
        this.updateBtn = page.getByRole('button', { name: 'Update' });
        this.logoutBtn = page.getByRole('button', { name: 'Log-out' });
        this.errorMsg  = page.locator('#msg');
        this.greeting  = page.getByText(/greetings, [\w]*/i);
    }

    async goto() {
        await this.gotoSafe('/profile');
    }

    async updateProfile(patch: UserInfoPatch) {
        if (patch.name)     await this.name.fill(patch.name);
        if (patch.email)    await this.email.fill(patch.email);
        if (patch.password) await this.password.fill(patch.password);

        await this.updateBtn.click({ timeout: 0 });
    }
}
