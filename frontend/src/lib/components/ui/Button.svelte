<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		children?: Snippet;
		variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'success';
		size?: 'sm' | 'md' | 'lg';
		type?: 'button' | 'submit' | 'reset';
		disabled?: boolean;
		loading?: boolean;
		class?: string;
		title?: string;
		onclick?: (e: MouseEvent) => void;
	}

	let {
		children,
		variant = 'primary',
		size = 'md',
		type = 'button',
		disabled = false,
		loading = false,
		class: className = '',
		title,
		onclick
	}: Props = $props();

	const variantClasses = {
		primary:
			'bg-[#007AFF] hover:bg-[#0062CC] dark:bg-[#0A84FF] dark:hover:bg-[#409CFF] text-white active:scale-[0.98]',
		secondary:
			'bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-100 active:scale-[0.98]',
		outline:
			'border border-slate-200 dark:border-white/10 hover:bg-slate-100 dark:hover:bg-white/5 text-slate-700 dark:text-slate-200 active:scale-[0.98]',
		ghost:
			'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/5 active:scale-[0.98]',
		danger:
			'bg-rose-500 hover:bg-rose-600 text-white active:scale-[0.98]',
		success:
			'bg-emerald-500 hover:bg-emerald-600 text-white active:scale-[0.98]'
	};

	const sizeClasses = {
		sm: 'h-8 px-2.5 text-xs rounded-lg gap-1.5 font-medium',
		md: 'h-9 px-3.5 text-xs sm:text-sm rounded-xl gap-2 font-medium',
		lg: 'h-9 px-4 text-xs sm:text-sm rounded-xl gap-2 font-medium'
	};
</script>

<button
	{type}
	{title}
	disabled={disabled || loading}
	class="inline-flex items-center justify-center transition-all duration-150 select-none cursor-pointer disabled:opacity-50 disabled:pointer-events-none disabled:cursor-not-allowed {variantClasses[
		variant
	]} {sizeClasses[size]} {className}"
	{onclick}
>
	{#if loading}
		<svg
			class="animate-spin h-4 w-4 shrink-0 text-current"
			xmlns="http://www.w3.org/2000/svg"
			fill="none"
			viewBox="0 0 24 24"
		>
			<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3"></circle>
			<path
				class="opacity-75"
				fill="currentColor"
				d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
			></path>
		</svg>
	{/if}
	{@render children?.()}
</button>
