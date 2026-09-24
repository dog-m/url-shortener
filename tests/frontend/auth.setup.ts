// inspired by: https://playwright.dev/docs/auth

import { test as setup } from '@playwright/test';
import { SESSION_STATE_ADMIN, SESSION_STATE_USER } from './misc/states';


setup('authenticate as admin', async ({ request }) => {
    await request.post('api/v1/login', {
        form: {
            'username': 'admin@url-shortener.internal',
            'password': 'admin',
        },
        failOnStatusCode: true,
    });
    await request.storageState({ path: SESSION_STATE_ADMIN });
});


setup.skip('authenticate as user', async ({ request }) => {
    await request.post('api/v1/login', {
        form: {
            'username': 'user@url-shortener.internal',
            'password': 'user',
        },
        failOnStatusCode: true,
    });
    await request.storageState({ path: SESSION_STATE_USER });
});
