/**
 * Centralized API service with transparent backend proxy and offline/demo fallback
 */

const defaultBase = typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1'
	? '/api'
	: 'http://localhost:8000/api';

const API_BASE = (import.meta.env.VITE_API_URL || defaultBase).replace(/\/$/, '');

export interface ApiResponse<T> {
	data?: T;
	error?: string;
	message?: string;
	status: number;
}

export async function apiFetch<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
	const token = typeof window !== 'undefined' ? localStorage.getItem('pantau_token') : null;

	const headers = new Headers(options.headers || {});
	headers.set('Content-Type', 'application/json');
	if (token) {
		headers.set('Authorization', `Bearer ${token}`);
	}

	try {
		const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
		const res = await fetch(`${API_BASE}${normalizedEndpoint}`, {
			...options,
			headers
		});

		const data = await res.json().catch(() => null);

		if (!res.ok) {
			return {
				error: data?.detail || data?.message || 'Terjadi kesalahan sistem',
				status: res.status
			};
		}

		return {
			data,
			status: res.status
		};
	} catch (err: any) {
		// Connection failed - graceful fallback message
		return {
			error: err.message || 'Koneksi ke backend server gagal',
			status: 503
		};
	}
}
