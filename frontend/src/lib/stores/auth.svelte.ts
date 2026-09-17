import type { User, Tenant, Subscription, Role, UserRole } from '$lib/types';

export interface PredefinedUser {
	user: User;
	workspace: Tenant;
	subscription: Subscription;
}

export const PREDEFINED_USERS: Record<'user_a' | 'user_b' | 'user_c' | 'user_d', PredefinedUser> = {
	// User A: Regular Subscriber
	user_a: {
		user: {
			id: '019934a1-0000-7000-8000-000000000001',
			email: 'budi@pantauduit.id',
			name: 'Budi Santoso',
			avatar_url: '',
			status: 'ACTIVE',
			is_superadmin: false,
			role: 'SUBSCRIBER',
			email_verified_at: '2026-09-08T00:00:00Z',
			created_at: '2026-09-08T00:00:00Z'
		},
		workspace: {
			id: '019934a1-0000-7000-8000-000000000011',
			name: 'Workspace Pribadi Budi',
			slug: 'budi-personal',
			type: 'PERSONAL',
			currency: 'IDR',
			timezone: 'Asia/Jakarta'
		},
		subscription: {
			id: 'sub-001',
			tenant_id: '019934a1-0000-7000-8000-000000000011',
			plan_id: 'plan-pro',
			status: 'ACTIVE',
			tier: 'pro',
			started_at: '2026-09-01T00:00:00Z',
			current_period_start: '2026-09-01T00:00:00Z',
			current_period_end: '2026-10-01T00:00:00Z',
			cancel_at_period_end: false,
			plan: {
				id: 'plan-pro',
				code: 'pro_monthly',
				name: 'Pro Member',
				description: 'Paket langganan pribadi dengan integrasi Telegram bot tanpa batas',
				price: 49000,
				currency: 'IDR',
				interval: 'MONTHLY',
				interval_count: 1,
				trial_period_days: 7,
				is_active: true,
				sort_order: 2,
				features: [
					{ id: 'f-1', plan_id: 'plan-pro', feature_key: 'telegram_bot_access', feature_value: 'true' },
					{ id: 'f-2', plan_id: 'plan-pro', feature_key: 'nlp_parser_enabled', feature_value: 'true' },
					{ id: 'f-3', plan_id: 'plan-pro', feature_key: 'max_accounts', feature_value: '10' }
				]
			}
		}
	},

	// User B: Tenant / Workspace Admin
	user_b: {
		user: {
			id: '019934a1-0000-7000-8000-000000000002',
			email: 'hendra@rahardjo.com',
			name: 'Hendra Pratama',
			avatar_url: '',
			status: 'ACTIVE',
			is_superadmin: false,
			role: 'ADMIN',
			email_verified_at: '2026-08-01T00:00:00Z',
			created_at: '2026-08-01T00:00:00Z'
		},
		workspace: {
			id: '019934a1-0000-7000-8000-000000000012',
			name: 'Keuangan Keluarga Pratama',
			slug: 'pratama-family',
			type: 'FAMILY',
			currency: 'IDR',
			timezone: 'Asia/Jakarta'
		},
		subscription: {
			id: 'sub-002',
			tenant_id: '019934a1-0000-7000-8000-000000000012',
			plan_id: 'plan-ent',
			status: 'ACTIVE',
			tier: 'enterprise',
			started_at: '2026-08-01T00:00:00Z',
			current_period_start: '2026-08-01T00:00:00Z',
			current_period_end: '2026-09-30T00:00:00Z',
			cancel_at_period_end: false,
			plan: {
				id: 'plan-ent',
				code: 'enterprise_monthly',
				name: 'Family & Bisnis',
				description: 'Paket kolaborasi multi-pengguna dan RBAC keluarga',
				price: 149000,
				currency: 'IDR',
				interval: 'MONTHLY',
				interval_count: 1,
				trial_period_days: 14,
				is_active: true,
				sort_order: 3,
				features: [
					{ id: 'f-1', plan_id: 'plan-ent', feature_key: 'multi_user_limit', feature_value: '5' },
					{ id: 'f-2', plan_id: 'plan-ent', feature_key: 'rbac_enabled', feature_value: 'true' }
				]
			}
		}
	},

	// User C: Platform Superuser (Root / Superadmin)
	user_c: {
		user: {
			id: '019934a1-0000-7000-8000-000000000003',
			email: 'admin@pantauduit.id',
			name: 'Super Admin',
			avatar_url: '',
			status: 'ACTIVE',
			is_superadmin: true,
			role: 'SUPERUSER',
			email_verified_at: '2026-01-01T00:00:00Z',
			created_at: '2026-01-01T00:00:00Z'
		},
		workspace: {
			id: '019934a1-0000-7000-8000-000000000013',
			name: 'PantauDuit Platform Master',
			slug: 'pantauduit-master',
			type: 'BUSINESS',
			currency: 'IDR',
			timezone: 'Asia/Jakarta'
		},
		subscription: {
			id: 'sub-003',
			tenant_id: '019934a1-0000-7000-8000-000000000013',
			plan_id: 'plan-ent',
			status: 'ACTIVE',
			tier: 'enterprise',
			started_at: '2026-01-01T00:00:00Z',
			current_period_start: '2026-01-01T00:00:00Z',
			current_period_end: '2099-12-31T00:00:00Z',
			cancel_at_period_end: false
		}
	},

	// User D: Business / Company Workspace (HR & Payroll Management)
	user_d: {
		user: {
			id: '019934a1-0000-7000-8000-000000000004',
			email: 'reza.aditya@pantauduit.id',
			name: 'Reza Aditya Pratama',
			avatar_url: '',
			status: 'ACTIVE',
			is_superadmin: false,
			role: 'ADMIN',
			email_verified_at: '2026-01-15T00:00:00Z',
			created_at: '2026-01-15T00:00:00Z'
		},
		workspace: {
			id: '019934a1-0000-7000-8000-000000000014',
			name: 'PT Pantau Duit Solusindo',
			slug: 'pantau-tech-corp',
			type: 'BUSINESS',
			currency: 'IDR',
			timezone: 'Asia/Jakarta'
		},
		subscription: {
			id: 'sub-004',
			tenant_id: '019934a1-0000-7000-8000-000000000014',
			plan_id: 'plan-business',
			status: 'ACTIVE',
			tier: 'enterprise',
			started_at: '2026-01-01T00:00:00Z',
			current_period_start: '2026-09-01T00:00:00Z',
			current_period_end: '2026-10-01T00:00:00Z',
			cancel_at_period_end: false
		}
	}
};

