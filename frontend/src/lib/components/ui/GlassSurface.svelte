<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		children?: Snippet;
		class?: string;
		elevated?: boolean;
		interactive?: boolean;
		onclick?: (e: MouseEvent) => void;
	}

	let {
		children,
		class: className = '',
		elevated = false,
		interactive = false,
		onclick
	}: Props = $props();
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<!-- svelte-ignore a11y_click_events_have_key_events -->
<div
	class="rounded-2xl transition-all duration-200 border {elevated
		? 'bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border-slate-200/80 dark:border-white/10'
		: 'bg-gradient-to-b from-white/90 via-white/80 to-slate-50/70 dark:from-[#151926]/90 dark:via-[#131622]/85 dark:to-[#0f121d]/80 backdrop-blur-xl border-slate-200/60 dark:border-white/5'} {interactive
		? 'hover:border-[#007AFF]/50 active:scale-[0.99] cursor-pointer'
		: ''} {className}"
	{onclick}
>
	{@render children?.()}
</div>
