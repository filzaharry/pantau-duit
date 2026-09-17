<script lang="ts">
	import type { Budget } from '$lib/types';
	import { formatRupiah } from '$lib/utils/formatters';
	import { AlertTriangle, CheckCircle2, PieChart } from 'lucide-svelte';

	interface Props {
		budget: Budget;
	}

	let { budget }: Props = $props();

	const percentage = $derived(
		budget.amount > 0 ? Math.round((budget.spent_amount / budget.amount) * 100) : 0
	);

	const isExceeded = $derived(percentage >= 100);
	const isWarning = $derived(percentage >= budget.alert_threshold_percent && !isExceeded);

	import ProgressBar from '$lib/components/ui/ProgressBar.svelte';
</script>

<div class="p-4 sm:p-5 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] flex flex-col gap-3 hover:border-blue-500/30 transition-all">
	<div class="flex items-center justify-between">
		<div class="flex items-center gap-2.5">
			<div class="w-8 h-8 rounded-xl bg-blue-500/10 dark:bg-blue-500/20 text-[#007AFF] dark:text-[#0A84FF] border border-blue-500/20 flex items-center justify-center shrink-0">
				<PieChart class="w-4 h-4" />
			</div>
			<span class="text-sm font-semibold text-slate-900 dark:text-white tracking-tight truncate">
				{budget.name}
			</span>
		</div>
		<div class="flex items-center gap-1.5">
			{#if isExceeded}
				<span class="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-600 dark:text-rose-400">
					<AlertTriangle class="w-3 h-3" />
					Over Limit ({percentage}%)
				</span>
			{:else if isWarning}
				<span class="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-600 dark:text-amber-400">
					<AlertTriangle class="w-3 h-3" />
					{percentage}% Terpakai
				</span>
			{:else}
				<span class="text-xs font-semibold text-slate-500 dark:text-slate-400">
					{percentage}%
				</span>
			{/if}
		</div>
	</div>

	<!-- Progress Bar with Radar Beacon & Gradient -->
	<ProgressBar
		value={percentage}
		variant={isExceeded ? 'rose' : isWarning ? 'amber' : 'blue'}
		size="md"
	/>

	<!-- Amounts -->
	<div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 font-medium">
		<span>Terpakai: {formatRupiah(budget.spent_amount)}</span>
		<span>Batas: {formatRupiah(budget.amount)}</span>
	</div>
</div>
