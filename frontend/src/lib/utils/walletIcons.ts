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
		const preset = WALLET_PRESETS.find((p) => p.id.toLowerCase() === icon.toLowerCase());
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
