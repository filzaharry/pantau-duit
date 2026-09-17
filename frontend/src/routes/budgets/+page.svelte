<script lang="ts">
	import { authStore } from '$lib/stores/auth.svelte';
	import { financialStore } from '$lib/stores/financial.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import { formatRupiah } from '$lib/utils/formatters';
	import BudgetProgress from '$lib/components/financial/BudgetProgress.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import AmountInput from '$lib/components/ui/AmountInput.svelte';
	import Select from '$lib/components/ui/Select.svelte';
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
		ShieldCheck
	} from 'lucide-svelte';

	let isAddBudgetOpen = $state(false);
	let selectedCategory = $state(financialStore.categories.find((c) => c.type === 'EXPENSE')?.id || '');
	let limitAmount = $state(1500000);
	let thresholdPercent = $state(80);
	let formError = $state('');

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

	const categoryOptions = $derived(
		financialStore.categories
			.filter((c) => c.type === 'EXPENSE')
			.map((c) => ({
				value: c.id,
				label: c.name
			}))
	);

	function handleAddBudget() {
		formError = '';
		if (!selectedCategory) {
			formError = 'Pilih kategori anggaran.';
			return;
		}

		if (limitAmount <= 0) {
			formError = 'Batas nominal harus lebih besar dari 0.';
			return;
		}

		const cat = financialStore.categories.find((c) => c.id === selectedCategory);
		financialStore.budgets.push({
			id: `bgt-${Date.now()}`,
			tenant_id: 'tenant-demo-uuid-001',
			category_id: selectedCategory,
			category: cat,
			name: cat?.name || 'Anggaran Belanja',
			amount: limitAmount,
			period: 'MONTHLY',
			limit_amount: limitAmount,
			spent_amount: 0,
			alert_threshold_percent: thresholdPercent,
			is_active: true,
			created_at: new Date().toISOString()
		});

		notificationStore.toast(`Anggaran ${cat?.name || ''} berhasil ditambahkan!`, 'success');
		isAddBudgetOpen = false;
	}
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full pb-24 lg:pb-10">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
		<div>
			<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
				<PieChart class="w-6 h-6 text-[#007AFF] dark:text-[#0A84FF]" />
				<span>{authStore.isSuperuser ? 'Batas Anggaran Sistem' : 'Anggaran Pengeluaran Bulanan'}</span>
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
				{authStore.isSuperuser
					? 'Batas biaya server, domain, database, dan kebutuhan sistem'
					: 'Kendalikan gaya hidup dan cegah overspending dengan sistem kuota per pos biaya'}
			</p>
		</div>

		<Button variant="primary" onclick={() => (isAddBudgetOpen = true)}>
			<Plus class="w-4 h-4" />
			<span>Pasang Anggaran Baru</span>
		</Button>
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
		<ProgressBar value={overallPercent} variant="auto" size="lg" />

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

	<!-- Threshold Guidance Box -->
	<div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
		<div class="p-3 rounded-2xl bg-emerald-500/5 border border-emerald-500/20 text-emerald-700 dark:text-emerald-400 flex items-center gap-2">
			<CheckCircle2 class="w-4 h-4 shrink-0" />
			<span><strong>&lt; 80%:</strong> Kuota belanja masih aman</span>
		</div>
		<div class="p-3 rounded-2xl bg-amber-500/5 border border-amber-500/20 text-amber-700 dark:text-amber-400 flex items-center gap-2">
			<AlertTriangle class="w-4 h-4 shrink-0" />
			<span><strong>80 - 99%:</strong> Mendekati batas limit bulanan</span>
		</div>
		<div class="p-3 rounded-2xl bg-rose-500/5 border border-rose-500/20 text-rose-700 dark:text-rose-400 flex items-center gap-2">
			<ShieldAlert class="w-4 h-4 shrink-0" />
			<span><strong>&ge; 100%:</strong> Overbudget, segera rem belanja</span>
		</div>
	</div>

	<!-- List of Budgets Grid -->
	<div class="space-y-3">
		<h3 class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
			Daftar Pos Anggaran Aktif ({financialStore.budgets.length})
		</h3>

		{#if financialStore.budgets.length > 0}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
				{#each financialStore.budgets as budget}
					<BudgetProgress {budget} />
				{/each}
			</div>
		{:else}
			<EmptyState
				title="Belum ada pos anggaran"
				description="Buat pos anggaran untuk makanan, transportasi, hiburan, dll."
			/>
		{/if}
	</div>

	<!-- Add Budget Modal -->
	<Modal
		bind:open={isAddBudgetOpen}
		title="Buat Anggaran Baru"
		description="Tentukan plafon belanja bulanan untuk kategori tertentu"
	>
		<div class="space-y-4">
			<Select
				bind:value={selectedCategory}
				options={categoryOptions}
				label="Kategori Belanja"
			/>

			<AmountInput
				bind:value={limitAmount}
				label="Batas Plafon Bulanan (Limit)"
			/>

			<Input
				type="number"
				bind:value={thresholdPercent}
				label="Persentase Peringatan (%)"
				placeholder="80"
			/>

			{#if formError}
				<p class="text-xs font-medium text-rose-500 bg-rose-50 dark:bg-rose-950/30 p-2.5 rounded-xl border border-rose-200">
					{formError}
				</p>
			{/if}
		</div>

		{#snippet footer()}
			<Button variant="ghost" onclick={() => (isAddBudgetOpen = false)}>Batal</Button>
			<Button variant="primary" onclick={handleAddBudget}>Pasang Anggaran</Button>
		{/snippet}
	</Modal>
</div>
