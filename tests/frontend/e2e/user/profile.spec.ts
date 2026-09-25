import { test as base, expect } from '@playwright/test';
import { UserProfilePage } from '../../models/UserProfilePage';
import { SESSION_STATE_ADMIN } from '../../misc/states';
import { randomUUID } from 'crypto';


const test = base.extend<{ profilePage: UserProfilePage }>({

    profilePage: async ({ page }, use) => {
        const profilePage = new UserProfilePage(page);
        await profilePage.goto();
        await use(profilePage);
    },

});


test.describe('user profile', () => {
    test.use({
        storageState: SESSION_STATE_ADMIN,
    });


    test('should send the correct JSON payload when updating profile', async ({ page, profilePage }) => {
        const testName  = 'John Doe';
        const testEmail = `john+${randomUUID()}@example.com`;
        const testPwd   = 'qwerty$:123';

        // set up a listener for the specific request
        const requestPromise = page.waitForRequest(
            req => req.url().includes('/api/v1/user/') && req.method() === 'PATCH', {
                timeout: 5000,
            }
        );

        // act
        await profilePage.updateProfile({
            name: testName,
            email: testEmail,
            password: testPwd,
        });

        // wait for the request to be intercepted
        const request = await requestPromise;

        // verify
        const payload = request.postDataJSON();
        expect(payload).toEqual({
            name: testName,
            email: testEmail,
            password: testPwd,
        });
    });

});
