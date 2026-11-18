import { type Locator, type Page, expect } from '@playwright/test';
import { BasePage, type GotoOptions } from './BasePage';
import { nullIfEmpty } from '../misc/utils';


export interface UrlEditData {
    original_url: string;
    is_active: boolean;
    is_open_access: boolean;
    title: string;
    description: string;
    expires_at: string | null;
}


export class UrlEditPage extends BasePage {
    readonly pageHeading: Locator;
    readonly originalUrlInput: Locator;
    readonly isActiveChk: Locator;
    readonly isOpenAccessChk: Locator;
    readonly titleInput: Locator;
    readonly descriptionBox: Locator;
    readonly expiresAtInput: Locator;
    readonly submitBtn: Locator;
    readonly messageEl: Locator;


    constructor(page: Page) {
        super(page);

        this.pageHeading = page.locator('h3');

        const form = page.locator('form#main-form');
        this.originalUrlInput = form.locator('input[name="original_url"]');
        this.isActiveChk      = form.locator('input[name="is_active"]');
        this.isOpenAccessChk  = form.locator('input[name="is_open_access"]');
        this.titleInput       = form.locator('input[name="title"]');
        this.descriptionBox   = form.locator('textarea[name="description"]');
        this.expiresAtInput   = form.locator('input[name="expires_at"]');
        this.submitBtn        = form.locator('button[type="submit"]');

        this.messageEl = page.locator('#msg');
    }


    async goto(urlId: string, options?: GotoOptions) {
        await this.gotoSafe(`/urls/${urlId}/edit`, options);
    }


    async getFormValues(): Promise<UrlEditData> {
        return {
            original_url:   await this.originalUrlInput.inputValue(),
            is_active:      await this.isActiveChk.isChecked(),
            is_open_access: await this.isOpenAccessChk.isChecked(),
            title:          await this.titleInput.inputValue(),
            description:    await this.descriptionBox.inputValue(),
            expires_at:     nullIfEmpty(await this.expiresAtInput.inputValue()),
        };
    }


    async fill(data: Partial<UrlEditData>) {
        if (data.original_url) await this.originalUrlInput.fill(data.original_url);
        if (data.title)        await this.titleInput.fill(data.title);
        if (data.description)  await this.descriptionBox.fill(data.description);
        await this.checkOrUncheck(this.isActiveChk, data.is_active);
        await this.checkOrUncheck(this.isOpenAccessChk, data.is_open_access);
        if (data.expires_at)
            await this.expiresAtInput.fill(data.expires_at);
        else
            await this.expiresAtInput.clear();
    }


    async save() {
        await this.submitBtn.click({ timeout: 0 });
        // waiting for the update to register
        await expect(this.messageEl).toContainText('Updated successfully', { timeout: 1000, });
    }


    async update(data: Partial<UrlEditData>) {
        await this.fill(data);
        await this.save();
    }


    async isMessageOk(): Promise<boolean> {
        return this.messageEl.locator('.msg-ok').isVisible({ timeout: 100, });
    }


    async isMessageError(): Promise<boolean> {
        return this.messageEl.locator('.msg-err').isVisible({ timeout: 100, });
    }


    async getMessage(): Promise<string> {
        return await this.messageEl.textContent({ timeout: 100, }) ?? '';
    }
}
