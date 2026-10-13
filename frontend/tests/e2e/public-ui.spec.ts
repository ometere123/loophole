import {expect, test, type Page} from '@playwright/test';

type WalletOptions = {chainId?: string; reject?: boolean};

async function installWallet(page: Page, options: WalletOptions = {}) {
  await page.addInitScript(({chainId, reject}) => {
    const listeners: Record<string, Array<(...args: unknown[]) => void>> = {};
    let connected = false;
    const emit = (event: string, ...args: unknown[]) => {
      for (const listener of listeners[event] ?? []) listener(...args);
    };
    const ethereum = {
      // A minimal EIP-1193 provider; no wallet-vendor extensions are assumed.
      __emit: emit,
      selectedAddress: '0x951e6b75530774ff82321a5ae54e14f778f0c855',
      chainId,
      on(event: string, listener: (...args: unknown[]) => void) {
        listeners[event] ??= [];
        listeners[event].push(listener);
      },
      removeListener() {},
      async request({method}: {method: string}) {
        if (reject && method === 'eth_requestAccounts') {
          const error = Object.assign(new Error('User rejected the request'), {code: 4001});
          throw error;
        }
        if (method === 'eth_requestAccounts') {
          connected = true;
          return [this.selectedAddress];
        }
        if (method === 'eth_accounts') return connected ? [this.selectedAddress] : [];
        if (method === 'eth_chainId') return this.chainId;
        if (method === 'wallet_switchEthereumChain') {
          this.chainId = '0xf22f';
          emit('chainChanged', this.chainId);
          return null;
        }
        if (method === 'wallet_addEthereumChain') return null;
        throw new Error(`Unsupported wallet method: ${method}`);
      },
    };
    Object.defineProperty(window, 'ethereum', {value: ethereum, configurable: true});
  }, {chainId: options.chainId ?? '0xf22f', reject: options.reject ?? false});
}

test('public home and create screens expose the live deployment state', async ({page}) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/Loophole/i);
  await expect(page.getByRole('heading', {name: /good rules need/i})).toBeVisible();
  await expect(page.getByRole('link', {name: /explore challenges/i})).toBeVisible();
  await page.goto('/create');
  await expect(page.getByRole('heading', {name: /what's the challenge/i})).toBeVisible();
});

test('injected wallet connection is visible on Studionet', async ({page}) => {
  await installWallet(page);
  await page.goto('/');
  await page.getByRole('button', {name: /connect wallet/i}).click();
  await expect(page.getByRole('button', {name: /0x951e/i})).toBeVisible();
});

test('wrong network blocks wallet actions', async ({page}) => {
  await installWallet(page, {chainId: '0x1'});
  await page.goto('/');
  await page.getByRole('button', {name: /connect wallet/i}).click();
  await expect(page.getByRole('button', {name: /switch network/i})).toBeVisible();
});

test('wallet rejection is surfaced', async ({page}) => {
  await installWallet(page, {reject: true});
  await page.goto('/');
  await page.getByRole('button', {name: /connect wallet/i}).click();
  await expect(page.locator('.global-alert')).toContainText(/rejected/i);
});

test('mobile navigation opens without horizontal overflow', async ({page}) => {
  await page.setViewportSize({width: 390, height: 844});
  await page.goto('/');
  await page.getByRole('button', {name: /toggle menu/i}).click();
  await expect(page.getByRole('navigation', {name: /main navigation/i})).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
});

test('wallet network change is reflected without a reload', async ({page}) => {
  await installWallet(page);
  await page.goto('/');
  await page.getByRole('button', {name: /connect wallet/i}).click();
  await expect(page.getByRole('button', {name: /0x951e/i})).toBeVisible();
  await page.evaluate(() => {
    const wallet = (window as any).ethereum;
    wallet.chainId = '0x1';
    wallet.__emit('chainChanged', '0x1');
  });
  await expect(page.getByRole('button', {name: /switch network/i})).toBeVisible();
  await page.getByRole('button', {name: /switch network/i}).click();
  await expect(page.getByRole('button', {name: /0x951e/i})).toBeVisible();
});

test('account change invalidates previous wallet identity', async ({page}) => {
  await installWallet(page);
  await page.goto('/');
  await page.getByRole('button', {name: /connect wallet/i}).click();
  await page.evaluate(() => {
    const wallet = (window as any).ethereum;
    wallet.selectedAddress = '0x2222222222222222222222222222222222222222';
    wallet.__emit('accountsChanged', [wallet.selectedAddress]);
  });
  await expect(page.getByRole('button', {name: /0x2222/i})).toBeVisible();
  await expect(page.getByRole('button', {name: /0x951e/i})).toHaveCount(0);
});

test('creation wizard rejects incomplete rulebooks before any wallet submission', async ({page}) => {
  await installWallet(page);
  await page.goto('/create');
  await page.getByPlaceholder('e.g. The Originality Olympics').fill('Unclear eligibility');
  await page.getByPlaceholder(/Our campaign should reward educational/i).fill('Reward original meaningful educational work rather than spam posts.');
  await page.getByRole('button', {name: /continue/i}).click();
  await expect(page.getByRole('heading', {name: /write the rulebook/i})).toBeVisible();
  await page.getByRole('button', {name: /continue/i}).click();
  await expect(page.locator('.wizard-card .notice.danger[role="alert"]')).toContainText(/Publish at least 20 characters of rules/i);
  await expect(page.getByRole('heading', {name: /write the rulebook/i})).toBeVisible();
});
