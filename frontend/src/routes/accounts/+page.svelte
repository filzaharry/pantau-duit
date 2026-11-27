<script lang="ts">
	import { authStore } from '$lib/stores/auth.svelte';
	import { financialStore } from '$lib/stores/financial.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import { formatRupiah } from '$lib/utils/formatters';
	import { WALLET_PRESETS, getWalletImage } from '$lib/utils/walletIcons';
	import AccountCard from '$lib/components/financial/AccountCard.svelte';
	import AddTransactionModal from '$lib/components/financial/AddTransactionModal.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import AmountInput from '$lib/components/ui/AmountInput.svelte';
	import Select from '$lib/components/ui/Select.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import type { Account, AccountType } from '$lib/types';
	import {
		Wallet,
		Plus,
		ArrowLeftRight,
		Building2,
		Banknote,
		Smartphone,
		Search,
		Filter,
		Trash2,
		AlertTriangle,
		Image as ImageIcon
	} from 'lucide-svelte';

	let isTransferModalOpen = $state(false);
	let isAddAccountOpen = $state(false);
	let searchQuery = $state('');
	let selectedType = $state<'ALL' | 'BANK' | 'E_WALLET' | 'CASH' | 'INVESTMENT'>('ALL');
	let isFilterOpen = $state(false);

	const isFilterActive = $derived(selectedType !== 'ALL');

	const availablePresets = $derived(
		financialStore.walletMasters.length > 0
			? financialStore.walletMasters.map((wm) => ({
					id: wm.code,
					name: wm.name,
					category: wm.category,
					image: getWalletImage(wm.image || wm.code, wm.category),
					color: wm.color || '#007AFF'
				}))
			: WALLET_PRESETS
	);

	function resetFilters() {
		selectedType = 'ALL';
		isFilterOpen = false;
	}

	const filteredAccounts = $derived(
		financialStore.accounts.filter((a) => {
			if (selectedType !== 'ALL' && a.type !== selectedType) return false;
			if (searchQuery.trim()) {
				const q = searchQuery.toLowerCase();
				return a.name.toLowerCase().includes(q) || (a.institution_name && a.institution_name.toLowerCase().includes(q));
			}
			return true;
		})
	);

	// Delete Confirmation Modal State
	let isDeleteConfirmOpen = $state(false);
	let accountToDelete = $state<Account | null>(null);

	function openDeleteModal(account: Account) {
		accountToDelete = account;
		isDeleteConfirmOpen = true;
	}

	async function confirmDeleteAccount() {
		if (!accountToDelete) return;
		await financialStore.deleteAccount(accountToDelete.id);
		isDeleteConfirmOpen = false;
		accountToDelete = null;
	}

	// Edit Account Modal State
	let isEditAccountOpen = $state(false);
	let accountToEdit = $state<Account | null>(null);
	let editName = $state('');
	let editAccountNumber = $state('');
	let editIcon = $state('bca');
	let editColor = $state('');
	let editError = $state('');

	function openEditModal(account: Account) {
		accountToEdit = account;
		editName = account.name;
		editAccountNumber = account.account_number || '';
		editIcon = account.icon || 'bca';
		editColor = account.color || '';
		editError = '';
		isEditAccountOpen = true;
	}

	async function handleSaveEditAccount() {
		if (!accountToEdit) return;
		if (!editName.trim()) {
			editError = 'Nama rekening tidak boleh kosong.';
			return;
		}

		await financialStore.updateAccount(accountToEdit.id, {
			name: editName.trim(),
			account_number: editAccountNumber.trim(),
			icon: editIcon,
			color: editColor || accountToEdit.color
		});

		isEditAccountOpen = false;
		accountToEdit = null;
	}

	// Add Account Form
	let accountName = $state('');
	let accountType = $state<AccountType>('BANK');
	let institutionName = $state('');
	let initialBalance = $state(0);
	let accountNumber = $state('');
	let selectedIcon = $state('bca');
	let selectedColor = $state('#0060C4');
	let formError = $state('');

	async function handleAddAccount() {
		formError = '';
		if (!accountName.trim()) {
			formError = 'Nama rekening harus diisi.';
			return;
		}

		await financialStore.addAccount({
			name: accountName.trim(),
			type: accountType || 'BANK',
			opening_balance: initialBalance,
			account_number: accountNumber.trim(),
			institution_name: institutionName.trim(),
			icon: selectedIcon,
			color: selectedColor
		});

		isAddAccountOpen = false;
		accountName = '';
		institutionName = '';
		initialBalance = 0;
		accountNumber = '';
		selectedIcon = 'bca';
		selectedColor = '#0060C4';
	}

	// Calculate counts & balances
	const bankAccounts = $derived(financialStore.accounts.filter((a) => a.type === 'BANK'));
	const eWalletAccounts = $derived(financialStore.accounts.filter((a) => a.type === 'E_WALLET'));
	const cashAccounts = $derived(financialStore.accounts.filter((a) => a.type === 'CASH'));

	const bankCount = $derived(bankAccounts.length);
	const eWalletCount = $derived(eWalletAccounts.length);
	const cashCount = $derived(cashAccounts.length);

	const bankBalance = $derived(
		bankAccounts.reduce((acc, a) => acc + (a.current_balance || a.balance || 0), 0)
	);
	const eWalletBalance = $derived(
		eWalletAccounts.reduce((acc, a) => acc + (a.current_balance || a.balance || 0), 0)
	);
	const cashBalance = $derived(
		cashAccounts.reduce((acc, a) => acc + (a.current_balance || a.balance || 0), 0)
	);
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full pb-24 lg:pb-10">
	<!-- Page Header -->
	<div class="pb-2 border-b border-slate-200/80 dark:border-white/10">
		<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
			<Wallet class="w-6 h-6 text-[#007AFF] dark:text-[#0A84FF]" />
			<span>{authStore.isSuperuser ? 'Kas & Rekening Sistem' : 'Rekening & Dompet Digital'}</span>
		</h1>
		<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
			{authStore.isSuperuser
				? 'Saldo terkumpul dari payment gateway dan bank operasional'
				: 'Kelola seluruh saldo akun bank, e-wallet, uang tunai, dan akun investasi'}
		</p>
	</div>

	<!-- Top Metric Ribbon Strip -->
	<div class="p-3 sm:p-5 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
		<div class="grid grid-cols-2 lg:grid-cols-4 gap-2.5 sm:gap-4 lg:divide-x divide-slate-100 dark:divide-white/5">
			<!-- Col 1: Total Saldo -->
			<div class="flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-blue-500/10 text-[#007AFF] dark:text-[#0A84FF] flex items-center justify-center shrink-0">
					<Wallet class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Total Saldo</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">{formatRupiah(financialStore.totalBalance)}</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">{financialStore.accounts.length} Akun Aktif</span>
				</div>
			</div>

			<!-- Col 2: Rekening Bank -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-blue-500/10 dark:bg-blue-500/20 text-[#007AFF] dark:text-[#0A84FF] flex items-center justify-center shrink-0">
					<Building2 class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">
						{authStore.isSuperuser ? 'Bank Bisnis' : 'Rekening Bank'}
					</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">{formatRupiah(bankBalance)}</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">{bankCount} Akun Bank</span>
				</div>
			</div>

			<!-- Col 3: Dompet Digital (E-Wallet) -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-cyan-500/10 dark:bg-cyan-500/20 text-cyan-600 dark:text-cyan-400 flex items-center justify-center shrink-0">
					<Smartphone class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">
						{authStore.isSuperuser ? 'Payment Gateway' : 'Dompet Digital'}
					</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">{formatRupiah(eWalletBalance)}</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">{eWalletCount} Akun PG</span>
				</div>
			</div>

			<!-- Col 4: Uang Kas & Tunai -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-emerald-500/10 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
					<Banknote class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">
						{authStore.isSuperuser ? 'Saldo Server' : 'Uang Kas & Tunai'}
					</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">{formatRupiah(cashBalance)}</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">{cashCount} Akun Kas</span>
				</div>
			</div>
		</div>
	</div>

	<!-- Unified Action Toolbar -->
	<div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
		<!-- Search Field -->
		<div class="relative w-full sm:w-[40%] sm:max-w-[40%]">
			<Search class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="Cari rekening atau nama bank..."
				class="w-full h-9 pl-9 pr-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:border-[#007AFF] transition-colors"
			/>
		</div>

		<!-- Action Buttons: Filter, Transfer, Tambah Rekening -->
		<div class="flex items-center gap-2">
			<!-- Filter Button with Popover -->
			<div class="relative">
				<Button
					variant="ghost"
					onclick={() => (isFilterOpen = !isFilterOpen)}
					class="h-9 px-3 text-xs border border-slate-200/80 dark:border-white/10 {isFilterActive ? 'text-[#007AFF] border-[#007AFF]/40 bg-[#007AFF]/5' : ''}"
				>
					<Filter class="w-3.5 h-3.5 mr-1.5" />
					<span>Filter</span>
					{#if isFilterActive}
						<span class="w-1.5 h-1.5 rounded-full bg-[#007AFF] ml-1"></span>
					{/if}
				</Button>

				{#if isFilterOpen}
					<button
						type="button"
						aria-label="Tutup menu filter"
						class="fixed inset-0 z-30 cursor-default bg-transparent"
						onclick={() => (isFilterOpen = false)}
					></button>

					<div class="absolute right-0 top-full mt-2 w-56 p-3 rounded-2xl bg-white dark:bg-[#151926] border border-slate-200/80 dark:border-white/10 shadow-2xl z-40 space-y-3">
						<div>
							<span class="text-[11px] font-semibold text-slate-700 dark:text-slate-300 block mb-1.5">Tipe Rekening</span>
							<select
								bind:value={selectedType}
								class="w-full h-8 px-2.5 rounded-lg border border-slate-200/80 dark:border-white/10 bg-slate-50 dark:bg-white/5 text-xs text-slate-700 dark:text-slate-300 focus:outline-none focus:border-[#007AFF]"
							>
								<option value="ALL">Semua Tipe</option>
								<option value="BANK">Rekening Bank</option>
								<option value="E_WALLET">Dompet Digital</option>
								<option value="CASH">Uang Tunai</option>
								<option value="INVESTMENT">Investasi</option>
							</select>
						</div>

						{#if isFilterActive}
							<div class="pt-1 border-t border-slate-100 dark:border-white/5 flex justify-end">
								<button
									type="button"
									onclick={resetFilters}
									class="text-[11px] font-semibold text-rose-500 hover:underline cursor-pointer"
								>
									Reset Filter
								</button>
							</div>
						{/if}
					</div>
				{/if}
			</div>

			<Button variant="primary" class="h-9 px-3.5 text-xs" onclick={() => (isAddAccountOpen = true)}>
				<Plus class="w-4 h-4 mr-1.5" />
				<span>Tambah Rekening</span>
			</Button>
		</div>
	</div>

	<!-- Accounts Cards Grid -->
	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 sm:gap-4">
		{#each filteredAccounts as account (account.id)}
			<AccountCard {account} />
		{/each}

		<!-- + Tambah Rekening Interactive Card -->
		<button
			type="button"
			onclick={() => (isAddAccountOpen = true)}
			class="p-3.5 sm:p-5 rounded-2xl border border-dashed border-slate-200/90 dark:border-white/10 hover:border-[#007AFF] dark:hover:border-[#0A84FF] flex flex-row sm:flex-col items-center justify-center text-left sm:text-center gap-3 sm:gap-2.5 group transition-all min-h-[56px] sm:min-h-[140px] bg-slate-50/50 dark:bg-white/[0.01] hover:bg-blue-50/20 dark:hover:bg-blue-500/[0.02] cursor-pointer"
		>
			<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-blue-500/10 dark:bg-blue-500/20 text-[#007AFF] dark:text-[#0A84FF] flex items-center justify-center shrink-0 group-hover:scale-110 transition-transform">
				<Plus class="w-4 h-4 sm:w-5 sm:h-5" />
			</div>
			<div>
				<span class="text-xs font-semibold text-slate-900 dark:text-white block group-hover:text-[#007AFF] dark:group-hover:text-[#0A84FF]">Tambah Rekening</span>
				<span class="text-[10px] sm:text-[11px] text-slate-400 block">Hubungkan bank / e-wallet baru</span>
			</div>
		</button>
	</div>

	<!-- Transfer & Add Account Modals -->
	<AddTransactionModal bind:open={isTransferModalOpen} />

	<!-- Add Account Modal with Image Badge Picker -->
	<Modal
		bind:open={isAddAccountOpen}
		title="Tambah Rekening / Dompet Baru"
		description="Tambahkan sumber dana baru untuk dicatat di PantauDuit"
	>
		<div class="space-y-4 max-h-[75vh] overflow-y-auto pr-1">
			<Input
				bind:value={accountName}
				label="Nama Rekening / Dompet *"
				placeholder="Contoh: BCA Utama, GoPay, Dompet Harian"
			/>

			<!-- Visual Image / Badge Selection -->
			<div>
				<div class="flex items-center justify-between mb-2">
					<span class="block text-xs font-semibold text-slate-700 dark:text-slate-300">
						Pilih Gambar & Ciri Khas Dompet
					</span>
					<a href="/wallet-master" class="text-[11px] font-semibold text-[#007AFF] hover:underline flex items-center gap-1">
						+ Kelola Master Dompet
					</a>
				</div>
				<div class="grid grid-cols-4 sm:grid-cols-7 gap-2 p-2.5 rounded-2xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/[0.06] max-h-48 overflow-y-auto">
					{#each availablePresets as preset}
						<button
							type="button"
							onclick={() => {
								selectedIcon = preset.id;
								selectedColor = preset.color;
								if (!accountName.trim() || accountName === 'Bank BCA') {
									accountName = preset.name;
								}
								accountType = preset.category as AccountType;
							}}
							class="p-1.5 rounded-xl border flex flex-col items-center justify-center gap-1 transition-all cursor-pointer {selectedIcon === preset.id ? 'border-[#007AFF] bg-blue-50/50 dark:bg-blue-500/10 ring-2 ring-[#007AFF]/30 scale-105 shadow-sm' : 'border-transparent hover:border-slate-200 dark:hover:border-white/10 hover:bg-white dark:hover:bg-white/5'}"
							title={preset.name}
						>
							<img src={preset.image} alt={preset.name} class="w-8 h-8 rounded-lg object-contain shadow-xs" />
							<span class="text-[9px] font-semibold text-slate-600 dark:text-slate-400 truncate w-full text-center">
								{preset.name.replace('Bank ', '')}
							</span>
						</button>
					{/each}
				</div>
			</div>

			<Input
				bind:value={institutionName}
				label="Nama Institusi / Bank (Opsional)"
				placeholder="Contoh: Bank Central Asia, GoTo, Bank Mandiri"
			/>

			<Input
				bind:value={accountNumber}
				label="Nomor Rekening / HP (Opsional)"
				placeholder="Contoh: 1234567890 atau 0812xxxx"
			/>

			<AmountInput
				bind:value={initialBalance}
				label="Saldo Awal Saat Ini"
				showPercentageChips={false}
			/>

			<div class="p-3 rounded-xl bg-blue-50/60 dark:bg-blue-500/5 border border-blue-200/50 dark:border-blue-500/20 text-slate-600 dark:text-slate-300 text-[11px] leading-relaxed">
				💡 <strong>Otomatis Tercatat</strong>: Nilai saldo awal di atas akan otomatis dicatat sebagai transaksi pemasukan pertama Anda di modul Riwayat Transaksi dan Dashboard.
			</div>

			{#if formError}
				<p class="text-xs font-semibold text-rose-500 bg-rose-50 dark:bg-rose-950/30 p-2.5 rounded-xl border border-rose-200">
					{formError}
				</p>
			{/if}
		</div>

		{#snippet footer()}
			<Button variant="ghost" onclick={() => (isAddAccountOpen = false)}>Batal</Button>
			<Button variant="primary" onclick={handleAddAccount}>Simpan Rekening</Button>
		{/snippet}
	</Modal>

	<!-- Edit Account Modal (Change Image & Details) -->
	<Modal
		bind:open={isEditAccountOpen}
		title="Ubah Rekening / Gambar Dompet"
		description="Sesuaikan nama, logo gambar, dan detail dompet Anda"
	>
		<div class="space-y-4 max-h-[75vh] overflow-y-auto pr-1">
			<Input
				bind:value={editName}
				label="Nama Rekening / Dompet *"
				placeholder="Contoh: BCA Utama, Dompet Belanja"
			/>

			<!-- Visual Image / Badge Selection for Edit -->
			<div>
				<div class="flex items-center justify-between mb-2">
					<span class="block text-xs font-semibold text-slate-700 dark:text-slate-300">
						Ganti Gambar & Ciri Khas Dompet
					</span>
					<a href="/wallet-master" class="text-[11px] font-semibold text-[#007AFF] hover:underline flex items-center gap-1">
						+ Kelola Master Dompet
					</a>
				</div>
				<div class="grid grid-cols-4 sm:grid-cols-7 gap-2 p-2.5 rounded-2xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/[0.06] max-h-48 overflow-y-auto">
					{#each availablePresets as preset}
						<button
							type="button"
							onclick={() => {
								editIcon = preset.id;
								editColor = preset.color;
							}}
							class="p-1.5 rounded-xl border flex flex-col items-center justify-center gap-1 transition-all cursor-pointer {editIcon === preset.id || editIcon === preset.image ? 'border-[#007AFF] bg-blue-50/50 dark:bg-blue-500/10 ring-2 ring-[#007AFF]/30 scale-105 shadow-sm' : 'border-transparent hover:border-slate-200 dark:hover:border-white/10 hover:bg-white dark:hover:bg-white/5'}"
							title={preset.name}
						>
							<img src={preset.image} alt={preset.name} class="w-8 h-8 rounded-lg object-contain shadow-xs" />
							<span class="text-[9px] font-semibold text-slate-600 dark:text-slate-400 truncate w-full text-center">
								{preset.name.replace('Bank ', '')}
							</span>
						</button>
					{/each}
				</div>
			</div>

			<Input
				bind:value={editAccountNumber}
				label="Nomor Rekening / HP (Opsional)"
				placeholder="Contoh: 1234567890"
			/>

			{#if editError}
				<p class="text-xs font-semibold text-rose-500 bg-rose-50 dark:bg-rose-950/30 p-2.5 rounded-xl border border-rose-200">
					{editError}
				</p>
			{/if}
		</div>

		{#snippet footer()}
			<Button variant="ghost" onclick={() => (isEditAccountOpen = false)}>Batal</Button>
			<Button variant="primary" onclick={handleSaveEditAccount}>Simpan Perubahan</Button>
		{/snippet}
	</Modal>

	<!-- Delete Account Confirmation Modal (Soft Delete Safe Confirmation) -->
	<Modal
		bind:open={isDeleteConfirmOpen}
		title="Hapus Rekening / Dompet"
		description="Konfirmasi penghapusan rekening dan transaksi terkait"
	>
		<div class="space-y-3">
			<div class="flex items-start gap-3 p-3.5 rounded-2xl bg-rose-50 dark:bg-rose-950/20 border border-rose-200/80 dark:border-rose-900/40">
				<AlertTriangle class="w-5 h-5 text-rose-600 dark:text-rose-400 shrink-0 mt-0.5" />
				<div class="text-xs space-y-1.5 text-slate-700 dark:text-slate-300">
					<p>
						Apakah Anda yakin ingin menghapus rekening <strong class="text-slate-900 dark:text-white font-semibold">{accountToDelete?.name}</strong>?
					</p>
					<p class="text-slate-500 dark:text-slate-400 text-[11px] leading-relaxed">
						Semua riwayat transaksi di rekening ini juga akan otomatis disembunyikan dari dashboard dan laporan. Sistem menggunakan <strong>soft delete</strong> sehingga data tetap aman dan tersimpan di database untuk keperluan pemulihan (rollback).
					</p>
				</div>
			</div>
		</div>

		{#snippet footer()}
			<Button variant="ghost" onclick={() => (isDeleteConfirmOpen = false)}>Batal</Button>
			<button
				type="button"
				onclick={confirmDeleteAccount}
				class="inline-flex items-center justify-center gap-1.5 px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold shadow-sm transition-all cursor-pointer"
			>
				<Trash2 class="w-3.5 h-3.5" />
				<span>Ya, Hapus Rekening</span>
			</button>
		{/snippet}
	</Modal>
</div>
