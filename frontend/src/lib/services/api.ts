/**
 * Centralized API service with transparent backend proxy and offline/demo fallback
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

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
		const res = await fetch(`${API_BASE}${endpoint}`, {
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
