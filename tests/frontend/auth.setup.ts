// inspired by: https://playwright.dev/docs/auth

import { expect, test as setup } from '@playwright/test';
import { hasSessionCookie, SESSION_STATE_ADMIN, SESSION_STATE_USER } from './misc/states';


setup('authenticate as admin', async ({ request, context }) => {
    let response = await request.post('api/v1/login', {
        form: {
            'username': 'admin@url-shortener.internal',
            'password': 'admin',
        },
        failOnStatusCode: true,
    });

    // sanity checks
    expect(response.ok()).toBeTruthy();
    expect(hasSessionCookie(context)).toBeTruthy();

    await request.storageState({ path: SESSION_STATE_ADMIN });
});


setup('authenticate as user', async ({ request, context }) => {
    let response = await request.post('api/v1/login', {
        form: {
            'username': 'user@url-shortener.internal',
            'password': 'user',
        },
        failOnStatusCode: true,
    });

    // sanity checks
    expect(response.ok()).toBeTruthy();
    expect(hasSessionCookie(context)).toBeTruthy();

    await request.storageState({ path: SESSION_STATE_USER });
});
