<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		children?: Snippet;
		ariaLabel: string;
		variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'glass';
		size?: 'sm' | 'md' | 'lg';
		type?: 'button' | 'submit' | 'reset';
		disabled?: boolean;
		class?: string;
		onclick?: (e: MouseEvent) => void;
	}

	let {
		children,
		ariaLabel,
		variant = 'ghost',
		size = 'md',
		type = 'button',
		disabled = false,
		class: className = '',
		onclick
	}: Props = $props();

	const variantClasses = {
		primary: 'bg-[#007AFF] text-white hover:bg-[#0062CC]',
		secondary: 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-200',
		outline: 'border border-slate-200 dark:border-white/10 text-slate-700 dark:text-slate-200',
		ghost: 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/5',
		glass: 'bg-white/60 dark:bg-white/5 backdrop-blur-md border border-slate-200/60 dark:border-white/10 text-slate-700 dark:text-slate-200'
	};

	const sizeClasses = {
		sm: 'w-8 h-8 rounded-lg',
		md: 'w-9 h-9 rounded-xl',
		lg: 'w-10 h-10 rounded-xl'
	};
</script>

<button
	{type}
	aria-label={ariaLabel}
	disabled={disabled}
	class="inline-flex items-center justify-center transition-all duration-150 active:scale-95 disabled:opacity-50 cursor-pointer {variantClasses[
		variant
	]} {sizeClasses[size]} {className}"
	{onclick}
>
	{@render children?.()}
</button>
