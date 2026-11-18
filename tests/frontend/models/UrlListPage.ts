import { type Locator, type Page, expect } from '@playwright/test';
import { BasePage, GotoOptions } from './BasePage';
import { UrlOverviewPage } from './UrlOverviewPage';


export interface UrlListItem {
    id: string;
    title: string;
    description: string;
    categories: string[];
}


export class UrlListPage extends BasePage {
    readonly addUrlBtn: Locator;
    readonly searchInput: Locator;
    readonly sortSelect: Locator;
    readonly ascSelect: Locator;
    readonly searchButton: Locator;
    readonly urlContainer: Locator;
    readonly urlItems: Locator;
    readonly noResults: Locator;
    readonly prevPageLink: Locator;
    readonly nextPageLink: Locator;
    readonly pageDisplay: Locator;


    constructor(page: Page) {
        super(page);

        this.addUrlBtn = page.locator('a[href="/urls/new"] > button');

        this.searchInput  = page.locator('input[name="q"]');
        this.sortSelect   = page.locator('select[name="sort"]');
        this.ascSelect    = page.locator('select[name="asc"]');
        this.searchButton = page.getByRole('button', { name: 'Show!' });

        this.urlContainer = page.locator('.url-container');
        this.urlItems     = page.locator('.url-item');
        this.noResults    = page.locator('p:has-text("No results")');

        this.prevPageLink = page.locator('a[rel="prev"]');
        this.nextPageLink = page.locator('a[rel="next"]');
        this.pageDisplay  = page.locator('.page-number');
    }


    async goto(options?: GotoOptions) {
        await this.gotoSafe('/urls', options);
    }


    async search(query: string) {
        await this.searchInput.fill(query);
        await this.searchButton.click();
        await this.page.waitForURL(
            url => url.pathname === '/urls' && url.searchParams.has('q'),
            { timeout: 3000 }
        );
    }


    async sort(by: string, asc: boolean = true) {
        await this.sortSelect.selectOption(by);
        await this.ascSelect.selectOption(asc ? 'on' : 'off');
        await this.searchButton.click();
    }


    async filterByCategory(category: string) {
        const url = new URL(this.page.url());
        const searchParams = new URLSearchParams(url.search);
        searchParams.set('c', category);
        url.search = searchParams.toString();
        await this.page.goto(url.toString());
        await this.page.waitForURL(url.toString(), { timeout: 3000 });
    }


    async filterByHashtag(tag: string) {
        // Click the hashtag link in the description
        const hashtagLink = this.page.locator(`a:has-text("#${tag}")`);
        await expect(hashtagLink.first()).toBeVisible({ timeout: 3000 });
        await hashtagLink.first().click();
    }


    async goPrevPage() {
        await expect(this.prevPageLink).toBeVisible();
        await this.prevPageLink.click();
    }


    async goNextPage() {
        await expect(this.nextPageLink).toBeVisible();
        await this.nextPageLink.click();
    }


    async getUrls(): Promise<UrlListItem[]> {
        const items = await this.urlItems.all();
        const urls: UrlListItem[] = [];

        for (const item of items) {
            const link = item.locator('a');
            await expect(link).toBeVisible({ timeout: 2000 });

            // URL ID link format: [<code>u/xxx</code>] <span>title</span>
            const idText = await item.locator('code').innerText();
            const id = idText.replace('u/', '');
            const title = await item.locator('.title span').innerText();

            // Description text
            const descText = await item.locator('.contains-hashtags').innerText();
            // Parse hashtags from description
            const hashtags = descText.match(/#\w+/g) ?? [];

            // Category labels (excluding hashtags)
            const categoryElements = item.locator('.category-label');
            const categories = [];
            for (const el of await categoryElements.all()) {
                const label = await el.textContent();
                if (label) {
                    categories.push(label.trim());
                }
            }

            // Filter out hashtags from categories (they're separate links)
            urls.push({
                id,
                title,
                description: descText.replace(/#\w+/g, '').trim(),
                categories,
            });
        }

        return urls;
    }


    async getUrlItemsCount(): Promise<number> {
        return this.urlItems.count();
    }


    async findUrlItemById(id: string): Promise<Locator | null> {
        const items = await this.urlItems.all();
        for (const item of items) {
            const code = item.locator('code');
            const codeText = await code.textContent();
            if (codeText === `u/${id}`) {
                return item;
            }
        }
        return null;
    }


    async openUrlOverview(urlId: string): Promise<UrlOverviewPage> {
        const item = await this.findUrlItemById(urlId);
        if (item) {
            const link = item.locator('.title a');
            await link.click({ timeout: 3000 });
            return new UrlOverviewPage(this.page);
        }

        throw new Error(`URL with id "${urlId}" not found in the list`);
    }


    async openUrlOverviewByIndex(index: number): Promise<UrlOverviewPage> {
        const items = await this.urlItems.all();
        if (index >= items.length) {
            throw new Error(`Index ${index} is out of range. Only ${items.length} items visible.`);
        }
        const link = items[index].locator('.title a');
        await link.click({ timeout: 3000 });
        return new UrlOverviewPage(this.page);
    }


    async goToNewUrlPage() {
        await this.addUrlBtn.click();
    }


    async getCurrentPage(): Promise<number> {
        return parseInt(await this.pageDisplay.textContent() ?? '1', 10);
    }


    async hasNoResults(): Promise<boolean> {
        return this.noResults.isVisible();
    }
}
