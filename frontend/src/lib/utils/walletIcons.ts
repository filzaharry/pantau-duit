import { financialStore } from '$lib/stores/financial.svelte';

export interface WalletPreset {
	id: string;
	name: string;
	category: 'BANK' | 'E_WALLET' | 'CASH' | 'INVESTMENT' | 'OTHER';
	image: string;
	color: string;
}

export const WALLET_PRESETS: WalletPreset[] = [
	{ id: 'bca', name: 'Bank BCA', category: 'BANK', image: '/wallets/bca.svg', color: '#0060C4' },
	{ id: 'mandiri', name: 'Bank Mandiri', category: 'BANK', image: '/wallets/mandiri.svg', color: '#0D47A1' },
	{ id: 'bri', name: 'Bank BRI', category: 'BANK', image: '/wallets/bri.svg', color: '#0284C7' },
	{ id: 'bni', name: 'Bank BNI', category: 'BANK', image: '/wallets/bni.svg', color: '#0F766E' },
	{ id: 'jago', name: 'Bank Jago', category: 'BANK', image: '/wallets/jago.svg', color: '#EA580C' },
	{ id: 'gopay', name: 'GoPay', category: 'E_WALLET', image: '/wallets/gopay.svg', color: '#00AED6' },
	{ id: 'ovo', name: 'OVO', category: 'E_WALLET', image: '/wallets/ovo.svg', color: '#7C3AED' },
	{ id: 'dana', name: 'DANA', category: 'E_WALLET', image: '/wallets/dana.svg', color: '#118EEA' },
	{ id: 'shopeepay', name: 'ShopeePay', category: 'E_WALLET', image: '/wallets/shopeepay.svg', color: '#EE4D2D' },
	{ id: 'cash', name: 'Uang Tunai (Cash)', category: 'CASH', image: '/wallets/cash.svg', color: '#10B981' },
	{ id: 'wallet', name: 'Dompet Kulit', category: 'CASH', image: '/wallets/wallet.svg', color: '#B45309' },
	{ id: 'piggy', name: 'Celengan Tabungan', category: 'OTHER', image: '/wallets/piggy.svg', color: '#EC4899' },
	{ id: 'vault', name: 'Brankas Simpanan', category: 'OTHER', image: '/wallets/vault.svg', color: '#475569' },
	{ id: 'crypto', name: 'Kripto / RDN', category: 'INVESTMENT', image: '/wallets/crypto.svg', color: '#D97706' },
	{ id: 'gold', name: 'Emas & Logam Mulia', category: 'INVESTMENT', image: '/wallets/vault.svg', color: '#EAB308' }
];

export function getWalletImage(icon?: string, type?: string): string {
	if (icon) {
		if (icon.startsWith('/') || icon.startsWith('http') || icon.startsWith('data:image/')) {
			return icon;
		}

		// 1. Lookup in dynamic walletMasters from financialStore
		if (financialStore?.walletMasters?.length) {
			const wm = financialStore.walletMasters.find(
				(m) =>
					m.code?.toLowerCase() === icon.toLowerCase() ||
					m.id === icon ||
					m.name?.toLowerCase() === icon.toLowerCase()
			);
			if (wm?.image) {
				return wm.image;
			}
		}

		// 2. Lookup in static presets
		const preset = WALLET_PRESETS.find((p) => p.id.toLowerCase() === icon.toLowerCase() || p.name.toLowerCase() === icon.toLowerCase());
		if (preset) return preset.image;
	}

	// Fallback based on type
	switch (type) {
		case 'BANK':
			return '/wallets/bca.svg';
		case 'E_WALLET':
			return '/wallets/gopay.svg';
		case 'CASH':
			return '/wallets/cash.svg';
		case 'INVESTMENT':
			return '/wallets/crypto.svg';
		default:
			return '/wallets/wallet.svg';
	}
}

export function getWalletColor(icon?: string, type?: string, explicitColor?: string, name?: string): string {
	// 1. Lookup in dynamic walletMasters from financialStore
	if (financialStore?.walletMasters?.length && icon) {
		const wm = financialStore.walletMasters.find(
			(m) =>
				m.code?.toLowerCase() === icon.toLowerCase() ||
				m.id === icon ||
				m.name?.toLowerCase() === icon.toLowerCase()
		);
		if (wm?.color) return wm.color;
	}

	if (explicitColor && explicitColor !== '#007AFF' && explicitColor !== '#000000') {
		return explicitColor;
	}

	if (icon) {
		const preset = WALLET_PRESETS.find((p) => p.id.toLowerCase() === icon.toLowerCase() || p.name.toLowerCase() === icon.toLowerCase());
		if (preset?.color) return preset.color;
	}

	const lowerName = (name || '').toLowerCase();
	if (lowerName.includes('emas') || lowerName.includes('gold')) {
		return '#D97706';
	}
	if (lowerName.includes('bitcoin') || lowerName.includes('btc') || lowerName.includes('crypto')) {
		return '#F59E0B';
	}

	switch (type) {
		case 'BANK':
			return '#0060C4';
		case 'E_WALLET':
			return '#00AED6';
		case 'CASH':
			return '#10B981';
		case 'INVESTMENT':
			return '#D97706';
		case 'OTHER':
			return '#EC4899';
		default:
			return explicitColor || '#007AFF';
	}
}

export function hexToRgba(hex: string, alpha: number): string {
	if (!hex) return `rgba(0, 122, 255, ${alpha})`;
	let clean = hex.replace('#', '').trim();
	if (clean.length === 3) {
		clean = clean.split('').map((c) => c + c).join('');
	}
	if (clean.length !== 6) {
		return `rgba(0, 122, 255, ${alpha})`;
	}
	const num = parseInt(clean, 16);
	if (isNaN(num)) return `rgba(0, 122, 255, ${alpha})`;
	const r = (num >> 16) & 255;
	const g = (num >> 8) & 255;
	const b = num & 255;
	return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}
