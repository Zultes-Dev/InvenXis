export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatDate(dateStr: string): string {
  try {
    return new Intl.DateTimeFormat('es-CO', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    }).format(new Date(dateStr));
  } catch {
    return dateStr;
  }
}

export function formatDateTime(dateStr: string): string {
  try {
    return new Intl.DateTimeFormat('es-CO', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(new Date(dateStr));
  } catch {
    return dateStr;
  }
}

export function getStockColor(cantidad: number, stockMin: number): string {
  if (cantidad === 0) return 'text-red-500';
  if (cantidad <= stockMin) return 'text-amber-500';
  return 'text-emerald-500';
}

export function getStockStatus(cantidad: number, stockMin: number): { label: string; color: 'success' | 'warning' | 'danger' } {
  if (cantidad === 0) return { label: 'Sin Stock', color: 'danger' };
  if (cantidad <= stockMin) return { label: 'Stock Bajo', color: 'warning' };
  return { label: 'Normal', color: 'success' };
}

export function getEstadoPedidoColor(estado: string): 'success' | 'warning' | 'danger' | 'info' | 'muted' {
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'muted'> = {
    recibido: 'success',
    parcial: 'warning',
    pendiente: 'info',
    cancelado: 'danger',
  };
  return map[estado] || 'muted';
}

export function getEstadoVentaColor(estado: string): 'success' | 'warning' | 'danger' | 'info' | 'muted' {
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'muted'> = {
    completada: 'success',
    pendiente: 'warning',
    pendiente_pago: 'warning',
    cancelada: 'danger',
  };
  return map[estado] || 'muted';
}

export function downloadBlob(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}
