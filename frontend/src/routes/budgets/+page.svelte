<script lang="ts">
	import { authStore } from '$lib/stores/auth.svelte';
	import { financialStore } from '$lib/stores/financial.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import { formatRupiah } from '$lib/utils/formatters';
	import BudgetProgress from '$lib/components/financial/BudgetProgress.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import AmountInput from '$lib/components/ui/AmountInput.svelte';
	import CategorySuggestSelect from '$lib/components/ui/CategorySuggestSelect.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import GlassSurface from '$lib/components/ui/GlassSurface.svelte';
	import EmptyState from '$lib/components/ui/EmptyState.svelte';
	import ProgressBar from '$lib/components/ui/ProgressBar.svelte';
	import {
		PieChart,
		Plus,
		AlertTriangle,
		CheckCircle2,
		ShieldAlert,
		Sparkles,
		ArrowUpRight,
		ShieldCheck,
		Search,
		Filter,
		Trash2,
		Info
	} from 'lucide-svelte';

	let isAddBudgetOpen = $state(false);
	let isStatusModalOpen = $state(false);
	let selectedCategory = $state(financialStore.categories.find((c) => c.type === 'EXPENSE')?.id || '');
	let limitAmount = $state(0);
	let thresholdPercent = $state(80);
	let formError = $state('');
	let searchQuery = $state('');
	let selectedStatus = $state<'ALL' | 'NORMAL' | 'WARNING' | 'EXCEEDED'>('ALL');
	let isFilterOpen = $state(false);

	const isFilterActive = $derived(selectedStatus !== 'ALL');

	function resetFilters() {
		selectedStatus = 'ALL';
		isFilterOpen = false;
	}

	const filteredBudgets = $derived(
		financialStore.budgets.filter((b) => {
			const pct = b.amount > 0 ? Math.round((b.spent_amount / b.amount) * 100) : 0;
			if (selectedStatus === 'EXCEEDED' && pct < 100) return false;
			if (selectedStatus === 'WARNING' && (pct < b.alert_threshold_percent || pct >= 100)) return false;
			if (selectedStatus === 'NORMAL' && pct >= b.alert_threshold_percent) return false;

			if (searchQuery.trim()) {
				const q = searchQuery.toLowerCase();
				return b.name.toLowerCase().includes(q);
			}
			return true;
		})
	);

	let budgetToDelete = $state<any>(null);
	let isDeleteModalOpen = $state(false);
	let isDeletingBudget = $state(false);

	function promptDeleteBudget(b: any) {
		budgetToDelete = b;
		isDeleteModalOpen = true;
	}

	async function confirmDeleteBudget() {
		if (!budgetToDelete) return;
		const hasTx = (budgetToDelete.spent_amount || 0) > 0 ||
			financialStore.transactions.some((t) => Boolean(t.category_id && budgetToDelete.category_id && t.category_id === budgetToDelete.category_id));
		if (hasTx) {
			notificationStore.toast('Pos anggaran ini sudah memiliki riwayat transaksi dan tidak dapat dihapus.', 'error');
			isDeleteModalOpen = false;
			budgetToDelete = null;
			return;
		}
		isDeletingBudget = true;
		try {
			await financialStore.deleteBudget(budgetToDelete.id);
			isDeleteModalOpen = false;
			budgetToDelete = null;
		} finally {
			isDeletingBudget = false;
		}
	}

	// Overall totals
	const totalBudgetLimit = $derived(
		financialStore.budgets.reduce((acc, b) => acc + (b.limit_amount ?? b.amount ?? 0), 0)
	);

	const totalBudgetSpent = $derived(
		financialStore.budgets.reduce((acc, b) => acc + (b.spent_amount || 0), 0)
	);

	const totalRemaining = $derived(
		Math.max(0, totalBudgetLimit - totalBudgetSpent)
	);

	const overallPercent = $derived(
		totalBudgetLimit > 0 ? Math.round((totalBudgetSpent / totalBudgetLimit) * 100) : 0
	);

	let isSubmitting = $state(false);

	async function handleAddBudget() {
		formError = '';
		if (!selectedCategory) {
			formError = 'Pilih kategori belanja yang ingin dibatasi.';
			return;
		}

		if (limitAmount <= 0) {
			formError = 'Nominal batas maksimal belanja harus lebih dari 0.';
			return;
		}

		if (limitAmount > financialStore.totalBalance && financialStore.totalBalance > 0) {
			formError = `Nominal batas (${formatRupiah(limitAmount)}) melebihi total saldo dompet Anda saat ini (${formatRupiah(financialStore.totalBalance)}). Tetapkan batas sesuai ketersediaan uang Anda.`;
			return;
		}

		isSubmitting = true;
		try {
			const cat = financialStore.categories.find((c) => c.id === selectedCategory);
			const res = await financialStore.addBudget({
				category_id: selectedCategory,
				name: cat?.name || 'Batas Belanja',
				amount: limitAmount,
				alert_threshold_percent: thresholdPercent
			});

			if (res) {
				isAddBudgetOpen = false;
				limitAmount = 0;
			}
		} finally {
			isSubmitting = false;
		}
	}
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full pb-24 lg:pb-10">
	<!-- Page Header -->
	<div class="pb-2 border-b border-slate-200/80 dark:border-white/10">
		<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
			<PieChart class="w-6 h-6 text-[#007AFF] dark:text-[#0A84FF]" />
			<span>{authStore.isSuperuser ? 'Batas Anggaran Sistem' : 'Anggaran Pengeluaran Bulanan'}</span>
		</h1>
		<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
			{authStore.isSuperuser
				? 'Batas biaya server, domain, database, dan kebutuhan sistem'
				: 'Kendalikan gaya hidup dan cegah belanja berlebihan dengan sistem kuota per pos belanja'}
		</p>
	</div>

	<!-- Monthly Budget Health Overview -->
	<div class="p-6 sm:p-7 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] space-y-5">
		<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
			<div>
				<div class="flex items-center gap-2">
					<span class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
						Total Anggaran Bulan Ini
					</span>
					<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-[#007AFF]/10 text-[#007AFF] dark:text-[#0A84FF]">
						Bulan Berjalan
					</span>
				</div>
				<h2 class="text-3xl sm:text-4xl font-semibold text-slate-900 dark:text-white tracking-tight mt-1">
					{formatRupiah(totalBudgetLimit)}
				</h2>
			</div>

			<div class="flex items-center gap-2">
				<span
					class="px-3.5 py-1.5 rounded-full text-xs font-semibold {overallPercent >= 100
						? 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20'
						: overallPercent >= 80
							? 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20'
							: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'}"
				>
					{overallPercent}% Terpakai
				</span>
			</div>
		</div>

		<!-- Combined Progress Bar with Radar Beacon & Gradient -->
		<ProgressBar value={overallPercent} variant={overallPercent >= 100 ? 'rose' : overallPercent >= 80 ? 'amber' : 'emerald'} size="lg" />

		<!-- Cute & Lively Summary Metric Badges -->
		<div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
			<!-- Spent Card -->
			<div class="p-3.5 sm:p-4 rounded-2xl bg-slate-50/70 dark:bg-white/[0.03] border border-slate-200/70 dark:border-white/10 flex items-center justify-between hover:border-rose-500/30 transition-all">
				<div class="flex items-center gap-3">
					<div class="w-9 h-9 rounded-xl bg-rose-500/10 dark:bg-rose-500/20 text-rose-600 dark:text-rose-400 border border-rose-500/20 flex items-center justify-center shrink-0">
						<ArrowUpRight class="w-4 h-4" />
					</div>
					<div>
						<span class="text-[10px] text-slate-400 font-semibold uppercase tracking-wider block leading-tight">Sudah Dibelanjakan</span>
						<p class="text-sm sm:text-base font-semibold text-rose-600 dark:text-rose-400 leading-tight mt-0.5">
							{formatRupiah(totalBudgetSpent)}
						</p>
					</div>
				</div>
				<span class="text-xs font-semibold text-rose-500 dark:text-rose-400 px-2 py-0.5 rounded-lg bg-rose-500/10">
					{overallPercent}%
				</span>
			</div>

			<!-- Remaining Card -->
			<div class="p-3.5 sm:p-4 rounded-2xl bg-slate-50/70 dark:bg-white/[0.03] border border-slate-200/70 dark:border-white/10 flex items-center justify-between hover:border-emerald-500/30 transition-all">
				<div class="flex items-center gap-3">
					<div class="w-9 h-9 rounded-xl bg-emerald-500/10 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 flex items-center justify-center shrink-0">
						<ShieldCheck class="w-4 h-4" />
					</div>
					<div>
						<span class="text-[10px] text-slate-400 font-semibold uppercase tracking-wider block leading-tight">Sisa Kuota Aman</span>
						<p class="text-sm sm:text-base font-semibold text-emerald-600 dark:text-emerald-400 leading-tight mt-0.5">
							{formatRupiah(totalRemaining)}
						</p>
					</div>
				</div>
				<span class="text-xs font-semibold text-emerald-500 dark:text-emerald-400 px-2 py-0.5 rounded-lg bg-emerald-500/10">
					{100 - Math.min(overallPercent, 100)}%
				</span>
			</div>
		</div>
	</div>

	<!-- Unified Action Toolbar: Search (Max 40%), Status Legend Button, Filter Button & Create Button -->
	<div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
		<!-- Search Field (Max 40% Width) -->
		<div class="relative w-full sm:w-[40%] sm:max-w-[40%]">
			<Search class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="Cari pos anggaran..."
				class="w-full h-9 pl-9 pr-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:border-[#007AFF] transition-colors"
			/>
		</div>

		<!-- Action Buttons: Keterangan Status, Filter & Pasang Anggaran (Aligned inline) -->
		<div class="flex items-center gap-2">
			<!-- Button: Keterangan Status Modal -->
			<Button
				variant="ghost"
				onclick={() => (isStatusModalOpen = true)}
				class="h-9 px-3 text-xs border border-slate-200/80 dark:border-white/10 hover:border-[#007AFF] hover:text-[#007AFF] transition-colors"
			>
				<Info class="w-3.5 h-3.5 mr-1.5" />
				<span>Keterangan Status</span>
			</Button>

			<!-- Filter Button with Popover -->
			<div class="relative">
				<Button
					variant="ghost"
					onclick={() => (isFilterOpen = !isFilterOpen)}
					class="h-9 px-3 text-xs border border-slate-200/80 dark:border-white/10 {isFilterActive ? 'text-[#007AFF] border-[#007AFF]/40 bg-[#007AFF]/5' : ''}"
				>
					<Filter class="w-3.5 h-3.5 mr-1.5" />
					<span>Filter</span>
					{#if isFilterActive}
						<span class="w-1.5 h-1.5 rounded-full bg-[#007AFF] ml-1"></span>
					{/if}
				</Button>

				{#if isFilterOpen}
					<button
						type="button"
						aria-label="Tutup menu filter"
						class="fixed inset-0 z-30 cursor-default bg-transparent"
						onclick={() => (isFilterOpen = false)}
					></button>

					<div class="absolute right-0 top-full mt-2 w-56 p-3 rounded-2xl bg-white dark:bg-[#151926] border border-slate-200/80 dark:border-white/10 shadow-2xl z-40 space-y-3">
						<div>
							<span class="text-[11px] font-semibold text-slate-700 dark:text-slate-300 block mb-1.5">Status Batas</span>
							<select
								bind:value={selectedStatus}
								class="w-full h-8 px-2.5 rounded-lg border border-slate-200/80 dark:border-white/10 bg-slate-50 dark:bg-white/5 text-xs text-slate-700 dark:text-slate-300 focus:outline-none focus:border-[#007AFF]"
							>
								<option value="ALL">Semua Status</option>
								<option value="NORMAL">Aman (&lt; 80%)</option>
								<option value="WARNING">Mendekati Batas (80-99%)</option>
								<option value="EXCEEDED">Lewat Batas (&ge; 100%)</option>
							</select>
						</div>

						{#if isFilterActive}
							<div class="pt-1 border-t border-slate-100 dark:border-white/5 flex justify-end">
								<button
									type="button"
									onclick={resetFilters}
									class="text-[11px] font-semibold text-rose-500 hover:underline cursor-pointer"
								>
									Reset Filter
								</button>
							</div>
						{/if}
					</div>
				{/if}
			</div>

			<Button variant="primary" onclick={() => (isAddBudgetOpen = true)} class="h-9 px-3.5 text-xs">
				<Plus class="w-4 h-4 mr-1.5" />
				<span>Pasang Anggaran Baru</span>
			</Button>
		</div>
	</div>

	<!-- List of Budgets Grid -->
	<div class="space-y-3">
		<h3 class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
			Daftar Pos Anggaran ({filteredBudgets.length})
		</h3>

		{#if filteredBudgets.length > 0}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
				{#each filteredBudgets as budget}
					<BudgetProgress {budget} ondelete={promptDeleteBudget} />
				{/each}
			</div>
		{:else}
			<EmptyState
				title="Belum ada pos anggaran yang cocok"
				description="Coba ubah kata kunci pencarian atau sesuaikan filter Anda."
			/>
		{/if}
	</div>

	<!-- Add Budget Modal -->
	<Modal
		bind:open={isAddBudgetOpen}
		title="Pasang Batas Pengeluaran"
		description="Batasi jumlah uang yang boleh keluar per kategori agar pengeluaran terkontrol dan tidak kebablasan"
	>
		<div class="space-y-4">
			<!-- Saldo Kas Tersedia Hero Banner -->
			<div class="relative overflow-hidden p-4 sm:p-5 rounded-2xl bg-gradient-to-br from-blue-50/90 via-indigo-50/50 to-emerald-50/40 dark:from-[#131c31] dark:via-[#161a2b] dark:to-[#112423] border border-blue-200/70 dark:border-blue-500/20 shadow-sm flex items-center justify-between gap-4">
				<div class="relative z-10 space-y-1.5 flex-1 min-w-0">
					<div class="flex items-center gap-1.5 text-[#007AFF] dark:text-[#38bdf8]">
						<Sparkles class="w-3.5 h-3.5" />
						<span class="text-[11px] font-semibold uppercase tracking-wider">
							Total Saldo Kas Anda Saat Ini
						</span>
					</div>
					<h3 class="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white tracking-tight">
						{formatRupiah(financialStore.totalBalance)}
					</h3>
					<p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed max-w-sm">
						Batas belanja akan memantau pengeluaran riil Anda setiap ada transaksi.
					</p>
				</div>

				<!-- 3D Money Asset (Transparent) -->
				<div class="relative z-10 shrink-0 w-20 h-20 sm:w-24 sm:h-24 flex items-center justify-center pointer-events-none select-none">
					<img
						src="/budget-money-3d.png"
						alt="Uang Kas & Dompet 3D"
						class="w-full h-full object-contain drop-shadow-md transform hover:scale-105 transition-transform"
					/>
				</div>

				<!-- Subtle background ambient radial light -->
				<div class="absolute -right-6 -bottom-6 w-32 h-32 bg-blue-500/10 dark:bg-blue-400/10 rounded-full blur-2xl pointer-events-none"></div>
			</div>

			<CategorySuggestSelect
				bind:value={selectedCategory}
				categoryType="EXPENSE"
				label="Pilih Kategori Kebutuhan"
				placeholder="Ketik untuk mencari atau tambah kategori baru..."
			/>

			<AmountInput
				bind:value={limitAmount}
				label="Maksimal Belanja Sebulan (Batas Kuota)"
				referenceBalance={financialStore.totalBalance}
				balanceLabel="Total Saldo Kas Anda"
			/>

			<Input
				type="number"
				bind:value={thresholdPercent}
				label="Beri Peringatan Saat Belanja Mencapai (%)"
				placeholder="80"
			/>

			{#if formError}
				<p class="text-xs font-medium text-rose-500 bg-rose-50 dark:bg-rose-950/30 p-2.5 rounded-xl border border-rose-200 dark:border-rose-900">
					{formError}
				</p>
			{/if}
		</div>

		{#snippet footer()}
			<Button variant="ghost" onclick={() => (isAddBudgetOpen = false)}>Batal</Button>
			<Button variant="primary" onclick={handleAddBudget} disabled={isSubmitting}>
				{isSubmitting ? 'Menyimpan...' : 'Simpan Batas Belanja'}
			</Button>
		{/snippet}
	</Modal>

	<!-- Modal Konfirmasi Hapus Pos Anggaran -->
	<Modal
		bind:open={isDeleteModalOpen}
		title="Hapus Pos Anggaran?"
		description="Apakah Anda yakin ingin menghapus pos batas belanja ini? Riwayat transaksi pengeluaran sebelumnya akan tetap tersimpan aman."
	>
		{#if budgetToDelete}
			<div class="p-4 rounded-2xl bg-rose-50/70 dark:bg-rose-950/20 border border-rose-200/80 dark:border-rose-900/40 text-xs text-rose-800 dark:text-rose-200 space-y-2">
				<div class="flex items-center gap-2">
					<AlertTriangle class="w-4 h-4 text-rose-600 dark:text-rose-400 shrink-0" />
					<span class="font-semibold text-sm text-slate-900 dark:text-white">{budgetToDelete.name}</span>
				</div>
				<div class="flex items-center justify-between text-xs text-slate-600 dark:text-slate-300 pt-1 border-t border-rose-200/60 dark:border-rose-900/40">
					<span>Batas Kuota: <strong>{formatRupiah(budgetToDelete.amount)}</strong></span>
					<span>Terpakai: <strong>{formatRupiah(budgetToDelete.spent_amount || 0)}</strong></span>
				</div>
			</div>
		{/if}

		{#snippet footer()}
			<Button variant="ghost" onclick={() => (isDeleteModalOpen = false)}>Batal</Button>
			<Button variant="danger" onclick={confirmDeleteBudget} disabled={isDeletingBudget}>
				{isDeletingBudget ? 'Menghapus...' : 'Ya, Hapus Anggaran'}
			</Button>
		{/snippet}
	</Modal>

	<!-- Modal Panduan Keterangan Status Kuota Anggaran -->
	<Modal
		bind:open={isStatusModalOpen}
		title="Arti Status & Batas Kuota Anggaran"
		description="Panduan indikator warna radar untuk mengendalikan pengeluaran bulanan Anda"
	>
		<div class="space-y-4">
			<!-- Saldo Kas & Health Radar Hero Banner -->
			<div class="relative overflow-hidden p-4 sm:p-5 rounded-2xl bg-gradient-to-br from-emerald-50/90 via-teal-50/50 to-blue-50/60 dark:from-[#112423] dark:via-[#131c31] dark:to-[#151926] border border-emerald-200/70 dark:border-emerald-500/20 shadow-sm flex items-center justify-between gap-4">
				<div class="relative z-10 space-y-1.5 flex-1 min-w-0">
					<div class="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400">
						<Sparkles class="w-3.5 h-3.5" />
						<span class="text-[11px] font-semibold uppercase tracking-wider">
							Sistem Radar & Kontrol Pengeluaran
						</span>
					</div>
					<h3 class="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
						Kendalikan Belanja Sebelum Kebablasan
					</h3>
					<p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed max-w-sm">
						Setiap kartu pos anggaran dipantau secara langsung berdasarkan perbandingan belanja riil dengan batas kuota yang Anda tetapkan.
					</p>
				</div>

				<!-- 3D Status Gauge Asset (Transparent) -->
				<div class="relative z-10 shrink-0 w-20 h-20 sm:w-24 sm:h-24 flex items-center justify-center pointer-events-none select-none">
					<img
						src="/budget-status-guide-3d.png"
						alt="Status & Limit Gauge 3D"
						class="w-full h-full object-contain drop-shadow-md transform hover:scale-105 transition-transform"
					/>
				</div>

				<!-- Ambient Glow -->
				<div class="absolute -right-6 -bottom-6 w-32 h-32 bg-emerald-500/10 dark:bg-emerald-400/10 rounded-full blur-2xl pointer-events-none"></div>
			</div>

			<!-- Status Cards List -->
			<div class="space-y-2.5">
				<!-- 1. Aman (< 80%) -->
				<div class="p-3.5 rounded-2xl bg-emerald-50/60 dark:bg-emerald-950/20 border border-emerald-200/80 dark:border-emerald-800/40 flex items-start gap-3">
					<div class="w-8 h-8 rounded-xl bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 flex items-center justify-center shrink-0 mt-0.5">
						<CheckCircle2 class="w-4 h-4" />
					</div>
					<div class="flex-1 min-w-0 space-y-0.5">
						<div class="flex items-center justify-between gap-2">
							<span class="text-xs font-semibold text-emerald-800 dark:text-emerald-300">
								&lt; 80% &bull; Kuota Belanja Masih Aman
							</span>
							<span class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border border-emerald-500/20">
								Aman
							</span>
						</div>
						<p class="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
							Pengeluaran masih jauh dari batas limit. Anda masih memiliki sisa kuota yang leluasa untuk kategori ini.
						</p>
					</div>
				</div>

				<!-- 2. Peringatan (80% - 99%) -->
				<div class="p-3.5 rounded-2xl bg-amber-50/60 dark:bg-amber-950/20 border border-amber-200/80 dark:border-amber-800/40 flex items-start gap-3">
					<div class="w-8 h-8 rounded-xl bg-amber-500/15 text-amber-600 dark:text-amber-400 border border-amber-500/30 flex items-center justify-center shrink-0 mt-0.5">
						<AlertTriangle class="w-4 h-4" />
					</div>
					<div class="flex-1 min-w-0 space-y-0.5">
						<div class="flex items-center justify-between gap-2">
							<span class="text-xs font-semibold text-amber-800 dark:text-amber-300">
								80% &ndash; 99% &bull; Mendekati Batas Limit Bulanan
							</span>
							<span class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-700 dark:text-amber-300 border border-amber-500/20">
								Waspada
							</span>
						</div>
						<p class="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
							Pengeluaran sudah menyentuh batas peringatan. Batasi belanja non-primer pada pos ini agar sisa anggaran mencukupi hingga akhir bulan.
						</p>
					</div>
				</div>

				<!-- 3. Lewat Batas (>= 100%) -->
				<div class="p-3.5 rounded-2xl bg-rose-50/60 dark:bg-rose-950/20 border border-rose-200/80 dark:border-rose-800/40 flex items-start gap-3">
					<div class="w-8 h-8 rounded-xl bg-rose-500/15 text-rose-600 dark:text-rose-400 border border-rose-500/30 flex items-center justify-center shrink-0 mt-0.5">
						<ShieldAlert class="w-4 h-4" />
					</div>
					<div class="flex-1 min-w-0 space-y-0.5">
						<div class="flex items-center justify-between gap-2">
							<span class="text-xs font-semibold text-rose-800 dark:text-rose-300">
								&ge; 100% &bull; Lewat Batas, Segera Rem Belanja
							</span>
							<span class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-rose-500/15 text-rose-700 dark:text-rose-300 border border-rose-500/20">
								Overbudget
							</span>
						</div>
						<p class="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
							Total belanja telah melampaui kuota maksimal. Segera hentikan pengeluaran pada pos ini atau alihkan saldo dari pos lain jika darurat.
						</p>
					</div>
				</div>
			</div>
		</div>

		{#snippet footer()}
			<Button variant="primary" onclick={() => (isStatusModalOpen = false)}>
				Saya Mengerti
			</Button>
		{/snippet}
	</Modal>
</div>
