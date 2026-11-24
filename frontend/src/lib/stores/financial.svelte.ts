import type { Account, Category, Transaction, Budget, FinancialGoal, InvestmentHolding } from '$lib/types';
import { apiFetch } from '$lib/services/api';
import { notificationStore } from './notifications.svelte';
import { authStore } from './auth.svelte';

class FinancialStore {
	// ==========================================
	// 1. DATA PRIBADI (SUBSCRIBER) - DEFAULT KOSONG (0 DATA)
	// ==========================================
	personalAccounts = $state<Account[]>([]);

	personalCategories = $state<Category[]>([
		{ id: 'cat-1', name: 'Makanan & Minuman', slug: 'makanan-minuman', type: 'EXPENSE', icon: 'utensils', color: '#EF4444', is_system: true },
		{ id: 'cat-2', name: 'Transportasi', slug: 'transportasi', type: 'EXPENSE', icon: 'car', color: '#F97316', is_system: true },
		{ id: 'cat-3', name: 'Listrik & Internet', slug: 'listrik-internet', type: 'EXPENSE', icon: 'bolt', color: '#EAB308', is_system: true },
		{ id: 'cat-4', name: 'Belanja Harian', slug: 'belanja-harian', type: 'EXPENSE', icon: 'shopping-cart', color: '#84CC16', is_system: true },
		{ id: 'cat-5', name: 'Hiburan', slug: 'hiburan', type: 'EXPENSE', icon: 'film', color: '#06B6D4', is_system: true },
		{ id: 'cat-6', name: 'Gaji Bulanan', slug: 'gaji', type: 'INCOME', icon: 'money-bill-wave', color: '#10B981', is_system: true },
		{ id: 'cat-7', name: 'Freelance', slug: 'freelance', type: 'INCOME', icon: 'laptop-code', color: '#34D399', is_system: true },
		{ id: 'cat-8', name: 'Hasil Investasi', slug: 'hasil-investasi', type: 'INCOME', icon: 'chart-line', color: '#22C55E', is_system: true }
	]);

	personalTransactions = $state<Transaction[]>([]);

	personalBudgets = $state<Budget[]>([]);

	personalGoals = $state<FinancialGoal[]>([]);

	personalInvestments = $state<InvestmentHolding[]>([]);

	// ==========================================
	// 2. DATA PLATFORM / SISTEM (SUPERUSER)
	// ==========================================
	platformAccounts = $state<Account[]>([
		{
			id: 'acc-plat-1',
			tenant_id: '019934a1-0000-7000-8000-000000000003',
			name: 'BCA Bisnis',
			type: 'BANK',
			institution_name: 'Bank Central Asia (PT Pantau Duit)',
			account_number: '8830192831',
			currency: 'IDR',
			opening_balance: 25000000,
			current_balance: 42850000,
			balance: 42850000,
			status: 'ACTIVE',
			is_active: true,
			color: '#00529C',
			icon: 'building-columns'
		},
		{
			id: 'acc-plat-2',
			tenant_id: '019934a1-0000-7000-8000-000000000003',
			name: 'Midtrans Escrow',
			type: 'E_WALLET',
			institution_name: 'Midtrans Payment Gateway',
			account_number: 'MID-PD-9921',
			currency: 'IDR',
			opening_balance: 5000000,
			current_balance: 8420000,
			balance: 8420000,
			status: 'ACTIVE',
			is_active: true,
			color: '#00AED6',
			icon: 'wallet'
		},
		{
			id: 'acc-plat-3',
			tenant_id: '019934a1-0000-7000-8000-000000000003',
			name: 'Xendit Payout',
			type: 'E_WALLET',
			institution_name: 'Xendit Indonesia',
			account_number: 'XND-PD-1024',
			currency: 'IDR',
			opening_balance: 3000000,
			current_balance: 5150000,
			balance: 5150000,
			status: 'ACTIVE',
			is_active: true,
			color: '#10B981',
			icon: 'wallet'
		},
		{
			id: 'acc-plat-4',
			tenant_id: '019934a1-0000-7000-8000-000000000003',
			name: 'Saldo Server Prepaid',
			type: 'CASH',
			institution_name: 'Hetzner Cloud Credit',
			account_number: 'HTZ-EUR-POOL',
			currency: 'IDR',
			opening_balance: 2000000,
			current_balance: 3200000,
			balance: 3200000,
			status: 'ACTIVE',
			is_active: true,
			color: '#6366F1',
			icon: 'server'
		}
	]);

