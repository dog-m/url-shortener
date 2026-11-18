import { Locator, type Page, expect } from '@playwright/test';


export type GotoOptions = Parameters<Page['goto']>[1];
export type CheckUncheckOptions = Parameters<Locator['check']>[0];


export class BasePage {
    constructor(readonly page: Page) {}

    /**
     * Navigates to a path and verifies the server responded
     * with a success code and didn't redirect to somewhere else.
     */
    async gotoSafe(path: string, options?: GotoOptions, expectedUrlPart?: string) {
        const response = await this.page.goto(path, options);

        // HTTP status
        expect(response?.ok(), `Failed to load ${path}. Status: ${response?.status()}`).toBeTruthy();

        // unexpected redirects
        expect(this.page.url(), `Redirected unexpectedly to ${this.page.url()}`).toContain(
            expectedUrlPart ?? path
        );
    }


    async checkOrUncheck(checkbox: Locator, checked?: boolean, options?: CheckUncheckOptions) {
        if (checked)
            await checkbox.check(options);
        else
            await checkbox.uncheck(options);
    }
}
