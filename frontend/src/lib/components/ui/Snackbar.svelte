<script lang="ts">
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from 'lucide-svelte';

	const icons = {
		success: CheckCircle2,
		error: AlertCircle,
		warning: AlertTriangle,
		info: Info
	};

	const bgStyles = {
		success: 'bg-emerald-600/95 dark:bg-emerald-500/90 text-white border-emerald-400/40 shadow-emerald-600/25',
		error: 'bg-rose-600/95 dark:bg-rose-500/90 text-white border-rose-400/40 shadow-rose-600/25',
		warning: 'bg-amber-600/95 dark:bg-amber-500/90 text-white border-amber-400/40 shadow-amber-600/25',
		info: 'bg-[#007AFF]/95 dark:bg-[#0A84FF]/90 text-white border-blue-400/40 shadow-blue-600/25'
	};
</script>

<div
	class="fixed bottom-5 right-0 left-0 sm:left-auto sm:right-5 z-50 flex flex-col items-center sm:items-end gap-2.5 px-4 pointer-events-none"
	aria-live="polite"
>
	{#each notificationStore.toasts as toast (toast.id)}
		{@const Icon = icons[toast.type]}
		<div
			class="pointer-events-auto flex items-start gap-3 p-3.5 sm:p-4 rounded-2xl backdrop-blur-xl border shadow-xl max-w-md w-full sm:w-auto text-sm font-medium animate-in fade-in slide-in-from-bottom-3 duration-250 {bgStyles[
				toast.type
			]}"
		>
			<Icon class="w-5 h-5 shrink-0 mt-0.5" />
			<div class="flex-1 space-y-0.5 min-w-[200px]">
				{#if toast.title}
					<div class="font-semibold text-xs sm:text-sm tracking-tight opacity-95">
						{toast.title}
					</div>
				{/if}
				<div class="text-xs sm:text-xs leading-relaxed opacity-90">
					{toast.message}
				</div>
				{#if toast.details}
					<pre class="mt-1 p-1.5 rounded-lg bg-black/20 text-[10px] font-mono leading-tight whitespace-pre-wrap max-h-24 overflow-y-auto">{toast.details}</pre>
				{/if}
			</div>

			<button
				type="button"
				onclick={() => notificationStore.removeToast(toast.id)}
				class="w-6 h-6 rounded-full flex items-center justify-center opacity-80 hover:opacity-100 hover:bg-white/20 transition-all -mr-1 -mt-1"
				aria-label="Tutup notifikasi"
			>
				<X class="w-3.5 h-3.5" />
			</button>
		</div>
	{/each}
</div>