	platformCategories = $state<Category[]>([
		// Pemasukan Sistem
		{ id: 'pcat-1', name: 'Langganan Pro', slug: 'langganan-pro', type: 'INCOME', icon: 'crown', color: '#10B981', is_system: true },
		{ id: 'pcat-2', name: 'Langganan Tahunan', slug: 'langganan-tahunan', type: 'INCOME', icon: 'sparkles', color: '#059669', is_system: true },
		{ id: 'pcat-3', name: 'Langganan Family', slug: 'langganan-family', type: 'INCOME', icon: 'users', color: '#34D399', is_system: true },
		{ id: 'pcat-4', name: 'Pencairan PG', slug: 'pencairan-pg', type: 'INCOME', icon: 'arrow-down-left', color: '#0284C7', is_system: true },

		// Pengeluaran Sistem
		{ id: 'pcat-5', name: 'Sewa Server', slug: 'sewa-server', type: 'EXPENSE', icon: 'server', color: '#EF4444', is_system: true },
		{ id: 'pcat-6', name: 'Beli Domain', slug: 'beli-domain', type: 'EXPENSE', icon: 'globe', color: '#F97316', is_system: true },
		{ id: 'pcat-7', name: 'Database & Redis', slug: 'database-redis', type: 'EXPENSE', icon: 'database', color: '#EAB308', is_system: true },
		{ id: 'pcat-8', name: 'Cloudflare & WAF', slug: 'cloudflare-waf', type: 'EXPENSE', icon: 'shield', color: '#F59E0B', is_system: true },
		{ id: 'pcat-9', name: 'Layanan API', slug: 'layanan-api', type: 'EXPENSE', icon: 'cpu', color: '#EC4899', is_system: true }
	]);

