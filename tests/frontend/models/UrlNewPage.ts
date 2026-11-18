import { type Locator, type Page } from '@playwright/test';
import { BasePage, GotoOptions } from './BasePage';
import { nullIfEmpty } from '../misc/utils';


export interface UrlCreateData {
    original_url: string;
    is_active: boolean;
    is_open_access: boolean;
    title: string;
    description: string;
    expires_at: string | null;
}


export class UrlNewPage extends BasePage {
    readonly originalUrlInput: Locator;
    readonly isActiveCheckbox: Locator;
    readonly isOpenAccessCheckbox: Locator;
    readonly titleInput: Locator;
    readonly descriptionTextarea: Locator;
    readonly expiresAtInput: Locator;
    readonly submitBtn: Locator;
    readonly messageEl: Locator;


    constructor(page: Page) {
        super(page);

        const form = page.locator('form#main-form');
        this.originalUrlInput     = form.locator('input[name="original_url"]');
        this.isActiveCheckbox     = form.locator('input[name="is_active"]');
        this.isOpenAccessCheckbox = form.locator('input[name="is_open_access"]');
        this.titleInput           = form.locator('input[name="title"]');
        this.descriptionTextarea  = form.locator('textarea[name="description"]');
        this.expiresAtInput       = form.locator('input[name="expires_at"]');
        this.submitBtn            = form.locator('button.create');
        this.messageEl = page.locator('#msg');
    }


    async goto(options?: GotoOptions) {
        await this.gotoSafe('/urls/new', options);
    }


    async fill(data: Partial<UrlCreateData>) {
        if (data.original_url) await this.originalUrlInput.fill(data.original_url);
        if (data.title)        await this.titleInput.fill(data.title);
        if (data.description)  await this.descriptionTextarea.fill(data.description);
        await this.checkOrUncheck(this.isActiveCheckbox, data.is_active);
        await this.checkOrUncheck(this.isOpenAccessCheckbox, data.is_open_access);
        if (data.expires_at)
            await this.expiresAtInput.fill(data.expires_at);
        else
            await this.expiresAtInput.clear();
    }


    async getFormValues(): Promise<UrlCreateData> {
        return {
            original_url:   await this.originalUrlInput.inputValue(),
            is_active:      await this.isActiveCheckbox.isChecked(),
            is_open_access: await this.isOpenAccessCheckbox.isChecked(),
            title:          await this.titleInput.inputValue(),
            description:    await this.descriptionTextarea.inputValue(),
            expires_at:     nullIfEmpty(await this.expiresAtInput.inputValue()),
        };
    }


    async create(data: Partial<UrlCreateData>) {
        await this.fill(data);
        await this.submitBtn.click({ timeout: 0 });

        // Wait for the success redirect to overview page
        await this.page.waitForURL(url => url.pathname.includes('/overview'), {
            timeout: 3000,
        });

        // Extract the URL ID from the path
        const urlId = this.page.url().split('/').pop();
        if (!urlId) {
            throw new Error('Could not extract URL ID from redirect path');
        }

        return urlId;
    }


    async getMessage(): Promise<string> {
        return await this.messageEl.textContent() ?? '';
    }


    async isMessageOk(): Promise<boolean> {
        return this.messageEl.locator('.msg-ok').isVisible();
    }


    async isMessageError(): Promise<boolean> {
        return this.messageEl.locator('.msg-err').isVisible();
    }
}
