<script lang="ts">
	import type { Snippet } from 'svelte';
	import { X } from 'lucide-svelte';

	interface Props {
		open?: boolean;
		side?: 'right' | 'bottom';
		size?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';
		title?: string;
		description?: string;
		children?: Snippet;
		footer?: Snippet;
		onClose?: () => void;
		class?: string;
	}

	let {
		open = $bindable(false),
		side = 'right',
		size = 'lg',
		title,
		description,
		children,
		footer,
		onClose,
		class: customClass = ''
	}: Props = $props();

	function handleClose() {
		open = false;
		if (onClose) onClose();
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Escape' && open) {
			handleClose();
		}
	}

	const rightSizes = {
		sm: 'sm:max-w-md',
		md: 'sm:max-w-lg',
		lg: 'sm:max-w-xl',
		xl: 'sm:max-w-3xl',
		'2xl': 'sm:max-w-4xl',
		full: 'sm:max-w-6xl'
	};

	const bottomHeights = {
		sm: 'max-h-[50vh]',
		md: 'max-h-[65vh]',
		lg: 'max-h-[80vh]',
		xl: 'max-h-[90vh]',
		'2xl': 'max-h-[95vh]',
		full: 'max-h-[95vh]'
	};
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
	<div class="fixed inset-0 z-50 overflow-hidden" role="dialog" aria-modal="true">
		<!-- Backdrop overlay -->
		<button
			type="button"
			tabindex="-1"
			onclick={handleClose}
			class="fixed inset-0 bg-slate-950/60 backdrop-blur-xs transition-opacity duration-300 animate-in fade-in"
			aria-label="Tutup panel"
		></button>

		<!-- Sheet Container -->
		<div
			class="fixed inset-0 pointer-events-none flex {side === 'right'
				? 'justify-end'
				: 'items-end'}"
		>
			<div
				class="pointer-events-auto w-full flex flex-col bg-white dark:bg-[#121624] border-slate-200/80 dark:border-white/10 shadow-2xl transition-all duration-300 {side ===
				'right'
					? `h-full ${rightSizes[size]} border-l animate-in slide-in-from-right duration-300`
					: `rounded-t-3xl ${bottomHeights[size]} border-t animate-in slide-in-from-bottom duration-300`} {customClass}"
			>
				<!-- Bottom sheet pull handle bar on mobile -->
				{#if side === 'bottom'}
					<div class="w-full flex items-center justify-center pt-3 pb-1">
						<div class="w-12 h-1.5 rounded-full bg-slate-300 dark:bg-white/20"></div>
					</div>
				{/if}

				<!-- Header -->
				<div class="px-6 py-4 border-b border-slate-200/80 dark:border-white/10 flex items-start justify-between gap-4 shrink-0">
					<div>
						{#if title}
							<h2 class="text-base sm:text-lg font-semibold text-slate-900 dark:text-white tracking-tight">
								{title}
							</h2>
						{/if}
						{#if description}
							<p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
								{description}
							</p>
						{/if}
					</div>

					<button
						type="button"
						onclick={handleClose}
						class="p-2 -mr-2 rounded-2xl text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-white/5 transition-colors"
						aria-label="Tutup"
					>
						<X class="w-5 h-5" />
					</button>
				</div>

				<!-- Scrollable Body Content -->
				<div class="flex-1 overflow-y-auto px-6 py-5 space-y-4">
					{#if children}
						{@render children()}
					{/if}
				</div>

				<!-- Footer -->
				{#if footer}
					<div class="px-6 py-4 border-t border-slate-200/80 dark:border-white/10 bg-slate-50/50 dark:bg-white/[0.02] shrink-0">
						{@render footer()}
					</div>
				{/if}
			</div>
		</div>
	</div>
{/if}