	platformTransactions = $state<Transaction[]>([
		{
			id: 'ptx-1',
			tenant_id: '019934a1-0000-7000-8000-000000000003',
			account_id: 'acc-plat-2',
			category_id: 'pcat-1',
			amount: 49000,
			currency: 'IDR',
			transaction_type: 'INCOME',
			transaction_date: new Date(Date.now() - 1000 * 60 * 20).toISOString(),
			source: 'DASHBOARD',
			status: 'COMPLETED',
			description: '@budipratama - Langganan Pro',
			notes: 'Pembayaran langganan via Midtrans QRIS',
			created_at: new Date(Date.now() - 1000 * 60 * 20).toISOString(),
			account_name: 'Midtrans Escrow',
			category_name: 'Langganan Pro',
			category_icon: 'crown',
			category_color: '#10B981'
		},
		{
			id: 'ptx-2',
			tenant_id: '019934a1-0000-7000-8000-000000000003',
			account_id: 'acc-plat-1',
			category_id: 'pcat-2',
			amount: 490000,
			currency: 'IDR',
			transaction_type: 'INCOME',
			transaction_date: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
			source: 'DASHBOARD',
			status: 'COMPLETED',
			description: '@anisa_m - Langganan Tahunan',
			notes: 'Paket Pro Tahunan hemat 2 bulan via BCA VA',
			created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
			account_name: 'BCA Bisnis',
			category_name: 'Langganan Tahunan',
			category_icon: 'sparkles',
			category_color: '#059669'
		},
		{
			id: 'ptx-3',
			tenant_id: '019934a1-0000-7000-8000-000000000003',
			account_id: 'acc-plat-4',
			category_id: 'pcat-5',
			amount: 750000,
			currency: 'IDR',
			transaction_type: 'EXPENSE',
			transaction_date: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
			source: 'DASHBOARD',
			status: 'COMPLETED',
			description: 'Sewa Server VPS Hetzner CPX31',
			notes: 'VPS Produksi & Webhook Telegram Bot 4 vCPU 8GB RAM',
			created_at: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
			account_name: 'Saldo Server Prepaid',
			category_name: 'Sewa Server',
			category_icon: 'server',
			category_color: '#EF4444'
		},
		{
			id: 'ptx-4',
			tenant_id: '019934a1-0000-7000-8000-000000000003',
			account_id: 'acc-plat-2',
			category_id: 'pcat-1',
			amount: 49000,
			currency: 'IDR',
			transaction_type: 'INCOME',
			transaction_date: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString(),
			source: 'DASHBOARD',
			status: 'COMPLETED',
			description: '@reza_f - Langganan Pro',
			notes: 'Pembayaran langganan via GoPay Midtrans',
			created_at: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString(),
			account_name: 'Midtrans Escrow',
			category_name: 'Langganan Pro',
			category_icon: 'crown',
			category_color: '#10B981'
		},
		{
			id: 'ptx-5',
			tenant_id: '019934a1-0000-7000-8000-000000000003',
			account_id: 'acc-plat-1',
			category_id: 'pcat-6',
			amount: 250000,
			currency: 'IDR',
			transaction_type: 'EXPENSE',
			transaction_date: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
			source: 'DASHBOARD',
			status: 'COMPLETED',
			description: 'Perpanjang Domain pantauduit.id',
			notes: 'Registrar PANDI ID periode 1 tahun',
			created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
			account_name: 'BCA Bisnis',
			category_name: 'Beli Domain',
			category_icon: 'globe',
			category_color: '#F97316'
		},
		{
			id: 'ptx-6',
			tenant_id: '019934a1-0000-7000-8000-000000000003',
			account_id: 'acc-plat-1',
			category_id: 'pcat-7',
			amount: 420000,
			currency: 'IDR',
			transaction_type: 'EXPENSE',
			transaction_date: new Date(Date.now() - 1000 * 60 * 60 * 28).toISOString(),
			source: 'DASHBOARD',
			status: 'COMPLETED',
			description: 'Sewa Database Supabase Pro',
			notes: 'Managed PostgreSQL & Redis Cache Cluster',
			created_at: new Date(Date.now() - 1000 * 60 * 60 * 28).toISOString(),
			account_name: 'BCA Bisnis',
			category_name: 'Database & Redis',
			category_icon: 'database',
			category_color: '#EAB308'
		},
		{
			id: 'ptx-7',
			tenant_id: '019934a1-0000-7000-8000-000000000003',
			account_id: 'acc-plat-3',
			category_id: 'pcat-3',
			amount: 149000,
			currency: 'IDR',
			transaction_type: 'INCOME',
			transaction_date: new Date(Date.now() - 1000 * 60 * 60 * 36).toISOString(),
			source: 'DASHBOARD',
			status: 'COMPLETED',
			description: '@hendra_p - Langganan Family',
			notes: 'Paket Family kolaborasi 5 user via Xendit VA',
			created_at: new Date(Date.now() - 1000 * 60 * 60 * 36).toISOString(),
			account_name: 'Xendit Payout',
			category_name: 'Langganan Family',
			category_icon: 'users',
			category_color: '#34D399'
		},
		{
			id: 'ptx-8',
			tenant_id: '019934a1-0000-7000-8000-000000000003',
			account_id: 'acc-plat-2',
			destination_account_id: 'acc-plat-1',
			amount: 3500000,
			currency: 'IDR',
			transaction_type: 'TRANSFER',
			transaction_date: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(),
			source: 'DASHBOARD',
			status: 'COMPLETED',
			description: 'Tarik Saldo Midtrans ke BCA Bisnis',
			notes: 'Settlement payout berkala dana langganan',
			created_at: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(),
			account_name: 'Midtrans Escrow',
			destination_account_name: 'BCA Bisnis'
		},
		{
			id: 'ptx-9',
			tenant_id: '019934a1-0000-7000-8000-000000000003',
			account_id: 'acc-plat-1',
			category_id: 'pcat-8',
			amount: 315000,
			currency: 'IDR',
			transaction_type: 'EXPENSE',
			transaction_date: new Date(Date.now() - 1000 * 60 * 60 * 55).toISOString(),
			source: 'DASHBOARD',
			status: 'COMPLETED',
			description: 'Cloudflare Pro & WAF Firewall',
			notes: 'Proteksi DDoS, caching CDN, dan SSL certificate',
			created_at: new Date(Date.now() - 1000 * 60 * 60 * 55).toISOString(),
			account_name: 'BCA Bisnis',
			category_name: 'Cloudflare & WAF',
			category_icon: 'shield',
			category_color: '#F59E0B'
		},
		{
			id: 'ptx-10',
			tenant_id: '019934a1-0000-7000-8000-000000000003',
			account_id: 'acc-plat-1',
			category_id: 'pcat-9',
			amount: 125000,
			currency: 'IDR',
			transaction_type: 'EXPENSE',
			transaction_date: new Date(Date.now() - 1000 * 60 * 60 * 60).toISOString(),
			source: 'DASHBOARD',
			status: 'COMPLETED',
			description: 'Resend Email & OTP SMS API',
			notes: 'Layanan kirim email verifikasi & notifikasi telegram',
			created_at: new Date(Date.now() - 1000 * 60 * 60 * 60).toISOString(),
			account_name: 'BCA Bisnis',
			category_name: 'Layanan API',
			category_icon: 'cpu',
			category_color: '#EC4899'
		},
		{
			id: 'ptx-11',
			tenant_id: '019934a1-0000-7000-8000-000000000003',
			account_id: 'acc-plat-2',
			category_id: 'pcat-1',
			amount: 49000,
			currency: 'IDR',
			transaction_type: 'INCOME',
			transaction_date: new Date(Date.now() - 1000 * 60 * 60 * 72).toISOString(),
			source: 'DASHBOARD',
			status: 'COMPLETED',
			description: '@siti_rahma - Langganan Pro',
			notes: 'Pembayaran langganan via ShopeePay',
			created_at: new Date(Date.now() - 1000 * 60 * 60 * 72).toISOString(),
			account_name: 'Midtrans Escrow',
			category_name: 'Langganan Pro',
			category_icon: 'crown',
			category_color: '#10B981'
		},
		{
			id: 'ptx-12',
			tenant_id: '019934a1-0000-7000-8000-000000000003',
			account_id: 'acc-plat-2',
			category_id: 'pcat-1',
			amount: 49000,
			currency: 'IDR',
			transaction_type: 'INCOME',
			transaction_date: new Date(Date.now() - 1000 * 60 * 60 * 80).toISOString(),
			source: 'DASHBOARD',
			status: 'COMPLETED',
			description: '@dimas_n - Langganan Pro',
			notes: 'Pembayaran langganan via Mandiri VA',
			created_at: new Date(Date.now() - 1000 * 60 * 60 * 80).toISOString(),
			account_name: 'Midtrans Escrow',
			category_name: 'Langganan Pro',
			category_icon: 'crown',
			category_color: '#10B981'
		}
	]);

