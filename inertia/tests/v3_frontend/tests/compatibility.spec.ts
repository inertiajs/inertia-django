import { expect, test } from '@playwright/test'

test('uses Django partial-reload and once-prop responses with the v3 client', async ({ page }) => {
  await page.goto('/v3/nested/')
  await expect(page.getByTestId('props')).toContainText('en-US')
  await expect(page.getByTestId('props')).toContainText('UTC')

  const [response] = await Promise.all([
    page.waitForResponse(
      (candidate) => candidate.request().headers()['x-inertia-partial-data'] === 'config.locale',
    ),
    page.getByRole('button', { name: 'Reload locale' }).click(),
  ])
  expect(response.status()).toBe(200)
  await expect(response.json()).resolves.toMatchObject({
    props: { config: { locale: 'en-US' } },
  })

  await expect(page.getByTestId('props')).toContainText('en-US')
  await expect(page.getByTestId('props')).toContainText('UTC')
})
