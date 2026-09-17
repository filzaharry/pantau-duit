<script lang="ts">
	import { AlertTriangle, RotateCcw } from 'lucide-svelte';
	import Button from './Button.svelte';

	interface Props {
		title?: string;
		message?: string;
		status?: number;
		onretry?: () => void;
	}

	let {
		title = 'Terjadi Kesalahan',
		message = 'Gagal memuat data dari server. Silakan coba kembali.',
		status,
		onretry
	}: Props = $props();
</script>

<div class="flex flex-col items-center justify-center p-8 text-center rounded-2xl border border-rose-200/60 dark:border-rose-900/30 bg-rose-50/30 dark:bg-rose-950/10">
	<div class="w-12 h-12 rounded-2xl bg-rose-500/10 text-rose-500 flex items-center justify-center mb-3">
		<AlertTriangle class="w-6 h-6" />
	</div>
	{#if status}
		<span class="text-xs font-mono font-semibold px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-600 dark:text-rose-400 mb-1">
			Error {status}
		</span>
	{/if}
	<h4 class="text-base font-semibold text-slate-900 dark:text-white tracking-tight">{title}</h4>
	<p class="text-xs text-slate-500 dark:text-slate-400 max-w-sm mt-1 mb-4">{message}</p>
	{#if onretry}
		<Button variant="outline" size="sm" onclick={onretry}>
			<RotateCcw class="w-3.5 h-3.5" />
			Coba Lagi
		</Button>
	{/if}
</div>