	platformBudgets = $state<Budget[]>([
		{
			id: 'pb-1',
			tenant_id: '019934a1-0000-7000-8000-000000000003',
			category_id: 'pcat-5',
			name: 'Sewa Server',
			amount: 2000000,
			limit_amount: 2000000,
			spent_amount: 750000,
			period: 'MONTHLY',
			start_date: '2026-09-01',
			end_date: '2026-09-30',
			alert_threshold_percent: 80,
			is_active: true,
			category_name: 'Sewa Server',
			category_icon: 'server'
		},
		{
			id: 'pb-2',
			tenant_id: '019934a1-0000-7000-8000-000000000003',
			category_id: 'pcat-7',
			name: 'Database & Redis',
			amount: 1000000,
			limit_amount: 1000000,
			spent_amount: 420000,
			period: 'MONTHLY',
			start_date: '2026-09-01',
			end_date: '2026-09-30',
			alert_threshold_percent: 80,
			is_active: true,
			category_name: 'Database & Redis',
			category_icon: 'database'
		},
		{
			id: 'pb-3',
			tenant_id: '019934a1-0000-7000-8000-000000000003',
			category_id: 'pcat-6',
			name: 'Beli Domain',
			amount: 500000,
			limit_amount: 500000,
			spent_amount: 250000,
			period: 'MONTHLY',
			start_date: '2026-09-01',
			end_date: '2026-09-30',
			alert_threshold_percent: 80,
			is_active: true,
			category_name: 'Beli Domain',
			category_icon: 'globe'
		},
		{
			id: 'pb-4',
			tenant_id: '019934a1-0000-7000-8000-000000000003',
			category_id: 'pcat-9',
			name: 'Layanan API',
			amount: 500000,
			limit_amount: 500000,
			spent_amount: 125000,
			period: 'MONTHLY',
			start_date: '2026-09-01',
			end_date: '2026-09-30',
			alert_threshold_percent: 80,
			is_active: true,
			category_name: 'Layanan API',
			category_icon: 'cpu'
		}
	]);

	platformGoals = $state<FinancialGoal[]>([
		{
			id: 'pg-1',
			tenant_id: '019934a1-0000-7000-8000-000000000003',
			name: 'Dana Cadangan Server 1 Tahun',
			target_amount: 30000000,
			current_amount: 18000000,
			target_date: '2027-01-01',
			status: 'IN_PROGRESS',
			color: '#10B981',
			icon: 'shield-check'
		}
	]);

	platformInvestments = $state<InvestmentHolding[]>([
		{
			id: 'pinv-1',
			tenant_id: '019934a1-0000-7000-8000-000000000003',
			account_id: 'acc-plat-1',
			asset_id: 'asset-plat-1',
			symbol: 'RDPU-MAN',
			name: 'Dana Cadangan Server (RDPU)',
			asset_class: 'DEPOSIT',
			quantity: 25000,
			buy_price_avg: 1000,
			current_price: 1050,
			currency: 'IDR',
			unit_label: 'unit',
			updated_at: new Date().toISOString()
		},
		{
			id: 'pinv-2',
			tenant_id: '019934a1-0000-7000-8000-000000000003',
			account_id: 'acc-plat-1',
			asset_id: 'asset-plat-2',
			symbol: 'DEP-PAJAK',
			name: 'Kas Cadangan Pajak PT',
			asset_class: 'DEPOSIT',
			quantity: 1,
			buy_price_avg: 15000000,
			current_price: 15500000,
			currency: 'IDR',
			unit_label: 'bilyet',
			updated_at: new Date().toISOString()
		}
	]);

