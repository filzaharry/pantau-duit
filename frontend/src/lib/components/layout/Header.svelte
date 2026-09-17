<script lang="ts">
	import { authStore } from '$lib/stores/auth.svelte';
	import { themeStore } from '$lib/stores/theme.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import IconButton from '$lib/components/ui/IconButton.svelte';
	import { formatRelativeTime } from '$lib/utils/formatters';
	import {
		Sun,
		Moon,
		Bell,
		User,
		LogOut,
		Settings,
		CheckCheck,
		ExternalLink,
		Sparkles
	} from 'lucide-svelte';

	let isNotifOpen = $state(false);
	let isUserMenuOpen = $state(false);

	function toggleTheme() {
		themeStore.setTheme(themeStore.isDark ? 'light' : 'dark');
	}

	function getRoleBadgeStyle(role?: string) {
		switch (role) {
			case 'SUPERUSER':
				return 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20';
			case 'ADMIN':
				return 'bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border-indigo-500/20';
			default:
				return 'bg-[#007AFF]/10 text-[#007AFF] dark:text-[#0A84FF] border-[#007AFF]/20';
		}
	}
</script>

<header class="sticky top-0 z-30 w-full bg-gradient-to-b from-white/95 via-white/90 to-slate-50/80 dark:from-[#131726]/95 dark:via-[#101422]/90 dark:to-[#0c0f1a]/85 backdrop-blur-md border-b border-slate-200/60 dark:border-white/[0.06] safe-top px-4 sm:px-6 h-14 sm:h-[3.75rem] flex items-center justify-between transition-all">
	<!-- Left: App Logo -->
	<div class="flex items-center gap-3">
		<a href="/dashboard" class="flex items-center gap-2 select-none group">
			<div class="w-8 h-8 rounded-lg bg-gradient-to-br from-[#007AFF] to-[#0055B3] text-white flex items-center justify-center font-semibold text-sm">
				P
			</div>
			<div class="flex flex-col">
				<span class="text-xs sm:text-sm font-semibold tracking-tight text-slate-900 dark:text-white leading-none">
					Pantau<span class="text-[#007AFF] dark:text-[#0A84FF]">Duit</span>
				</span>
				<span class="text-[9px] sm:text-[10px] text-slate-400 font-medium leading-none mt-0.5">
					{authStore.isSuperuser ? 'Console' : 'Finansial'}
				</span>
			</div>
		</a>
	</div>

	<!-- Right: Theme, Notifications Popover, and Profile Popover -->
	<div class="flex items-center gap-2 sm:gap-3">
		<!-- Theme Toggle -->
		<IconButton
			ariaLabel="Ganti Mode Tema ({themeStore.isDark ? 'Gelap' : 'Terang'})"
			variant="ghost"
			onclick={toggleTheme}
		>
			{#if themeStore.isDark}
				<Moon class="w-4 h-4 sm:w-5 sm:h-5 text-[#0A84FF]" />
			{:else}
				<Sun class="w-4 h-4 sm:w-5 sm:h-5 text-[#007AFF]" />
			{/if}
		</IconButton>

		<!-- Notification Bell with Attached Popover Container -->
		<div class="relative">
			<IconButton
				ariaLabel="Notifikasi"
				variant="ghost"
				onclick={() => { isNotifOpen = !isNotifOpen; isUserMenuOpen = false; }}
			>
				<Bell class="w-4 h-4 sm:w-5 sm:h-5" />
			</IconButton>

			{#if notificationStore.unreadCount > 0}
				<span class="absolute top-1.5 right-1.5 w-3.5 h-3.5 rounded-full bg-rose-500 text-white text-[9px] font-semibold flex items-center justify-center pointer-events-none ring-2 ring-white dark:ring-[#131B2A]">
					{notificationStore.unreadCount}
				</span>
			{/if}

			{#if isNotifOpen}
				<!-- Backdrop to close on click outside -->
				<button
					type="button"
					aria-label="Tutup notifikasi"
					class="fixed inset-0 z-40 cursor-default bg-transparent"
					onclick={() => (isNotifOpen = false)}
				></button>

				<!-- Attached Popover Container -->
				<div class="absolute right-0 top-full mt-2 w-80 sm:w-96 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/90 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/80 dark:border-white/10 z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-150">
					<!-- Popover Header -->
					<div class="p-4 border-b border-slate-100 dark:border-white/5 flex items-center justify-between">
						<div class="flex items-center gap-2">
							<span class="text-xs font-semibold uppercase tracking-wider text-slate-900 dark:text-white">
								Notifikasi
							</span>
							{#if notificationStore.unreadCount > 0}
								<span class="px-1.5 py-0.5 rounded-full text-[10px] font-semibold bg-rose-500/10 text-rose-600">
									{notificationStore.unreadCount} baru
								</span>
							{/if}
						</div>

						<button
							type="button"
							onclick={() => notificationStore.markAllAsRead()}
							class="text-xs font-semibold text-[#007AFF] dark:text-[#0A84FF] hover:underline flex items-center gap-1"
						>
							<CheckCheck class="w-3.5 h-3.5" />
							<span>Semua Dibaca</span>
						</button>
					</div>

					<!-- Scrollable Notification List -->
					<div class="max-h-80 overflow-y-auto divide-y divide-slate-100 dark:divide-white/5">
						{#if notificationStore.notifications.length > 0}
							{#each notificationStore.notifications.slice(0, 6) as item}
								<div class="p-3.5 hover:bg-slate-50 dark:hover:bg-white/[0.02] transition-colors {!item.is_read ? 'bg-[#007AFF]/5 dark:bg-[#0A84FF]/5' : ''}">
									<div class="flex items-start justify-between gap-2">
										<p class="text-xs font-semibold text-slate-900 dark:text-white truncate">
											{item.title}
										</p>
										<span class="text-[10px] text-slate-400 shrink-0">
											{formatRelativeTime(item.created_at)}
										</span>
									</div>
									<p class="text-xs text-slate-500 dark:text-slate-400 mt-1 line-clamp-2 leading-relaxed">
										{item.message}
									</p>
								</div>
							{/each}
						{:else}
							<div class="p-6 text-center text-xs text-slate-400">
								Tidak ada notifikasi baru
							</div>
						{/if}
					</div>

					<!-- Popover Footer -->
					<div class="p-2.5 border-t border-slate-100 dark:border-white/5 text-center bg-slate-50/50 dark:bg-white/[0.01]">
						<a
							href="/notifications"
							onclick={() => (isNotifOpen = false)}
							class="text-xs font-semibold text-[#007AFF] dark:text-[#0A84FF] hover:underline"
						>
							Buka Semua Notifikasi &rarr;
						</a>
					</div>
				</div>
			{/if}
		</div>

		<!-- User Section with Attached Popover Container -->
		<div class="relative">
			<button
				type="button"
				onclick={() => { isUserMenuOpen = !isUserMenuOpen; isNotifOpen = false; }}
				class="flex items-center gap-2 pl-1 sm:pl-2 select-none group focus:outline-none"
				aria-label="Menu Pengguna"
			>
				<div class="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center font-semibold text-xs text-slate-700 dark:text-slate-200 border border-slate-300/80 dark:border-white/10 group-hover:border-[#007AFF] transition-all">
					{authStore.user?.name.slice(0, 2).toUpperCase() || 'US'}
				</div>

				<div class="hidden md:flex flex-col text-left">
					<span class="text-xs font-semibold text-slate-900 dark:text-white leading-none truncate max-w-[120px]">
						{authStore.user?.name || 'User'}
					</span>
					<span class="text-[9px] font-semibold uppercase tracking-wider mt-0.5 leading-none {authStore.isSuperuser ? 'text-purple-500' : authStore.isAdmin ? 'text-indigo-500' : 'text-[#007AFF]'}">
						{authStore.user?.role || 'SUBSCRIBER'}
					</span>
				</div>
			</button>

			{#if isUserMenuOpen}
				<!-- Backdrop to close on click outside -->
				<button
					type="button"
					aria-label="Tutup menu"
					class="fixed inset-0 z-40 cursor-default bg-transparent"
					onclick={() => (isUserMenuOpen = false)}
				></button>

				<!-- Attached Popover Container -->
				<div class="absolute right-0 top-full mt-2 w-64 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/90 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/80 dark:border-white/10 z-50 p-4 space-y-3 animate-in fade-in slide-in-from-top-2 duration-150">
					<!-- User Profile Info -->
					<div class="flex items-center gap-3 pb-3 border-b border-slate-100 dark:border-white/5">
						<div class="w-10 h-10 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center font-semibold text-sm text-slate-800 dark:text-slate-100">
							{authStore.user?.name.slice(0, 2).toUpperCase() || 'US'}
						</div>
						<div class="min-w-0 flex-1">
							<p class="text-xs font-semibold text-slate-900 dark:text-white truncate">
								{authStore.user?.name}
							</p>
							<p class="text-[11px] text-slate-400 truncate">
								{authStore.user?.email}
							</p>
						</div>
					</div>

					<!-- Role Badge -->
					<div class="flex items-center justify-between text-xs">
						<span class="text-slate-400">Hak Akses</span>
						<span class="px-2 py-0.5 rounded text-[10px] font-semibold uppercase border {getRoleBadgeStyle(authStore.user?.role)}">
							{authStore.user?.role || 'SUBSCRIBER'}
						</span>
					</div>

					<!-- Navigation Actions: Settings & Logout -->
					<div class="pt-2 border-t border-slate-100 dark:border-white/5 space-y-1">
						<a
							href="/settings"
							onclick={() => (isUserMenuOpen = false)}
							class="flex items-center gap-2 px-2.5 py-2 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-white/5 transition-colors"
						>
							<Settings class="w-3.5 h-3.5 text-slate-400" />
							<span>Pengaturan</span>
						</a>

						<button
							type="button"
							onclick={() => { isUserMenuOpen = false; authStore.requestLogout(); }}
							class="w-full flex items-center gap-2 px-2.5 py-2 rounded-xl text-xs font-semibold text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-colors text-left"
						>
							<LogOut class="w-3.5 h-3.5" />
							<span>Keluar Akun</span>
						</button>
					</div>
				</div>
			{/if}
		</div>
	</div>
</header>
