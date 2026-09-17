/**
 * Currency, Date and Number formatting utilities following Indonesian locale
 */

export function formatRupiah(amount: number | string, compact = false): string {
	const num = typeof amount === 'string' ? parseFloat(amount) : amount;
	if (isNaN(num)) return 'Rp 0';

	if (compact && Math.abs(num) >= 1_000_000_000) {
		return `Rp ${(num / 1_000_000_000).toFixed(1).replace('.', ',')} M`;
	}
	if (compact && Math.abs(num) >= 1_000_000) {
		return `Rp ${(num / 1_000_000).toFixed(1).replace('.', ',')} jt`;
	}
	if (compact && Math.abs(num) >= 100_000) {
		return `Rp ${(num / 1_000).toFixed(0)} rb`;
	}

	return new Intl.NumberFormat('id-ID', {
		style: 'currency',
		currency: 'IDR',
		minimumFractionDigits: 0,
		maximumFractionDigits: 0
	}).format(num);
}

export function formatDate(dateString: string): string {
	try {
		const date = new Date(dateString);
		return new Intl.DateTimeFormat('id-ID', {
			day: 'numeric',
			month: 'short',
			year: 'numeric'
		}).format(date);
	} catch {
		return dateString;
	}
}

export function formatDateTime(dateString: string): string {
	try {
		const date = new Date(dateString);
		return new Intl.DateTimeFormat('id-ID', {
			day: 'numeric',
			month: 'short',
			year: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		}).format(date);
	} catch {
		return dateString;
	}
}

export function formatRelativeTime(dateString: string): string {
	try {
		const date = new Date(dateString);
		const now = new Date();
		const diffSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

		if (diffSeconds < 60) return 'Baru saja';
		if (diffSeconds < 3600) return `${Math.floor(diffSeconds / 60)} mnt lalu`;
		if (diffSeconds < 86400) return `${Math.floor(diffSeconds / 3600)} jam lalu`;
		if (diffSeconds < 172800) return 'Kemarin';

		return formatDate(dateString);
	} catch {
		return dateString;
	}
}