	// ==========================================
	// REACTIVE SCOPED ACCESSORS
	// ==========================================
	get accounts(): Account[] {
		return authStore.isSuperuser ? this.platformAccounts : this.personalAccounts;
	}
	set accounts(val: Account[]) {
		if (authStore.isSuperuser) {
			this.platformAccounts = val;
		} else {
			this.personalAccounts = val;
		}
	}

	get categories(): Category[] {
		return authStore.isSuperuser ? this.platformCategories : this.personalCategories;
	}
	set categories(val: Category[]) {
		if (authStore.isSuperuser) {
			this.platformCategories = val;
		} else {
			this.personalCategories = val;
		}
	}

	get transactions(): Transaction[] {
		return authStore.isSuperuser ? this.platformTransactions : this.personalTransactions;
	}
	set transactions(val: Transaction[]) {
		if (authStore.isSuperuser) {
			this.platformTransactions = val;
		} else {
			this.personalTransactions = val;
		}
	}

	get budgets(): Budget[] {
		return authStore.isSuperuser ? this.platformBudgets : this.personalBudgets;
	}
	set budgets(val: Budget[]) {
		if (authStore.isSuperuser) {
			this.platformBudgets = val;
		} else {
			this.personalBudgets = val;
		}
	}

	get goals(): FinancialGoal[] {
		return authStore.isSuperuser ? this.platformGoals : this.personalGoals;
	}
	set goals(val: FinancialGoal[]) {
		if (authStore.isSuperuser) {
			this.platformGoals = val;
		} else {
			this.personalGoals = val;
		}
	}

	get investments(): InvestmentHolding[] {
		return authStore.isSuperuser ? this.platformInvestments : this.personalInvestments;
	}
	set investments(val: InvestmentHolding[]) {
		if (authStore.isSuperuser) {
			this.platformInvestments = val;
		} else {
			this.personalInvestments = val;
		}
	}

	// ==========================================
	// REACTIVE TOTALS
	// ==========================================
	totalBalance = $derived(
		this.accounts.reduce((sum, acc) => sum + Number(acc.current_balance || acc.balance || 0), 0)
	);

	monthlyIncome = $derived(
		this.transactions
			.filter((t) => t.transaction_type === 'INCOME' && t.status === 'COMPLETED')
			.reduce((sum, t) => sum + Number(t.amount), 0)
	);

	monthlyExpense = $derived(
		this.transactions
			.filter((t) => t.transaction_type === 'EXPENSE' && t.status === 'COMPLETED')
			.reduce((sum, t) => sum + Number(t.amount), 0)
	);

	monthlyTransfers = $derived(
		this.transactions
			.filter((t) => t.transaction_type === 'TRANSFER' && t.status === 'COMPLETED')
			.reduce((sum, t) => sum + Number(t.amount), 0)
	);

	totalInvestedValue = $derived(
		this.investments.reduce((sum, inv) => sum + Number(inv.quantity * inv.current_price), 0)
	);

	constructor() {
		if (typeof window !== 'undefined') {
			this.loadFromDatabase();
		}
	}

	reset() {
		this.personalAccounts = [];
		this.personalTransactions = [];
		this.personalBudgets = [];
		this.personalGoals = [];
		this.personalInvestments = [];
	}

	async loadFromDatabase() {
		try {
			const [accRes, txRes, catRes, budgetRes, goalRes, invRes] = await Promise.all([
				apiFetch<Account[]>('/accounts'),
				apiFetch<Transaction[]>('/transactions'),
				apiFetch<Category[]>('/categories'),
				apiFetch<Budget[]>('/budgets'),
				apiFetch<FinancialGoal[]>('/goals'),
				apiFetch<InvestmentHolding[]>('/investments')
			]);

			if (accRes.data) {
				this.personalAccounts = accRes.data;
				this.platformAccounts = accRes.data;
			}
			if (txRes.data) {
				this.personalTransactions = txRes.data;
				this.platformTransactions = txRes.data;
			}
			if (catRes.data && catRes.data.length > 0) {
				this.personalCategories = catRes.data;
				this.platformCategories = catRes.data;
			}
			if (budgetRes.data) {
				this.personalBudgets = budgetRes.data;
				this.platformBudgets = budgetRes.data;
			}
			if (goalRes.data) {
				this.personalGoals = goalRes.data;
				this.platformGoals = goalRes.data;
			}
			if (invRes.data) {
				this.personalInvestments = invRes.data;
				this.platformInvestments = invRes.data;
			}
		} catch (err) {
			console.warn('Fallback to local cache:', err);
		}
	}

