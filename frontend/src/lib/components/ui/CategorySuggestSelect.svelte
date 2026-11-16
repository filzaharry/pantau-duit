<script lang="ts">
	import { financialStore } from '$lib/stores/financial.svelte';
	import type { Category } from '$lib/types';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import {
		ChevronDown,
		Search,
		Check,
		Plus,
		Settings2,
		Pencil,
		Trash2,
		Tag,
		X,
		AlertCircle
	} from 'lucide-svelte';

	interface Props {
		value?: string;
		categoryType?: 'EXPENSE' | 'INCOME' | 'ALL';
		label?: string;
		placeholder?: string;
		error?: string;
		disabled?: boolean;
	}

	let {
		value = $bindable(''),
		categoryType = 'EXPENSE',
		label = 'Kategori',
		placeholder = 'Ketik atau pilih kategori...',
		error,
		disabled = false
	}: Props = $props();

	let isOpen = $state(false);
	let searchQuery = $state('');
	let containerEl: HTMLElement | null = $state(null);
	let inputEl: HTMLInputElement | null = $state(null);
	let openUpwards = $state(false);

	// Category Management Modal State
	let isManageModalOpen = $state(false);
	let newCatName = $state('');
	let newCatType = $state<'EXPENSE' | 'INCOME'>('EXPENSE');
	let editingCatId = $state<string | null>(null);
	let editingCatName = $state('');
	let isSaving = $state(false);
	let manageError = $state('');

	// Currently available categories from real database
	const availableCategories = $derived(
		financialStore.categories.filter((c) => {
			if (categoryType === 'ALL') return true;
			return c.type === categoryType || c.type === 'BOTH';
		})
	);

	// Currently selected category
	const selectedCategory = $derived(
		financialStore.categories.find((c) => c.id === value)
	);

	// Filtered categories based on search input
	const filteredCategories = $derived(
		availableCategories.filter((c) => {
			if (!searchQuery.trim()) return true;
			return c.name.toLowerCase().includes(searchQuery.toLowerCase().trim());
		})
	);

	// Exact match check
	const exactMatch = $derived(
		availableCategories.some(
			(c) => c.name.toLowerCase().trim() === searchQuery.toLowerCase().trim()
		)
	);

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
				openUpwards = spaceBelow < 280;
			}
			setTimeout(() => {
				inputEl?.focus();
			}, 50);
		}
	}

	function selectCategory(catId: string) {
		value = catId;
		isOpen = false;
		searchQuery = '';
	}

	async function handleQuickAdd() {
		const name = searchQuery.trim();
		if (!name) return;

		isSaving = true;
		try {
			const created = await financialStore.addCategory({
				name,
				type: categoryType === 'ALL' ? 'EXPENSE' : categoryType,
				icon: 'tag',
				color: '#007AFF'
			});
			if (created) {
				value = created.id;
				isOpen = false;
				searchQuery = '';
			}
		} finally {
			isSaving = false;
		}
	}

	function handleClickOutside(event: MouseEvent) {
		if (!containerEl) return;
		const path = event.composedPath ? event.composedPath() : [];
		if (path.includes(containerEl) || containerEl.contains(event.target as Node)) {
			return;
		}
		isOpen = false;
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Escape' && isOpen) {
			isOpen = false;
		}
	}

	// ================= Management Actions =================
	function openManageModal() {
		isOpen = false;
		newCatName = '';
		newCatType = categoryType === 'INCOME' ? 'INCOME' : 'EXPENSE';
		editingCatId = null;
		manageError = '';
		isManageModalOpen = true;
	}

	async function handleCreateNewInModal() {
		manageError = '';
		if (!newCatName.trim()) {
			manageError = 'Nama kategori wajib diisi.';
			return;
		}
		isSaving = true;
		try {
			const res = await financialStore.addCategory({
				name: newCatName.trim(),
				type: newCatType,
				color: '#007AFF'
			});
			if (res) {
				newCatName = '';
			}
		} finally {
			isSaving = false;
		}
	}

	function startEdit(cat: Category) {
		editingCatId = cat.id;
		editingCatName = cat.name;
	}

	async function saveEdit(catId: string) {
		if (!editingCatName.trim()) return;
		isSaving = true;
		try {
			await financialStore.updateCategory(catId, {
				name: editingCatName.trim()
			});
			editingCatId = null;
		} finally {
			isSaving = false;
		}
	}

	async function handleDelete(catId: string) {
		if (confirm('Hapus kategori ini dari database? Transaksi yang menggunakan kategori ini akan dialihkan ke kategori umum.')) {
			isSaving = true;
			try {
				await financialStore.deleteCategory(catId);
				if (value === catId) {
					value = '';
				}
			} finally {
				isSaving = false;
			}
		}
	}
