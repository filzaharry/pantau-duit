<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		value?: string | number;
		label?: string;
		placeholder?: string;
		type?: string;
		disabled?: boolean;
		required?: boolean;
		error?: string;
		hint?: string;
		class?: string;
		icon?: Snippet;
		oninput?: (e: Event) => void;
		onchange?: (e: Event) => void;
	}

	let {
		value = $bindable(''),
		label,
		placeholder = '',
		type = 'text',
		disabled = false,
		required = false,
		error,
		hint,
		class: className = '',
		icon,
		oninput,
		onchange
	}: Props = $props();

	const inputId = 'input-' + Math.random().toString(36).substring(2, 9);
</script>

<div class="flex flex-col gap-1.5 w-full {className}">
	{#if label}
		<label for={inputId} class="text-xs font-medium text-slate-600 dark:text-slate-300">
			{label}
			{#if required}<span class="text-rose-500 ml-0.5">*</span>{/if}
		</label>
	{/if}

	<div class="relative flex items-center">
		{#if icon}
			<div class="absolute left-3.5 flex items-center pointer-events-none text-slate-400">
				{@render icon()}
			</div>
		{/if}

		<input
			id={inputId}
			{type}
			bind:value
			{placeholder}
			{disabled}
			{required}
			{oninput}
			{onchange}
			class="w-full h-9 px-3 {icon
				? 'pl-9'
				: ''} text-xs sm:text-sm rounded-xl transition-all duration-150 outline-none border {error
				? 'border-rose-400 dark:border-rose-500 bg-rose-50/30 dark:bg-rose-950/20 text-rose-900 dark:text-rose-200'
				: 'border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-[#151E2E]/80 focus:border-[#007AFF] dark:focus:border-[#0A84FF] focus:ring-1 focus:ring-[#007AFF]/15 text-slate-900 dark:text-slate-100'} placeholder:text-slate-400 dark:placeholder:text-slate-500 disabled:opacity-50 disabled:bg-slate-100 dark:disabled:bg-slate-900"
		/>
	</div>

	{#if error}
		<p class="text-xs text-rose-500 mt-0.5">{error}</p>
	{:else if hint}
		<p class="text-xs text-slate-400 dark:text-slate-500 mt-0.5">{hint}</p>
	{/if}
</div>
