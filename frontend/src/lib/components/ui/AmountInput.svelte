<script lang="ts">
	interface Props {
		value?: number;
		label?: string;
		error?: string;
		class?: string;
		onchange?: (val: number) => void;
	}

	let {
		value = $bindable(0),
		label = 'Jumlah Nominal',
		error,
		class: className = '',
		onchange
	}: Props = $props();

	function handleInput(e: Event) {
		const target = e.target as HTMLInputElement;
		const raw = target.value.replace(/\D/g, '');
		const num = raw ? parseInt(raw, 10) : 0;
		value = num;
		onchange?.(num);
	}

	function addAmount(inc: number) {
		value = (value || 0) + inc;
		onchange?.(value);
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
		<span class="text-xs font-medium text-slate-600 dark:text-slate-300">{label}</span>
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
				class="text-xs font-semibold px-2 py-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
			>
				Reset
			</button>
		{/if}
	</div>

	<!-- Quick Amount Chips for Fast Mobile Input -->
	<div class="flex items-center gap-1.5 overflow-x-auto no-scrollbar py-0.5">
		<button
			type="button"
			onclick={() => addAmount(10000)}
			class="px-2.5 py-1 text-xs font-medium rounded-lg bg-slate-100 dark:bg-white/5 hover:bg-[#007AFF]/10 hover:text-[#007AFF] text-slate-600 dark:text-slate-300 transition-colors whitespace-nowrap"
		>
			+10rb
		</button>
		<button
			type="button"
			onclick={() => addAmount(25000)}
			class="px-2.5 py-1 text-xs font-medium rounded-lg bg-slate-100 dark:bg-white/5 hover:bg-[#007AFF]/10 hover:text-[#007AFF] text-slate-600 dark:text-slate-300 transition-colors whitespace-nowrap"
		>
			+25rb
		</button>
		<button
			type="button"
			onclick={() => addAmount(50000)}
			class="px-2.5 py-1 text-xs font-medium rounded-lg bg-slate-100 dark:bg-white/5 hover:bg-[#007AFF]/10 hover:text-[#007AFF] text-slate-600 dark:text-slate-300 transition-colors whitespace-nowrap"
		>
			+50rb
		</button>
		<button
			type="button"
			onclick={() => addAmount(100000)}
			class="px-2.5 py-1 text-xs font-medium rounded-lg bg-slate-100 dark:bg-white/5 hover:bg-[#007AFF]/10 hover:text-[#007AFF] text-slate-600 dark:text-slate-300 transition-colors whitespace-nowrap"
		>
			+100rb
		</button>
		<button
			type="button"
			onclick={() => addAmount(500000)}
			class="px-2.5 py-1 text-xs font-medium rounded-lg bg-slate-100 dark:bg-white/5 hover:bg-[#007AFF]/10 hover:text-[#007AFF] text-slate-600 dark:text-slate-300 transition-colors whitespace-nowrap"
		>
			+500rb
		</button>
	</div>

	{#if error}
		<p class="text-xs text-rose-500">{error}</p>
	{/if}
</div>
