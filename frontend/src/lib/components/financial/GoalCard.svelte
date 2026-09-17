<script lang="ts">
	import type { FinancialGoal } from '$lib/types';
	import { formatRupiah, formatDate } from '$lib/utils/formatters';
	import { Target, Plus } from 'lucide-svelte';
	import ProgressBar from '$lib/components/ui/ProgressBar.svelte';

	interface Props {
		goal: FinancialGoal;
		ontopup?: (g: FinancialGoal) => void;
	}

	let { goal, ontopup }: Props = $props();

	const percentage = $derived(
		goal.target_amount > 0 ? Math.round((goal.current_amount / goal.target_amount) * 100) : 0
	);
</script>

<div class="p-4 sm:p-5 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] flex flex-col justify-between gap-3.5 hover:border-blue-500/30 transition-all">
	<div class="flex items-start justify-between">
		<div class="flex items-center gap-3">
			<div
				class="w-10 h-10 rounded-xl flex items-center justify-center text-white font-semibold shrink-0"
				style="background-color: {goal.color || '#10B981'};"
			>
				<Target class="w-5 h-5" />
			</div>
			<div>
				<h4 class="text-sm font-semibold text-slate-900 dark:text-white tracking-tight">{goal.name}</h4>
				{#if goal.target_date}
					<span class="text-[11px] text-slate-500 dark:text-slate-400">Target: {formatDate(goal.target_date)}</span>
				{/if}
			</div>
		</div>

		<span class="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-white/5 text-slate-700 dark:text-slate-300">
			{percentage}%
		</span>
	</div>

	<!-- Progress Bar with Radar Beacon & Gradient -->
	<ProgressBar value={percentage} variant="emerald" size="md" />

	<!-- Balances & Action -->
	<div class="flex items-center justify-between pt-1 border-t border-slate-100 dark:border-white/5">
		<div class="text-xs">
			<span class="font-semibold text-slate-900 dark:text-white">{formatRupiah(goal.current_amount)}</span>
			<span class="text-slate-400"> / {formatRupiah(goal.target_amount, true)}</span>
		</div>

		{#if ontopup}
			<button
				type="button"
				onclick={() => ontopup(goal)}
				class="text-xs font-semibold px-2.5 py-1 rounded-lg bg-[#007AFF]/10 text-[#007AFF] dark:text-[#0A84FF] hover:bg-[#007AFF]/20 transition-colors inline-flex items-center gap-1 cursor-pointer"
			>
				<Plus class="w-3 h-3" />
				Setor
			</button>
		{/if}
	</div>
</div>
