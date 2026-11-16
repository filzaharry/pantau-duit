import type { User, Tenant, Subscription, Role, UserRole } from '$lib/types';
import { apiFetch } from '$lib/services/api';
import { financialStore } from './financial.svelte';

class AuthStore {
	user = $state<User | null>(null);
	workspace = $state<Tenant | null>(null);
	subscription = $state<Subscription | null>(null);
	permissions = $state<string[]>([]);

	isLoading = $state<boolean>(true);
	isInitialized = $state<boolean>(false);
	isLogoutModalOpen = $state<boolean>(false);

	// Derived role & workspace checks
	isAuthenticated = $derived(this.user !== null);
	isSuperuser = $derived(this.user?.role === 'SUPERUSER' || Boolean(this.user?.is_superadmin));
	isAdmin = $derived(this.user?.role === 'ADMIN');
	isSubscriber = $derived(this.user?.role === 'SUBSCRIBER');
	isBusiness = $derived(this.workspace?.type === 'BUSINESS');

	constructor() {
		if (typeof window !== 'undefined') {
			this.init();
		}
	}

	/**
	 * Verify session and restore user data directly from PostgreSQL backend
	 */
	async init() {
		if (typeof window === 'undefined') return;

		const token = localStorage.getItem('pantau_token');
		if (!token) {
			this.clearSession();
			this.isLoading = false;
			this.isInitialized = true;
			return;
		}

		try {
			const res = await apiFetch<{
				user: User;
				workspace: Tenant;
				subscription: Subscription;
			}>('/auth/me');

			if (res.data && res.data.user) {
				this.user = res.data.user;
				this.workspace = res.data.workspace || null;
				this.subscription = res.data.subscription || null;
				this.permissions = res.data.user.permissions || [];
				financialStore.reset();
				financialStore.loadFromDatabase();
			} else {
				// Invalid or expired token
				this.clearSession();
			}
		} catch (e) {
			console.error('Failed to verify session against backend:', e);
			this.clearSession();
		} finally {
			this.isLoading = false;
			this.isInitialized = true;
		}
	}

	/**
	 * Granular permission check strictly driven by database roles and permissions
	 */
	can(permissionSlug: string): boolean {
		if (this.isSuperuser) return true;
		if (this.permissions.includes(permissionSlug)) return true;
		if (this.user?.permissions?.includes(permissionSlug)) return true;
		return false;
	}

	/**
	 * Authenticate user with database credentials
	 */
	async login(email?: string, password?: string): Promise<{ success: boolean; error?: string }> {
		const cleanEmail = (email || '').toLowerCase().trim();
		if (!cleanEmail) {
			return { success: false, error: 'Email wajib diisi' };
		}

		try {
			const res = await apiFetch<{
				user: User;
				workspace: Tenant;
				subscription: Subscription;
				token: string;
			}>('/auth/login', {
				method: 'POST',
				body: JSON.stringify({
					email: cleanEmail,
					password: password || ''
				})
			});

			if (res.data && res.data.user && res.data.token) {
				if (typeof window !== 'undefined') {
					localStorage.setItem('pantau_token', res.data.token);
					localStorage.setItem('pantau_user_email', cleanEmail);
				}
				this.user = res.data.user;
				this.workspace = res.data.workspace || null;
				this.subscription = res.data.subscription || null;
				this.permissions = res.data.user.permissions || [];
				financialStore.reset();
				await financialStore.loadFromDatabase();
				this.isLoading = false;
				return { success: true };
			} else {
				return {
					success: false,
					error: res.error || 'Email atau kata sandi tidak valid'
				};
			}
		} catch (e: any) {
			return {
				success: false,
				error: e.message || 'Gagal terhubung ke database backend'
			};
		}
	}

	clearSession() {
		this.user = null;
		this.workspace = null;
		this.subscription = null;
		this.permissions = [];
		financialStore.reset();
		if (typeof window !== 'undefined') {
			localStorage.removeItem('pantau_token');
			localStorage.removeItem('pantau_user_email');
			localStorage.removeItem('pantau_active_user');
		}
	}

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
		this.clearSession();
		if (typeof window !== 'undefined') {
			window.location.href = '/login';
		}
	}
}

export const authStore = new AuthStore();
