import { test, expect } from '@playwright/test';

test('synthetic case shows aligned evidence and labeled result', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('SYNTHETIC DEMONSTRATION', { exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Create demo case' }).click();
  await expect(page.getByRole('heading', { name: 'Radiology / Imaging' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Genomics & Liquid Biopsy' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Clinical & EHR' })).toBeVisible();
  await expect(page.getByText('Required inputs aligned')).toBeVisible();
  await page.getByRole('button', { name: 'Run research inference' }).click();
  await expect(page.getByText('SYNTHETIC FIXTURE SCORE')).toBeVisible();
  await expect(page.getByText(/not a trained model or clinical risk estimate/)).toBeVisible();
  await page.getByRole('button', { name: 'Model evaluation' }).click();
  await expect(page.getByText('Real patients evaluated')).toBeVisible();
  await expect(page.getByText('None', { exact: true })).toBeVisible();
});
