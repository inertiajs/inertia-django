import { expect, test } from '@playwright/test'

test('uses Django partial-reload and once-prop responses with the v3 client', async ({ page }) => {
  await page.goto('/v3/nested/')
  await expect(page.getByTestId('props')).toContainText('en-US')
  await expect(page.getByTestId('props')).toContainText('UTC')

  const response = page.waitForResponse(
    (candidate) => candidate.request().headers()['x-inertia-partial-data'] === 'config.locale',
  )
  await page.getByRole('button', { name: 'Reload locale' }).click()
  await response

  await expect(page.getByTestId('props')).toContainText('en-US')
  await expect(page.getByTestId('props')).toContainText('UTC')
})
