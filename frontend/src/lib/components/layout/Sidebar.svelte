<script lang="ts">
	import { page } from '$app/state';
	import { authStore } from '$lib/stores/auth.svelte';
	import {
		LayoutDashboard,
		Receipt,
		Wallet,
		PieChart,
		Target,
		TrendingUp,
		BarChart3,
		Bot,
		Crown,
		Settings,
		ChevronLeft,
		ChevronRight,
		LogOut,
		Sparkles,
		Shield,
		Building2,
		Lock,
		Server,
		Terminal,
		Users,
		KeyRound,
		FolderTree,
		SlidersHorizontal,
		Briefcase,
		CalendarCheck,
		Clock,
		Fingerprint,
		ScrollText
	} from 'lucide-svelte';

	interface Props {
		collapsed?: boolean;
		onToggleCollapse?: () => void;
		onOpenQuickAction?: () => void;
	}

	let {
		collapsed = $bindable(false),
		onToggleCollapse,
		onOpenQuickAction
	}: Props = $props();

	// Dynamic Navigation depending on whether user is Superuser or Regular Subscriber/Admin
	const userNavGroups = [
		{
			title: 'KEUANGAN SAYA',
			items: [
				{ href: '/dashboard', label: 'Ringkasan Saya', icon: LayoutDashboard },
				{ href: '/transactions', label: 'Riwayat Transaksi', icon: Receipt },
				{ href: '/accounts', label: 'Dompet & Rekening', icon: Wallet },
				{ href: '/budgets', label: 'Batas Belanja', icon: PieChart },
				{ href: '/goals', label: 'Target Tabungan', icon: Target },
				{ href: '/investments', label: 'Investasi & Aset', icon: TrendingUp }
			]
		},
		{
			title: 'LAPORAN & SISTEM',
			items: [
				{ href: '/reports', label: 'Laporan Keuangan', icon: BarChart3 },
				{ href: '/telegram', label: 'Bot Telegram', icon: Bot, badge: 'Aktif' },
				{ href: '/settings', label: 'Pengaturan Akun', icon: Settings },
				{ href: '/landing', label: 'Halaman Depan', icon: Sparkles }
			]
		}
	];

	const superAdminNavGroups = [
		{
			title: 'TATA KELOLA PLATFORM',
			items: [
				{ href: '/dashboard', label: 'Ringkasan Platform', icon: Shield },
				{ href: '/users', label: 'Pengguna', icon: Users },
				{ href: '/roles', label: 'Role & Izin Akses', icon: KeyRound },
				{ href: '/menus', label: 'Navigasi Menu', icon: FolderTree },
				{ href: '/parameters', label: 'Parameter Sistem', icon: SlidersHorizontal }
			]
		},
		{
			title: 'BOT & SISTEM',
			items: [
				{ href: '/telegram', label: 'Bot Telegram', icon: Bot, badge: 'Aktif' },
				{ href: '/audit-logs', label: 'Audit Keamanan', icon: Terminal },
				{ href: '/settings', label: 'Pengaturan', icon: Settings }
			]
		},
		{
			title: 'FINANSIAL SAYA',
			items: [
				{ href: '/transactions', label: 'Riwayat Transaksi', icon: Receipt },
				{ href: '/accounts', label: 'Dompet & Rekening', icon: Wallet },
				{ href: '/budgets', label: 'Batas Belanja', icon: PieChart },
				{ href: '/investments', label: 'Investasi', icon: TrendingUp }
			]
		}
	];

	const companyNavGroups = [
		{
			title: 'PUSAT KONTROL',
			items: [
				{ href: '/company', label: 'Command Center', icon: Building2 }
			]
		},
		{
			title: 'OPERASIONAL & PRESENSI',
			items: [
				{ href: '/company/attendance', label: 'Presensi & Shift', icon: Clock, badge: 'Realtime' },
				{ href: '/company/fingerprint', label: 'Mesin Fingerprint', icon: Fingerprint, badge: 'Online' },
				{ href: '/company/leaves', label: 'Izin & Cuti', icon: CalendarCheck }
			]
		},
		{
			title: 'SDM & KEPEGAWAIAN',
			items: [
				{ href: '/company/employees', label: 'Direktori Karyawan', icon: Users, badge: '8 Staf' },
				{ href: '/company/documents', label: 'Dokumen & Surat HR', icon: ScrollText }
			]
		},
		{
			title: 'PENGGAJIAN & BIAYA',
			items: [
				{ href: '/company/payroll', label: 'Payroll & Slip Gaji', icon: Briefcase, badge: 'Auto' },
				{ href: '/company/reimbursements', label: 'Klaim Biaya', icon: Receipt }
			]
		},
		{
			title: 'KEUANGAN BISNIS',
			items: [
				{ href: '/transactions', label: 'Arus Kas Perusahaan', icon: TrendingUp },
				{ href: '/accounts', label: 'Rekening & Kas Bisnis', icon: Wallet },
				{ href: '/reports', label: 'Laporan Finansial', icon: BarChart3 }
			]
		},
		{
			title: 'SISTEM',
			items: [
				{ href: '/telegram', label: 'Bot Telegram', icon: Bot, badge: 'Sync' },
				{ href: '/subscription', label: 'Paket Perusahaan', icon: Crown },
				{ href: '/settings', label: 'Pengaturan Bisnis', icon: Settings }
			]
		}
	];

	const navGroups = $derived(
		authStore.isSuperuser
			? superAdminNavGroups
			: authStore.isBusiness
			? companyNavGroups
			: userNavGroups
	);

	function isCurrent(href: string): boolean {
		return page.url.pathname === href || (href !== '/dashboard' && page.url.pathname.startsWith(href));
	}
