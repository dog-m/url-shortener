// inspired by: https://stackoverflow.com/a/79820020

import { test as teardown } from '@playwright/test';
import { SESSION_STATE_ADMIN, SESSION_STATE_USER } from './misc/states';
import { unlink } from 'node:fs';


teardown('cleanup sessions', async () => {
    unlink(SESSION_STATE_ADMIN, err => {
        if (err) throw err;
        console.log('Admin session removed');
    });
    unlink(SESSION_STATE_USER, err => {
        if (err) throw err;
        console.log('User session removed');
    });
});
