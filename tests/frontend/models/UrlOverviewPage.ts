import { type Locator, type Page } from '@playwright/test';
import { BasePage } from './BasePage';
import { UrlEditPage } from './UrlEditPage';
import { UrlListPage } from './UrlListPage';


export interface UrlInfoData {
    id: string;
    title: string;
    original_url: string;
    description: string;
    status: string[];
    created_at: string;
    updated_at: string;
}


export class UrlOverviewPage extends BasePage {
    readonly idText: Locator;
    readonly titleText: Locator;
    readonly originalUrlSpan: Locator;
    readonly statusLabels: Locator;
    readonly descriptionText: Locator;
    readonly createdAtText: Locator;
    readonly updatedAtText: Locator;
    readonly statsContainer: Locator;
    readonly copyShortLinkBtn: Locator;
    readonly copyLongUrlBtn: Locator;
    readonly editBtn: Locator;
    readonly deleteBtn: Locator;
    readonly redirectBtn: Locator;


    constructor(page: Page) {
        super(page);

        this.idText           = page.locator('table tr:nth-child(1) td:nth-child(2)');
        this.titleText        = page.locator('table tr:nth-child(2) td:nth-child(2)');
        this.originalUrlSpan  = page.locator('span#addr');
        this.statusLabels     = page.locator('.category-label');
        this.descriptionText  = page.locator('.contains-hashtags');
        this.createdAtText    = page.locator('td:has-text("Created")').locator('.. td:nth-child(2)');
        this.updatedAtText    = page.locator('td:has-text("updated")').locator('.. td:nth-child(2)');
        this.statsContainer   = page.locator('#stats-container');
        this.copyShortLinkBtn = page.locator('#copy-short-link');
        this.copyLongUrlBtn   = page.locator('#copy-long-addr');
        this.editBtn          = page.getByRole('button', { name: 'Edit' });
        this.deleteBtn        = page.locator('button.danger');
        this.redirectBtn      = page.locator('a[href*="/u/"]');
    }


    async goto(urlId: string) {
        await this.gotoSafe(`/urls/${urlId}/overview`);
    }


    async getUrlInfo(): Promise<UrlInfoData> {
        // Extract URL ID from page URL
        const urlParts = this.page.url().split('/');
        const id = urlParts[urlParts.length - 2];

        return {
            id,
            title:        await this.titleText.textContent() ?? '',
            original_url: await this.originalUrlSpan.textContent() ?? '',
            description:  await this.descriptionText.textContent() ?? '',
            status:       (await this.statusLabels.allTextContents()).map(t => t.trim()),
            created_at:   await this.createdAtText.textContent() ?? '',
            updated_at:   await this.updatedAtText.textContent() ?? '',
        };
    }


    async getShortLink(): Promise<string> {
        return `${new URL(this.page.url()).origin}/u/${
            this.page.url().split('/').pop()
        }`;
    }


    async copyShortLink(): Promise<string> {
        await this.copyShortLinkBtn.click();
        const text = await this.page.evaluate(() => {
            return navigator.clipboard.readText();
        });
        return text;
    }


    async copyLongUrl(): Promise<string> {
        await this.copyLongUrlBtn.click();
        const text = await this.page.evaluate(() => {
            return navigator.clipboard.readText();
        });
        return text;
    }


    async goToEdit(): Promise<UrlEditPage> {
        await this.editBtn.click({ timeout: 3000 });
        return new UrlEditPage(this.page);
    }


    async delete(confirm: boolean = false) {
        // intercept the confirmation dialog
        this.page.on('dialog', async dialog => {
            await (confirm ? dialog.accept() : dialog.dismiss());
        });

        await this.deleteBtn.click();

        // should redirect back to /urls after deletion
        await this.page.waitForURL(url => url.pathname === '/urls', {
            timeout: 3000,
        });
        return new UrlListPage(this.page);
    }


    async getStats(): Promise<{ visible: boolean; hasTable: boolean }> {
        const isVisible = await this.statsContainer.isVisible();
        const hasTable = await this.statsContainer.locator('table').count() > 0;
        return { visible: isVisible, hasTable };
    }


    async clickRedirectLink(): Promise<string> {
        const href = await this.redirectBtn.getAttribute('href');
        if (href) {
            await this.redirectBtn.click({ timeout: 3000 });
            return href;
        }
        throw new Error('No redirect link found');
    }
}
