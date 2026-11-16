<script lang="ts">
	import type { Budget } from '$lib/types';
	import { financialStore } from '$lib/stores/financial.svelte';
	import { formatRupiah } from '$lib/utils/formatters';
	import { AlertTriangle, CheckCircle2, ShieldAlert, ShieldCheck, Trash2 } from 'lucide-svelte';
	import ProgressBar from '$lib/components/ui/ProgressBar.svelte';

	interface Props {
		budget: Budget;
		ondelete?: (b: Budget) => void;
	}

	let { budget, ondelete }: Props = $props();

	const percentage = $derived(
		budget.amount > 0 ? Math.round((budget.spent_amount / budget.amount) * 100) : 0
	);

	const isExceeded = $derived(percentage >= 100);
	const isWarning = $derived(percentage >= (budget.alert_threshold_percent || 80) && !isExceeded);
	const isSafe = $derived(!isExceeded && !isWarning);

	// Sembunyikan tombol hapus jika sudah ada riwayat transaksi minimal 1 pada pos anggaran ini
	const hasTransactions = $derived(
		(budget.spent_amount || 0) > 0 ||
		financialStore.transactions.some(
			(t) => Boolean(t.category_id && budget.category_id && t.category_id === budget.category_id)
		)
	);
</script>

<div
	class="p-4 sm:p-5 rounded-2xl transition-all flex flex-col gap-3.5 border {isExceeded
		? 'border-rose-400/60 dark:border-rose-800/70 bg-gradient-to-b from-rose-50/50 via-white to-slate-50/80 dark:from-rose-950/25 dark:via-[#151926] dark:to-[#0f121d] shadow-sm shadow-rose-500/5 hover:border-rose-500'
		: isWarning
			? 'border-amber-400/60 dark:border-amber-800/70 bg-gradient-to-b from-amber-50/50 via-white to-slate-50/80 dark:from-amber-950/25 dark:via-[#151926] dark:to-[#0f121d] shadow-sm shadow-amber-500/5 hover:border-amber-500'
			: 'border-slate-200/70 dark:border-white/[0.06] bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] hover:border-emerald-500/30'}"
>
	<div class="flex items-center justify-between gap-2">
		<!-- Left: Icon Box + Category Name -->
		<div class="flex items-center gap-2.5 min-w-0">
			<div
				class="w-9 h-9 rounded-xl flex items-center justify-center shrink-0 border {isExceeded
					? 'bg-rose-500/15 text-rose-600 dark:text-rose-400 border-rose-500/30'
					: isWarning
						? 'bg-amber-500/15 text-amber-600 dark:text-amber-400 border-amber-500/30'
						: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20'}"
			>
				{#if isExceeded}
					<ShieldAlert class="w-4 h-4" />
				{:else if isWarning}
					<AlertTriangle class="w-4 h-4" />
				{:else}
					<ShieldCheck class="w-4 h-4" />
				{/if}
			</div>
			<span class="text-sm font-semibold text-slate-900 dark:text-white tracking-tight truncate">
				{budget.name}
			</span>
		</div>

		<!-- Right: Status Badge & Delete Button -->
		<div class="flex items-center gap-1.5 shrink-0">
			{#if isExceeded}
				<span
					class="inline-flex items-center gap-1 text-[11px] font-semibold px-2.5 py-1 rounded-full bg-rose-500/15 text-rose-600 dark:text-rose-400 border border-rose-500/30"
				>
					<ShieldAlert class="w-3 h-3 text-rose-500" />
					<span>Lewat Batas ({percentage}%)</span>
				</span>
			{:else if isWarning}
				<span
					class="inline-flex items-center gap-1 text-[11px] font-semibold px-2.5 py-1 rounded-full bg-amber-500/15 text-amber-700 dark:text-amber-300 border border-amber-500/30"
				>
					<AlertTriangle class="w-3 h-3 text-amber-600" />
					<span>Mendekati Limit ({percentage}%)</span>
				</span>
			{:else}
				<span
					class="inline-flex items-center gap-1 text-[11px] font-semibold px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20"
				>
					<CheckCircle2 class="w-3 h-3 text-emerald-500" />
					<span>Aman ({percentage}%)</span>
				</span>
			{/if}

			{#if ondelete && !hasTransactions}
				<button
					type="button"
					onclick={() => ondelete(budget)}
					class="p-1 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-colors cursor-pointer ml-0.5"
					title="Hapus Pos Anggaran"
				>
					<Trash2 class="w-3.5 h-3.5" />
				</button>
			{/if}
		</div>
	</div>

	<!-- Progress Bar with Radar Beacon & Matching Color Variant -->
	<ProgressBar
		value={percentage}
		variant={isExceeded ? 'rose' : isWarning ? 'amber' : 'emerald'}
		size="md"
	/>

	<!-- Amounts -->
	<div class="flex items-center justify-between text-xs font-medium text-slate-500 dark:text-slate-400">
		<span class={isExceeded ? 'text-rose-600 dark:text-rose-400 font-semibold' : isWarning ? 'text-amber-600 dark:text-amber-400 font-semibold' : ''}>
			Terpakai: {formatRupiah(budget.spent_amount)}
		</span>
		<span>Batas: {formatRupiah(budget.amount)}</span>
	</div>
</div>
