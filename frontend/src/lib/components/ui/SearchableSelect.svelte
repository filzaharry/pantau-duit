<script lang="ts">
	import { ChevronDown, Search, Check, Plus } from 'lucide-svelte';

	export interface Option {
		value: string;
		label: string;
	}

	interface Props {
		value?: string;
		options: Option[];
		label?: string;
		placeholder?: string;
		error?: string;
		disabled?: boolean;
		allowCreate?: boolean;
		onCreate?: (name: string) => Promise<string | void> | string | void;
	}

	let {
		value = $bindable(''),
		options = [],
		label,
		placeholder = 'Pilih opsi...',
		error,
		disabled = false,
		allowCreate = false,
		onCreate
	}: Props = $props();

	let isOpen = $state(false);
	let searchQuery = $state('');
	let triggerEl = $state<HTMLButtonElement | null>(null);
	let searchInputEl = $state<HTMLInputElement | null>(null);
	let dropdownEl = $state<HTMLDivElement | null>(null);
	let isCreating = $state(false);

	let coords = $state({
		top: 0,
		left: 0,
		width: 0,
		maxHeight: 260,
		openUpwards: false
	});

	const selectedOption = $derived(options.find((opt) => opt.value === value));

	const filteredOptions = $derived(
		options.filter((opt) => {
			if (!searchQuery.trim()) return true;
			return opt.label.toLowerCase().includes(searchQuery.toLowerCase().trim());
		})
	);

	const exactMatch = $derived(
		options.some(
			(opt) => opt.label.toLowerCase().trim() === searchQuery.toLowerCase().trim()
		)
	);

	function updateCoords() {
		if (!triggerEl) return;
		const rect = triggerEl.getBoundingClientRect();
		const viewportHeight = window.innerHeight;
		const viewportWidth = window.innerWidth;

		const spaceBelow = viewportHeight - rect.bottom - 16;
		const spaceAbove = rect.top - 16;

		// If space below is less than 180px and space above has more room, open upwards
		const openUpwards = spaceBelow < 180 && spaceAbove > spaceBelow;
		const availableSpace = openUpwards ? spaceAbove : spaceBelow;
		const maxHeight = Math.min(260, Math.max(140, availableSpace));

		const width = Math.min(rect.width, viewportWidth - 24);
		const left = Math.max(12, Math.min(rect.left, viewportWidth - width - 12));

		coords = {
			top: openUpwards ? rect.top - 6 : rect.bottom + 6,
			left,
			width,
			maxHeight,
			openUpwards
		};
	}

	function toggleOpen() {
		if (disabled) return;
		isOpen = !isOpen;
		if (isOpen) {
			searchQuery = '';
			updateCoords();
			setTimeout(() => {
				updateCoords();
				searchInputEl?.focus();
			}, 30);
		}
	}

	function closeDropdown() {
		isOpen = false;
		searchQuery = '';
	}

	function selectOption(val: string) {
		value = val;
		closeDropdown();
	}

	async function handleCreate() {
		const name = searchQuery.trim();
		if (!name || !onCreate) return;
		isCreating = true;
		try {
			const newId = await onCreate(name);
			if (newId) {
				value = newId;
			}
			closeDropdown();
		} finally {
			isCreating = false;
		}
	}

	function handleWindowClick(e: MouseEvent) {
		if (!isOpen) return;
		const target = e.target as Node;
		if (triggerEl?.contains(target) || dropdownEl?.contains(target)) {
			return;
		}
		closeDropdown();
	}

	function handleWindowScroll() {
		if (isOpen) {
			if (!triggerEl) return;
			const rect = triggerEl.getBoundingClientRect();
			// Auto close if trigger scrolled out of viewport
			if (rect.bottom < 0 || rect.top > window.innerHeight) {
				closeDropdown();
			} else {
				updateCoords();
			}
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape' && isOpen) {
			closeDropdown();
		}
	}
</script>

<svelte:window
	onclick={handleWindowClick}
	onscroll={handleWindowScroll}
	onresize={handleWindowScroll}
	onkeydown={handleKeydown}
/>

