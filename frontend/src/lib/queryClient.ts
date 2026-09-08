import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      gcTime: 5 * 60_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

/** Desenvuelve el envelope { success, data } de la API. */
export function unwrap<T>(res: { data: { data?: T } & T }): T {
  const body = res.data as { data?: T } & T;
  return (body.data ?? body) as T;
}

export interface Paginated<T> {
  results: T[];
  count: number;
  total_pages: number;
}

export function unwrapPaginated<T>(res: {
  data: { results: T[]; count: number; total_pages: number };
}): Paginated<T> {
  return res.data;
}
