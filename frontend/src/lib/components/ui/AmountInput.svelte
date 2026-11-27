<script lang="ts">
	import { financialStore } from '$lib/stores/financial.svelte';
	import { formatRupiah } from '$lib/utils/formatters';
	import { Wallet } from 'lucide-svelte';

	interface Props {
		value?: number;
		label?: string;
		error?: string;
		class?: string;
		referenceBalance?: number;
		balanceLabel?: string;
		showBalance?: boolean;
		showPercentageChips?: boolean;
		onchange?: (val: number) => void;
	}

	let {
		value = $bindable(0),
		label = 'Jumlah Nominal',
		error,
		class: className = '',
		referenceBalance,
		balanceLabel = 'Saldo',
		showBalance = false,
		showPercentageChips = true,
		onchange
	}: Props = $props();

	// If referenceBalance is provided, use it; otherwise 0
	const activeBalance = $derived(
		referenceBalance !== undefined ? referenceBalance : 0
	);

	function handleInput(e: Event) {
		const target = e.target as HTMLInputElement;
		const raw = target.value.replace(/\D/g, '');
		const num = raw ? parseInt(raw, 10) : 0;
		value = num;
		onchange?.(num);
	}

	function setPercentage(pct: number) {
		if (activeBalance <= 0) return;
		const target = Math.round((activeBalance * pct) / 100);
		value = target;
		onchange?.(target);
	}

	function clearAmount() {
		value = 0;
		onchange?.(0);
	}

	const displayFormatted = $derived(
		value > 0 ? new Intl.NumberFormat('id-ID').format(value) : ''
	);
</script>

<div class="flex flex-col gap-2 w-full {className}">
	{#if label}
		<div class="flex items-center justify-between gap-1.5">
			<span class="text-xs font-medium text-slate-600 dark:text-slate-300">{label}</span>
			{#if showBalance && activeBalance !== undefined}
				<div class="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
					<Wallet class="w-3.5 h-3.5 text-[#007AFF] dark:text-[#0A84FF]" />
					<span>{balanceLabel}:</span>
					<span class="font-semibold text-slate-900 dark:text-white">{formatRupiah(activeBalance)}</span>
				</div>
			{/if}
		</div>
	{/if}

	<div
		class="relative flex items-center h-14 px-4 rounded-2xl border transition-all duration-150 {error
			? 'border-rose-400 bg-rose-50/20 dark:bg-rose-950/20'
			: 'border-slate-200 dark:border-white/10 bg-white/90 dark:bg-[#151E2E]/90 focus-within:border-[#007AFF] focus-within:ring-2 focus-within:ring-[#007AFF]/15'}"
	>
		<span class="text-lg font-semibold text-slate-400 dark:text-slate-500 select-none mr-2">Rp</span>
		<input
			type="text"
			inputmode="numeric"
			placeholder="0"
			value={displayFormatted}
			oninput={handleInput}
			class="w-full text-2xl font-semibold bg-transparent outline-none text-slate-900 dark:text-white tracking-tight"
		/>
		{#if value > 0}
			<button
				type="button"
				onclick={clearAmount}
				class="text-xs font-semibold px-2 py-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 cursor-pointer"
			>
				Reset
			</button>
		{/if}
	</div>

	<!-- Percentage Chips based on Available Balance -->
	{#if showPercentageChips && activeBalance > 0}
		<div class="flex items-center gap-1.5 overflow-x-auto no-scrollbar py-0.5">
			{#each [10, 25, 50, 75, 100] as pct}
				{@const targetVal = Math.round((activeBalance * pct) / 100)}
				{@const isSelected = value > 0 && Math.abs(value - targetVal) < 1}
				<button
					type="button"
					onclick={() => setPercentage(pct)}
					class="px-2.5 py-1 text-xs font-semibold rounded-lg transition-all whitespace-nowrap cursor-pointer {isSelected
						? 'bg-[#007AFF] text-white shadow-sm'
						: 'bg-slate-100 dark:bg-white/5 hover:bg-[#007AFF]/10 hover:text-[#007AFF] text-slate-600 dark:text-slate-300'}"
				>
					{pct}%
				</button>
			{/each}
		</div>
	{/if}

	{#if error}
		<p class="text-xs text-rose-500">{error}</p>
	{/if}
</div>
