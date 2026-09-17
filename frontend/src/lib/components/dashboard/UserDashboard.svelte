<script lang="ts">
	import { authStore } from '$lib/stores/auth.svelte';
	import { financialStore } from '$lib/stores/financial.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import { formatRupiah, formatDateTime, formatRelativeTime } from '$lib/utils/formatters';
	import AddTransactionModal from '$lib/components/financial/AddTransactionModal.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import ProgressBar from '$lib/components/ui/ProgressBar.svelte';
	import SpendingDonut from '$lib/components/charts/SpendingDonut.svelte';
	import CashflowBar from '$lib/components/charts/CashflowBar.svelte';
	import type { Transaction } from '$lib/types';
	import {
		Eye,
		EyeOff,
		ArrowLeftRight,
		Building2,
		Wallet,
		Banknote,
		ChevronRight,
		CheckCircle2,
		ArrowUpRight,
		ArrowDownLeft,
		BarChart3,
		PieChart,
		Trash2,
		Shield,
		Bot,
		Sliders,
		Plus,
		Receipt,
		Target,
		TrendingUp,
		MoreHorizontal
	} from 'lucide-svelte';

	let isAddModalOpen = $state(false);
	let hideBalance = $state(false);

	// Modals for Progressive Disclosure
	let isBudgetModalOpen = $state(false);
	let isChartModalOpen = $state(false);
	let selectedTx = $state<Transaction | null>(null);

	// Date formatted in Indonesian
	const todayDate = new Intl.DateTimeFormat('id-ID', {
		weekday: 'long',
		year: 'numeric',
		month: 'long',
		day: 'numeric'
	}).format(new Date());

	// Net cashflow calculation
	const netSavings = $derived(
		financialStore.monthlyIncome - financialStore.monthlyExpense
	);

	// Total Budget Limit & Spent
	const totalBudgetLimit = $derived(
		financialStore.budgets.reduce((acc, b) => acc + (b.limit_amount ?? b.amount ?? 0), 0)
	);
	const totalBudgetSpent = $derived(
		financialStore.budgets.reduce((acc, b) => acc + (b.spent_amount || 0), 0)
	);
	const remainingBudget = $derived(Math.max(0, totalBudgetLimit - totalBudgetSpent));
	const budgetPercent = $derived(
		totalBudgetLimit > 0 ? Math.round((totalBudgetSpent / totalBudgetLimit) * 100) : 0
	);

	function handleDeleteSelectedTx() {
		if (!selectedTx) return;
		financialStore.deleteTransaction(selectedTx.id);
		selectedTx = null;
		notificationStore.toast('Transaksi berhasil dihapus', 'info');
	}
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full pb-24 lg:pb-10">
	<!-- 1. TOP GREETING & DATE -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
		<div>
			<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight">
				Halo, {authStore.user?.name || 'Budi Santoso'} 👋
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-0.5">
				{todayDate}
			</p>
		</div>

		<div class="flex items-center gap-2 self-start sm:self-auto">
			<a
				href="/telegram"
				class="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 text-xs font-semibold"
			>
				<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
				<span>Telegram Bot Aktif</span>
			</a>
		</div>
	</div>



	<!-- 3. HERO FINANCIAL CARD WITH 3D IMAGE BANNER & ENLARGED METRICS -->
	<div class="relative overflow-hidden rounded-3xl border border-slate-200/70 dark:border-white/10 bg-white dark:bg-slate-900 transition-all">
		<!-- Light mode 3D banner image -->
		<img
			src="/hero_banner_3d.jpg"
			alt="Finance 3D Background"
			class="absolute inset-0 w-full h-full object-cover object-[82%_center] sm:object-right pointer-events-none select-none dark:hidden"
			loading="eager"
		/>

		<!-- Dark mode 3D banner image -->
		<img
			src="/hero_banner_dark_3d.jpg"
			alt="Finance 3D Background Dark"
			class="absolute inset-0 w-full h-full object-cover object-[82%_center] sm:object-right pointer-events-none select-none hidden dark:block"
			loading="eager"
		/>

		<!-- Subtle ambient gradient veil for perfect contrast on text side -->
		<div class="absolute inset-0 bg-gradient-to-r from-white/95 via-white/85 to-white/20 sm:from-white/95 sm:via-white/70 sm:to-transparent dark:from-slate-950/95 dark:via-slate-950/80 dark:to-slate-950/20 sm:dark:from-slate-950/95 sm:dark:via-slate-950/70 sm:dark:to-transparent pointer-events-none"></div>

		<!-- Main Card Content -->
		<div class="relative z-10 p-5 sm:p-7 flex flex-col gap-5 max-w-full lg:max-w-[68%]">
			<!-- Header: Title & Privacy Eye Toggle -->
			<div class="flex items-center justify-between">
				<span class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
					Total Saldo
				</span>

				<div class="flex items-center gap-2">
					<span class="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
						<CheckCircle2 class="w-3.5 h-3.5" />
						Sehat
					</span>

					<button
						type="button"
						onclick={() => (hideBalance = !hideBalance)}
						class="text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 p-1"
						aria-label={hideBalance ? 'Tampilkan saldo' : 'Sembunyikan saldo'}
					>
						{#if hideBalance}
							<EyeOff class="w-4 h-4" />
						{:else}
							<Eye class="w-4 h-4" />
						{/if}
					</button>
				</div>
			</div>

			<!-- Main Prominent Balance -->
			<div>
				<h2 class="text-3xl sm:text-4xl font-semibold text-slate-900 dark:text-white tracking-tight">
					{#if hideBalance}
						Rp ••••••••••
					{:else}
						{formatRupiah(financialStore.totalBalance)}
					{/if}
				</h2>
			</div>

			<!-- 3 Essential Glance Metrics: Pemasukan, Pengeluaran, Tabungan (Enlarged Nominals) -->
			<div class="grid grid-cols-3 gap-2 sm:gap-4 p-3.5 sm:p-4 rounded-2xl bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border border-slate-200/60 dark:border-white/10">
				<!-- Inflow -->
				<div class="flex flex-col">
					<div class="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 font-medium">
						<span class="w-2 h-2 rounded-full bg-emerald-500 shrink-0"></span>
						<span class="truncate">Pemasukan</span>
					</div>
					<span class="text-base sm:text-lg lg:text-xl font-semibold text-emerald-600 dark:text-emerald-400 mt-1.5 truncate tracking-tight">
						{#if hideBalance}
							••••••
						{:else}
							{formatRupiah(financialStore.monthlyIncome, true)}
						{/if}
					</span>
				</div>

				<!-- Outflow -->
				<div class="flex flex-col border-x border-slate-200/60 dark:border-white/10 px-2 sm:px-4">
					<div class="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 font-medium">
						<span class="w-2 h-2 rounded-full bg-rose-500 shrink-0"></span>
						<span class="truncate">Pengeluaran</span>
					</div>
					<span class="text-base sm:text-lg lg:text-xl font-semibold text-rose-600 dark:text-rose-400 mt-1.5 truncate tracking-tight">
						{#if hideBalance}
							••••••
						{:else}
							{formatRupiah(financialStore.monthlyExpense, true)}
						{/if}
					</span>
				</div>

				<!-- Sisa Uang / Net (Blue) -->
				<div class="flex flex-col text-right">
					<div class="flex items-center justify-end gap-1.5 text-xs text-slate-500 dark:text-slate-400 font-medium">
						<span class="w-2 h-2 rounded-full bg-[#007AFF] shrink-0"></span>
						<span class="truncate">Tabungan</span>
					</div>
					<span class="text-base sm:text-lg lg:text-xl font-semibold text-[#007AFF] dark:text-[#0A84FF] mt-1.5 truncate tracking-tight">
						{#if hideBalance}
							••••••
						{:else}
							{netSavings >= 0 ? '+' : ''}{formatRupiah(netSavings, true)}
						{/if}
					</span>
				</div>
			</div>

			<!-- Budget Quota Status in Frosted Glass -->
			<div class="p-3 sm:p-3.5 rounded-2xl bg-white/75 dark:bg-slate-900/75 backdrop-blur-md border border-slate-200/50 dark:border-white/5 space-y-2">
				<div class="flex items-center justify-between text-xs">
					<span class="text-slate-700 dark:text-slate-300 font-semibold">
						Batas Belanja
					</span>
					<span class="font-semibold text-emerald-600 dark:text-emerald-400">
						Sisa: {formatRupiah(remainingBudget)}
					</span>
				</div>

				<!-- Visual Progress Bar with Radar Beacon & Gradient -->
				<ProgressBar value={budgetPercent} variant="auto" size="md" />

				<div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
					<span>Terpakai {formatRupiah(totalBudgetSpent)} / {formatRupiah(totalBudgetLimit)}</span>
					<!-- Progressive Disclosure: Detail Kuota Button -->
					<button
						type="button"
						onclick={() => (isBudgetModalOpen = true)}
						class="font-semibold text-[#007AFF] dark:text-[#0A84FF] hover:underline"
					>
						Rincian &rarr;
					</button>
				</div>
			</div>
		</div>
	</div>

	<!-- 4. REKENING & DOMPET (Clean 4-column cards with Blue Accents) -->
	<div class="space-y-3">
		<div class="flex items-center justify-between">
			<span class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
				Rekening & Dompet
			</span>
			<a href="/accounts" class="text-xs font-semibold text-[#007AFF] dark:text-[#0A84FF] hover:underline flex items-center">
				Kelola <ChevronRight class="w-3.5 h-3.5 ml-0.5" />
			</a>
		</div>

		<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
			{#each financialStore.accounts as acc}
				<div class="p-4 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] flex flex-col justify-between h-36 transition-all hover:border-blue-500/30 hover:-translate-y-0.5">
					<!-- Top Row: Icon and More Button -->
					<div class="flex items-center justify-between">
						<div class="w-10 h-10 rounded-xl flex items-center justify-center text-white shrink-0" style="background-color: {acc.color || '#007AFF'};">
							{#if acc.type === 'BANK'}
								<Building2 class="w-5 h-5" />
							{:else if acc.type === 'E_WALLET'}
								<Wallet class="w-5 h-5" />
							{:else}
								<Banknote class="w-5 h-5" />
							{/if}
						</div>

						<a href="/accounts" class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1" title="Kelola Rekening">
							<MoreHorizontal class="w-4 h-4" />
						</a>
					</div>

					<!-- Bottom Row: Account Info -->
					<div>
						<h4 class="text-xs font-semibold text-slate-900 dark:text-white truncate">
							{acc.name}
						</h4>
						<p class="text-[11px] text-slate-400 truncate">
							{acc.type.replace('_', ' ')}
						</p>

						<div class="flex items-center justify-between mt-2 pt-2 border-t border-slate-100 dark:border-white/5">
							<div class="flex items-center gap-1.5">
								<span class="w-2 h-2 rounded-full bg-[#007AFF]"></span>
								<span class="text-[10px] font-semibold text-slate-500 dark:text-slate-400">Aktif</span>
							</div>
							<span class="text-xs font-semibold text-slate-900 dark:text-white">
								{#if hideBalance}
									••••••
								{:else}
									{formatRupiah(acc.current_balance)}
								{/if}
							</span>
						</div>
					</div>
				</div>
			{/each}
		</div>
	</div>

	<!-- 5. DUAL PANELS (Rincian Finansial & Aksi Cepat in Blue Accent) -->
	<div class="grid grid-cols-1 lg:grid-cols-2 gap-6 pt-2">
		<!-- Left Panel: Rincian Finansial -->
		<div class="p-5 sm:p-6 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] flex flex-col justify-between space-y-5">
			<div>
				<h3 class="text-sm font-semibold text-slate-900 dark:text-white tracking-tight mb-4">
					Rincian Finansial
				</h3>

				<div class="space-y-3.5 text-xs">
					<!-- Row 1: Plan Type -->
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2.5 text-slate-500 dark:text-slate-400">
							<Wallet class="w-4 h-4 text-[#007AFF]" />
							<span>Tipe Paket</span>
						</div>
						<span class="font-semibold text-slate-900 dark:text-white">Personal Pro</span>
					</div>

					<!-- Row 2: Monthly Budget -->
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2.5 text-slate-500 dark:text-slate-400">
							<Target class="w-4 h-4 text-[#007AFF]" />
							<span>Batas Belanja Bulanan</span>
						</div>
						<span class="font-semibold text-slate-900 dark:text-white">{formatRupiah(totalBudgetLimit)}</span>
					</div>

					<!-- Row 3: Net Cashflow -->
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2.5 text-slate-500 dark:text-slate-400">
							<TrendingUp class="w-4 h-4 text-[#007AFF]" />
							<span>Arus Kas Bersih</span>
						</div>
						<span class="font-semibold text-emerald-600 dark:text-emerald-400">
							{netSavings >= 0 ? '+' : ''}{formatRupiah(netSavings)}
						</span>
					</div>

					<!-- Row 4: Total Transactions -->
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2.5 text-slate-500 dark:text-slate-400">
							<Receipt class="w-4 h-4 text-[#007AFF]" />
							<span>Transaksi Terdata</span>
						</div>
						<span class="font-semibold text-slate-900 dark:text-white">{financialStore.transactions.length} Mutasi</span>
					</div>

					<!-- Row 5: Telegram Integration -->
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2.5 text-slate-500 dark:text-slate-400">
							<Bot class="w-4 h-4 text-[#007AFF]" />
							<span>Bot Telegram</span>
						</div>
						<a href="/telegram" class="font-semibold text-[#007AFF] dark:text-[#0A84FF] hover:underline flex items-center gap-1">
							@pantauduit_bot <ChevronRight class="w-3.5 h-3.5" />
						</a>
					</div>
				</div>
			</div>

			<!-- Full-Width Action Button -->
			<button
				type="button"
				onclick={() => (isChartModalOpen = true)}
				class="w-full py-2.5 px-4 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-[#181c28] dark:hover:bg-[#202535] text-slate-800 dark:text-slate-200 text-xs font-semibold transition-colors flex items-center justify-center gap-2"
			>
				<PieChart class="w-4 h-4 text-[#007AFF]" />
				<span>Buka Diagram & Analisis Finansial</span>
			</button>
		</div>

		<!-- Right Panel: Aksi Cepat -->
		<div class="p-5 sm:p-6 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] flex flex-col justify-between space-y-4">
			<div>
				<h3 class="text-sm font-semibold text-slate-900 dark:text-white tracking-tight mb-3">
					Aksi Cepat
				</h3>

				<div class="divide-y divide-slate-100 dark:divide-white/5">
					<!-- Action 1: Catat Transaksi Baru -->
					<button
						type="button"
						onclick={() => (isAddModalOpen = true)}
						class="w-full py-3 flex items-center justify-between gap-3 text-left group hover:opacity-80 transition-opacity"
					>
						<div class="flex items-center gap-3 min-w-0">
							<div class="w-9 h-9 rounded-xl bg-blue-500/10 text-[#007AFF] dark:text-[#0A84FF] flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
								<Plus class="w-4 h-4" />
							</div>
							<div class="min-w-0">
								<h4 class="text-xs font-semibold text-slate-900 dark:text-white">Catat Transaksi</h4>
								<p class="text-[11px] text-slate-400 truncate">Catat pengeluaran, pemasukan, atau transfer</p>
							</div>
						</div>
						<ChevronRight class="w-4 h-4 text-slate-400 group-hover:text-[#007AFF] group-hover:translate-x-0.5 transition-all shrink-0" />
					</button>

					<!-- Action 2: Analisis Pos Belanja -->
					<button
						type="button"
						onclick={() => (isChartModalOpen = true)}
						class="w-full py-3 flex items-center justify-between gap-3 text-left group hover:opacity-80 transition-opacity"
					>
						<div class="flex items-center gap-3 min-w-0">
							<div class="w-9 h-9 rounded-xl bg-blue-500/10 text-[#007AFF] dark:text-[#0A84FF] flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
								<BarChart3 class="w-4 h-4" />
							</div>
							<div class="min-w-0">
								<h4 class="text-xs font-semibold text-slate-900 dark:text-white">Analisis Pos Belanja</h4>
								<p class="text-[11px] text-slate-400 truncate">Buka diagram donat pengeluaran & grafik tren</p>
							</div>
						</div>
						<ChevronRight class="w-4 h-4 text-slate-400 group-hover:text-[#007AFF] group-hover:translate-x-0.5 transition-all shrink-0" />
					</button>

					<!-- Action 3: Rincian Kuota Belanja -->
					<button
						type="button"
						onclick={() => (isBudgetModalOpen = true)}
						class="w-full py-3 flex items-center justify-between gap-3 text-left group hover:opacity-80 transition-opacity"
					>
						<div class="flex items-center gap-3 min-w-0">
							<div class="w-9 h-9 rounded-xl bg-blue-500/10 text-[#007AFF] dark:text-[#0A84FF] flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
								<Target class="w-4 h-4" />
							</div>
							<div class="min-w-0">
								<h4 class="text-xs font-semibold text-slate-900 dark:text-white">Rincian Kuota Belanja</h4>
								<p class="text-[11px] text-slate-400 truncate">Periksa sisa kuota tiap pos pengeluaran bulanan</p>
							</div>
						</div>
						<ChevronRight class="w-4 h-4 text-slate-400 group-hover:text-[#007AFF] group-hover:translate-x-0.5 transition-all shrink-0" />
					</button>

					<!-- Action 4: Kelola Seluruh Transaksi -->
					<a
						href="/transactions"
						class="w-full py-3 flex items-center justify-between gap-3 text-left group hover:opacity-80 transition-opacity"
					>
						<div class="flex items-center gap-3 min-w-0">
							<div class="w-9 h-9 rounded-xl bg-blue-500/10 text-[#007AFF] dark:text-[#0A84FF] flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
								<Receipt class="w-4 h-4" />
							</div>
							<div class="min-w-0">
								<h4 class="text-xs font-semibold text-slate-900 dark:text-white">Riwayat Transaksi Lengkap</h4>
								<p class="text-[11px] text-slate-400 truncate">Filter, cari, dan telusuri seluruh mutasi rekening</p>
							</div>
						</div>
						<ChevronRight class="w-4 h-4 text-slate-400 group-hover:text-[#007AFF] group-hover:translate-x-0.5 transition-all shrink-0" />
					</a>
				</div>
			</div>
		</div>
	</div>

	<!-- 6. TRANSAKSI TERBARU -->
	<div class="space-y-3 pt-2">
		<div class="flex items-center justify-between">
			<span class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
				Transaksi Terkini
			</span>
			<a href="/transactions" class="text-xs font-semibold text-[#007AFF] dark:text-[#0A84FF] hover:underline flex items-center">
				Lihat Semua ({financialStore.transactions.length}) <ChevronRight class="w-3.5 h-3.5 ml-0.5" />
			</a>
		</div>

		<div class="rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] divide-y divide-slate-100 dark:divide-white/5 overflow-hidden">
			{#each financialStore.transactions.slice(0, 5) as tx}
				<!-- Progressive Disclosure: Clicking row opens Transaction Detail Bottom Sheet / Modal -->
				<button
					type="button"
					onclick={() => (selectedTx = tx)}
					class="w-full text-left p-3.5 flex items-center justify-between gap-3 hover:bg-slate-50/70 dark:hover:bg-white/[0.02] transition-colors"
				>
					<div class="flex items-center gap-3 min-w-0">
						<div class="w-9 h-9 rounded-xl flex items-center justify-center shrink-0 {tx.transaction_type === 'EXPENSE'
							? 'bg-rose-500/10 text-rose-600 dark:text-rose-400'
							: tx.transaction_type === 'INCOME'
								? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
								: 'bg-blue-500/10 text-[#007AFF] dark:text-[#0A84FF]'}">
							{#if tx.transaction_type === 'EXPENSE'}
								<ArrowUpRight class="w-4 h-4" />
							{:else if tx.transaction_type === 'INCOME'}
								<ArrowDownLeft class="w-4 h-4" />
							{:else}
								<ArrowLeftRight class="w-4 h-4" />
							{/if}
						</div>
						<div class="min-w-0">
							<p class="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white truncate">
								{tx.description}
							</p>
							<p class="text-xs text-slate-400 mt-0.5">
								{tx.account_name || 'BCA'} &bull; {formatRelativeTime(tx.created_at || tx.transaction_date)}
							</p>
						</div>
					</div>

					<div class="text-right shrink-0">
						<span class="text-xs sm:text-sm font-semibold {tx.transaction_type === 'EXPENSE'
							? 'text-rose-600 dark:text-rose-400'
							: tx.transaction_type === 'INCOME'
								? 'text-emerald-600 dark:text-emerald-400'
								: 'text-[#007AFF] dark:text-[#0A84FF]'}">
							{tx.transaction_type === 'EXPENSE' ? '-' : tx.transaction_type === 'INCOME' ? '+' : ''}{formatRupiah(tx.amount)}
						</span>
					</div>
				</button>
			{/each}
		</div>
	</div>

	<!-- ========================================================================= -->
	<!-- PROGRESSIVE DISCLOSURE MODALS & BOTTOM SHEETS (Responsive) -->
	<!-- ========================================================================= -->

	<!-- 1. Add Transaction Modal -->
	<AddTransactionModal bind:open={isAddModalOpen} />

	<!-- 2. Budget Breakdown Modal (Bottom Sheet on Mobile) -->
	<Modal
		bind:open={isBudgetModalOpen}
		title="Pos Anggaran"
		description="Status kuota untuk setiap kategori pengeluaran bulan ini"
	>
		<div class="space-y-4">
			{#each financialStore.budgets as budget}
				{@const pct = budget.amount > 0 ? Math.round((budget.spent_amount / budget.amount) * 100) : 0}
				<div class="p-3.5 rounded-2xl bg-slate-50 dark:bg-white/[0.03] border border-slate-100 dark:border-white/5 space-y-2">
					<div class="flex items-center justify-between text-xs">
						<span class="font-semibold text-slate-900 dark:text-white">
							{budget.name}
						</span>
						<span class="font-semibold {pct >= 100 ? 'text-rose-500' : pct >= 80 ? 'text-amber-500' : 'text-emerald-500'}">
							{formatRupiah(budget.spent_amount)} / {formatRupiah(budget.amount)} ({pct}%)
						</span>
					</div>

					<!-- Modal Progress Bar with Radar Beacon & Gradient -->
					<ProgressBar value={pct} variant="auto" size="sm" />

					<div class="flex justify-between text-xs text-slate-400">
						<span>Sisa: {formatRupiah(Math.max(0, budget.amount - budget.spent_amount))}</span>
						<span>Status: {pct >= 100 ? 'Overbudget' : pct >= 80 ? 'Waspada' : 'Aman'}</span>
					</div>
				</div>
			{/each}
		</div>
	</Modal>

	<!-- 3. Transaction Detail Modal (Bottom Sheet on Mobile) -->
	{#if selectedTx}
		<Modal
			open={true}
			title="Detail Transaksi"
			description="Informasi mutasi dan sumber pencatatan"
			onclose={() => (selectedTx = null)}
		>
			<div class="space-y-4">
				<div class="text-center p-4 rounded-2xl bg-slate-50 dark:bg-white/[0.03] border border-slate-100 dark:border-white/5">
					<span class="text-xs text-slate-400 uppercase font-semibold">Nominal</span>
					<h3 class="text-2xl font-semibold mt-1 {selectedTx.transaction_type === 'EXPENSE'
						? 'text-rose-600 dark:text-rose-400'
						: selectedTx.transaction_type === 'INCOME'
							? 'text-emerald-600 dark:text-emerald-400'
							: 'text-[#007AFF]'}">
						{selectedTx.transaction_type === 'EXPENSE' ? '-' : selectedTx.transaction_type === 'INCOME' ? '+' : ''}{formatRupiah(selectedTx.amount)}
					</h3>
					<span class="px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase mt-2 inline-block border {selectedTx.transaction_type === 'EXPENSE'
						? 'bg-rose-500/10 text-rose-600 border-rose-500/20'
						: selectedTx.transaction_type === 'INCOME'
							? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20'
							: 'bg-blue-500/10 text-blue-600 border-blue-500/20'}">
						{selectedTx.transaction_type}
					</span>
				</div>

				<div class="space-y-2 text-xs">
					<div class="flex justify-between py-1.5 border-b border-slate-100 dark:border-white/5">
						<span class="text-slate-400">Deskripsi</span>
						<span class="font-semibold text-slate-900 dark:text-white">{selectedTx.description}</span>
					</div>

					<div class="flex justify-between py-1.5 border-b border-slate-100 dark:border-white/5">
						<span class="text-slate-400">Sumber</span>
						<span class="font-semibold text-slate-900 dark:text-white">{selectedTx.account_name || 'BCA Tabungan'}</span>
					</div>

					{#if selectedTx.destination_account_name}
						<div class="flex justify-between py-1.5 border-b border-slate-100 dark:border-white/5">
							<span class="text-slate-400">Tujuan</span>
							<span class="font-semibold text-[#007AFF]">{selectedTx.destination_account_name}</span>
						</div>
					{/if}

					<div class="flex justify-between py-1.5 border-b border-slate-100 dark:border-white/5">
						<span class="text-slate-400">Waktu</span>
						<span class="font-semibold text-slate-900 dark:text-white">{formatDateTime(selectedTx.created_at || selectedTx.transaction_date)}</span>
					</div>

					<div class="flex justify-between py-1.5 border-b border-slate-100 dark:border-white/5">
						<span class="text-slate-400">Metode</span>
						<span class="font-semibold text-slate-900 dark:text-white">{selectedTx.source}</span>
					</div>
				</div>

				<button
					type="button"
					onclick={handleDeleteSelectedTx}
					class="w-full py-2.5 rounded-xl bg-rose-50 dark:bg-rose-950/30 text-rose-600 dark:text-rose-400 border border-rose-200/60 dark:border-rose-900/40 text-xs font-semibold flex items-center justify-center gap-2 hover:bg-rose-100 transition-colors"
				>
					<Trash2 class="w-4 h-4" />
					<span>Hapus Transaksi</span>
				</button>
			</div>
		</Modal>
	{/if}

	<!-- 4. Financial Charts Modal (Bottom Sheet on Mobile) -->
	<Modal
		bind:open={isChartModalOpen}
		title="Grafik Finansial"
		description="Visualisasi pembagian pos pengeluaran dan tren arus kas"
	>
		<div class="space-y-6">
			<SpendingDonut />
			<CashflowBar />
		</div>
	</Modal>
</div>
