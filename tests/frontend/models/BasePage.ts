import { type Page, expect } from '@playwright/test';

export class BasePage {
    constructor(protected readonly page: Page) {}

    /**
     * Navigates to a path and verifies the server responded
     * with a success code and didn't redirect to somewhere else.
     */
    async gotoSafe(path: string, expectedUrlPart?: string) {
        const response = await this.page.goto(path);

        // HTTP status
        expect(response?.ok(), `Failed to load ${path}. Status: ${response?.status()}`).toBeTruthy();

        // unexpected redirects
        expect(this.page.url(), `Redirected unexpectedly to ${this.page.url()}`).toContain(
            expectedUrlPart ?? path
        );
    }
}
