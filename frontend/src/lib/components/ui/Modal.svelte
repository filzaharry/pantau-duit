<script lang="ts">
	import type { Snippet } from 'svelte';
	import { X } from 'lucide-svelte';

	interface Props {
		open?: boolean;
		title?: string;
		description?: string;
		children?: Snippet;
		footer?: Snippet;
		onclose?: () => void;
	}

	let {
		open = $bindable(false),
		title,
		description,
		children,
		footer,
		onclose
	}: Props = $props();

	function handleBackdropClick(e: MouseEvent) {
		if (e.target === e.currentTarget) {
			close();
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape' && open) {
			close();
		}
	}

	function close() {
		open = false;
		onclose?.();
	}
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
	<!-- Backdrop with smooth fade -->
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<div
		class="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/45 backdrop-blur-sm transition-all duration-200"
		onclick={handleBackdropClick}
	>
		<!-- Modal Container: Bottom Sheet on Mobile (<640px) / Centered Dialog on Desktop (>=640px) -->
		<div
			class="relative w-full max-w-lg max-h-[90vh] flex flex-col bg-gradient-to-b from-white via-white/95 to-slate-50/90 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] rounded-t-[28px] sm:rounded-3xl border-t sm:border border-slate-200/80 dark:border-white/10 overflow-hidden animate-in fade-in slide-in-from-bottom-6 sm:slide-in-from-bottom-2 duration-200"
			role="dialog"
			aria-modal="true"
			aria-labelledby={title ? 'modal-title' : undefined}
		>
			<!-- Mobile Drag Handle Bar -->
			<div class="sm:hidden flex justify-center pt-2.5 pb-1">
				<div class="w-10 h-1 rounded-full bg-slate-300 dark:bg-slate-700"></div>
			</div>

			<!-- Header -->
			<div class="flex items-center justify-between px-5 pt-3 sm:pt-5 pb-3 border-b border-slate-100 dark:border-white/5 rounded-t-[28px] sm:rounded-t-3xl bg-transparent">
				<div>
					{#if title}
						<h3 id="modal-title" class="text-lg font-semibold text-slate-900 dark:text-white tracking-tight">
							{title}
						</h3>
					{/if}
					{#if description}
						<p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{description}</p>
					{/if}
				</div>

				<button
					type="button"
					onclick={close}
					class="w-8 h-8 rounded-full flex items-center justify-center text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-white/5 transition-colors"
					aria-label="Tutup dialog"
				>
					<X class="w-4 h-4" />
				</button>
			</div>

			<!-- Body -->
			<div class="p-5 sm:p-6 overflow-y-auto overflow-x-hidden flex-1 no-scrollbar space-y-4">
				{@render children?.()}
			</div>

			<!-- Footer with Generous Bottom Padding (32px / pb-8) to ensure buttons never crowd the bottom edge -->
			{#if footer}
				<div class="px-6 pt-4 pb-8 sm:px-6 sm:pt-4 sm:pb-8 border-t border-slate-100 dark:border-white/5 bg-slate-50/70 dark:bg-white/[0.02] flex items-center justify-end gap-3 rounded-b-[28px] sm:rounded-b-3xl shrink-0">
					{@render footer()}
				</div>
			{/if}
		</div>
	</div>
{/if}
