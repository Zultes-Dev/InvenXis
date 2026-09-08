import axios, { AxiosError } from 'axios';
import type { AxiosRequestConfig, InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

let isRefreshing = false;
let failedQueue: Array<{ resolve: (token: string) => void; reject: (error: Error) => void }> = [];

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) prom.reject(error);
    else prom.resolve(token!);
  });
  failedQueue = [];
};

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const accessToken = localStorage.getItem('access_token');
    if (accessToken && config.headers) config.headers.Authorization = `Bearer ${accessToken}`;
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };
    if (error.response?.status !== 401 || originalRequest._retry) return Promise.reject(error);

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      }).then((token) => {
        if (originalRequest.headers) originalRequest.headers.Authorization = `Bearer ${token}`;
        return api(originalRequest);
      }).catch((err) => Promise.reject(err));
    }

    originalRequest._retry = true;
    isRefreshing = true;

    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      localStorage.clear();
      window.location.href = '/login';
      return Promise.reject(error);
    }

    try {
      const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, { refresh: refreshToken });
      const newAccess = response.data.data?.access || response.data.access;
      localStorage.setItem('access_token', newAccess);
      processQueue(null, newAccess);
      if (originalRequest.headers) originalRequest.headers.Authorization = `Bearer ${newAccess}`;
      return api(originalRequest);
    } catch (refreshError) {
      processQueue(refreshError as Error, null);
      localStorage.clear();
      window.location.href = '/login';
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);

export const authApi = {
  login: (credentials: { username: string; password: string }) =>
    api.post('/auth/login/', credentials),
  refreshToken: (refresh: string) =>
    api.post('/auth/refresh/', { refresh }),
  logout: (refresh: string) =>
    api.post('/auth/logout/', { refresh }),
  me: () => api.get('/auth/me/'),
};

export const productosApi = {
  list: (params?: Record<string, any>) => api.get('/productos/', { params }),
  get: (id: number) => api.get(`/productos/${id}/`),
  create: (data: any) => api.post('/productos/', data),
  update: (id: number, data: any) => api.put(`/productos/${id}/`, data),
  partialUpdate: (id: number, data: any) => api.patch(`/productos/${id}/`, data),
  delete: (id: number) => api.delete(`/productos/${id}/`),
};

export const proveedoresApi = {
  list: (params?: Record<string, any>) => api.get('/proveedores/', { params }),
  get: (id: number) => api.get(`/proveedores/${id}/`),
  create: (data: any) => api.post('/proveedores/', data),
  update: (id: number, data: any) => api.put(`/proveedores/${id}/`, data),
  partialUpdate: (id: number, data: any) => api.patch(`/proveedores/${id}/`, data),
  delete: (id: number) => api.delete(`/proveedores/${id}/`),
  getPedidos: (proveedorId: number, params?: Record<string, any>) =>
    api.get(`/proveedores/${proveedorId}/pedidos/`, { params }),
};

export const pedidosApi = {
  get: (id: number) => api.get(`/pedidos/${id}/`),
  create: (proveedorId: number, data: any) => api.post(`/proveedores/${proveedorId}/pedidos/`, data),
  update: (id: number, data: any) => api.patch(`/pedidos/${id}/`, data),
  delete: (id: number) => api.delete(`/pedidos/${id}/`),
};

export const ventasApi = {
  list: (params?: Record<string, any>) => api.get('/ventas/', { params }),
  create: (data: any) => api.post('/ventas/', data),
};

export const reportesApi = {
  inventario: () => api.get('/reportes/inventario/'),
  masVendidos: (params?: any) => api.get('/reportes/mas-vendidos/', { params }),
  ventas: (params?: any) => api.get('/reportes/ventas/', { params }),
  exportExcel: (tipo: string) => api.get(`/reportes/exportar/excel/${tipo}/`, { responseType: 'blob' }),
  exportPdf: (tipo: string) => api.get(`/reportes/exportar/pdf/${tipo}/`, { responseType: 'blob' }),
};

export const dashboardApi = {
  get: () => api.get('/dashboard/'),
};

export default api;