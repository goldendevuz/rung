import { test, expect } from '@playwright/test'

test('home page loads', async ({ page }) => {
  await page.goto('http://localhost')
  await expect(page).toHaveTitle(/Rung/)
})

test('login route returns 200', async ({ page }) => {
  const resp = await page.goto('http://localhost/login')
  expect(resp?.status()).toBe(200)
})

test('/p/test route returns 200', async ({ page }) => {
  const resp = await page.goto('http://localhost/p/test')
  expect(resp?.status()).toBe(200)
})
