<script lang="ts">
	interface Option {
		value: string;
		label: string;
	}

	interface Props {
		value?: string;
		options: Option[];
		label?: string;
		error?: string;
		disabled?: boolean;
		class?: string;
		onchange?: (val: string) => void;
	}

	let {
		value = $bindable(''),
		options,
		label,
		error,
		disabled = false,
		class: className = '',
		onchange
	}: Props = $props();

	const selectId = 'select-' + Math.random().toString(36).substring(2, 9);
</script>

<div class="flex flex-col gap-1.5 w-full {className}">
	{#if label}
		<label for={selectId} class="text-xs font-medium text-slate-600 dark:text-slate-300">
			{label}
		</label>
	{/if}

	<div class="relative">
		<select
			id={selectId}
			bind:value
			{disabled}
			onchange={(e) => onchange?.((e.target as HTMLSelectElement).value)}
			class="w-full h-9 px-3 pr-8 text-xs sm:text-sm rounded-xl appearance-none outline-none border transition-all duration-150 {error
				? 'border-rose-400 bg-rose-50/20 text-rose-900'
				: 'border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-[#151E2E]/80 focus:border-[#007AFF] focus:ring-1 focus:ring-[#007AFF]/15 text-slate-900 dark:text-slate-100'} disabled:opacity-50"
		>
			{#each options as opt}
				<option value={opt.value} class="dark:bg-[#151E2E] dark:text-white">{opt.label}</option>
			{/each}
		</select>
		<div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400">
			<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
			</svg>
		</div>
	</div>

	{#if error}
		<p class="text-xs text-rose-500">{error}</p>
	{/if}
</div>
