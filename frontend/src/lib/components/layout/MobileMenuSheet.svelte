<script lang="ts">
	import Modal from '$lib/components/ui/Modal.svelte';
	import { authStore } from '$lib/stores/auth.svelte';
	import {
		PieChart,
		Target,
		TrendingUp,
		BarChart3,
		Bot,
		Crown,
		Bell,
		Settings,
		LogOut,
		Sparkles,
		Building2,
		Server,
		Terminal,
		Shield,
		Users,
		KeyRound,
		FolderTree,
		SlidersHorizontal
	} from 'lucide-svelte';

	interface Props {
		open?: boolean;
		onclose?: () => void;
	}

	let { open = $bindable(false), onclose }: Props = $props();

	const userMenuItems = [
		{ href: '/budgets', label: 'Batas Belanja', icon: PieChart, color: 'text-amber-500' },
		{ href: '/goals', label: 'Target Tabungan', icon: Target, color: 'text-emerald-500' },
		{ href: '/investments', label: 'Portofolio Investasi', icon: TrendingUp, color: 'text-indigo-500' },
		{ href: '/reports', label: 'Laporan & Analisis', icon: BarChart3, color: 'text-blue-500' },
		{ href: '/telegram', label: 'Telegram Asisten', icon: Bot, color: 'text-[#007AFF]', badge: 'AI' },
		{ href: '/subscription', label: 'Paket Langganan', icon: Crown, color: 'text-yellow-500' },
		{ href: '/notifications', label: 'Pusat Notifikasi', icon: Bell, color: 'text-rose-500' },
		{ href: '/settings', label: 'Pengaturan Akun', icon: Settings, color: 'text-slate-500' }
	];

	const superAdminMenuItems = [
		{ href: '/dashboard', label: 'Ringkasan Platform', icon: Shield, color: 'text-[#007AFF]' },
		{ href: '/users', label: 'Pengguna', icon: Users, color: 'text-[#007AFF]', badge: '284' },
		{ href: '/roles', label: 'Role & Izin Akses', icon: KeyRound, color: 'text-purple-500' },
		{ href: '/menus', label: 'Navigasi Menu', icon: FolderTree, color: 'text-emerald-500' },
		{ href: '/parameters', label: 'Parameter Sistem', icon: SlidersHorizontal, color: 'text-indigo-500' },
		{ href: '/telegram', label: 'Bot Telegram', icon: Bot, color: 'text-[#0088cc]', badge: 'Aktif' },
		{ href: '/audit-logs', label: 'Audit Keamanan', icon: Terminal, color: 'text-emerald-500' },
		{ href: '/settings', label: 'Pengaturan Akun', icon: Settings, color: 'text-slate-500' }
	];

	const menuItems = $derived(
		authStore.isSuperuser ? superAdminMenuItems : userMenuItems
	);

	function handleNavigate() {
		open = false;
	}
</script>

<Modal bind:open title="Menu & Fitur Lengkap" description="Akses seluruh modul finansial dan pengaturan" {onclose}>
	<div class="space-y-4">
		<!-- User Info Banner -->
		<div class="p-3.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200/70 dark:border-white/10 flex items-center justify-between">
			<div class="flex items-center gap-3">
				<div class="w-10 h-10 rounded-full bg-gradient-to-br from-[#007AFF] to-[#0055B3] text-white flex items-center justify-center font-semibold text-sm">
					{authStore.user?.name.slice(0, 2).toUpperCase() || 'US'}
				</div>
				<div>
					<p class="text-sm font-semibold text-slate-900 dark:text-white leading-tight">
						{authStore.user?.name}
					</p>
					<p class="text-xs text-slate-500 dark:text-slate-400">
						{authStore.user?.role || 'SUBSCRIBER'} &bull; {authStore.user?.email}
					</p>
				</div>
			</div>
			<div class="flex items-center gap-1 px-2.5 py-1 rounded-full bg-[#007AFF]/10 text-[#007AFF] dark:text-[#0A84FF] text-xs font-semibold">
				<Sparkles class="w-3.5 h-3.5" />
				<span>{authStore.subscription?.tier?.toUpperCase() || 'PRO'}</span>
			</div>
		</div>

		<!-- Grid of Feature Cards -->
		<div class="grid grid-cols-2 gap-2.5">
			{#each menuItems as item}
				<a
					href={item.href}
					onclick={handleNavigate}
					class="p-3 rounded-2xl bg-white dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/5 hover:border-[#007AFF]/40 flex flex-col gap-2 transition-all active:scale-[0.98]"
				>
					<div class="flex items-center justify-between">
						<div class="w-8 h-8 rounded-xl bg-slate-100 dark:bg-white/5 flex items-center justify-center {item.color}">
							<item.icon class="w-4 h-4" />
						</div>
						{#if item.badge}
							<span class="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-[#007AFF]/10 text-[#007AFF]">
								{item.badge}
							</span>
						{/if}
					</div>
					<span class="text-xs font-semibold text-slate-900 dark:text-white leading-snug">
						{item.label}
					</span>
				</a>
			{/each}
		</div>

		<!-- Logout Button -->
		<button
			type="button"
			onclick={() => {
				open = false;
				authStore.requestLogout();
			}}
			class="w-full mt-2 py-3 rounded-2xl bg-rose-50 dark:bg-rose-950/30 text-rose-600 dark:text-rose-400 border border-rose-200/60 dark:border-rose-900/40 text-xs font-semibold flex items-center justify-center gap-2 hover:bg-rose-100 transition-colors"
		>
			<LogOut class="w-4 h-4" />
			<span>Keluar dari Akun</span>
		</button>
	</div>
</Modal>