	// ==========================================
	// MUTATION ACTIONS
	// ==========================================
	async addTransaction(payload: Partial<Transaction>) {
		if (this.accounts.length === 0) {
			notificationStore.showToast('Minimal harus ada 1 dompet atau rekening sebelum mencatat transaksi.', 'error');
			return null;
		}

		const amount = Number(payload.amount || 0);

		// Synchronize directly with PostgreSQL database
		try {
			const res = await apiFetch<any>('/transactions', {
				method: 'POST',
				body: JSON.stringify({
					account_id: payload.account_id,
					destination_account_id: payload.destination_account_id,
					category_id: payload.category_id,
					amount,
					transaction_type: payload.transaction_type || 'EXPENSE',
					transaction_date: payload.transaction_date,
					source: payload.source === 'TELEGRAM' ? 'TELEGRAM' : 'DASHBOARD',
					description: payload.description || 'Transaksi',
					notes: payload.notes
				})
			});
			if (res.data) {
				await this.loadFromDatabase();
				notificationStore.showToast('Transaksi berhasil dicatat ke database!', 'success');
				return res.data;
			}
			throw new Error(res.error || 'Gagal menyimpan transaksi ke database');
		} catch (err: any) {
			console.error('API sync failed:', err);
			notificationStore.showToast(err?.message || 'Gagal menyimpan transaksi ke database', 'error');
			return null;
		}
	}

	async updateTransaction(id: string, payload: { description?: string; amount?: number; category_id?: string; notes?: string }) {
		try {
			await apiFetch(`/transactions/${id}`, {
				method: 'PUT',
				body: JSON.stringify(payload)
			});
			await this.loadFromDatabase();
			notificationStore.showToast('Transaksi berhasil diperbarui!', 'success');
			return;
		} catch (err) {
			console.warn('API update transaction failed:', err);
		}

		// Fallback local update
		this.transactions = this.transactions.map((t) => {
			if (t.id === id) {
				const cat = payload.category_id ? this.categories.find((c) => c.id === payload.category_id) : undefined;
				return {
					...t,
					description: payload.description !== undefined ? payload.description : t.description,
					amount: payload.amount !== undefined ? payload.amount : t.amount,
					category_id: payload.category_id !== undefined ? payload.category_id : t.category_id,
					category_name: cat ? cat.name : t.category_name,
					notes: payload.notes !== undefined ? payload.notes : t.notes
				};
			}
			return t;
		});
		notificationStore.showToast('Transaksi berhasil diperbarui!', 'success');
	}

	async deleteTransaction(id: string) {
		const tx = this.transactions.find((t) => t.id === id);

		// Optimistic removal and ledger revert
		if (tx) {
			const account = this.accounts.find((a) => a.id === tx.account_id);
			const destAccount = tx.destination_account_id
				? this.accounts.find((a) => a.id === tx.destination_account_id)
				: undefined;

			if (account) {
				if (tx.transaction_type === 'EXPENSE') {
					account.current_balance = Number(account.current_balance || 0) + tx.amount;
					account.balance = account.current_balance;
				} else if (tx.transaction_type === 'INCOME') {
					account.current_balance = Number(account.current_balance || 0) - tx.amount;
					account.balance = account.current_balance;
				} else if (tx.transaction_type === 'TRANSFER' && destAccount) {
					account.current_balance = Number(account.current_balance || 0) + tx.amount;
					account.balance = account.current_balance;
					destAccount.current_balance = Number(destAccount.current_balance || 0) - tx.amount;
					destAccount.balance = destAccount.current_balance;
				}
			}

			// Immediately filter out from reactive stores
			this.personalTransactions = this.personalTransactions.filter((t) => t.id !== id);
			this.platformTransactions = this.platformTransactions.filter((t) => t.id !== id);
		}

		try {
			const res = await apiFetch<any>(`/transactions/${id}`, { method: 'DELETE' });
			if (res.error) {
				console.error('API delete error:', res.error);
				notificationStore.showToast(res.error, 'error');
				await this.loadFromDatabase();
				return false;
			}
			notificationStore.showToast('Transaksi berhasil dihapus', 'info');
			await this.loadFromDatabase();
			return true;
		} catch (err: any) {
			console.error('API delete sync failed:', err);
			notificationStore.showToast(err?.message || 'Gagal menghapus transaksi dari database', 'error');
			await this.loadFromDatabase();
			return false;
		}
	}

