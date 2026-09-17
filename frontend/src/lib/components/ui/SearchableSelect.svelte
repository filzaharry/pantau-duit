<script lang="ts">
	import { ChevronDown, Search, Check } from 'lucide-svelte';

	interface Option {
		value: string;
		label: string;
		sublabel?: string;
	}

	interface Props {
		value?: string;
		options: Option[];
		label?: string;
		placeholder?: string;
		error?: string;
		disabled?: boolean;
	}

	let {
		value = $bindable(''),
		options = [],
		label,
		placeholder = 'Pilih opsi...',
		error,
		disabled = false
	}: Props = $props();

	let isOpen = $state(false);
	let searchQuery = $state('');
	let containerEl: HTMLElement | null = $state(null);
	let searchInputEl: HTMLInputElement | null = $state(null);
	let openUpwards = $state(false);

	// Currently selected option object
	const selectedOption = $derived(options.find((opt) => opt.value === value));

	// Filtered options based on search query
	const filteredOptions = $derived(
		options.filter((opt) => {
			if (!searchQuery.trim()) return true;
			const q = searchQuery.toLowerCase().trim();
			return (
				opt.label.toLowerCase().includes(q) ||
				(opt.sublabel && opt.sublabel.toLowerCase().includes(q))
			);
		})
	);

	// Load with max limit of 10 items as requested
	const displayedOptions = $derived(filteredOptions.slice(0, 10));

	function toggleOpen() {
		if (disabled) return;
		isOpen = !isOpen;
		if (isOpen) {
			searchQuery = '';
			if (containerEl) {
				const dialogEl = containerEl.closest('[role="dialog"]');
				const bottomBoundary = dialogEl
					? dialogEl.getBoundingClientRect().bottom
					: window.innerHeight;
				const spaceBelow = bottomBoundary - containerEl.getBoundingClientRect().bottom;
				openUpwards = spaceBelow < 250;
			}
			// Auto focus input on next tick
			setTimeout(() => {
				searchInputEl?.focus();
			}, 50);
		}
	}

	function selectOption(val: string) {
		value = val;
		isOpen = false;
		searchQuery = '';
	}

	function handleClickOutside(event: MouseEvent) {
		if (containerEl && !containerEl.contains(event.target as Node)) {
			isOpen = false;
		}
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Escape' && isOpen) {
			isOpen = false;
		}
	}
</script>

<svelte:window onclick={handleClickOutside} onkeydown={handleKeydown} />

<div class="relative w-full" bind:this={containerEl}>
	{#if label}
		<span class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
			{label}
		</span>
	{/if}

	<!-- Custom Trigger Button -->
	<button
		type="button"
		{disabled}
		onclick={toggleOpen}
		class="w-full h-9 flex items-center justify-between px-3 rounded-xl text-xs sm:text-sm bg-white dark:bg-[#151E2E] border border-slate-200/80 dark:border-white/10 hover:border-[#007AFF] text-left transition-colors focus:outline-none focus:ring-1 focus:ring-[#007AFF]/20 disabled:opacity-50 disabled:cursor-not-allowed"
	>
		<span class="truncate font-medium {selectedOption ? 'text-slate-900 dark:text-white' : 'text-slate-400 dark:text-slate-500'}">
			{selectedOption ? selectedOption.label : placeholder}
		</span>
		<ChevronDown
			class="w-4 h-4 text-slate-400 dark:text-slate-500 shrink-0 ml-2 transition-transform duration-200 {isOpen ? 'rotate-180 text-[#007AFF]' : ''}"
		/>
	</button>

	<!-- Custom Search-Suggest Popover -->
	{#if isOpen}
		<div
			class="absolute left-0 {openUpwards ? 'bottom-full mb-1.5' : 'top-full mt-1.5'} z-50 w-full min-w-[240px] p-2 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/90 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200 dark:border-white/10 animate-in fade-in zoom-in-95 duration-150"
		>
			<!-- Search input header -->
			<div class="relative mb-2">
				<Search class="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
				<input
					type="text"
					bind:this={searchInputEl}
					bind:value={searchQuery}
					placeholder="Cari..."
					class="w-full h-8 pl-8 pr-3 rounded-lg bg-slate-50 dark:bg-white/5 text-xs text-slate-900 dark:text-white placeholder:text-slate-400 border border-slate-200/60 dark:border-white/10 outline-none focus:border-[#007AFF]"
				/>
			</div>

			<!-- Options List with Max 10 items and overflow-y-auto -->
			<div class="max-h-52 overflow-y-auto space-y-0.5 pr-0.5">
				{#if displayedOptions.length === 0}
					<div class="py-4 text-center text-xs text-slate-400">
						Tidak ada hasil ditemukan
					</div>
				{:else}
					{#each displayedOptions as opt}
						{@const isSelected = opt.value === value}
						<button
							type="button"
							onclick={() => selectOption(opt.value)}
							class="w-full flex items-center justify-between px-2.5 py-2 rounded-xl text-xs text-left transition-colors {isSelected
								? 'bg-[#007AFF]/10 text-[#007AFF] font-semibold'
								: 'text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-white/5'}"
						>
							<div class="truncate mr-2">
								<span class="block truncate">{opt.label}</span>
								{#if opt.sublabel}
									<span class="block text-[10px] text-slate-400">{opt.sublabel}</span>
								{/if}
							</div>
							{#if isSelected}
								<Check class="w-3.5 h-3.5 text-[#007AFF] shrink-0" />
							{/if}
						</button>
					{/each}
				{/if}
			</div>

			<!-- Hint if there are more than 10 matches -->
			{#if filteredOptions.length > 10}
				<div class="pt-1.5 mt-1 border-t border-slate-100 dark:border-white/5 text-[10px] text-slate-400 text-center">
					Menampilkan 10 dari {filteredOptions.length} pilihan
				</div>
			{/if}
		</div>
	{/if}

	{#if error}
		<p class="text-xs text-rose-500 mt-1">{error}</p>
	{/if}
</div>