</script>

<aside
	class="hidden lg:flex flex-col shrink-0 border-r border-slate-200/70 dark:border-white/5 glass-panel transition-all duration-300 select-none {collapsed
		? 'w-20'
		: 'w-64'}"
>
	<!-- Main Navigation Links with Category Headers -->
	<nav class="flex-1 px-3 py-3 space-y-4 overflow-y-auto no-scrollbar">
		{#each navGroups as group}
			<div>
				{#if !collapsed}
					<div class="px-3 pb-2 text-[10px] font-semibold tracking-wider uppercase text-slate-400 dark:text-slate-500">
						{group.title}
					</div>
				{/if}

				<div class="space-y-1">
					{#each group.items as item}
						{@const active = isCurrent(item.href)}
						<a
							href={item.href}
							title={item.label}
							class="group flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold transition-all duration-150 {active
								? 'bg-[#007AFF]/10 dark:bg-[#0A84FF]/15 text-[#007AFF] dark:text-[#0A84FF]'
								: 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-white/5 hover:text-slate-900 dark:hover:text-slate-100'}"
						>
							<item.icon
								class="w-4 h-4 shrink-0 transition-transform group-hover:scale-105 {active
									? 'text-[#007AFF] dark:text-[#0A84FF]'
									: 'text-slate-400 dark:text-slate-500 group-hover:text-slate-600 dark:group-hover:text-slate-300'}"
							/>

							{#if !collapsed}
								<span class="flex-1 truncate">{item.label}</span>

								{#if item.badge}
									<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
										{item.badge}
									</span>
								{/if}
							{/if}
						</a>
					{/each}
				</div>
			</div>
		{/each}
	</nav>

	<!-- Footer: Role Status Badge in Sidebar -->
	{#if !collapsed}
		<div class="p-3 mx-3 my-2 rounded-2xl {authStore.isSuperuser
			? 'bg-purple-500/10 border border-purple-500/20'
			: 'bg-gradient-to-br from-blue-500/10 via-[#007AFF]/5 to-indigo-500/10 border border-[#007AFF]/20 dark:border-[#0A84FF]/20'}">
			<div class="flex items-center gap-2 mb-1">
				{#if authStore.isSuperuser}
					<Shield class="w-4 h-4 text-purple-600" />
					<span class="text-xs font-semibold text-purple-700 dark:text-purple-300">
						Superadmin Platform
					</span>
				{:else}
					<Sparkles class="w-4 h-4 text-[#007AFF] dark:text-[#0A84FF]" />
					<span class="text-xs font-semibold text-slate-900 dark:text-white">
						Paket {authStore.subscription?.tier?.toUpperCase() || 'PRO'}
					</span>
				{/if}
			</div>
			<p class="text-[11px] text-slate-500 dark:text-slate-400 leading-snug">
				{authStore.isSuperuser
					? 'Akses kontrol cluster & telemetri sistem.'
					: 'Asisten Telegram & tracking keuangan aktif.'}
			</p>
		</div>
	{/if}

	<!-- Footer: Collapse Toggle & Logout -->
	<div class="p-3 border-t border-slate-200/70 dark:border-white/5 flex items-center justify-between">
		{#if !collapsed}
			<button
				type="button"
				onclick={() => authStore.requestLogout()}
				class="flex items-center gap-2 px-2.5 py-2 rounded-xl text-xs font-semibold text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-500/10 transition-colors"
			>
				<LogOut class="w-4 h-4" />
				<span>Keluar</span>
			</button>
		{/if}

		<button
			type="button"
			onclick={onToggleCollapse}
			class="p-2 rounded-xl text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-white/5 transition-colors {collapsed ? 'mx-auto' : ''}"
			title={collapsed ? 'Perluas Sidebar' : 'Ciutkan Sidebar'}
			aria-label={collapsed ? 'Perluas Sidebar' : 'Ciutkan Sidebar'}
		>
			{#if collapsed}
				<ChevronRight class="w-4 h-4" />
			{:else}
				<ChevronLeft class="w-4 h-4" />
			{/if}
		</button>
	</div>
</aside>