	async addAccount(payload: { name: string; type: string; opening_balance?: number; account_number?: string; institution_name?: string; icon?: string; color?: string }) {
		try {
			const res = await apiFetch<any>('/accounts', {
				method: 'POST',
				body: JSON.stringify({
					name: payload.name,
					type: payload.type,
					opening_balance: payload.opening_balance || 0,
					account_number: payload.account_number || '',
					institution_name: payload.institution_name || '',
					icon: payload.icon || 'wallet',
					color: payload.color || '#007AFF'
				})
			});
			if (res.data) {
				await this.loadFromDatabase();
				notificationStore.showToast('Rekening baru berhasil ditambahkan!', 'success');
				return res.data;
			}
			throw new Error(res.error || 'Gagal menambahkan rekening');
		} catch (err: any) {
			console.error('API add account failed:', err);
			notificationStore.showToast(err?.message || 'Gagal menambahkan rekening ke database', 'error');
			return null;
		}
	}

	async updateAccount(id: string, payload: { name: string; type?: string; account_number?: string; icon?: string; color?: string }) {
		try {
			const res = await apiFetch<any>(`/accounts/${id}`, {
				method: 'PUT',
				body: JSON.stringify(payload)
			});
			if (res.data || res.status === 200) {
				await this.loadFromDatabase();
				notificationStore.showToast('Rekening berhasil diperbarui!', 'success');
				return res.data;
			}
			throw new Error(res.error || 'Gagal memperbarui rekening');
		} catch (err: any) {
			console.error('API update account failed:', err);
			notificationStore.showToast(err?.message || 'Gagal memperbarui rekening ke database', 'error');
			return null;
		}
	}

	async deleteAccount(id: string) {
		try {
			await apiFetch(`/accounts/${id}`, { method: 'DELETE' });
			await this.loadFromDatabase();
			notificationStore.showToast('Rekening dan transaksi terkait berhasil dihapus', 'info');
			return;
		} catch (err) {
			console.warn('API delete account failed:', err);
		}
		this.accounts = this.accounts.filter((a) => a.id !== id);
		this.transactions = this.transactions.filter((t) => t.account_id !== id && t.destination_account_id !== id);
		notificationStore.showToast('Rekening berhasil dihapus', 'info');
	}

	async addBudget(payload: { category_id: string; amount: number; name?: string; alert_threshold_percent?: number }) {
		try {
			const res = await apiFetch<any>('/budgets', {
				method: 'POST',
				body: JSON.stringify(payload)
			});
			if (res.data) {
				await this.loadFromDatabase();
				notificationStore.showToast('Batas pengeluaran berhasil disimpan!', 'success');
				return res.data;
			}
			throw new Error(res.error || 'Gagal menyimpan batas pengeluaran');
		} catch (err: any) {
			console.error('API add budget failed:', err);
			notificationStore.showToast(err?.message || 'Gagal menyimpan batas pengeluaran', 'error');
			return null;
		}
	}

	async deleteBudget(id: string) {
		try {
			await apiFetch(`/budgets/${id}`, { method: 'DELETE' });
			await this.loadFromDatabase();
			notificationStore.showToast('Batas pengeluaran berhasil dihapus', 'info');
		} catch (err: any) {
			console.error('API delete budget failed:', err);
			notificationStore.showToast(err?.message || 'Gagal menghapus batas pengeluaran', 'error');
		}
	}

	async addGoal(payload: { name: string; target_amount: number; target_date?: string; initial_deposit?: number; account_id?: string; color?: string; icon?: string }) {
		try {
			const res = await apiFetch<any>('/goals', {
				method: 'POST',
				body: JSON.stringify(payload)
			});
			if (res.data) {
				await this.loadFromDatabase();
				notificationStore.showToast('Target tabungan baru berhasil dibuat!', 'success');
				return res.data;
			}
			throw new Error(res.error || 'Gagal membuat target tabungan');
		} catch (err: any) {
			console.error('API add goal failed:', err);
			notificationStore.showToast(err?.message || 'Gagal membuat target tabungan', 'error');
			return null;
		}
	}

