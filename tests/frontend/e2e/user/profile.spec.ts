import { test as base, expect } from '@playwright/test';
import { UserProfilePage } from '../../models/UserProfilePage';
import { SESSION_STATE_USER } from '../../misc/states';
import { randomUUID } from 'crypto';


const test = base.extend<{ profilePage: UserProfilePage }>({

    profilePage: async ({ page }, use) => {
        const pom = new UserProfilePage(page);
        await pom.goto();
        await use(pom);
    },

});


test.describe('user profile', () => {
    test.use({
        storageState: SESSION_STATE_USER,
    });


    test('update JSON payload', async ({ page, profilePage }) => {
        const apiEndpoint        = '/api/v1/user/';
        const apiEndpointPattern = `${apiEndpoint}**`;
        const testName  = 'John Doe';
        const testEmail = `john+${randomUUID()}@example.com`;
        const testPwd   = 'qwerty$:123';

        // setup interception
        await page.route(apiEndpointPattern, async (route, request) => {
            if (request.method() === 'PATCH')
                await route.fulfill({
                    status: 200,
                    json: { status: 'ok', }
                });
            else
                await route.continue();
        });

        // set up a listener for the specific request
        const requestPromise = page.waitForRequest(req =>
            req.url().includes(apiEndpoint) && req.method() === 'PATCH', {
                timeout: 1000,
            }
        );

        // act
        await profilePage.updateProfile({
            name: testName,
            email: testEmail,
            password: testPwd,
        });

        // wait for the request to be intercepted
        let payload = (await requestPromise).postDataJSON();

        // verify
        expect(payload).toEqual({
            name: testName,
            email: testEmail,
            password: testPwd,
        });

        expect(await profilePage.greeting.textContent()).toBe('Greetings, user.');
    });

});
