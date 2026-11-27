<script lang="ts">
	import { financialStore } from '$lib/stores/financial.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import { getWalletImage, WALLET_PRESETS } from '$lib/utils/walletIcons';
	import type { WalletMaster } from '$lib/types';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import {
		SlidersHorizontal,
		Plus,
		Search,
		Filter,
		Upload,
		Trash2,
		Pencil,
		Building2,
		Smartphone,
		Banknote,
		TrendingUp,
		ShieldCheck,
		Sparkles,
		AlertTriangle,
		Check
	} from 'lucide-svelte';

	let searchQuery = $state('');
	let selectedCategory = $state<'ALL' | 'BANK' | 'E_WALLET' | 'CASH' | 'INVESTMENT' | 'OTHER'>('ALL');

	// Create / Edit Modal State
	let isModalOpen = $state(false);
	let isEditing = $state(false);
	let editingId = $state<string | null>(null);

	let formName = $state('');
	let formCategory = $state<'BANK' | 'E_WALLET' | 'CASH' | 'INVESTMENT' | 'OTHER'>('BANK');
	let formColor = $state('#007AFF');
	let formDescription = $state('');
	let formImage = $state('');
	let imagePreview = $state('');
	let formError = $state('');
	let isSubmitting = $state(false);

	// Delete Modal State
	let isDeleteModalOpen = $state(false);
	let itemToDelete = $state<WalletMaster | null>(null);

	const categoryOptions = [
		{ value: 'BANK', label: 'Rekening Bank', icon: Building2 },
		{ value: 'E_WALLET', label: 'Dompet Digital (E-Wallet)', icon: Smartphone },
		{ value: 'CASH', label: 'Uang Kas & Tunai', icon: Banknote },
		{ value: 'INVESTMENT', label: 'Investasi & Aset', icon: TrendingUp },
		{ value: 'OTHER', label: 'Lainnya / Tabungan Khusus', icon: Sparkles }
	];

	const presetColors = [
		'#0060C4', '#0D47A1', '#0284C7', '#0F766E', '#10B981',
		'#00AED6', '#7C3AED', '#118EEA', '#EE4D2D', '#EA580C',
		'#B45309', '#EC4899', '#475569', '#D97706', '#EAB308'
	];

	// Filtered master wallets
	const filteredMasters = $derived(
		financialStore.walletMasters.filter((wm) => {
			if (selectedCategory !== 'ALL' && wm.category !== selectedCategory) return false;
			if (searchQuery.trim()) {
				const q = searchQuery.toLowerCase().trim();
				return (
					wm.name.toLowerCase().includes(q) ||
					wm.code.toLowerCase().includes(q) ||
					(wm.description && wm.description.toLowerCase().includes(q))
				);
			}
			return true;
		})
	);

	function openCreateModal() {
		isEditing = false;
		editingId = null;
		formName = '';
		formCategory = 'BANK';
		formColor = '#007AFF';
		formDescription = '';
		formImage = '/wallets/wallet.svg';
		imagePreview = '/wallets/wallet.svg';
		formError = '';
		isModalOpen = true;
	}

	function openEditModal(wm: WalletMaster) {
		isEditing = true;
		editingId = wm.id;
		formName = wm.name;
		formCategory = wm.category;
		formColor = wm.color || '#007AFF';
		formDescription = wm.description || '';
		formImage = wm.image || '/wallets/wallet.svg';
		imagePreview = wm.image || '/wallets/wallet.svg';
		formError = '';
		isModalOpen = true;
	}

	function openDeleteModal(wm: WalletMaster) {
		itemToDelete = wm;
		isDeleteModalOpen = true;
	}

	function handleFileUpload(e: Event) {
		const target = e.target as HTMLInputElement;
		const file = target.files?.[0];
		if (!file) return;

		// Limit file size to 2MB
		if (file.size > 2 * 1024 * 1024) {
			formError = 'Ukuran gambar maksimal 2MB.';
			return;
		}

		const reader = new FileReader();
		reader.onload = () => {
			const dataUrl = reader.result as string;
			formImage = dataUrl;
			imagePreview = dataUrl;
		};
		reader.readAsDataURL(file);
	}

	async function handleSubmit() {
		formError = '';
		if (!formName.trim()) {
			formError = 'Nama master dompet tidak boleh kosong.';
			return;
		}

		isSubmitting = true;
		try {
			if (isEditing && editingId) {
				const res = await financialStore.updateWalletMaster(editingId, {
					name: formName.trim(),
					category: formCategory,
					color: formColor,
					image: formImage,
					description: formDescription.trim()
				});
				if (res) isModalOpen = false;
			} else {
				const res = await financialStore.addWalletMaster({
					name: formName.trim(),
					category: formCategory,
					color: formColor,
					image: formImage,
					description: formDescription.trim()
				});
				if (res) isModalOpen = false;
			}
		} finally {
			isSubmitting = false;
		}
	}

	async function confirmDelete() {
		if (!itemToDelete) return;
		await financialStore.deleteWalletMaster(itemToDelete.id);
		isDeleteModalOpen = false;
		itemToDelete = null;
	}
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full pb-24 lg:pb-10">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200/80 dark:border-white/10">
		<div>
			<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
				<SlidersHorizontal class="w-6 h-6 text-[#007AFF] dark:text-[#0A84FF]" />
				<span>Master Dompet & Ciri Khas</span>
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
				Kelola template dompet, jenis rekening, dan kustomisasi logo / gambar dompet Anda
			</p>
		</div>

		<Button variant="primary" class="h-9 px-4 text-xs shrink-0" onclick={openCreateModal}>
			<Plus class="w-4 h-4 mr-1.5" />
			<span>Tambah Master Dompet</span>
		</Button>
	</div>

	<!-- Unified Filter & Search Bar -->
	<div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
		<!-- Search Field -->
		<div class="relative w-full sm:w-72">
			<Search class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="Cari master dompet..."
				class="w-full h-9 pl-9 pr-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:border-[#007AFF] transition-colors"
			/>
		</div>

		<!-- Category Chips -->
		<div class="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0 scrollbar-none">
			<button
				type="button"
				onclick={() => (selectedCategory = 'ALL')}
				class="px-3 h-8 rounded-lg text-xs font-medium whitespace-nowrap transition-colors {selectedCategory === 'ALL'
					? 'bg-[#007AFF] text-white'
					: 'bg-slate-100 dark:bg-white/5 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
			>
				Semua ({financialStore.walletMasters.length})
			</button>
			{#each categoryOptions as opt}
				{@const count = financialStore.walletMasters.filter((w) => w.category === opt.value).length}
				<button
					type="button"
					onclick={() => (selectedCategory = opt.value as any)}
					class="px-3 h-8 rounded-lg text-xs font-medium whitespace-nowrap transition-colors {selectedCategory === opt.value
						? 'bg-[#007AFF] text-white'
						: 'bg-slate-100 dark:bg-white/5 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
				>
					{opt.label.split(' ')[0]} ({count})
				</button>
			{/each}
		</div>
	</div>

	<!-- Master Dompet Cards Grid -->
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 sm:gap-4">
		{#each filteredMasters as wm (wm.id)}
			{@const imageSrc = getWalletImage(wm.image || wm.code, wm.category)}
			{@const usedCount = financialStore.accounts.filter((a) => a.icon === wm.code || a.name.toLowerCase() === wm.name.toLowerCase()).length}
			<div
				class="p-4 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] flex flex-col justify-between gap-3 relative group hover:border-[#007AFF]/40 hover:-translate-y-0.5 transition-all"
			>
				<!-- Top: Actions & Badges -->
				<div class="flex items-start justify-between gap-2">
					<div class="flex items-center gap-1.5">
						{#if wm.is_system}
							<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-semibold bg-blue-500/10 text-[#007AFF] dark:text-[#0A84FF]">
								<ShieldCheck class="w-3 h-3" />
								<span>Bawaan</span>
							</span>
						{:else}
							<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
								<Sparkles class="w-3 h-3" />
								<span>Kustom</span>
							</span>
						{/if}
						<span class="px-2 py-0.5 rounded-md text-[10px] font-medium bg-slate-100 dark:bg-white/5 text-slate-500 dark:text-slate-400">
							{wm.category.replace('_', ' ')}
						</span>
					</div>

					{#if !wm.is_system}
						<div class="flex items-center gap-1">
							<button
								type="button"
								onclick={() => openEditModal(wm)}
								class="p-1 rounded-md text-slate-400 hover:text-[#007AFF] hover:bg-slate-100 dark:hover:bg-white/5 transition-colors"
								title="Edit Master Dompet"
							>
								<Pencil class="w-3.5 h-3.5" />
							</button>
							<button
								type="button"
								onclick={() => openDeleteModal(wm)}
								class="p-1 rounded-md text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-colors"
								title="Hapus Master Dompet"
							>
								<Trash2 class="w-3.5 h-3.5" />
							</button>
						</div>
					{/if}
				</div>

				<!-- Middle: Logo & Info -->
				<div class="flex items-center gap-3">
					<div
						class="w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 p-1 bg-slate-50 dark:bg-white/5 border border-slate-200/60 dark:border-white/10 shadow-sm relative overflow-hidden"
						style="border-color: {wm.color ? wm.color + '40' : 'transparent'}"
					>
						<img
							src={imageSrc}
							alt={wm.name}
							class="w-full h-full object-contain rounded-xl"
							loading="lazy"
						/>
					</div>
					<div class="min-w-0 flex-1">
						<h3 class="text-sm font-semibold text-slate-900 dark:text-white truncate" title={wm.name}>
							{wm.name}
						</h3>
						<p class="text-xs text-slate-400 truncate mt-0.5">
							{wm.description || `Kode: ${wm.code}`}
						</p>
					</div>
				</div>

				<!-- Bottom: Accent Strip & Usage Count -->
				<div class="pt-2 border-t border-slate-100 dark:border-white/5 flex items-center justify-between text-[11px] text-slate-400">
					<div class="flex items-center gap-1.5">
						<span class="w-2.5 h-2.5 rounded-full" style="background-color: {wm.color || '#007AFF'}"></span>
						<span>{wm.color || '#007AFF'}</span>
					</div>
					<span>{usedCount} Akun Memakai</span>
				</div>
			</div>
		{/each}

		<!-- Add Card Shortcut -->
		<button
			type="button"
			onclick={openCreateModal}
			class="p-5 rounded-2xl border border-dashed border-slate-200/90 dark:border-white/10 hover:border-[#007AFF] flex flex-col items-center justify-center text-center gap-2 group transition-all min-h-[140px] bg-slate-50/50 dark:bg-white/[0.01] hover:bg-blue-50/20 cursor-pointer"
		>
			<div class="w-10 h-10 rounded-xl bg-blue-500/10 text-[#007AFF] flex items-center justify-center group-hover:scale-110 transition-transform">
				<Plus class="w-5 h-5" />
			</div>
			<div>
				<span class="text-xs font-semibold text-slate-900 dark:text-white block group-hover:text-[#007AFF]">Tambah Master Dompet</span>
				<span class="text-[11px] text-slate-400 block">Buat preset dompet / upload logo baru</span>
			</div>
		</button>
	</div>

	<!-- Add / Edit Modal -->
	<Modal
		bind:open={isModalOpen}
		title={isEditing ? 'Ubah Master Dompet' : 'Tambah Master Dompet Baru'}
		description="Tambahkan jenis atau ciri khas dompet baru ke dalam sistem"
	>
		<form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-4">
			<Input
				bind:value={formName}
				label="Nama Master Dompet *"
				placeholder="Contoh: Bank Neo Commerce, PayPal, Tabungan Emas"
			/>

			<div>
				<label for="category-select" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
					Kategori Dompet *
				</label>
				<select
					id="category-select"
					bind:value={formCategory}
					class="w-full h-10 px-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-[#007AFF]"
				>
					{#each categoryOptions as opt}
						<option value={opt.value}>{opt.label}</option>
					{/each}
				</select>
			</div>

			<!-- Image / Icon Upload & Preview -->
			<div>
				<span class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
					Logo / Gambar Dompet *
				</span>
				<div class="flex items-center gap-4 p-3 rounded-2xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200/80 dark:border-white/10">
					<!-- Preview Box -->
					<div class="w-16 h-16 rounded-2xl bg-white dark:bg-white/5 border border-slate-200/80 dark:border-white/10 flex items-center justify-center p-1 shrink-0 overflow-hidden shadow-sm">
						<img
							src={imagePreview || '/wallets/wallet.svg'}
							alt="Preview"
							class="w-full h-full object-contain rounded-xl"
						/>
					</div>

					<!-- Upload Controls -->
					<div class="flex-1 space-y-1.5">
						<label class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#007AFF] text-white text-xs font-semibold hover:bg-blue-600 transition-colors cursor-pointer">
							<Upload class="w-3.5 h-3.5" />
							<span>Upload Gambar / Logo</span>
							<input
								type="file"
								accept="image/png,image/jpeg,image/svg+xml,image/webp"
								onchange={handleFileUpload}
								class="hidden"
							/>
						</label>
						<p class="text-[11px] text-slate-400">
							Format PNG, JPG, SVG, atau WebP (Maks. 2MB).
						</p>
					</div>
				</div>

				<!-- Quick Presets Picker as an alternative -->
				<div class="mt-2.5">
					<span class="text-[11px] text-slate-500 font-medium block mb-1.5">Atau pilih dari ikon bawaan:</span>
					<div class="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
						{#each WALLET_PRESETS as preset}
							<button
								type="button"
								onclick={() => {
									formImage = preset.image;
									imagePreview = preset.image;
								}}
								class="w-8 h-8 rounded-lg p-1 border transition-all shrink-0 bg-white dark:bg-white/5 {imagePreview === preset.image
									? 'border-[#007AFF] ring-2 ring-[#007AFF]/20'
									: 'border-slate-200 dark:border-white/10 hover:border-slate-300'}"
								title={preset.name}
							>
								<img src={preset.image} alt={preset.name} class="w-full h-full object-contain" />
							</button>
						{/each}
					</div>
				</div>
			</div>

			<!-- Color Picker -->
			<div>
				<span class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
					Warna Ciri Khas
				</span>
				<div class="flex items-center gap-2 flex-wrap">
					{#each presetColors as col}
						<button
							type="button"
							onclick={() => (formColor = col)}
							class="w-6 h-6 rounded-full flex items-center justify-center transition-transform hover:scale-110"
							style="background-color: {col}"
						>
							{#if formColor === col}
								<Check class="w-3.5 h-3.5 text-white" />
							{/if}
						</button>
					{/each}
				</div>
			</div>

			<Input
				bind:value={formDescription}
				label="Catatan / Keterangan Singkat"
				placeholder="Contoh: Rekening utama untuk transaksi bisnis"
			/>

			{#if formError}
				<p class="text-xs text-rose-500 bg-rose-50 dark:bg-rose-950/30 p-2.5 rounded-xl border border-rose-200 dark:border-rose-900">
					{formError}
				</p>
			{/if}

			<div class="pt-3 flex items-center justify-end gap-2 border-t border-slate-100 dark:border-white/5">
				<Button variant="ghost" onclick={() => (isModalOpen = false)} class="text-xs">
					Batal
				</Button>
				<Button variant="primary" type="submit" disabled={isSubmitting} class="text-xs">
					{isSubmitting ? 'Menyimpan...' : isEditing ? 'Simpan Perubahan' : 'Buat Master Dompet'}
				</Button>
			</div>
		</form>
	</Modal>

	<!-- Delete Confirmation Modal -->
	<Modal
		bind:open={isDeleteModalOpen}
		title="Hapus Master Dompet"
		description="Apakah Anda yakin ingin menghapus master dompet ini?"
	>
		<div class="space-y-4">
			<div class="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-700 dark:text-rose-400 flex items-start gap-2.5">
				<AlertTriangle class="w-4 h-4 shrink-0 mt-0.5 text-rose-500" />
				<span>
					Master dompet <strong>{itemToDelete?.name}</strong> akan dihapus dari daftar pilihan dompet. Rekening yang sudah dibuat menggunakan template ini tidak akan terhapus.
				</span>
			</div>

			<div class="pt-2 flex items-center justify-end gap-2">
				<Button variant="ghost" onclick={() => (isDeleteModalOpen = false)} class="text-xs">
					Batal
				</Button>
				<Button variant="danger" onclick={confirmDelete} class="text-xs">
					Hapus Master Dompet
				</Button>
			</div>
		</div>
	</Modal>
</div>
