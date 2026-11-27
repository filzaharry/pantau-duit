<script lang="ts">
	import { authStore } from '$lib/stores/auth.svelte';
	import { financialStore } from '$lib/stores/financial.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import { formatRupiah } from '$lib/utils/formatters';
	import { WALLET_PRESETS, getWalletImage, hexToRgba } from '$lib/utils/walletIcons';
	import AccountCard from '$lib/components/financial/AccountCard.svelte';
	import AddTransactionModal from '$lib/components/financial/AddTransactionModal.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Table, { type TableColumn } from '$lib/components/ui/Table.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import AmountInput from '$lib/components/ui/AmountInput.svelte';
	import Select from '$lib/components/ui/Select.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import type { Account, AccountType, Transaction } from '$lib/types';
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
		Image as ImageIcon,
		ChevronRight,
		Coins,
		Layers,
		ArrowUpRight
	} from 'lucide-svelte';

	let viewMode = $state<'ACCOUNTS' | 'ASSET_TYPES'>('ACCOUNTS');
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

	// Asset Groups Aggregation (Per Tipe Tabungan / Aset)
	interface AssetGroup {
		key: string;
		name: string;
		code: string;
		category: AccountType;
		image: string;
		color: string;
		totalBalance: number;
		transactionCount: number;
		accounts: {
			id: string;
			name: string;
			balance: number;
			txCount: number;
			icon?: string;
			color?: string;
		}[];
		transactions: (Transaction & { account_name?: string })[];
	}

	let selectedAssetGroup = $state<AssetGroup | null>(null);
	let isAssetDetailOpen = $state(false);

	function openAssetDetail(group: AssetGroup) {
		selectedAssetGroup = group;
		isAssetDetailOpen = true;
	}

	function detectAssetType(text: string, account?: Account) {
		const lower = (text + ' ' + (account?.name || '') + ' ' + (account?.icon || '')).toLowerCase();

		if (
			lower.includes('bitcoin') ||
			lower.includes('btc') ||
			lower.includes('crypto') ||
			lower.includes('kripto') ||
			lower.includes('eth') ||
			lower.includes('ethereum')
		) {
			return {
				key: 'CRYPTO',
				name: 'Bitcoin & Kripto',
				code: 'crypto',
				category: 'INVESTMENT' as AccountType,
				image: getWalletImage('crypto', 'INVESTMENT'),
				color: '#D97706'
			};
		}

		if (
			lower.includes('dollar') ||
			lower.includes('dolar') ||
			lower.includes('usd') ||
			lower.includes('valas')
		) {
			return {
				key: 'USD',
				name: 'Dollar USD & Valas',
				code: 'pluangdollarusd',
				category: 'BANK' as AccountType,
				image: getWalletImage('pluangdollarusd', 'BANK'),
				color: '#10B981'
			};
		}

		if (
			lower.includes('emas') ||
			lower.includes('gold') ||
			lower.includes('antam') ||
			lower.includes('logam mulia')
		) {
			return {
				key: 'GOLD',
				name: 'Emas & Logam Mulia',
				code: 'pluangemas',
				category: 'INVESTMENT' as AccountType,
				image: getWalletImage('pluangemas', 'INVESTMENT'),
				color: '#EAB308'
			};
		}

		if (
			lower.includes('cash') ||
			lower.includes('tunai') ||
			lower.includes('uang kas') ||
			account?.type === 'CASH' ||
			account?.icon === 'cash'
		) {
			return {
				key: 'CASH',
				name: 'Uang Tunai (Cash)',
				code: 'cash',
				category: 'CASH' as AccountType,
				image: getWalletImage('cash', 'CASH'),
				color: '#059669'
			};
		}

		if (
			account?.type === 'E_WALLET' ||
			lower.includes('gopay') ||
			lower.includes('ovo') ||
			lower.includes('dana') ||
			lower.includes('shopeepay')
		) {
			const iconCode = account?.icon || 'wallet';
			return {
				key: 'E_WALLET',
				name: 'Dompet Digital (E-Wallet)',
				code: iconCode,
				category: 'E_WALLET' as AccountType,
				image: getWalletImage(iconCode, 'E_WALLET'),
				color: '#00AED6'
			};
		}

		const bankCode = account?.icon || 'bca';
		return {
			key: 'BANK',
			name: account?.name || 'Rekening Bank',
			code: bankCode,
			category: 'BANK' as AccountType,
			image: getWalletImage(bankCode, 'BANK'),
			color: account?.color || '#0060C4'
		};
	}

	const assetGroups = $derived.by(() => {
		const groupsMap = new Map<string, AssetGroup>();

		function getOrCreateGroup(info: ReturnType<typeof detectAssetType>): AssetGroup {
			if (!groupsMap.has(info.key)) {
				groupsMap.set(info.key, {
					key: info.key,
					name: info.name,
					code: info.code,
					category: info.category,
					image: info.image,
					color: info.color,
					totalBalance: 0,
					transactionCount: 0,
					accounts: [],
					transactions: []
				});
			}
			return groupsMap.get(info.key)!;
		}

		const accounts = financialStore.accounts;
		const allTransactions = financialStore.transactions;

		const accountMap = new Map<string, Account>();
		accounts.forEach((a) => accountMap.set(a.id, a));

		const accountProcessedTxSum = new Map<string, number>();

		for (const tx of allTransactions) {
			const acc = accountMap.get(tx.account_id);
			if (!acc) continue;

			const info = detectAssetType(tx.description || '', acc);
			const group = getOrCreateGroup(info);

			let delta = 0;
			if (tx.transaction_type === 'INCOME') {
				delta = Number(tx.amount);
			} else if (tx.transaction_type === 'EXPENSE') {
				delta = -Number(tx.amount);
			} else if (tx.transaction_type === 'TRANSFER') {
				delta = -Number(tx.amount);
			}

			group.totalBalance += delta;
			group.transactionCount += 1;
			group.transactions.push({
				...tx,
				account_name: acc.name
			});

			accountProcessedTxSum.set(acc.id, (accountProcessedTxSum.get(acc.id) || 0) + delta);

			let accEntry = group.accounts.find((a) => a.id === acc.id);
			if (!accEntry) {
				accEntry = {
					id: acc.id,
					name: acc.name,
					balance: 0,
					txCount: 0,
					icon: acc.icon,
					color: acc.color
				};
				group.accounts.push(accEntry);
			}
			accEntry.balance += delta;
			accEntry.txCount += 1;
		}

		for (const acc of accounts) {
			const currentBal = Number(acc.current_balance || acc.balance || 0);
			const txSum = accountProcessedTxSum.get(acc.id) || 0;
			const remaining = currentBal - txSum;

			if (Math.abs(remaining) > 0.01) {
				const info = detectAssetType(acc.name, acc);
				const group = getOrCreateGroup(info);
				group.totalBalance += remaining;

				let accEntry = group.accounts.find((a) => a.id === acc.id);
				if (!accEntry) {
					accEntry = {
						id: acc.id,
						name: acc.name,
						balance: 0,
						txCount: 0,
						icon: acc.icon,
						color: acc.color
					};
					group.accounts.push(accEntry);
				}
				accEntry.balance += remaining;
			}
		}

		return Array.from(groupsMap.values())
			.filter((g) => g.accounts.length > 0 || g.totalBalance !== 0 || g.transactions.length > 0)
			.sort((a, b) => b.totalBalance - a.totalBalance);
	});

	const filteredAssetGroups = $derived(
		assetGroups.filter((g) => {
			if (selectedType !== 'ALL' && g.category !== selectedType) return false;
			if (searchQuery.trim()) {
				const q = searchQuery.toLowerCase();
				return (
					g.name.toLowerCase().includes(q) ||
					g.accounts.some((a) => a.name.toLowerCase().includes(q))
				);
			}
			return true;
		})
	);

	const assetTxColumns: TableColumn<any>[] = [
		{ key: 'transaction_date', header: 'Tanggal', width: '120px', sortable: true },
		{ key: 'account_name', header: 'Dompet Asal', width: '160px', sortable: true },
		{ key: 'description', header: 'Keterangan', sortable: true },
		{ key: 'amount', header: 'Nominal', align: 'right', width: '140px', sortable: true }
	];

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
	<div class="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-3">
		<!-- Left: Search Field & Segmented Switcher -->
		<div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 flex-1">
			<!-- Search Field -->
			<div class="relative w-full sm:w-64">
				<Search class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
				<input
					type="text"
					bind:value={searchQuery}
					placeholder={viewMode === 'ACCOUNTS' ? "Cari rekening atau nama bank..." : "Cari tipe aset atau dompet..."}
					class="w-full h-9 pl-9 pr-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:border-[#007AFF] transition-colors"
				/>
			</div>

			<!-- View Mode Segmented Switcher -->
			<div class="inline-flex p-1 rounded-xl bg-slate-100 dark:bg-white/5 border border-slate-200/80 dark:border-white/10 shrink-0 self-start sm:self-auto">
				<button
					type="button"
					onclick={() => (viewMode = 'ACCOUNTS')}
					class="px-3 py-1.5 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 cursor-pointer {viewMode === 'ACCOUNTS' ? 'bg-white dark:bg-[#1E2333] text-[#007AFF] dark:text-[#0A84FF] shadow-xs' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
				>
					<Wallet class="w-3.5 h-3.5" />
					<span>Per Dompet</span>
					<span class="text-[10px] px-1.5 py-0.2 rounded-full {viewMode === 'ACCOUNTS' ? 'bg-blue-50 dark:bg-blue-500/20 text-[#007AFF]' : 'bg-slate-200/60 dark:bg-white/10 text-slate-500'}">
						{financialStore.accounts.length}
					</span>
				</button>
				<button
					type="button"
					onclick={() => (viewMode = 'ASSET_TYPES')}
					class="px-3 py-1.5 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 cursor-pointer {viewMode === 'ASSET_TYPES' ? 'bg-white dark:bg-[#1E2333] text-[#007AFF] dark:text-[#0A84FF] shadow-xs' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
				>
					<Banknote class="w-3.5 h-3.5" />
					<span>Per Tipe Tabungan / Aset</span>
					<span class="text-[10px] px-1.5 py-0.2 rounded-full {viewMode === 'ASSET_TYPES' ? 'bg-blue-50 dark:bg-blue-500/20 text-[#007AFF]' : 'bg-slate-200/60 dark:bg-white/10 text-slate-500'}">
						{assetGroups.length}
					</span>
				</button>
			</div>
		</div>

		<!-- Action Buttons: Filter, + Tambah Rekening / Kelola Master Dompet -->
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
							<span class="text-[11px] font-semibold text-slate-700 dark:text-slate-300 block mb-1.5">Tipe Rekening / Aset</span>
							<select
								bind:value={selectedType}
								class="w-full h-8 px-2.5 rounded-lg border border-slate-200/80 dark:border-white/10 bg-slate-50 dark:bg-white/5 text-xs text-slate-700 dark:text-slate-300 focus:outline-none focus:border-[#007AFF]"
							>
								<option value="ALL">Semua Tipe</option>
								<option value="BANK">Rekening Bank</option>
								<option value="E_WALLET">Dompet Digital</option>
								<option value="CASH">Uang Tunai</option>
								<option value="INVESTMENT">Investasi & Kripto</option>
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

			{#if viewMode === 'ACCOUNTS'}
				<Button variant="primary" class="h-9 px-3.5 text-xs" onclick={() => (isAddAccountOpen = true)}>
					<Plus class="w-4 h-4 mr-1.5" />
					<span>Tambah Rekening</span>
				</Button>
			{/if}
		</div>
	</div>

	<!-- Cards Grid -->
	{#if viewMode === 'ACCOUNTS'}
		<!-- Mode 1: Per Dompet / Rekening -->
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
	{:else}
		<!-- Mode 2: Per Tipe Tabungan / Aset (Identical layout to AccountCard, pure information) -->
		{#if filteredAssetGroups.length === 0}
			<div class="p-8 text-center rounded-2xl bg-white dark:bg-[#151926] border border-slate-200/80 dark:border-white/10">
				<p class="text-xs text-slate-500 dark:text-slate-400">Tidak ada tipe aset yang sesuai filter pencarian.</p>
			</div>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 sm:gap-4">
				{#each filteredAssetGroups as group (group.key)}
					<button
						type="button"
						onclick={() => openAssetDetail(group)}
						class="p-4 sm:p-5 rounded-2xl bg-white dark:bg-[#151926] border flex flex-col justify-between gap-3 min-w-[240px] relative overflow-hidden group hover:-translate-y-0.5 hover:shadow-lg transition-all text-left cursor-pointer"
						style="
							border-color: {hexToRgba(group.color, 0.28)};
							box-shadow: 0 4px 20px -4px {hexToRgba(group.color, 0.08)};
						"
					>
						<!-- Subtle Brand Tint Overlay with Opacity -->
						<div
							class="absolute inset-0 pointer-events-none transition-opacity duration-300"
							style="background: linear-gradient(135deg, {hexToRgba(group.color, 0.08)} 0%, {hexToRgba(group.color, 0.16)} 100%);"
						></div>

						<!-- Ambient soft radial light from top right -->
						<div
							class="absolute -top-12 -right-12 w-32 h-32 rounded-full pointer-events-none blur-2xl opacity-40 group-hover:opacity-70 transition-opacity"
							style="background: {group.color};"
						></div>

						<!-- Card Content (Identical structure to AccountCard) -->
						<div class="relative z-10 flex flex-col justify-between gap-3 h-full w-full">
							<!-- Card Top: Logo & Title -->
							<div class="flex items-center justify-between gap-3 min-w-0">
								<div class="flex items-center gap-3 min-w-0 flex-1">
									<div
										class="w-11 h-11 rounded-2xl flex items-center justify-center shrink-0 p-1 border shadow-xs relative overflow-hidden group-hover:scale-105 transition-transform"
										style="background-color: {hexToRgba(group.color, 0.12)}; border-color: {hexToRgba(group.color, 0.25)};"
									>
										<img
											src={group.image}
											alt={group.name}
											class="w-full h-full object-contain rounded-xl"
											loading="lazy"
										/>
									</div>
									<div class="min-w-0 flex-1">
										<h4
											class="text-sm font-semibold text-slate-900 dark:text-white tracking-tight leading-snug truncate group-hover:opacity-85 transition-opacity"
											title={group.name}
										>
											{group.name}
										</h4>
										<span class="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5 block truncate">
											{group.category.replace('_', ' ')}
										</span>
									</div>
								</div>

								<div
									class="w-7 h-7 rounded-xl flex items-center justify-center transition-colors shrink-0"
									style="background-color: {hexToRgba(group.color, 0.12)}; color: {group.color};"
								>
									<ChevronRight class="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
								</div>
							</div>

							<!-- Card Balance & Status -->
							<div
								class="pt-2.5 border-t flex items-center justify-between"
								style="border-color: {hexToRgba(group.color, 0.18)};"
							>
								<div class="flex items-center gap-1.5">
									<span class="w-2 h-2 rounded-full" style="background-color: {group.color};"></span>
									<span class="text-[10px] font-semibold text-slate-600 dark:text-slate-400">Aktif</span>
								</div>
								<span class="text-sm sm:text-base font-semibold text-slate-900 dark:text-white tracking-tight">
									{formatRupiah(group.totalBalance)}
								</span>
							</div>
						</div>
					</button>
				{/each}
			</div>
		{/if}
	{/if}

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

	<!-- Detail Modal for Selected Asset Group (Read-Only Information) -->
	<Modal
		bind:open={isAssetDetailOpen}
		title={`Informasi ${selectedAssetGroup?.name || 'Aset'}`}
		description="Tinjauan akumulasi saldo dan riwayat mutasi transaksi di seluruh rekening"
		maxWidth="3xl"
	>
		{#if selectedAssetGroup}
			<div class="space-y-5 max-h-[75vh] overflow-y-auto pr-1">
				<!-- Header Card in Modal with Opacity Tint -->
				<div
					class="p-4 sm:p-5 rounded-2xl border flex flex-col sm:flex-row sm:items-center justify-between gap-4 relative overflow-hidden"
					style="
						background: linear-gradient(135deg, {hexToRgba(selectedAssetGroup.color, 0.08)} 0%, {hexToRgba(selectedAssetGroup.color, 0.18)} 100%);
						border-color: {hexToRgba(selectedAssetGroup.color, 0.3)};
					"
				>
					<div class="flex items-center gap-3.5 relative z-10 min-w-0">
						<div
							class="w-13 h-13 rounded-2xl flex items-center justify-center p-2 bg-white dark:bg-[#1E2333] border shadow-xs shrink-0"
							style="border-color: {hexToRgba(selectedAssetGroup.color, 0.3)};"
						>
							<img src={selectedAssetGroup.image} alt={selectedAssetGroup.name} class="w-full h-full object-contain rounded-xl" />
						</div>
						<div class="min-w-0">
							<div class="flex items-center gap-2">
								<h3 class="text-base sm:text-lg font-bold text-slate-900 dark:text-white truncate">{selectedAssetGroup.name}</h3>
								<span class="px-2 py-0.5 rounded-md text-[10px] font-semibold bg-white/80 dark:bg-white/10 text-slate-700 dark:text-slate-300 border border-slate-200/60 dark:border-white/10">
									{selectedAssetGroup.category.replace('_', ' ')}
								</span>
							</div>
							<span class="text-xs text-slate-500 dark:text-slate-400 block mt-0.5">
								Total {selectedAssetGroup.transactionCount} catatan mutasi di {selectedAssetGroup.accounts.length} dompet
							</span>
						</div>
					</div>
					<div class="text-left sm:text-right shrink-0 relative z-10 pt-2 sm:pt-0 border-t sm:border-t-0 border-slate-200/40">
						<span class="text-[10px] uppercase font-semibold text-slate-500 dark:text-slate-400 block tracking-wider">Total Akumulasi Saldo</span>
						<span class="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
							{formatRupiah(selectedAssetGroup.totalBalance)}
						</span>
					</div>
				</div>

				<!-- History Table (Purely Informational) -->
				<div class="space-y-2">
					<h4 class="text-xs font-semibold text-slate-700 dark:text-slate-300 flex items-center justify-between">
						<span>Tabel Riwayat Mutasi Transaksi ({selectedAssetGroup.transactions.length})</span>
					</h4>
					{#if selectedAssetGroup.transactions.length === 0}
						<div class="p-6 rounded-xl bg-slate-50 dark:bg-white/5 border border-slate-200/60 dark:border-white/10 text-center">
							<p class="text-xs text-slate-400">Tidak ada riwayat mutasi untuk aset ini.</p>
						</div>
					{:else}
						<Table
							columns={[
								{ key: 'transaction_date', header: 'Tanggal', width: '120px', sortable: true },
								{ key: 'account_name', header: 'Dompet / Rekening', width: '180px', sortable: true },
								{ key: 'transaction_type', header: 'Tipe', width: '100px', sortable: true },
								{ key: 'description', header: 'Keterangan / Catatan', sortable: true },
								{ key: 'amount', header: 'Nominal', align: 'right', width: '140px', sortable: true }
							]}
							items={selectedAssetGroup.transactions}
							pageSize={10}
							pageSizeOptions={[10, 25, 50]}
							defaultSortKey="transaction_date"
							defaultSortDirection="desc"
						>
							{#snippet row(tx, index)}
								<tr class="hover:bg-slate-50/60 dark:hover:bg-white/[0.02] transition-colors">
									<td class="p-3.5 text-xs text-slate-600 dark:text-slate-300 whitespace-nowrap">
										{new Date(tx.transaction_date).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })}
									</td>
									<td class="p-3.5 text-xs font-medium text-slate-800 dark:text-slate-200 whitespace-nowrap">
										<span class="px-2 py-0.5 rounded-md bg-slate-100 dark:bg-white/10 text-[11px] font-medium">
											{tx.account_name}
										</span>
									</td>
									<td class="p-3.5 text-xs whitespace-nowrap">
										<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold {tx.transaction_type === 'INCOME' ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' : tx.transaction_type === 'EXPENSE' ? 'bg-rose-500/10 text-rose-600 dark:text-rose-400' : 'bg-blue-500/10 text-blue-600 dark:text-blue-400'}">
											{tx.transaction_type}
										</span>
									</td>
									<td class="p-3.5 text-xs text-slate-700 dark:text-slate-300">
										<span class="font-medium text-slate-900 dark:text-white block">{tx.description}</span>
										{#if tx.notes}
											<span class="text-[10px] text-slate-400 block truncate max-w-sm mt-0.5">{tx.notes}</span>
										{/if}
									</td>
									<td class="p-3.5 text-xs text-right font-bold whitespace-nowrap">
										<span class={tx.transaction_type === 'INCOME' ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}>
											{tx.transaction_type === 'INCOME' ? '+' : '-'}{formatRupiah(tx.amount)}
										</span>
									</td>
								</tr>
							{/snippet}
						</Table>
					{/if}
				</div>
			</div>
		{/if}

		{#snippet footer()}
			<Button variant="ghost" onclick={() => (isAssetDetailOpen = false)}>Tutup</Button>
		{/snippet}
	</Modal>
</div>