<div class="relative w-full">
	{#if label}
		<span class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
			{label}
		</span>
	{/if}

	<!-- Custom Trigger Button (Clean plain text, chevron) -->
	<button
		type="button"
		bind:this={triggerEl}
		{disabled}
		onclick={toggleOpen}
		class="w-full h-10 flex items-center justify-between px-3 rounded-xl text-xs sm:text-sm bg-white dark:bg-[#151E2E] border border-slate-200/80 dark:border-white/10 hover:border-[#007AFF] text-left transition-colors focus:outline-none focus:ring-1 focus:ring-[#007AFF]/20 disabled:opacity-50 disabled:cursor-not-allowed"
	>
		<span class="truncate {selectedOption ? 'font-medium text-slate-900 dark:text-white' : 'text-slate-400 dark:text-slate-500'}">
			{selectedOption ? selectedOption.label : placeholder}
		</span>
		<ChevronDown
			class="w-4 h-4 text-slate-400 dark:text-slate-500 shrink-0 ml-2 transition-transform duration-200 {isOpen ? 'rotate-180 text-[#007AFF]' : ''}"
		/>
	</button>

	<!-- Fixed Floating Popover: never cut off by modal body/footer -->
	{#if isOpen}
		<div
			bind:this={dropdownEl}
			style="position: fixed; left: {coords.left}px; {coords.openUpwards ? `bottom: ${window.innerHeight - coords.top}px` : `top: ${coords.top}px`}; width: {coords.width}px; max-height: {coords.maxHeight}px; z-index: 9999;"
			class="flex flex-col rounded-xl bg-white dark:bg-[#151926] border border-slate-200 dark:border-white/10 shadow-2xl p-1.5 animate-in fade-in duration-100"
		>
			<!-- Search suggestion input header -->
			<div class="relative mb-1.5 shrink-0">
				<Search class="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
				<input
					type="text"
					bind:this={searchInputEl}
					bind:value={searchQuery}
					placeholder="Cari..."
					onkeydown={(e) => {
						if (e.key === 'Enter') {
							e.preventDefault();
							if (filteredOptions.length > 0) {
								selectOption(filteredOptions[0].value);
							} else if (allowCreate && !exactMatch && searchQuery.trim()) {
								handleCreate();
							}
						}
					}}
					class="w-full h-8 pl-8 pr-3 rounded-lg bg-slate-50 dark:bg-white/5 text-xs text-slate-900 dark:text-white placeholder:text-slate-400 border border-slate-200/60 dark:border-white/10 outline-none focus:border-[#007AFF]"
				/>
			</div>

			<!-- Options List: EXACTLY 1 plain text per row, no color, no image -->
			<div class="overflow-y-auto space-y-0.5 pr-0.5 flex-1 min-h-0">
				{#if filteredOptions.length === 0 && (!allowCreate || exactMatch || !searchQuery.trim())}
					<div class="py-3 text-center text-xs text-slate-400">
						Tidak ada hasil ditemukan
					</div>
				{:else}
					{#each filteredOptions as opt (opt.value)}
						{@const isSelected = opt.value === value}
						<button
							type="button"
							onclick={() => selectOption(opt.value)}
							class="w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs text-left transition-colors cursor-pointer {isSelected
								? 'bg-[#007AFF]/10 text-[#007AFF] font-medium'
								: 'text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-white/5'}"
						>
							<span class="truncate block">{opt.label}</span>
							{#if isSelected}
								<Check class="w-3.5 h-3.5 text-[#007AFF] shrink-0 ml-2" />
							{/if}
						</button>
					{/each}
				{/if}

				<!-- Plain text quick create option -->
				{#if allowCreate && !exactMatch && searchQuery.trim()}
					<button
						type="button"
						onclick={handleCreate}
						disabled={isCreating}
						class="w-full flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs text-left text-[#007AFF] hover:bg-[#007AFF]/10 font-medium transition-colors cursor-pointer border border-dashed border-[#007AFF]/30 mt-1"
					>
						<Plus class="w-3.5 h-3.5 shrink-0" />
						<span class="truncate">
							{isCreating ? 'Menyimpan...' : `Tambah "${searchQuery.trim()}"`}
						</span>
					</button>
				{/if}
			</div>
		</div>
	{/if}

	{#if error}
		<p class="text-xs text-rose-500 mt-1">{error}</p>
	{/if}
</div>
