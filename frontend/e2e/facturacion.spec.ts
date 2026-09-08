import { test, expect } from '@playwright/test';

// Flujo completo: API crea venta+factura, UI la lista, la emite y la ve.
test('facturación electrónica de punta a punta', async ({ page, request }) => {
  const api = 'http://127.0.0.1:8000/api';

  const login = await request.post(`${api}/auth/login/`, {
    data: { username: 'admin', password: 'admin' },
  });
  expect(login.ok()).toBeTruthy();
  const { access } = (await login.json()).data;
  const auth = { Authorization: `Bearer ${access}` };

  const prods = await request.get(`${api}/productos/?page_size=5`, {
    headers: auth,
  });
  const producto = (await prods.json()).results[0];

  const ventaRes = await request.post(`${api}/ventas/`, {
    headers: auth,
    data: {
      detalles: [
        {
          producto: producto.id,
          cantidad: 1,
          precio_unitario: producto.precio,
        },
      ],
    },
  });
  expect(ventaRes.ok()).toBeTruthy();
  const ventaId = (await ventaRes.json()).data.id;

  const facRes = await request.post(`${api}/ventas/${ventaId}/facturar/`, {
    headers: auth,
    data: { cliente_nombre: 'Cliente E2E', cliente_documento: '123456789' },
  });
  expect(facRes.status() === 201).toBeTruthy();
  const numero = (await facRes.json()).data.numero;

  // UI: login y lista de facturación
  await page.goto('/login');
  await page.getByPlaceholder('admin').fill('admin');
  await page.getByPlaceholder('••••••••').fill('admin');
  await page.getByRole('button', { name: 'Ingresar' }).click();
  await expect(page.getByText('Panel de Control')).toBeVisible({
    timeout: 15_000,
  });

  await page.getByRole('link', { name: 'Facturación' }).click();
  await expect(
    page.getByRole('main').getByRole('heading', { name: 'Facturación' }),
  ).toBeVisible();
  await expect(page.getByText(numero).first()).toBeVisible({
    timeout: 15_000,
  });

  // Emitir FE desde la UI
  await page.getByRole('button', { name: `Emitir ${numero}` }).click();
  await expect(page.getByText('validada', { exact: false }).first()).toBeVisible({
    timeout: 15_000,
  });

  // Detalle con CUFE
  await page.getByRole('button', { name: `Ver ${numero}` }).click();
  await expect(page.getByText(/CUFE:/)).toBeVisible({ timeout: 15_000 });
});
