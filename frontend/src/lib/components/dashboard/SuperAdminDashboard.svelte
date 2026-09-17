<script lang="ts">
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import { financialStore } from '$lib/stores/financial.svelte';
	import { formatRupiah } from '$lib/utils/formatters';
	import Button from '$lib/components/ui/Button.svelte';
	import ProgressBar from '$lib/components/ui/ProgressBar.svelte';
	import Table, { type TableColumn } from '$lib/components/ui/Table.svelte';
	import {
		Shield,
		Users,
		Receipt,
		Bot,
		CheckCircle2,
		ArrowRight,
		Activity,
		KeyRound,
		FolderTree,
		SlidersHorizontal,
		UserPlus,
		ExternalLink,
		Sparkles,
		Clock,
		Send,
		Wallet
	} from 'lucide-svelte';

	// 7 Days Daily Transaction Count (Frequency of personal finance records, NOT monetary amount)
	const activityTrend = [
		{ day: '06 Sep', count: 520, telegramPercent: 72 },
		{ day: '07 Sep', count: 640, telegramPercent: 75 },
		{ day: '08 Sep', count: 590, telegramPercent: 70 },
		{ day: '09 Sep', count: 710, telegramPercent: 76 },
		{ day: '10 Sep', count: 680, telegramPercent: 73 },
		{ day: '11 Sep', count: 820, telegramPercent: 78 },
		{ day: '12 Sep', count: 650, telegramPercent: 74 }
	];

	const maxDayCount = Math.max(...activityTrend.map((d) => d.count));

	// Recent Registered Users (Personal accounts)
	const recentUsers = [
		{
			id: 'usr-01',
			name: 'Budi Pratama',
			email: 'budi.pratama@gmail.com',
			telegram: '@budipratama',
			isTelegramLinked: true,
			plan: 'PRO',
			joinedAt: '12 Sep 2026, 18:30 WIB',
			status: 'ACTIVE'
		},
		{
			id: 'usr-02',
			name: 'Siti Rahmawati',
			email: 'siti.rahma@yahoo.com',
			telegram: '@siti_rahma',
			isTelegramLinked: true,
			plan: 'FREE',
			joinedAt: '12 Sep 2026, 16:15 WIB',
			status: 'ACTIVE'
		},
		{
			id: 'usr-03',
			name: 'Dimas Nugroho',
			email: 'dimas.nugroho@gmail.com',
			telegram: '-',
			isTelegramLinked: false,
			plan: 'FREE',
			joinedAt: '12 Sep 2026, 14:05 WIB',
			status: 'ACTIVE'
		},
		{
			id: 'usr-04',
			name: 'Anisa Maharani',
			email: 'anisa.mhrn@outlook.com',
			telegram: '@anisa_m',
			isTelegramLinked: true,
			plan: 'PRO',
			joinedAt: '11 Sep 2026, 21:40 WIB',
			status: 'ACTIVE'
		},
		{
			id: 'usr-05',
			name: 'Reza Fahrezi',
			email: 'reza.fahrezi@gmail.com',
			telegram: '@reza_f',
			isTelegramLinked: true,
			plan: 'FREE',
			joinedAt: '11 Sep 2026, 19:22 WIB',
			status: 'ACTIVE'
		}
	];

	const userColumns: TableColumn<any>[] = [
		{ key: 'name', header: 'Nama & Email', sortable: true },
		{ key: 'telegram', header: 'Telegram', sortable: true },
		{ key: 'plan', header: 'Paket Akun', sortable: true },
		{ key: 'joinedAt', header: 'Tanggal Bergabung', sortable: true },
		{ key: 'status', header: 'Status', sortable: true, align: 'right' }
	];
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full pb-24 lg:pb-10">
	<!-- Platform Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-200/80 dark:border-white/10">
		<div class="flex items-center gap-3">
			<div class="w-10 h-10 rounded-2xl bg-gradient-to-br from-[#007AFF] to-indigo-600 text-white flex items-center justify-center shadow-md shadow-blue-500/20">
				<Shield class="w-5 h-5" />
			</div>
			<div>
				<div class="flex items-center gap-2">
					<h1 class="text-xl font-semibold text-slate-900 dark:text-white tracking-tight">
						Ringkasan Platform PantauDuit
					</h1>
					<span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 uppercase tracking-wider">
						Sistem Normal
					</span>
				</div>
				<p class="text-xs text-slate-500 dark:text-slate-400">
					Pusat kontrol operasional platform pencatatan keuangan personal & bot Telegram
				</p>
			</div>
		</div>

		<div class="flex items-center gap-2 self-start sm:self-auto">
			<a
				href="/users"
				class="h-9 px-3.5 rounded-xl bg-[#007AFF] text-white text-xs font-semibold hover:bg-[#007AFF]/90 transition-all flex items-center gap-1.5 shadow-xs"
			>
				<UserPlus class="w-3.5 h-3.5" />
				<span>Kelola Pengguna</span>
			</a>
		</div>
	</div>

	<!-- 4-Column Platform Overview Ribbon -->
	<div class="p-3 sm:p-5 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
		<div class="grid grid-cols-2 lg:grid-cols-4 gap-2.5 sm:gap-4 lg:divide-x divide-slate-100 dark:divide-white/5">
			<!-- Col 1: Total Registered Users -->
			<div class="flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-[#007AFF]/10 text-[#007AFF] dark:text-[#0A84FF] flex items-center justify-center shrink-0">
					<Users class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Total Pengguna Terdaftar</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">284 Pengguna</span>
					<span class="text-[10px] sm:text-[11px] text-emerald-500 font-medium truncate block">+12 Pengguna baru minggu ini</span>
				</div>
			</div>

			<!-- Col 2: Telegram Bot Connected -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-blue-500/10 text-[#0088cc] flex items-center justify-center shrink-0">
					<Bot class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Terhubung Bot Telegram</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">210 Akun</span>
					<span class="text-[10px] sm:text-[11px] text-blue-500 font-medium truncate block">74% Tingkat Adopsi Bot</span>
				</div>
			</div>

			<!-- Col 3: User Activity / Recorded Entries -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400 flex items-center justify-center shrink-0">
					<Receipt class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Catatan Keuangan Dibuat</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">18.420 Catatan</span>
					<span class="text-[10px] sm:text-[11px] text-purple-600 dark:text-purple-400 font-medium truncate block">Rata-rata 65 catatan / user</span>
				</div>
			</div>

			<!-- Col 4: Service Health & Telegram Webhook -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
					<Activity class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Status Bot Telegram</span>
					<span class="text-xs sm:text-base font-semibold text-emerald-600 dark:text-emerald-400 truncate block">Online (42ms)</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">Webhook @PantauDuitBot Aktif</span>
				</div>
			</div>
		</div>
	</div>

	<!-- Finansial Sistem PantauDuit (Ringkasan Saldo & Arus Kas) -->
	<div class="p-4 sm:p-5 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] flex flex-col md:flex-row md:items-center justify-between gap-4">
		<div class="flex items-center gap-3">
			<div class="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
				<Wallet class="w-5 h-5" />
			</div>
			<div>
				<div class="flex items-center gap-2">
					<h3 class="text-sm font-semibold text-slate-900 dark:text-white">Finansial Sistem PantauDuit</h3>
					<span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
						Aktif
					</span>
				</div>
				<p class="text-xs text-slate-500 dark:text-slate-400">
					Saldo terkumpul, langganan masuk, dan pengeluaran server/domain
				</p>
			</div>
		</div>

		<div class="flex flex-wrap items-center gap-4 sm:gap-6">
			<div>
				<span class="text-[10px] uppercase text-slate-400 font-semibold block">Total Saldo</span>
				<span class="text-sm font-semibold text-slate-900 dark:text-white">
					{formatRupiah(financialStore.totalBalance)}
				</span>
			</div>
			<div class="border-l border-slate-200 dark:border-white/10 pl-4 sm:pl-6">
				<span class="text-[10px] uppercase text-slate-400 font-semibold block">Langganan Masuk</span>
				<span class="text-sm font-semibold text-emerald-600 dark:text-emerald-400">
					+{formatRupiah(financialStore.monthlyIncome)}
				</span>
			</div>
			<div class="border-l border-slate-200 dark:border-white/10 pl-4 sm:pl-6">
				<span class="text-[10px] uppercase text-slate-400 font-semibold block">Sewa Server & Domain</span>
				<span class="text-sm font-semibold text-rose-600 dark:text-rose-400">
					-{formatRupiah(financialStore.monthlyExpense)}
				</span>
			</div>
			<a
				href="/transactions"
				class="h-8 px-3 rounded-lg bg-[#007AFF]/10 hover:bg-[#007AFF]/15 text-[#007AFF] dark:text-[#0A84FF] text-xs font-semibold flex items-center gap-1.5 transition-all ml-auto md:ml-2"
			>
				<span>Buka Finansial</span>
				<ArrowRight class="w-3.5 h-3.5" />
			</a>
		</div>
	</div>

	<!-- Grid: 7-Day Activity Trend & Channel Proportion -->
	<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
		<!-- Left: 7-Day Daily Entries Activity Chart (2 cols) -->
		<div class="lg:col-span-2 p-5 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] space-y-4">
			<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 dark:border-white/5 pb-3">
				<div>
					<h2 class="text-sm font-semibold text-slate-900 dark:text-white uppercase tracking-wider flex items-center gap-2">
						<Activity class="w-4 h-4 text-[#007AFF] dark:text-[#0A84FF]" />
						<span>Frekuensi Pencatatan Finansial Pengguna (7 Hari Terakhir)</span>
					</h2>
					<p class="text-xs text-slate-500 dark:text-slate-400">
						Jumlah catatan pengeluaran & pemasukan yang diinput pengguna setiap hari
					</p>
				</div>

				<div class="flex items-center gap-3 text-xs">
					<div class="flex items-center gap-1.5">
						<span class="w-2.5 h-2.5 rounded-sm bg-[#007AFF]"></span>
						<span class="text-slate-500">Total Catatan Harian</span>
					</div>
				</div>
			</div>

			<!-- Visual Bar Chart -->
			<div class="pt-4 space-y-3">
				<div class="h-44 flex items-end justify-between gap-3 px-2">
					{#each activityTrend as item}
						{@const heightPercent = Math.round((item.count / maxDayCount) * 100)}

						<div class="flex-1 flex flex-col items-center gap-2 group h-full justify-end">
							<!-- Tooltip -->
							<div class="opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none text-center bg-slate-900 text-white dark:bg-white dark:text-slate-900 px-2 py-1 rounded-lg text-[10px] whitespace-nowrap mb-1 z-10 shadow-lg">
								<div class="font-semibold">{item.count} Catatan</div>
								<div class="text-[9px] opacity-80">{item.telegramPercent}% via Bot</div>
							</div>

							<!-- Bar Pill -->
							<div class="w-full max-w-[44px] rounded-xl overflow-hidden flex flex-col justify-end bg-slate-100 dark:bg-white/5 transition-all group-hover:brightness-110" style="height: {heightPercent}%;">
								<div class="w-full bg-[#007AFF]/90 rounded-xl transition-all h-full"></div>
							</div>

							<!-- Day Label -->
							<span class="text-[11px] font-medium text-slate-500 group-hover:text-slate-900 dark:group-hover:text-white transition-colors">
								{item.day}
							</span>
						</div>
					{/each}
				</div>

				<div class="pt-2 border-t border-slate-100 dark:border-white/5 flex items-center justify-between text-xs text-slate-500">
					<span>Rata-rata Harian: <strong>660 Catatan Keuangan</strong> / hari</span>
					<span class="text-emerald-500 font-medium">Aktivitas stabil & konsisten</span>
				</div>
			</div>
		</div>

		<!-- Right: Input Channels & Plan Tiers (1 col) -->
		<div class="p-5 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] space-y-5">
			<div>
				<h2 class="text-sm font-semibold text-slate-900 dark:text-white uppercase tracking-wider flex items-center gap-2">
					<Bot class="w-4 h-4 text-[#0088cc]" />
					<span>Kanal Input Pengguna</span>
				</h2>
				<p class="text-xs text-slate-500 dark:text-slate-400">
					Metode yang paling banyak digunakan pengguna untuk mencatat
				</p>
			</div>

			<!-- Channel Distribution Bars -->
			<div class="space-y-4 text-xs">
				<div>
					<div class="flex items-center justify-between mb-1.5">
						<span class="flex items-center gap-1.5 font-medium text-slate-800 dark:text-slate-200">
							<Bot class="w-3.5 h-3.5 text-[#0088cc]" />
							<span>Bot Telegram (Quick Chat / Struk)</span>
						</span>
						<span class="font-semibold text-slate-900 dark:text-white">74% (13.630 catatan)</span>
					</div>
					<ProgressBar value={74} variant="blue" size="sm" />
				</div>

				<div>
					<div class="flex items-center justify-between mb-1.5">
						<span class="flex items-center gap-1.5 font-medium text-slate-800 dark:text-slate-200">
							<Receipt class="w-3.5 h-3.5 text-purple-500" />
							<span>Web App (Form Manual)</span>
						</span>
						<span class="font-semibold text-slate-900 dark:text-white">26% (4.790 catatan)</span>
					</div>
					<ProgressBar value={26} variant="purple" size="sm" />
				</div>
			</div>

			<!-- Subscription Plan Breakdown -->
			<div class="pt-3 border-t border-slate-100 dark:border-white/5 space-y-2.5">
				<span class="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
					Distribusi Paket Pengguna
				</span>
				<div class="space-y-2 text-xs">
					<div class="flex items-center justify-between">
						<span class="text-slate-600 dark:text-slate-300">Pengguna Free (Gratis)</span>
						<strong class="text-slate-900 dark:text-white">242 Pengguna (85%)</strong>
					</div>
					<div class="flex items-center justify-between">
						<span class="text-slate-600 dark:text-slate-300">Pengguna Pro (Berbayar)</span>
						<strong class="text-emerald-600 dark:text-emerald-400">42 Pengguna (15%)</strong>
					</div>
				</div>
			</div>
		</div>
	</div>

	<!-- Recent Registered Users Table -->
	<Table
		title="Pengguna Terbaru Mendaftar"
		subtitle="5 pengguna personal terakhir yang mendaftar ke aplikasi"
		icon={Users}
		badge="{recentUsers.length} Pengguna"
		columns={userColumns}
		items={recentUsers}
		paginated={true}
		pageSize={5}
		pageSizeOptions={[5, 10, 20]}
	>
		{#snippet headerActions()}
			<a
				href="/users"
				class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-white/5 hover:bg-[#007AFF] hover:text-white text-slate-700 dark:text-slate-200 text-xs font-semibold transition-all"
			>
				<span>Lihat Semua Pengguna</span>
				<ArrowRight class="w-3.5 h-3.5" />
			</a>
		{/snippet}

		{#snippet row(user, index)}
			<tr class="hover:bg-slate-50/60 dark:hover:bg-white/[0.02] transition-colors">
				<td class="p-3.5">
					<p class="font-semibold text-slate-900 dark:text-white">{user.name}</p>
					<span class="text-[11px] text-slate-400">{user.email}</span>
				</td>
				<td class="p-3.5 whitespace-nowrap">
					{#if user.isTelegramLinked}
						<span class="inline-flex items-center gap-1 font-mono text-[#0088cc] font-medium">
							<Bot class="w-3 h-3" />
							<span>{user.telegram}</span>
						</span>
					{:else}
						<span class="text-slate-400 italic">Belum terhubung</span>
					{/if}
				</td>
				<td class="p-3.5 whitespace-nowrap">
					<span class="px-2 py-0.5 rounded-lg text-[10px] font-semibold {user.plan === 'PRO'
						? 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20'
						: 'bg-slate-100 dark:bg-white/5 text-slate-600 dark:text-slate-300'}">
						{user.plan === 'PRO' ? 'Pro Subscriber' : 'Free User'}
					</span>
				</td>
				<td class="p-3.5 text-slate-500 whitespace-nowrap">
					{user.joinedAt}
				</td>
				<td class="p-3.5 text-right whitespace-nowrap">
					<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-600 border border-emerald-500/20">
						Aktif
					</span>
				</td>
			</tr>
		{/snippet}
	</Table>

	<!-- Quick Navigation to Admin Modules -->
	<div class="space-y-3">
		<h2 class="text-xs font-semibold text-slate-400 uppercase tracking-wider">
			Pusat Tata Kelola Platform
		</h2>

		<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
			<a
				href="/users"
				class="p-4 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] hover:border-[#007AFF]/40 transition-all group"
			>
				<div class="flex items-center justify-between mb-2">
					<div class="w-8 h-8 rounded-xl bg-[#007AFF]/10 text-[#007AFF] dark:text-[#0A84FF] flex items-center justify-center">
						<Users class="w-4 h-4" />
					</div>
					<span class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-[#007AFF]/10 text-[#007AFF]">284 User</span>
				</div>
				<h4 class="text-xs font-semibold text-slate-900 dark:text-white group-hover:text-[#007AFF] transition-colors">
					Manajemen Pengguna
				</h4>
				<p class="text-[11px] text-slate-400 mt-0.5">
					Direktori user, paket langganan, & status aktif
				</p>
			</a>

			<a
				href="/roles"
				class="p-4 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] hover:border-purple-500/40 transition-all group"
			>
				<div class="flex items-center justify-between mb-2">
					<div class="w-8 h-8 rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400 flex items-center justify-center">
						<KeyRound class="w-4 h-4" />
					</div>
					<span class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-600">Hak Akses</span>
				</div>
				<h4 class="text-xs font-semibold text-slate-900 dark:text-white group-hover:text-purple-600 transition-colors">
					Role & Izin Fitur
				</h4>
				<p class="text-[11px] text-slate-400 mt-0.5">
					Atur kewenangan Superadmin, Pro, & Free
				</p>
			</a>

			<a
				href="/menus"
				class="p-4 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] hover:border-blue-500/40 transition-all group"
			>
				<div class="flex items-center justify-between mb-2">
					<div class="w-8 h-8 rounded-xl bg-blue-500/10 text-blue-500 flex items-center justify-center">
						<FolderTree class="w-4 h-4" />
					</div>
					<span class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-500">Navigasi</span>
				</div>
				<h4 class="text-xs font-semibold text-slate-900 dark:text-white group-hover:text-blue-500 transition-colors">
					Pengaturan Menu
				</h4>
				<p class="text-[11px] text-slate-400 mt-0.5">
					Visibilitas menu & urutan navigasi aplikasi
				</p>
			</a>

			<a
				href="/parameters"
				class="p-4 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] hover:border-emerald-500/40 transition-all group"
			>
				<div class="flex items-center justify-between mb-2">
					<div class="w-8 h-8 rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
						<SlidersHorizontal class="w-4 h-4" />
					</div>
					<span class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600">Global</span>
				</div>
				<h4 class="text-xs font-semibold text-slate-900 dark:text-white group-hover:text-emerald-500 transition-colors">
					Parameter Sistem
				</h4>
				<p class="text-[11px] text-slate-400 mt-0.5">
					Batas kuota, pesan bot, & mode pemeliharaan
				</p>
			</a>
		</div>
	</div>
</div>
