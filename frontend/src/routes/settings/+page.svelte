<script lang="ts">
	import { authStore } from '$lib/stores/auth.svelte';
	import { themeStore } from '$lib/stores/theme.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Select from '$lib/components/ui/Select.svelte';
	import Switch from '$lib/components/ui/Switch.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import {
		Settings,
		User,
		Moon,
		Sun,
		Globe,
		LogOut,
		Save,
		ShieldCheck,
		Building2,
		Bot,
		Bell,
		Key,
		CheckCircle2,
		Copy,
		ExternalLink,
		Smartphone,
		Sparkles
	} from 'lucide-svelte';

	let activeSection = $state<'all' | 'profile' | 'workspace' | 'appearance' | 'notifications' | 'security'>('all');

	// Form State
	let userName = $state(authStore.user?.name || '');
	let userEmail = $state(authStore.user?.email || '');
	let telegramUsername = $state('@budisantoso_id');
	let userPhone = $state('+62 812-3456-7890');
	let timezone = $state(authStore.workspace?.timezone || 'Asia/Jakarta');

	// Toggles
	let autoCategorize = $state(true);
	let pushNotifications = $state(true);
	let weeklyReport = $state(true);
	let transactionSound = $state(false);

	// Sync when authStore changes
	$effect(() => {
		userName = authStore.user?.name || '';
		userEmail = authStore.user?.email || '';
	});

	const themeOptions = [
		{ value: 'system', label: 'Ikuti Sistem (Otomatis)' },
		{ value: 'light', label: 'Mode Terang (Light)' },
		{ value: 'dark', label: 'Mode Gelap (Dark)' }
	];

	const timezoneOptions = [
		{ value: 'Asia/Jakarta', label: 'WIB — Jakarta, Surabaya (UTC+7)' },
		{ value: 'Asia/Makassar', label: 'WITA — Bali, Makassar (UTC+8)' },
		{ value: 'Asia/Jayapura', label: 'WIT — Jayapura, Ambon (UTC+9)' },
		{ value: 'Asia/Singapore', label: 'SGT — Singapore (UTC+8)' }
	];

	const languageOptions = [
		{ value: 'id', label: 'Bahasa Indonesia (ID)' },
		{ value: 'en', label: 'English (US)' }
	];

	function handleSaveProfile() {
		if (authStore.user) {
			authStore.user.name = userName.trim();
		}
		notificationStore.toast('Pengaturan berhasil diperbarui!', 'success');
	}

	function handleThemeChange(val: string) {
		themeStore.setTheme(val as 'light' | 'dark' | 'system');
	}

	function copyTenantId() {
		const id = authStore.workspace?.id || '019934a1-0000-7000-8000-000000000011';
		navigator.clipboard?.writeText(id);
		notificationStore.toast('Tenant ID disalin ke papan klip!', 'info');
	}

	const userInitials = $derived(
		userName
			.split(' ')
			.map((n) => n[0])
			.slice(0, 2)
			.join('')
			.toUpperCase() || 'PD'
	);
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full pb-24 lg:pb-10">
	<!-- Page Header: Consistent with Other Modules -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
		<div>
			<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
				<Settings class="w-6 h-6 text-[#007AFF] dark:text-[#0A84FF]" />
				<span>Pengaturan Akun & Preferensi</span>
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
				Kelola profil pribadi, ruang kerja, preferensi visual dasbor, dan integrasi bot Telegram
			</p>
		</div>

		<!-- Action Buttons -->
		<div class="flex items-center gap-2">
			<Button variant="primary" onclick={handleSaveProfile} class="h-9 px-4">
				<Save class="w-4 h-4" />
				<span>Simpan Perubahan</span>
			</Button>
		</div>
	</div>

	<!-- Top Metric Ribbon Strip (Segmented Settings Overview - 4 Columns matching /accounts & /investments) -->
	<div class="p-3 sm:p-5 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
		<div class="grid grid-cols-2 lg:grid-cols-4 gap-2.5 sm:gap-4 lg:divide-x divide-slate-100 dark:divide-white/5">
			<!-- Col 1: Profil Pengguna -->
			<div class="flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-blue-500/10 dark:bg-blue-500/20 text-[#007AFF] dark:text-[#0A84FF] flex items-center justify-center shrink-0">
					<User class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Pengguna Aktif</span>
					<span class="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white truncate block">{userName || 'Pengguna'}</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">{userEmail || 'Terautentikasi'}</span>
				</div>
			</div>

			<!-- Col 2: Hak Akses RBAC -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-indigo-500/10 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 flex items-center justify-center shrink-0">
					<ShieldCheck class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Peran & Akses</span>
					<span class="text-xs sm:text-sm font-semibold text-indigo-600 dark:text-indigo-400 truncate block">
						{authStore.user?.role || 'SUBSCRIBER'}
					</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">
						{authStore.isSuperuser ? 'Superadmin Platform' : authStore.isAdmin ? 'Admin Workspace' : 'Subscriber Pro'}
					</span>
				</div>
			</div>

			<!-- Col 3: Tenant Workspace -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-emerald-500/10 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
					<Building2 class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Ruang Kerja</span>
					<span class="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white truncate block">{authStore.workspace?.name || 'Workspace Pribadi'}</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">{authStore.workspace?.type || 'PERSONAL'} &bull; IDR</span>
				</div>
			</div>

			<!-- Col 4: Status Integrasi Bot -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-cyan-500/10 dark:bg-cyan-500/20 text-cyan-600 dark:text-cyan-400 flex items-center justify-center shrink-0">
					<Bot class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Bot Telegram</span>
					<div class="flex items-center gap-1.5 mt-0.5">
						<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
						<span class="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white truncate">Aktif & Terhubung</span>
					</div>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">Mode {themeStore.isDark ? 'Gelap' : 'Terang'}</span>
				</div>
			</div>
		</div>
	</div>

	<!-- Main Desktop Layout: Sidebar Navigator (Left) + Content Panels (Right) -->
	<div class="grid grid-cols-1 lg:grid-cols-12 gap-5 sm:gap-6 items-start">
		<!-- Left Column: Navigation Menu & Profile Summary Card (col-span-4 / col-span-3) -->
		<div class="lg:col-span-4 xl:col-span-3 space-y-4">
			<!-- Mini Profile Card -->
			<div class="p-5 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
				<div class="flex items-center gap-3.5">
					<div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-[#007AFF] to-blue-600 text-white flex items-center justify-center font-bold text-base shadow-sm shrink-0">
						{userInitials}
					</div>
					<div class="min-w-0 flex-1">
						<h3 class="text-sm font-semibold text-slate-900 dark:text-white truncate">{userName || 'Pengguna'}</h3>
						<p class="text-xs text-slate-400 truncate">{userEmail}</p>
						<span class="inline-flex items-center mt-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-[#007AFF]/10 text-[#007AFF] border border-[#007AFF]/20">
							{authStore.user?.role || 'SUBSCRIBER'}
						</span>
					</div>
				</div>
			</div>

			<!-- Navigation Tabs / Section Filter -->
			<div class="p-2 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] space-y-1">
				<button
					type="button"
					onclick={() => (activeSection = 'all')}
					class="w-full px-3 py-2 rounded-xl text-xs font-semibold flex items-center justify-between transition-all cursor-pointer {activeSection === 'all'
						? 'bg-[#007AFF] text-white shadow-sm'
						: 'text-slate-600 dark:text-slate-300 hover:bg-slate-100/70 dark:hover:bg-white/5'}"
				>
					<div class="flex items-center gap-2.5">
						<Settings class="w-4 h-4" />
						<span>Semua Pengaturan</span>
					</div>
				</button>

				<button
					type="button"
					onclick={() => (activeSection = 'profile')}
					class="w-full px-3 py-2 rounded-xl text-xs font-semibold flex items-center justify-between transition-all cursor-pointer {activeSection === 'profile'
						? 'bg-[#007AFF] text-white shadow-sm'
						: 'text-slate-600 dark:text-slate-300 hover:bg-slate-100/70 dark:hover:bg-white/5'}"
				>
					<div class="flex items-center gap-2.5">
						<User class="w-4 h-4" />
						<span>Profil & Identitas</span>
					</div>
				</button>

				<button
					type="button"
					onclick={() => (activeSection = 'workspace')}
					class="w-full px-3 py-2 rounded-xl text-xs font-semibold flex items-center justify-between transition-all cursor-pointer {activeSection === 'workspace'
						? 'bg-[#007AFF] text-white shadow-sm'
						: 'text-slate-600 dark:text-slate-300 hover:bg-slate-100/70 dark:hover:bg-white/5'}"
				>
					<div class="flex items-center gap-2.5">
						<Building2 class="w-4 h-4" />
						<span>Ruang Kerja & Akses</span>
					</div>
				</button>

				<button
					type="button"
					onclick={() => (activeSection = 'appearance')}
					class="w-full px-3 py-2 rounded-xl text-xs font-semibold flex items-center justify-between transition-all cursor-pointer {activeSection === 'appearance'
						? 'bg-[#007AFF] text-white shadow-sm'
						: 'text-slate-600 dark:text-slate-300 hover:bg-slate-100/70 dark:hover:bg-white/5'}"
				>
					<div class="flex items-center gap-2.5">
						<Globe class="w-4 h-4" />
						<span>Tampilan & Format</span>
					</div>
				</button>

				<button
					type="button"
					onclick={() => (activeSection = 'notifications')}
					class="w-full px-3 py-2 rounded-xl text-xs font-semibold flex items-center justify-between transition-all cursor-pointer {activeSection === 'notifications'
						? 'bg-[#007AFF] text-white shadow-sm'
						: 'text-slate-600 dark:text-slate-300 hover:bg-slate-100/70 dark:hover:bg-white/5'}"
				>
					<div class="flex items-center gap-2.5">
						<Bell class="w-4 h-4" />
						<span>Bot & Notifikasi</span>
					</div>
				</button>

				<button
					type="button"
					onclick={() => (activeSection = 'security')}
					class="w-full px-3 py-2 rounded-xl text-xs font-semibold flex items-center justify-between transition-all cursor-pointer {activeSection === 'security'
						? 'bg-rose-500 text-white shadow-sm'
						: 'text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/30'}"
				>
					<div class="flex items-center gap-2.5">
						<LogOut class="w-4 h-4" />
						<span>Sesi & Keamanan</span>
					</div>
				</button>
			</div>

			<!-- System Info Card -->
			<div class="p-4 rounded-2xl bg-slate-50/70 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/5 space-y-2">
				<div class="flex items-center justify-between text-[11px]">
					<span class="text-slate-400">Versi Aplikasi</span>
					<span class="font-semibold text-slate-700 dark:text-slate-300">v2.4.0 (Build 2026)</span>
				</div>
				<div class="flex items-center justify-between text-[11px]">
					<span class="text-slate-400">Status Server</span>
					<span class="font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
						<span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
						Online & Sehat
					</span>
				</div>
			</div>
		</div>

		<!-- Right Column: Settings Content Panels (col-span-8 / col-span-9) -->
		<div class="lg:col-span-8 xl:col-span-9 space-y-5">
			<!-- Section 1: Profil Pengguna & Identitas -->
			{#if activeSection === 'all' || activeSection === 'profile'}
				<div class="p-5 sm:p-6 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] space-y-4">
					<!-- Section Header -->
					<div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-white/5">
						<div class="flex items-center gap-2.5">
							<div class="w-8 h-8 rounded-xl bg-blue-500/10 dark:bg-blue-500/20 text-[#007AFF] dark:text-[#0A84FF] flex items-center justify-center shrink-0">
								<User class="w-4 h-4" />
							</div>
							<div>
								<h2 class="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white uppercase tracking-wider">
									Profil Pengguna & Identitas
								</h2>
								<p class="text-[11px] text-slate-400">Informasi nama akun dan kontak yang terdaftar</p>
							</div>
						</div>
					</div>

					<!-- Form Grid: 2 Columns with Uniform Field Heights (h-9) -->
					<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
						<Input
							bind:value={userName}
							label="Nama Lengkap"
							placeholder="Nama akun Anda"
						/>

						<Input
							bind:value={userEmail}
							label="Alamat Email Akun"
							disabled
							hint="Email terverifikasi sebagai ID akun utama"
						/>

						<Input
							bind:value={telegramUsername}
							label="Username Telegram Terhubung"
							placeholder="@username_telegram"
							hint="Digunakan untuk otorisasi perintah bot"
						/>

						<Input
							bind:value={userPhone}
							label="Nomor Telepon WhatsApp"
							placeholder="+62 8..."
							hint="Opsional untuk notifikasi pengingat darurat"
						/>
					</div>
				</div>
			{/if}

			<!-- Section 2: Ruang Kerja (Workspace) & RBAC -->
			{#if activeSection === 'all' || activeSection === 'workspace'}
				<div class="p-5 sm:p-6 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] space-y-4">
					<!-- Section Header -->
					<div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-white/5">
						<div class="flex items-center gap-2.5">
							<div class="w-8 h-8 rounded-xl bg-indigo-500/10 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 flex items-center justify-center shrink-0">
								<Building2 class="w-4 h-4" />
							</div>
							<div>
								<h2 class="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white uppercase tracking-wider">
									Ruang Kerja & Hak Akses (RBAC)
								</h2>
								<p class="text-[11px] text-slate-400">Identitas tenant ruang kerja dan izin wewenang akun</p>
							</div>
						</div>
					</div>

					<!-- Form Grid: 2 Columns Perfectly Aligned -->
					<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
						<Input
							value={authStore.workspace?.name || 'PantauDuit Workspace'}
							label="Nama Ruang Kerja (Tenant)"
							disabled
						/>

						<!-- Role Box: Aligned to exact same height (h-9) and spacing as Input -->
						<div class="flex flex-col gap-1.5 w-full">
							<span class="text-xs font-medium text-slate-600 dark:text-slate-300">
								Tingkat Wewenang (Role)
							</span>
							<div class="w-full h-9 px-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-slate-100/60 dark:bg-slate-900/60 flex items-center justify-between text-xs">
								<span class="font-semibold text-slate-900 dark:text-white">
									{authStore.user?.role || 'SUBSCRIBER'}
								</span>
								<span class="text-[10px] px-2 py-0.5 rounded font-semibold bg-[#007AFF]/10 text-[#007AFF] border border-[#007AFF]/20">
									{authStore.isSuperuser ? 'Superadmin Platform' : authStore.isAdmin ? 'Admin Tenant' : 'Pengguna Aktif'}
								</span>
							</div>
						</div>

						<!-- Tenant UUID with Copy Action -->
						<div class="flex flex-col gap-1.5 w-full">
							<span class="text-xs font-medium text-slate-600 dark:text-slate-300">
								ID Ruang Kerja (Tenant UUID)
							</span>
							<div class="relative flex items-center">
								<input
									type="text"
									readonly
									value={authStore.workspace?.id || '019934a1-0000-7000-8000-000000000011'}
									class="w-full h-9 pl-3 pr-9 text-xs font-mono rounded-xl border border-slate-200/80 dark:border-white/10 bg-slate-100/60 dark:bg-slate-900/60 text-slate-600 dark:text-slate-400 select-all outline-none"
								/>
								<button
									type="button"
									onclick={copyTenantId}
									title="Salin Tenant ID"
									class="absolute right-2.5 p-1 text-slate-400 hover:text-slate-700 dark:hover:text-white transition-colors cursor-pointer"
								>
									<Copy class="w-3.5 h-3.5" />
								</button>
							</div>
						</div>

						<!-- Status Langganan Box -->
						<div class="flex flex-col gap-1.5 w-full">
							<span class="text-xs font-medium text-slate-600 dark:text-slate-300">
								Status Langganan Paket
							</span>
							<div class="w-full h-9 px-3 rounded-xl border border-emerald-500/20 bg-emerald-500/5 dark:bg-emerald-500/10 flex items-center justify-between text-xs">
								<span class="font-semibold text-emerald-700 dark:text-emerald-400 flex items-center gap-1.5">
									<Sparkles class="w-3.5 h-3.5" />
									Paket PRO &bull; Aktif
								</span>
								<span class="text-[10px] text-slate-400">Aktif s/d Okt 2026</span>
							</div>
						</div>
					</div>
				</div>
			{/if}

			<!-- Section 3: Tampilan & Format -->
			{#if activeSection === 'all' || activeSection === 'appearance'}
				<div class="p-5 sm:p-6 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] space-y-4">
					<!-- Section Header -->
					<div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-white/5">
						<div class="flex items-center gap-2.5">
							<div class="w-8 h-8 rounded-xl bg-emerald-500/10 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
								<Globe class="w-4 h-4" />
							</div>
							<div>
								<h2 class="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white uppercase tracking-wider">
									Tampilan & Preferensi Format
								</h2>
								<p class="text-[11px] text-slate-400">Sesuaikan tema visual, mata uang dasar, dan tata letak lokal</p>
							</div>
						</div>
					</div>

					<!-- Form Grid: 2 Columns with Uniform Heights -->
					<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
						<!-- Theme Selector -->
						<div>
							<Select
								value={themeStore.current}
								options={themeOptions}
								label="Tema Antarmuka Aplikasi"
								onchange={handleThemeChange}
							/>
						</div>

						<!-- Primary Currency: Unified Container Style matching Select -->
						<div class="flex flex-col gap-1.5 w-full">
							<span class="text-xs font-medium text-slate-600 dark:text-slate-300">
								Mata Uang Acuan Utama
							</span>
							<div class="w-full h-9 px-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-slate-100/60 dark:bg-slate-900/60 flex items-center justify-between text-xs text-slate-900 dark:text-white font-medium">
								<span>IDR — Rupiah Indonesia (Rp)</span>
								<span class="text-[10px] px-1.5 py-0.2 rounded bg-slate-200 dark:bg-white/10 text-slate-600 dark:text-slate-300 font-semibold">Bawaan</span>
							</div>
						</div>

						<!-- Timezone -->
						<div>
							<Select
								bind:value={timezone}
								options={timezoneOptions}
								label="Zona Waktu Transaksi"
							/>
						</div>

						<!-- Language -->
						<div>
							<Select
								value="id"
								options={languageOptions}
								label="Bahasa Sistem"
							/>
						</div>
					</div>
				</div>
			{/if}

			<!-- Section 4: Bot Telegram & Notifikasi Otomatis -->
			{#if activeSection === 'all' || activeSection === 'notifications'}
				<div class="p-5 sm:p-6 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] space-y-4">
					<!-- Section Header -->
					<div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-white/5">
						<div class="flex items-center gap-2.5">
							<div class="w-8 h-8 rounded-xl bg-cyan-500/10 dark:bg-cyan-500/20 text-cyan-600 dark:text-cyan-400 flex items-center justify-center shrink-0">
								<Bot class="w-4 h-4" />
							</div>
							<div>
								<h2 class="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white uppercase tracking-wider">
									Otomatisasi Bot Telegram & Notifikasi
								</h2>
								<p class="text-[11px] text-slate-400">Pengaturan kecerdasan NLP bot dan peringatan batas keuangan</p>
							</div>
						</div>
					</div>

					<!-- Individual Aligned Switch Cards -->
					<div class="space-y-3">
						<!-- Switch 1: Auto-categorize -->
						<div class="p-4 rounded-2xl bg-slate-50/70 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/5 flex items-center justify-between gap-4">
							<div class="flex items-center gap-3.5 min-w-0">
								<div class="w-9 h-9 rounded-xl bg-blue-500/10 text-[#007AFF] flex items-center justify-center shrink-0">
									<Sparkles class="w-4 h-4" />
								</div>
								<div class="min-w-0">
									<h4 class="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white truncate">
										Auto-kategorisasi Pesan Telegram (AI / NLP)
									</h4>
									<p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
										Otomatis petakan pesan seperti <em>"makan siang 35rb"</em> ke kategori Makanan & Minuman
									</p>
								</div>
							</div>
							<div class="shrink-0">
								<Switch bind:checked={autoCategorize} />
							</div>
						</div>

						<!-- Switch 2: Overbudget Alert -->
						<div class="p-4 rounded-2xl bg-slate-50/70 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/5 flex items-center justify-between gap-4">
							<div class="flex items-center gap-3.5 min-w-0">
								<div class="w-9 h-9 rounded-xl bg-amber-500/10 text-amber-600 dark:text-amber-400 flex items-center justify-center shrink-0">
									<Bell class="w-4 h-4" />
								</div>
								<div class="min-w-0">
									<h4 class="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white truncate">
										Peringatan Batas Belanja (Overbudget Alert)
									</h4>
									<p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
										Kirim notifikasi instan Telegram saat pengeluaran mendekati 80% dari batas kuota bulanan
									</p>
								</div>
							</div>
							<div class="shrink-0">
								<Switch bind:checked={pushNotifications} />
							</div>
						</div>

						<!-- Switch 3: Weekly Financial Digest -->
						<div class="p-4 rounded-2xl bg-slate-50/70 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/5 flex items-center justify-between gap-4">
							<div class="flex items-center gap-3.5 min-w-0">
								<div class="w-9 h-9 rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400 flex items-center justify-center shrink-0">
									<Smartphone class="w-4 h-4" />
								</div>
								<div class="min-w-0">
									<h4 class="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white truncate">
										Laporan Ringkasan Finansial Mingguan
									</h4>
									<p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
										Kirim rekap total pengeluaran dan pemasukan setiap hari Minggu malam pukul 20:00 WIB
									</p>
								</div>
							</div>
							<div class="shrink-0">
								<Switch bind:checked={weeklyReport} />
							</div>
						</div>
					</div>
				</div>
			{/if}

			<!-- Section 5: Keamanan & Sesi (Danger Zone) -->
			{#if activeSection === 'all' || activeSection === 'security'}
				<div class="p-5 sm:p-6 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-rose-200/60 dark:border-rose-900/40 space-y-4">
					<div class="flex items-center justify-between pb-3 border-b border-rose-100 dark:border-rose-950/40">
						<div class="flex items-center gap-2.5">
							<div class="w-8 h-8 rounded-xl bg-rose-500/10 text-rose-600 dark:text-rose-400 flex items-center justify-center shrink-0">
								<Key class="w-4 h-4" />
							</div>
							<div>
								<h2 class="text-xs sm:text-sm font-semibold text-rose-700 dark:text-rose-400 uppercase tracking-wider">
									Sesi & Tindakan Akun
								</h2>
								<p class="text-[11px] text-slate-400">Pengelolaan sesi login peramban dan keamanan akun</p>
							</div>
						</div>
					</div>

					<div class="p-4 rounded-xl bg-rose-50/50 dark:bg-rose-950/20 border border-rose-200/50 dark:border-rose-900/30 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
						<div>
							<h4 class="text-xs sm:text-sm font-semibold text-rose-800 dark:text-rose-300">
								Keluar dari Sesi Dasbor
							</h4>
							<p class="text-xs text-rose-700/80 dark:text-rose-400/80 mt-0.5">
								Keluar dari akun PantauDuit pada peramban web ini. Sesi bot Telegram akan tetap aktif dan aman.
							</p>
						</div>

						<Button variant="danger" onclick={() => authStore.requestLogout()} class="h-9 px-4 shrink-0 justify-center">
							<LogOut class="w-4 h-4" />
							<span>Keluar Akun</span>
						</Button>
					</div>
				</div>
			{/if}
		</div>
	</div>
</div>
