<script lang="ts">
	import { goto } from '$app/navigation';
	import { financialStore } from '$lib/stores/financial.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import { formatRupiah, formatDate } from '$lib/utils/formatters';
	import { getWalletImage, WALLET_PRESETS } from '$lib/utils/walletIcons';
	import type { AccountType } from '$lib/types';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import AddTransactionModal from '$lib/components/financial/AddTransactionModal.svelte';
	import {
		ArrowLeft,
		ArrowLeftRight,
		Plus,
		Image as ImageIcon,
		Trash2,
		Wallet,
		ArrowUpRight,
		ArrowDownLeft,
		Search,
		Filter,
		Building2,
		Check,
		AlertTriangle,
		History,
		Calendar
	} from 'lucide-svelte';

	let { data } = $props<{ data: { id: string } }>();

	const account = $derived(financialStore.accounts.find((a) => a.id === data.id));
	const walletImage = $derived(account ? getWalletImage(account.icon, account.type) : '/wallets/wallet.svg');

	// Modals
	let isTransferModalOpen = $state(false);
	let isAddTxModalOpen = $state(false);
	let isEditModalOpen = $state(false);
	let isDeleteModalOpen = $state(false);

	// Edit Account Form State
	let editName = $state('');
	let editAccountNumber = $state('');
	let editIcon = $state('bca');
	let editType = $state<AccountType>('BANK');
	let editError = $state('');
	let isSavingEdit = $state(false);

	$effect(() => {
		if (account && !isEditModalOpen) {
			editName = account.name;
			editAccountNumber = account.account_number || '';
			editIcon = account.icon || 'bca';
			editType = account.type;
		}
	});

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

	function openEdit() {
		if (!account) return;
		editName = account.name;
		editAccountNumber = account.account_number || '';
		editIcon = account.icon || 'bca';
		editType = account.type;
		editError = '';
		isEditModalOpen = true;
	}

	async function handleSaveEdit() {
		if (!account) return;
		if (!editName.trim()) {
			editError = 'Nama rekening tidak boleh kosong.';
			return;
		}

		isSavingEdit = true;
		try {
			await financialStore.updateAccount(account.id, {
				name: editName.trim(),
				type: editType,
				account_number: editAccountNumber.trim(),
				icon: editIcon
			});
			isEditModalOpen = false;
		} finally {
			isSavingEdit = false;
		}
	}

	async function handleDelete() {
		if (!account) return;
		await financialStore.deleteAccount(account.id);
		isDeleteModalOpen = false;
		goto('/accounts');
	}

	// Filtered transactions for this specific account
	let txSearchQuery = $state('');
	let txTypeFilter = $state<'ALL' | 'INCOME' | 'EXPENSE' | 'TRANSFER'>('ALL');

	const accountTransactions = $derived(
		financialStore.transactions.filter((t) => {
			const isLinked = t.account_id === data.id || t.destination_account_id === data.id;
			if (!isLinked) return false;
			if (txTypeFilter !== 'ALL' && t.transaction_type !== txTypeFilter) return false;
			if (txSearchQuery.trim()) {
				const q = txSearchQuery.toLowerCase().trim();
				return (
					t.description.toLowerCase().includes(q) ||
					(t.category_name && t.category_name.toLowerCase().includes(q))
				);
			}
			return true;
		})
	);

	// Account specific metrics
	const totalIncomeThisAccount = $derived(
		financialStore.transactions
			.filter((t) => t.account_id === data.id && t.transaction_type === 'INCOME' && t.status === 'COMPLETED')
			.reduce((sum, t) => sum + Number(t.amount), 0)
	);

	const totalExpenseThisAccount = $derived(
		financialStore.transactions
			.filter((t) => t.account_id === data.id && t.transaction_type === 'EXPENSE' && t.status === 'COMPLETED')
			.reduce((sum, t) => sum + Number(t.amount), 0)
	);

	const totalTransferIn = $derived(
		financialStore.transactions
			.filter((t) => t.destination_account_id === data.id && t.transaction_type === 'TRANSFER' && t.status === 'COMPLETED')
			.reduce((sum, t) => sum + Number(t.amount), 0)
	);

	const totalTransferOut = $derived(
		financialStore.transactions
			.filter((t) => t.account_id === data.id && t.transaction_type === 'TRANSFER' && t.status === 'COMPLETED')
			.reduce((sum, t) => sum + Number(t.amount), 0)
	);
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full pb-24 lg:pb-10">
	<!-- Top Navigation Breadcrumb -->
	<div class="flex items-center justify-between">
		<a
			href="/accounts"
			class="inline-flex items-center gap-2 text-xs font-semibold text-slate-500 hover:text-[#007AFF] dark:text-slate-400 dark:hover:text-[#0A84FF] transition-colors"
		>
			<ArrowLeft class="w-4 h-4" />
			<span>Kembali ke Dompet & Rekening</span>
		</a>
	</div>

	{#if !account}
		<div class="p-8 rounded-2xl bg-white dark:bg-[#151926] border border-slate-200/80 dark:border-white/10 text-center space-y-3">
			<div class="w-12 h-12 rounded-xl bg-slate-100 dark:bg-white/5 flex items-center justify-center mx-auto text-slate-400">
				<Wallet class="w-6 h-6" />
			</div>
			<h2 class="text-base font-semibold text-slate-900 dark:text-white">Rekening Tidak Ditemukan</h2>
			<p class="text-xs text-slate-400 max-w-sm mx-auto">
				Rekening ini mungkin telah dihapus atau Anda tidak memiliki akses ke rekening ini.
			</p>
			<Button variant="primary" class="h-9 px-4 text-xs" onclick={() => goto('/accounts')}>
				Buka Daftar Rekening
			</Button>
		</div>
	{:else}
		<!-- Hero Detail Card -->
		<div class="p-5 sm:p-7 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/90 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/80 dark:border-white/10 shadow-sm relative overflow-hidden">
			<div class="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
				<!-- Left: Identity & Live Balance -->
				<div class="flex items-start sm:items-center gap-4 sm:gap-5 min-w-0">
					<div class="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl sm:rounded-3xl p-2 bg-slate-50 dark:bg-white/5 border border-slate-200/80 dark:border-white/10 flex items-center justify-center shrink-0 shadow-sm overflow-hidden">
						<img src={walletImage} alt={account.name} class="w-full h-full object-contain rounded-xl" />
					</div>
					<div class="min-w-0 space-y-1">
						<div class="flex items-center gap-2 flex-wrap">
							<h1 class="text-lg sm:text-2xl font-bold text-slate-900 dark:text-white tracking-tight truncate">
								{account.name}
							</h1>
							<span class="px-2.5 py-0.5 rounded-lg text-[10px] font-semibold bg-blue-500/10 text-[#007AFF] dark:text-[#0A84FF] uppercase tracking-wider">
								{account.type.replace('_', ' ')}
							</span>
							<span class="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-600 dark:text-emerald-400">
								<span class="w-2 h-2 rounded-full bg-emerald-500"></span>
								<span>Aktif</span>
							</span>
						</div>
						<p class="text-xs text-slate-500 dark:text-slate-400">
							{#if account.account_number}
								No. Rekening / ID: <span class="font-mono font-medium text-slate-700 dark:text-slate-300">{account.account_number}</span>
							{:else}
								Dompet Saldo Keuangan
							{/if}
						</p>
						<div class="pt-2">
							<span class="text-[11px] uppercase tracking-wider text-slate-400 font-semibold block">Total Saldo Saat Ini</span>
							<span class="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
								{formatRupiah(account.current_balance || account.balance || 0)}
							</span>
						</div>
					</div>
				</div>

				<!-- Right: Consolidated Action Buttons (Requested by user to keep cards clean) -->
				<div class="flex flex-wrap sm:flex-nowrap items-center gap-2.5 lg:self-center">
					<Button
						variant="outline"
						class="h-10 px-3.5 text-xs border-slate-200 dark:border-white/10 hover:border-[#007AFF]"
						onclick={() => (isTransferModalOpen = true)}
					>
						<ArrowLeftRight class="w-4 h-4 mr-1.5 text-[#007AFF]" />
						<span>Transfer Saldo</span>
					</Button>

					<Button
						variant="primary"
						class="h-10 px-4 text-xs"
						onclick={() => (isAddTxModalOpen = true)}
					>
						<Plus class="w-4 h-4 mr-1.5" />
						<span>Catat Transaksi</span>
					</Button>

					<Button
						variant="ghost"
						class="h-10 px-3 text-xs border border-slate-200/80 dark:border-white/10 hover:bg-slate-100 dark:hover:bg-white/5"
						onclick={openEdit}
						title="Ubah Nama, Gambar & Ciri Khas"
					>
						<ImageIcon class="w-4 h-4 mr-1.5 text-slate-500" />
						<span>Ubah Logo & Akun</span>
					</Button>

					<Button
						variant="ghost"
						class="h-10 px-3 text-xs border border-slate-200/80 dark:border-white/10 text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/20"
						onclick={() => (isDeleteModalOpen = true)}
						title="Hapus Rekening"
					>
						<Trash2 class="w-4 h-4" />
					</Button>
				</div>
			</div>

			<!-- Quick Financial Metrics Ribbon for this wallet -->
			<div class="mt-6 pt-5 border-t border-slate-100 dark:border-white/5 grid grid-cols-2 sm:grid-cols-4 gap-3">
				<div class="p-3 rounded-2xl bg-slate-50/70 dark:bg-white/[0.02] border border-slate-200/50 dark:border-white/[0.04]">
					<span class="text-[10px] text-slate-400 uppercase font-semibold block">Total Pemasukan</span>
					<span class="text-sm sm:text-base font-bold text-emerald-600 dark:text-emerald-400 mt-0.5 block truncate">
						+{formatRupiah(totalIncomeThisAccount)}
					</span>
				</div>

				<div class="p-3 rounded-2xl bg-slate-50/70 dark:bg-white/[0.02] border border-slate-200/50 dark:border-white/[0.04]">
					<span class="text-[10px] text-slate-400 uppercase font-semibold block">Total Pengeluaran</span>
					<span class="text-sm sm:text-base font-bold text-rose-600 dark:text-rose-400 mt-0.5 block truncate">
						-{formatRupiah(totalExpenseThisAccount)}
					</span>
				</div>

				<div class="p-3 rounded-2xl bg-slate-50/70 dark:bg-white/[0.02] border border-slate-200/50 dark:border-white/[0.04]">
					<span class="text-[10px] text-slate-400 uppercase font-semibold block">Transfer Masuk</span>
					<span class="text-sm sm:text-base font-bold text-[#007AFF] dark:text-[#0A84FF] mt-0.5 block truncate">
						+{formatRupiah(totalTransferIn)}
					</span>
				</div>

				<div class="p-3 rounded-2xl bg-slate-50/70 dark:bg-white/[0.02] border border-slate-200/50 dark:border-white/[0.04]">
					<span class="text-[10px] text-slate-400 uppercase font-semibold block">Transfer Keluar</span>
					<span class="text-sm sm:text-base font-bold text-amber-600 dark:text-amber-400 mt-0.5 block truncate">
						-{formatRupiah(totalTransferOut)}
					</span>
				</div>
			</div>
		</div>

		<!-- Transaction History Section Dedicated to this Account -->
		<div class="space-y-4">
			<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
				<div>
					<h2 class="text-base sm:text-lg font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
						<History class="w-5 h-5 text-[#007AFF]" />
						<span>Riwayat Mutasi Saldo</span>
					</h2>
					<p class="text-xs text-slate-500 dark:text-slate-400">
						Seluruh catatan transaksi dan mutasi yang terkait dengan rekening {account.name}
					</p>
				</div>

				<!-- Search and Filter -->
				<div class="flex items-center gap-2">
					<div class="relative w-full sm:w-56">
						<Search class="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
						<input
							type="text"
							bind:value={txSearchQuery}
							placeholder="Cari transaksi..."
							class="w-full h-8 pl-8 pr-3 rounded-lg border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:border-[#007AFF]"
						/>
					</div>

					<select
						bind:value={txTypeFilter}
						class="h-8 px-2 rounded-lg border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-700 dark:text-slate-300 focus:outline-none focus:border-[#007AFF]"
					>
						<option value="ALL">Semua Tipe</option>
						<option value="INCOME">Pemasukan</option>
						<option value="EXPENSE">Pengeluaran</option>
						<option value="TRANSFER">Transfer</option>
					</select>
				</div>
			</div>

			<!-- Transactions List / Table -->
			{#if accountTransactions.length === 0}
				<div class="p-8 rounded-2xl bg-white dark:bg-[#151926] border border-slate-200/80 dark:border-white/10 text-center space-y-2">
					<div class="w-10 h-10 rounded-xl bg-slate-100 dark:bg-white/5 flex items-center justify-center mx-auto text-slate-400">
						<Calendar class="w-5 h-5" />
					</div>
					<p class="text-xs font-semibold text-slate-700 dark:text-slate-300">Belum Ada Transaksi</p>
					<p class="text-[11px] text-slate-400 max-w-xs mx-auto">
						Transaksi pemasukan, pengeluaran, atau transfer yang menggunakan rekening ini akan muncul di sini.
					</p>
				</div>
			{:else}
				<div class="rounded-2xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-[#151926] overflow-hidden shadow-xs">
					<div class="overflow-x-auto">
						<table class="w-full text-left text-xs">
							<thead>
								<tr class="border-b border-slate-100 dark:border-white/5 bg-slate-50/50 dark:bg-white/[0.01] text-slate-400 text-[10px] uppercase tracking-wider font-semibold">
									<th class="py-3 px-4">Tanggal</th>
									<th class="py-3 px-4">Deskripsi / Catatan</th>
									<th class="py-3 px-4">Kategori / Tipe</th>
									<th class="py-3 px-4 text-right">Nominal</th>
									<th class="py-3 px-4 text-center">Aksi</th>
								</tr>
							</thead>
							<tbody class="divide-y divide-slate-100 dark:divide-white/5">
								{#each accountTransactions as tx (tx.id)}
									{@const isSource = tx.account_id === data.id}
									{@const isDest = tx.destination_account_id === data.id}
									{@const isTransferIn = tx.transaction_type === 'TRANSFER' && isDest}
									{@const isTransferOut = tx.transaction_type === 'TRANSFER' && isSource}
									{@const isIncome = tx.transaction_type === 'INCOME' || isTransferIn}

									<tr class="hover:bg-slate-50/60 dark:hover:bg-white/[0.02] transition-colors">
										<td class="py-3 px-4 text-slate-500 whitespace-nowrap">
											{formatDate(tx.transaction_date)}
										</td>
										<td class="py-3 px-4 font-medium text-slate-900 dark:text-white">
											<span class="block truncate max-w-xs">{tx.description}</span>
											{#if tx.transaction_type === 'TRANSFER'}
												<span class="text-[10px] text-slate-400 block mt-0.5">
													{isTransferIn ? 'Dari: ' + (tx.account_name || 'Rekening Asal') : 'Ke: ' + (tx.destination_account_name || 'Rekening Tujuan')}
												</span>
											{/if}
										</td>
										<td class="py-3 px-4 whitespace-nowrap">
											<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-semibold {isIncome ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' : 'bg-rose-500/10 text-rose-600 dark:text-rose-400'}">
												{#if isIncome}
													<ArrowDownLeft class="w-3 h-3" />
												{:else}
													<ArrowUpRight class="w-3 h-3" />
												{/if}
												<span>{tx.transaction_type}</span>
											</span>
											{#if tx.category_name}
												<span class="text-[11px] text-slate-500 dark:text-slate-400 ml-1.5">{tx.category_name}</span>
											{/if}
										</td>
										<td class="py-3 px-4 text-right font-semibold whitespace-nowrap {isIncome ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-900 dark:text-white'}">
											{isIncome ? '+' : '-'}{formatRupiah(tx.amount)}
										</td>
										<td class="py-3 px-4 text-center whitespace-nowrap">
											<button
												type="button"
												onclick={() => financialStore.deleteTransaction(tx.id)}
												class="p-1 rounded-md text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-colors"
												title="Hapus Transaksi"
											>
												<Trash2 class="w-3.5 h-3.5" />
											</button>
										</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				</div>
			{/if}
		</div>

		<!-- Modals -->
		<AddTransactionModal bind:open={isTransferModalOpen} />
		<AddTransactionModal bind:open={isAddTxModalOpen} />

		<!-- Edit Account Modal with Master Dompet Preset Picker -->
		<Modal
			bind:open={isEditModalOpen}
			title="Ubah Rekening & Ciri Khas Dompet"
			description="Perbarui informasi rekening, nama, atau logo ciri khas dompet"
		>
			<form onsubmit={(e) => { e.preventDefault(); handleSaveEdit(); }} class="space-y-4">
				<Input
					bind:value={editName}
					label="Nama Rekening / Dompet *"
					placeholder="Contoh: BCA Tabungan, Dompet Harian"
				/>

				<div>
					<label for="edit-account-type-select" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
						Tipe Akun *
					</label>
					<select
						id="edit-account-type-select"
						bind:value={editType}
						class="w-full h-10 px-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-[#007AFF]"
					>
						<option value="BANK">Rekening Bank</option>
						<option value="E_WALLET">Dompet Digital (E-Wallet)</option>
						<option value="CASH">Uang Tunai (Cash)</option>
						<option value="INVESTMENT">Rekening Investasi (RDN/Crypto)</option>
						<option value="OTHER">Lainnya / Khusus</option>
					</select>
				</div>

				<!-- Logo & Master Dompet Picker -->
				<div>
					<div class="flex items-center justify-between mb-2">
						<span class="block text-xs font-semibold text-slate-700 dark:text-slate-300">
							Pilih Logo & Ciri Khas Dompet
						</span>
						<a href="/wallet-master" class="text-[11px] font-semibold text-[#007AFF] hover:underline">
							+ Master Dompet
						</a>
					</div>
					<div class="grid grid-cols-4 sm:grid-cols-7 gap-2 p-2.5 rounded-2xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/[0.06] max-h-48 overflow-y-auto">
						{#each availablePresets as preset}
							<button
								type="button"
								onclick={() => (editIcon = preset.id)}
								class="p-1.5 rounded-xl border flex flex-col items-center justify-center gap-1 transition-all cursor-pointer {editIcon === preset.id
									? 'border-[#007AFF] bg-blue-50/50 dark:bg-blue-500/10 ring-2 ring-[#007AFF]/30 scale-105 shadow-sm'
									: 'border-transparent hover:border-slate-200 dark:hover:border-white/10 hover:bg-white dark:hover:bg-white/5'}"
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

				<div class="pt-3 flex items-center justify-end gap-2 border-t border-slate-100 dark:border-white/5">
					<Button variant="ghost" onclick={() => (isEditModalOpen = false)} class="text-xs">
						Batal
					</Button>
					<Button variant="primary" type="submit" disabled={isSavingEdit} class="text-xs">
						{isSavingEdit ? 'Menyimpan...' : 'Simpan Perubahan'}
					</Button>
				</div>
			</form>
		</Modal>

		<!-- Delete Account Modal -->
		<Modal
			bind:open={isDeleteModalOpen}
			title="Hapus Rekening / Dompet"
			description="Konfirmasi penghapusan rekening dan transaksi terkait"
		>
			<div class="space-y-4">
				<div class="flex items-start gap-3 p-3.5 rounded-2xl bg-rose-50 dark:bg-rose-950/20 border border-rose-200/80 dark:border-rose-900/40">
					<AlertTriangle class="w-5 h-5 text-rose-600 dark:text-rose-400 shrink-0 mt-0.5" />
					<div class="text-xs space-y-1.5 text-slate-700 dark:text-slate-300">
						<p>
							Apakah Anda yakin ingin menghapus rekening <strong class="text-slate-900 dark:text-white font-semibold">{account.name}</strong>?
						</p>
						<p class="text-slate-500 dark:text-slate-400 text-[11px] leading-relaxed">
							Semua riwayat mutasi transaksi di rekening ini akan otomatis disembunyikan menggunakan <strong>soft delete</strong> agar data tetap aman tersimpan di database.
						</p>
					</div>
				</div>

				<div class="pt-2 flex items-center justify-end gap-2">
					<Button variant="ghost" onclick={() => (isDeleteModalOpen = false)} class="text-xs">
						Batal
					</Button>
					<Button variant="danger" onclick={handleDelete} class="text-xs">
						Hapus Rekening
					</Button>
				</div>
			</div>
		</Modal>
	{/if}
</div>
