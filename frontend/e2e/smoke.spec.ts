import { test, expect } from '@playwright/test';

// Smoke: login -> dashboard -> productos.
// Requiere backend Django en 127.0.0.1:8000 con seed_data (admin/admin).
test('login como admin muestra dashboard y navega a productos', async ({
  page,
}) => {
  await page.goto('/login');

  await page.getByPlaceholder('admin').fill('admin');
  await page.getByPlaceholder('••••••••').fill('admin');
  await page.getByRole('button', { name: 'Ingresar' }).click();

  await expect(page.getByText('Panel de Control')).toBeVisible({
    timeout: 15_000,
  });

  await page.getByRole('link', { name: 'Productos' }).click();
  await expect(
    page.getByRole('heading', { name: 'Productos' }),
  ).toBeVisible({ timeout: 15_000 });
});
