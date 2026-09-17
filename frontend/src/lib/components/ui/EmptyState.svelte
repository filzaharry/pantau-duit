<script lang="ts">
	import type { Snippet } from 'svelte';
	import { Inbox } from 'lucide-svelte';

	interface Props {
		title: string;
		description: string;
		icon?: Snippet;
		action?: Snippet;
		class?: string;
	}

	let {
		title,
		description,
		icon,
		action,
		class: className = ''
	}: Props = $props();
</script>

<div class="flex flex-col items-center justify-center p-8 text-center rounded-2xl border border-dashed border-slate-200 dark:border-white/10 bg-slate-50/50 dark:bg-white/[0.02] {className}">
	<div class="w-12 h-12 rounded-2xl bg-[#007AFF]/10 dark:bg-[#0A84FF]/15 text-[#007AFF] dark:text-[#0A84FF] flex items-center justify-center mb-3">
		{#if icon}
			{@render icon()}
		{:else}
			<Inbox class="w-6 h-6" />
		{/if}
	</div>
	<h4 class="text-base font-semibold text-slate-900 dark:text-white tracking-tight">{title}</h4>
	<p class="text-xs text-slate-500 dark:text-slate-400 max-w-sm mt-1 mb-4">{description}</p>
	{#if action}
		{@render action()}
	{/if}
</div>
