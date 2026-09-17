import type { NotificationItem } from '$lib/types';

export interface Toast {
	id: string;
	type: 'success' | 'error' | 'warning' | 'info';
	title?: string;
	message: string;
	details?: string;
	duration?: number;
}

class NotificationStore {
	notifications = $state<NotificationItem[]>([
		{
			id: 'notif-1',
			title: 'Budget Alert (80%)',
			body: 'Pengeluaran Kategori Food & Beverage mencapai 80% dari batas bulanan.',
			message: 'Pengeluaran Kategori Food & Beverage mencapai 80% dari batas bulanan.',
			type: 'WARNING',
			channel: 'TELEGRAM',
			status: 'SENT',
			is_read: false,
			created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString()
		},
		{
			id: 'notif-2',
			title: 'Transaksi Telegram Tercatat',
			body: 'Bakso Urat Rp 15.000 berhasil dicatat via Telegram Bot.',
			message: 'Bakso Urat Rp 15.000 berhasil dicatat via Telegram Bot.',
			type: 'TELEGRAM',
			channel: 'TELEGRAM',
			status: 'SENT',
			is_read: false,
			created_at: new Date(Date.now() - 1000 * 60 * 120).toISOString()
		},
		{
			id: 'notif-3',
			title: 'Langganan Pro Aktif',
			body: 'Paket Pro Bulanan Anda aktif hingga 12 Oktober 2026.',
			message: 'Paket Pro Bulanan Anda aktif hingga 12 Oktober 2026.',
			type: 'SUCCESS',
			channel: 'DASHBOARD',
			status: 'READ',
			is_read: true,
			created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString(),
			read_at: new Date().toISOString()
		}
	]);

	toasts = $state<Toast[]>([]);

	unreadCount = $derived(
		this.notifications.filter((n) => n.status !== 'READ' && !n.is_read).length
	);

	showToast(
		message: string,
		type: 'success' | 'error' | 'warning' | 'info' = 'info',
		duration = 4000,
		title?: string,
		details?: string
	) {
		const id = Math.random().toString(36).substring(2, 9);
		const toast: Toast = { id, type, title, message, details, duration };
		this.toasts = [...this.toasts, toast];

		if (duration > 0) {
			setTimeout(() => {
				this.removeToast(id);
			}, duration);
		}
	}

	toast(message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info', duration = 4000) {
		this.showToast(message, type, duration);
	}

	success(message: string, title = 'Berhasil') {
		this.showToast(message, 'success', 3500, title);
	}

	error(message: string, title = 'Gagal', details?: string) {
		this.showToast(message, 'error', 6000, title, details);
	}

	warning(message: string, title = 'Peringatan') {
		this.showToast(message, 'warning', 4500, title);
	}

	info(message: string, title = 'Informasi') {
		this.showToast(message, 'info', 3500, title);
	}

	handleApiError(error: unknown, fallbackMessage = 'Terjadi kesalahan pada sistem.') {
		let message = fallbackMessage;
		let details: string | undefined;

		if (error instanceof Error) {
			message = error.message;
		} else if (typeof error === 'object' && error !== null) {
			const errObj = error as Record<string, any>;
			if (errObj.response?.data?.detail) {
				const detail = errObj.response.data.detail;
				if (typeof detail === 'string') {
					message = detail;
				} else if (Array.isArray(detail)) {
					// Pydantic validation error format
					message = 'Validasi data tidak sesuai:';
					details = detail.map((d) => `${d.loc?.join('.') || 'field'}: ${d.msg}`).join('\n');
				}
			} else if (errObj.message) {
				message = errObj.message;
			}
		}

		this.error(message, 'Kesalahan API', details);
	}

	removeToast(id: string) {
		this.toasts = this.toasts.filter((t) => t.id !== id);
	}

	markAsRead(id: string) {
		this.notifications = this.notifications.map((n) =>
			n.id === id ? { ...n, status: 'READ', is_read: true, read_at: new Date().toISOString() } : n
		);
	}

	markAllAsRead() {
		const now = new Date().toISOString();
		this.notifications = this.notifications.map((n) => ({
			...n,
			status: 'READ',
			is_read: true,
			read_at: now
		}));
		this.success('Semua notifikasi ditandai sudah dibaca');
	}

	deleteNotification(id: string) {
		this.notifications = this.notifications.filter((n) => n.id !== id);
		this.info('Notifikasi dihapus');
	}
}

export const notificationStore = new NotificationStore();
