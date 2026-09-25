// inspired by: https://playwright.dev/docs/auth

import { BrowserContext } from "@playwright/test";

export const SESSION_STATE_ADMIN = 'playwright/.auth/admin.json';
export const SESSION_STATE_USER  = 'playwright/.auth/user.json';

export async function hasSessionCookie(context: BrowserContext): Promise<boolean> {
    const cookies = await context.cookies();
    return cookies.find(c => c.name === 'u_session') !== undefined;
}