class AuthStore {
	// Active Profile - Default is user_a (Subscriber)
	currentAccountKey = $state<'user_a' | 'user_b' | 'user_c' | 'user_d'>('user_d');

	user = $state<User | null>(PREDEFINED_USERS.user_d.user);
	workspace = $state<Tenant>(PREDEFINED_USERS.user_d.workspace);
	subscription = $state<Subscription>(PREDEFINED_USERS.user_d.subscription);

	// Derived role & workspace checks
	isAuthenticated = $derived(this.user !== null);
	isSuperuser = $derived(this.user?.role === 'SUPERUSER' || Boolean(this.user?.is_superadmin));
	isAdmin = $derived(this.user?.role === 'ADMIN');
	isSubscriber = $derived(this.user?.role === 'SUBSCRIBER');
	isBusiness = $derived(this.workspace.type === 'BUSINESS');

	constructor() {
		if (typeof window !== 'undefined') {
			const saved = localStorage.getItem('pantau_active_user') as 'user_a' | 'user_b' | 'user_c' | 'user_d' | null;
			if (saved && PREDEFINED_USERS[saved]) {
				this.switchUser(saved);
			}
		}
	}

	switchUser(accountKey: 'user_a' | 'user_b' | 'user_c' | 'user_d') {
		const target = PREDEFINED_USERS[accountKey];
		if (!target) return;

		this.currentAccountKey = accountKey;
		this.user = { ...target.user };
		this.workspace = { ...target.workspace };
		this.subscription = { ...target.subscription };

		if (typeof window !== 'undefined') {
			localStorage.setItem('pantau_active_user', accountKey);
		}
	}

	setWorkspaceMode(mode: 'PERSONAL' | 'BUSINESS') {
		if (mode === 'BUSINESS') {
			this.switchUser('user_d');
		} else {
			this.switchUser('user_a');
		}
	}

	can(permissionSlug: string): boolean {
		if (this.isSuperuser) return true;
		if (this.isAdmin) return true;
		// Standard subscriber permissions
		const subscriberPerms = [
			'dashboard.view',
			'transactions.view',
			'transactions.create',
			'transactions.delete',
			'accounts.view',
			'accounts.create',
			'budgets.view',
			'budgets.create',
			'goals.view',
			'goals.create',
			'investments.view',
			'telegram.view',
			'settings.view'
		];
		return subscriberPerms.includes(permissionSlug);
	}

	async login(email?: string, password?: string) {
		const cleanEmail = (email || '').toLowerCase().trim();
		if (cleanEmail.includes('admin') || cleanEmail.includes('super') || cleanEmail === 'user_c') {
			this.switchUser('user_c');
		} else if (cleanEmail.includes('hendra') || cleanEmail === 'user_b') {
			this.switchUser('user_b');
		} else {
			this.switchUser('user_a');
		}
		return true;
	}

	isLogoutModalOpen = $state(false);

	requestLogout() {
		this.isLogoutModalOpen = true;
	}

	cancelLogout() {
		this.isLogoutModalOpen = false;
	}

	confirmLogout() {
		this.isLogoutModalOpen = false;
		this.logout();
	}

	logout() {
		this.user = null;
		if (typeof window !== 'undefined') {
			localStorage.removeItem('pantau_active_user');
			localStorage.removeItem('pantau_token');
			window.location.href = '/login';
		}
	}
}

export const authStore = new AuthStore();