</script>

<svelte:window onclick={handleClickOutside} onkeydown={handleKeydown} />

<div class="relative w-full" bind:this={containerEl}>
	{#if label}
		<div class="flex items-center justify-between mb-1.5">
			<span class="block text-xs font-semibold text-slate-700 dark:text-slate-300">
				{label}
			</span>
			<button
				type="button"
				onclick={(e) => {
					e.stopPropagation();
					openManageModal();
				}}
				class="text-[11px] font-medium text-[#007AFF] hover:underline flex items-center gap-1 cursor-pointer"
			>
				<Settings2 class="w-3 h-3" />
				<span>Atur Kategori</span>
			</button>
		</div>
	{/if}

	<!-- Custom Trigger Button (Stable in DOM, Never Unmounted On Click) -->
	<button
		type="button"
		{disabled}
		onclick={(e) => {
			e.stopPropagation();
			toggleOpen();
		}}
		class="w-full min-h-[38px] flex items-center justify-between px-3 rounded-xl bg-white dark:bg-[#151E2E] border text-left cursor-pointer transition-all outline-none {isOpen
			? 'border-[#007AFF] ring-2 ring-[#007AFF]/20 shadow-sm'
			: error
				? 'border-rose-400'
				: 'border-slate-200/80 dark:border-white/10 hover:border-[#007AFF]'} disabled:opacity-50 disabled:cursor-not-allowed"
	>
		{#if selectedCategory}
			<div class="flex items-center gap-2 truncate mr-2">
				<span
					class="w-2.5 h-2.5 rounded-full shrink-0"
					style="background-color: {selectedCategory.color || '#007AFF'};"
				></span>
				<span class="text-xs sm:text-sm font-medium text-slate-900 dark:text-white truncate">
					{selectedCategory.name}
				</span>
			</div>
		{:else}
			<span class="text-xs sm:text-sm text-slate-400 dark:text-slate-500 font-normal">
				{placeholder}
			</span>
		{/if}
		<ChevronDown
			class="w-4 h-4 text-slate-400 dark:text-slate-500 shrink-0 ml-1 transition-transform duration-200 {isOpen ? 'rotate-180 text-[#007AFF]' : ''}"
		/>
	</button>

	<!-- Suggestions Dropdown Menu -->
	{#if isOpen}
		<div
			role="presentation"
			onclick={(e) => e.stopPropagation()}
			onkeydown={(e) => e.stopPropagation()}
			class="absolute left-0 {openUpwards ? 'bottom-full mb-1.5' : 'top-full mt-1.5'} z-50 w-full min-w-[260px] p-2 rounded-2xl bg-white dark:bg-[#151926] border border-slate-200 dark:border-white/10 shadow-2xl animate-in fade-in zoom-in-95 duration-150"
		>
			<!-- Live Search Input Inside Dropdown -->
			<div class="relative mb-2">
				<Search class="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
				<input
					type="text"
					bind:this={inputEl}
					bind:value={searchQuery}
					placeholder="Ketik untuk mencari atau buat baru..."
					onkeydown={(e) => {
						if (e.key === 'Enter') {
							e.preventDefault();
							if (filteredCategories.length > 0) {
								selectCategory(filteredCategories[0].id);
							} else if (!exactMatch && searchQuery.trim()) {
								handleQuickAdd();
							}
						}
					}}
					class="w-full h-8 pl-8 pr-3 rounded-xl bg-slate-50 dark:bg-white/5 text-xs text-slate-900 dark:text-white placeholder:text-slate-400 border border-slate-200/80 dark:border-white/10 outline-none focus:border-[#007AFF]"
				/>
			</div>
			<!-- Categories List -->
			<div class="max-h-56 overflow-y-auto space-y-0.5 pr-0.5">
				{#each filteredCategories as cat}
					{@const isSelected = cat.id === value}
					<button
						type="button"
						onclick={() => selectCategory(cat.id)}
						class="w-full flex items-center justify-between px-2.5 py-2 rounded-xl text-xs text-left transition-colors cursor-pointer {isSelected
							? 'bg-[#007AFF]/10 text-[#007AFF] font-semibold'
							: 'text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-white/5'}"
					>
						<div class="flex items-center gap-2 truncate mr-2">
							<span
								class="w-2 h-2 rounded-full shrink-0"
								style="background-color: {cat.color || '#007AFF'};"
							></span>
							<span class="truncate">{cat.name}</span>
							{#if cat.is_system}
								<span class="text-[9px] px-1 py-0.2 rounded bg-slate-100 dark:bg-white/10 text-slate-400 font-normal shrink-0">
									Bawaan
								</span>
							{/if}
						</div>
						{#if isSelected}
							<Check class="w-3.5 h-3.5 text-[#007AFF] shrink-0" />
						{/if}
					</button>
				{/each}

				<!-- Quick Add Option when searching query doesn't match -->
				{#if !exactMatch && searchQuery.trim()}
					<button
						type="button"
						onclick={handleQuickAdd}
						disabled={isSaving}
						class="w-full flex items-center gap-2 px-2.5 py-2 rounded-xl text-xs text-left text-[#007AFF] dark:text-[#0A84FF] hover:bg-[#007AFF]/10 font-semibold transition-colors cursor-pointer border border-dashed border-[#007AFF]/30 mt-1"
					>
						<Plus class="w-3.5 h-3.5 shrink-0" />
						<span class="truncate">
							{isSaving ? 'Menyimpan...' : `Tambah "${searchQuery.trim()}" sebagai kategori baru`}
						</span>
					</button>
				{:else if filteredCategories.length === 0}
					<div class="py-4 text-center text-xs text-slate-400">
						Tidak ada kategori yang cocok
					</div>
				{/if}
			</div>

			<!-- Footer Action: Manage Categories Button -->
			<div class="pt-2 mt-1.5 border-t border-slate-100 dark:border-white/5 flex items-center justify-between px-1">
				<span class="text-[10px] text-slate-400">
					{filteredCategories.length} kategori dari database
				</span>
				<button
					type="button"
					onclick={openManageModal}
					class="text-[11px] font-semibold text-[#007AFF] hover:underline flex items-center gap-1 cursor-pointer"
				>
					<Settings2 class="w-3 h-3" />
					<span>Kelola Kategori</span>
				</button>
			</div>
		</div>
	{/if}

	{#if error}
		<p class="text-xs text-rose-500 mt-1">{error}</p>
	{/if}
</div>

<!-- ================= MODAL KELOLA KATEGORI (FULL CRUD DARI DATABASE) ================= -->
<Modal
	bind:open={isManageModalOpen}
	title="Kelola Kategori Kebutuhan"
	description="Tambah, ubah nama, atau hapus kategori belanja dan pendapatan di database Anda"
>
	<div class="space-y-4">
		<!-- Form Tambah Kategori Baru -->
		<div class="p-3.5 rounded-2xl bg-slate-50 dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/10 space-y-2.5">
			<span class="text-xs font-semibold text-slate-800 dark:text-white block">
				+ Buat Kategori Baru
			</span>
			<div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
				<input
					type="text"
					bind:value={newCatName}
					placeholder="Nama kategori baru..."
					class="flex-1 h-9 px-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-[#151E2E] text-xs text-slate-900 dark:text-white outline-none focus:border-[#007AFF]"
				/>
				<select
					bind:value={newCatType}
					class="h-9 px-2.5 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-[#151E2E] text-xs text-slate-700 dark:text-slate-300 outline-none focus:border-[#007AFF] cursor-pointer"
				>
					<option value="EXPENSE">Pengeluaran</option>
					<option value="INCOME">Pemasukan</option>
				</select>
				<Button
					variant="primary"
					onclick={handleCreateNewInModal}
					disabled={isSaving || !newCatName.trim()}
					class="h-9 px-3.5 text-xs whitespace-nowrap"
				>
					{isSaving ? 'Menyimpan...' : 'Tambah'}
				</Button>
			</div>
			{#if manageError}
				<p class="text-xs text-rose-500">{manageError}</p>
			{/if}
		</div>

		<!-- Daftar Kategori yang Ada di Database -->
		<div class="space-y-1.5">
			<span class="text-xs font-semibold text-slate-500 uppercase tracking-wider block">
				Daftar Kategori Terdaftar ({availableCategories.length})
			</span>
			<div class="max-h-60 overflow-y-auto space-y-1 pr-1 border border-slate-200/60 dark:border-white/5 rounded-2xl p-1.5">
				{#each availableCategories as cat}
					<div
						class="flex items-center justify-between p-2 rounded-xl bg-white dark:bg-white/[0.02] border border-slate-100 dark:border-white/5 hover:border-slate-200 dark:hover:border-white/10 transition-colors gap-2"
					>
						{#if editingCatId === cat.id}
							<input
								type="text"
								bind:value={editingCatName}
								class="flex-1 h-7 px-2 rounded-lg border border-[#007AFF] bg-white dark:bg-[#151E2E] text-xs text-slate-900 dark:text-white outline-none"
							/>
							<div class="flex items-center gap-1 shrink-0">
								<button
									type="button"
									onclick={() => saveEdit(cat.id)}
									class="px-2 py-1 rounded bg-[#007AFF] text-white text-[11px] font-semibold hover:bg-[#007AFF]/90"
								>
									Simpan
								</button>
								<button
									type="button"
									onclick={() => (editingCatId = null)}
									class="px-2 py-1 rounded text-slate-400 hover:text-slate-600 text-[11px]"
								>
									Batal
								</button>
							</div>
						{:else}
							<div class="flex items-center gap-2 truncate min-w-0">
								<span
									class="w-2.5 h-2.5 rounded-full shrink-0"
									style="background-color: {cat.color || '#007AFF'};"
								></span>
								<span class="text-xs font-medium text-slate-900 dark:text-white truncate">
									{cat.name}
								</span>
								{#if cat.is_system}
									<span class="text-[9px] px-1.5 py-0.5 rounded bg-slate-100 dark:bg-white/10 text-slate-400 font-normal shrink-0">
										Bawaan
									</span>
								{/if}
							</div>

							<div class="flex items-center gap-1 shrink-0">
								<!-- Edit Button -->
								<button
									type="button"
									onclick={() => startEdit(cat)}
									class="p-1 rounded-lg text-slate-400 hover:text-[#007AFF] hover:bg-[#007AFF]/10 transition-colors cursor-pointer"
									title="Ubah Nama Kategori"
								>
									<Pencil class="w-3.5 h-3.5" />
								</button>

								<!-- Delete Button (Hanya untuk kategori kustom / bukan bawaan) -->
								{#if !cat.is_system}
									<button
										type="button"
										onclick={() => handleDelete(cat.id)}
										class="p-1 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-colors cursor-pointer"
										title="Hapus Kategori"
									>
										<Trash2 class="w-3.5 h-3.5" />
									</button>
								{/if}
							</div>
						{/if}
					</div>
				{/each}
			</div>
		</div>
	</div>

	{#snippet footer()}
		<Button variant="primary" onclick={() => (isManageModalOpen = false)}>Selesai</Button>
	{/snippet}
</Modal>