	async contributeGoal(goalId: string, payload: { account_id: string; amount: number; notes?: string }) {
		try {
			const res = await apiFetch<any>(`/goals/${goalId}/contribute`, {
				method: 'POST',
				body: JSON.stringify(payload)
			});
			if (res.data) {
				await this.loadFromDatabase();
				notificationStore.showToast('Setoran tabungan berhasil disisihkan dari rekening!', 'success');
				return res.data;
			}
			throw new Error(res.error || 'Gagal menyetor tabungan');
		} catch (err: any) {
			console.error('API contribute goal failed:', err);
			notificationStore.showToast(err?.message || 'Gagal menyetor tabungan', 'error');
			return null;
		}
	}

	async withdrawGoal(goalId: string, payload: { account_id: string; amount: number }) {
		try {
			const res = await apiFetch<any>(`/goals/${goalId}/withdraw`, {
				method: 'POST',
				body: JSON.stringify(payload)
			});
			if (res.data) {
				await this.loadFromDatabase();
				notificationStore.showToast('Dana tabungan berhasil ditarik ke rekening!', 'success');
				return res.data;
			}
			throw new Error(res.error || 'Gagal menarik dana tabungan');
		} catch (err: any) {
			console.error('API withdraw goal failed:', err);
			notificationStore.showToast(err?.message || 'Gagal menarik tabungan', 'error');
			return null;
		}
	}

	async deleteGoal(id: string) {
		try {
			await apiFetch(`/goals/${id}`, { method: 'DELETE' });
			await this.loadFromDatabase();
			notificationStore.showToast('Target tabungan berhasil dihapus', 'info');
		} catch (err: any) {
			console.error('API delete goal failed:', err);
			notificationStore.showToast(err?.message || 'Gagal menghapus target tabungan', 'error');
		}
	}

	async addInvestment(payload: { account_id: string; name: string; symbol: string; asset_class: string; quantity: number; buy_price: number; current_price?: number; notes?: string }) {
		try {
			const res = await apiFetch<any>('/investments', {
				method: 'POST',
				body: JSON.stringify(payload)
			});
			if (res.data) {
				await this.loadFromDatabase();
				notificationStore.showToast('Aset investasi berhasil dibeli & dicatat!', 'success');
				return res.data;
			}
			throw new Error(res.error || 'Gagal mencatat investasi');
		} catch (err: any) {
			console.error('API add investment failed:', err);
			notificationStore.showToast(err?.message || 'Gagal mencatat investasi', 'error');
			return null;
		}
	}

	async deleteInvestment(id: string) {
		try {
			await apiFetch(`/investments/${id}`, { method: 'DELETE' });
			await this.loadFromDatabase();
			notificationStore.showToast('Aset investasi berhasil dihapus', 'info');
		} catch (err: any) {
			console.error('API delete investment failed:', err);
			notificationStore.showToast(err?.message || 'Gagal menghapus aset investasi', 'error');
		}
	}

	async addCategory(payload: { name: string; type?: string; icon?: string; color?: string }) {
		try {
			const res = await apiFetch<Category>('/categories', {
				method: 'POST',
				body: JSON.stringify(payload)
			});
			if (res.data) {
				await this.loadFromDatabase();
				notificationStore.showToast('Kategori baru berhasil ditambahkan', 'success');
				return res.data;
			}
			throw new Error(res.error || 'Gagal menambahkan kategori');
		} catch (err: any) {
			console.error('API add category failed:', err);
			notificationStore.showToast(err?.message || 'Gagal menambahkan kategori', 'error');
			return null;
		}
	}

	async updateCategory(id: string, payload: { name?: string; type?: string; icon?: string; color?: string }) {
		try {
			const res = await apiFetch<Category>(`/categories/${id}`, {
				method: 'PUT',
				body: JSON.stringify(payload)
			});
			if (res.data) {
				await this.loadFromDatabase();
				notificationStore.showToast('Kategori berhasil disesuaikan', 'success');
				return res.data;
			}
			throw new Error(res.error || 'Gagal memperbarui kategori');
		} catch (err: any) {
			console.error('API update category failed:', err);
			notificationStore.showToast(err?.message || 'Gagal memperbarui kategori', 'error');
			return null;
		}
	}

	async deleteCategory(id: string) {
		try {
			const res = await apiFetch<any>(`/categories/${id}`, {
				method: 'DELETE'
			});
			if (res.error) {
				throw new Error(res.error);
			}
			await this.loadFromDatabase();
			notificationStore.showToast('Kategori berhasil dihapus', 'info');
			return true;
		} catch (err: any) {
			console.error('API delete category failed:', err);
			notificationStore.showToast(err?.message || 'Gagal menghapus kategori', 'error');
			return false;
		}
	}
}

export const financialStore = new FinancialStore();
