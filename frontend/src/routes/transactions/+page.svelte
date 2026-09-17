<script lang="ts">
	import { authStore } from '$lib/stores/auth.svelte';
	import { financialStore } from '$lib/stores/financial.svelte';
	import { formatRupiah, formatDateTime } from '$lib/utils/formatters';
	import Table, { type TableColumn } from '$lib/components/ui/Table.svelte';
	import AddTransactionModal from '$lib/components/financial/AddTransactionModal.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import DatePicker from '$lib/components/ui/DatePicker.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import type { Transaction, TransactionType } from '$lib/types';
	import {
		Receipt,
		Search,
		Plus,
		ArrowDownLeft,
		ArrowUpRight,
		ArrowLeftRight,
		Filter,
		RotateCcw,
		Calendar,
		Wallet,
		Check,
		X,
		Bot,
		Globe,
		Building2,
		Eye,
		Shield,
		Trash2,
		Send,
		Crown,
		Sparkles,
		Server,
		Database,
		Cpu,
		Users,
		Utensils,
		Car,
		ShoppingBag,
		Film,
		Bolt,
		Banknote,
		Laptop
	} from 'lucide-svelte';


	let isAddModalOpen = $state(false);
	let isFilterModalOpen = $state(false);

	let searchQuery = $state('');
	let selectedType = $state<string>('ALL');
	let selectedAccount = $state<string>('ALL');
	let selectedCategory = $state<string>('ALL');
	let dateRangePreset = $state<'ALL' | 'THIS_MONTH' | 'LAST_7_DAYS' | 'LAST_30_DAYS' | 'CUSTOM'>('ALL');
	let startDate = $state('');
	let endDate = $state('');

	// Active filter count
	const activeFilterCount = $derived.by(() => {
		let count = 0;
		if (selectedType !== 'ALL') count++;
		if (selectedAccount !== 'ALL') count++;
		if (selectedCategory !== 'ALL') count++;
		if (dateRangePreset !== 'ALL') count++;
		return count;
	});

	function resetFilters() {
		selectedType = 'ALL';
		selectedAccount = 'ALL';
		selectedCategory = 'ALL';
		dateRangePreset = 'ALL';
		startDate = '';
		endDate = '';
	}

	const columns: TableColumn<Transaction>[] = [
		{ key: 'description', header: 'Deskripsi Transaksi', sortable: true },
		{ key: 'category_name', header: 'Kategori / Pos', sortable: true },
		{ key: 'account_name', header: 'Rekening', sortable: true },
		{ key: 'transaction_date', header: 'Waktu', sortable: true },
		{ key: 'amount', header: 'Nominal', align: 'right', sortable: true },
		{ key: 'actions', header: 'Aksi', align: 'right', sortable: false, width: '60px' }
	];

	function getCategoryIcon(iconName?: string) {
		switch (iconName) {
			case 'crown': return Crown;
			case 'sparkles': return Sparkles;
			case 'server': return Server;
			case 'globe': return Globe;
			case 'database': return Database;
			case 'shield': return Shield;
			case 'cpu': return Cpu;
			case 'users': return Users;
			case 'utensils': return Utensils;
			case 'car': return Car;
			case 'shopping-cart': return ShoppingBag;
			case 'film': return Film;
			case 'bolt': return Bolt;
			case 'money-bill-wave': return Banknote;
			case 'laptop-code': return Laptop;
			default: return Receipt;
		}
	}

	// Filtered transactions
	const filteredTransactions = $derived(
		financialStore.transactions.filter((tx) => {
			// Search filter
			if (searchQuery.trim()) {
				const q = searchQuery.toLowerCase();
				const descMatch = tx.description.toLowerCase().includes(q);
				const catMatch = tx.category?.name.toLowerCase().includes(q);
				const accMatch = tx.account?.name.toLowerCase().includes(q);
				if (!descMatch && !catMatch && !accMatch) return false;
			}

			// Type filter
			if (selectedType !== 'ALL' && tx.transaction_type !== selectedType) {
				return false;
			}

			// Account filter
			if (
				selectedAccount !== 'ALL' &&
				tx.account_id !== selectedAccount &&
				tx.destination_account_id !== selectedAccount
			) {
				return false;
			}

			// Category filter
			if (selectedCategory !== 'ALL' && tx.category_id !== selectedCategory) {
				return false;
			}

			// Date range filter
			if (dateRangePreset !== 'ALL') {
				const dateString = tx.transaction_date || tx.created_at;
				if (!dateString) return false;
				const txDate = new Date(dateString);
				if (dateRangePreset === 'THIS_MONTH') {
					const now = new Date();
					if (txDate.getMonth() !== now.getMonth() || txDate.getFullYear() !== now.getFullYear()) {
						return false;
					}
				} else if (dateRangePreset === 'LAST_7_DAYS') {
					const cutoff = new Date();
					cutoff.setDate(cutoff.getDate() - 7);
					if (txDate < cutoff) return false;
				} else if (dateRangePreset === 'LAST_30_DAYS') {
					const cutoff = new Date();
					cutoff.setDate(cutoff.getDate() - 30);
					if (txDate < cutoff) return false;
				} else if (dateRangePreset === 'CUSTOM') {
					if (startDate) {
						const start = new Date(startDate);
						start.setHours(0, 0, 0, 0);
						if (txDate < start) return false;
					}
					if (endDate) {
						const end = new Date(endDate);
						end.setHours(23, 59, 59, 999);
						if (txDate > end) return false;
					}
				}
			}

			return true;
		})
	);

	// Calculated totals for filtered transactions
	const filteredIncomeTransactions = $derived(
		filteredTransactions.filter((t) => t.transaction_type === 'INCOME')
	);
	const filteredExpenseTransactions = $derived(
		filteredTransactions.filter((t) => t.transaction_type === 'EXPENSE')
	);
	const filteredTransferTransactions = $derived(
		filteredTransactions.filter((t) => t.transaction_type === 'TRANSFER')
	);

	const filteredIncome = $derived(
		filteredIncomeTransactions.reduce((acc, t) => acc + t.amount, 0)
	);
	const filteredExpense = $derived(
		filteredExpenseTransactions.reduce((acc, t) => acc + t.amount, 0)
	);
	const filteredTransfer = $derived(
		filteredTransferTransactions.reduce((acc, t) => acc + t.amount, 0)
	);
</script>

<div class="space-y-4 sm:space-y-5 max-w-7xl mx-auto w-full pb-6 sm:pb-8">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
		<div>
			<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
				<Receipt class="w-6 h-6 text-[#007AFF] dark:text-[#0A84FF]" />
				<span>Riwayat Transaksi</span>
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
				{authStore.isSuperuser
					? 'Pemasukan langganan dan pengeluaran operasional sistem'
					: 'Kelola seluruh arus kas, pengeluaran, pemasukan, dan mutasi antar rekening'}
			</p>
		</div>

		<!-- Action Buttons -->
		<div class="flex items-center gap-2 w-full sm:w-auto">
			<Button variant="primary" class="w-full sm:w-auto justify-center" onclick={() => (isAddModalOpen = true)}>
				<Plus class="w-4 h-4" />
				<span>Catat Transaksi</span>
			</Button>
		</div>
	</div>

	<!-- 4-Column Segmented Ribbon Strip (2x2 on mobile, 4-col on desktop) -->
	<div class="p-3 sm:p-5 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
		<div class="grid grid-cols-2 lg:grid-cols-4 gap-2.5 sm:gap-4 lg:divide-x divide-slate-100 dark:divide-white/5">
			<!-- Col 1: Total Masuk -->
			<div class="flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-emerald-500/10 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
					<ArrowDownLeft class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Total Masuk</span>
					<span class="text-xs sm:text-base font-semibold text-emerald-600 dark:text-emerald-400 truncate block">
						{formatRupiah(filteredIncome, true)}
					</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">
						{filteredIncomeTransactions.length} Transaksi
					</span>
				</div>
			</div>

			<!-- Col 2: Total Keluar -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-rose-500/10 dark:bg-rose-500/20 text-rose-600 dark:text-rose-400 flex items-center justify-center shrink-0">
					<ArrowUpRight class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Total Keluar</span>
					<span class="text-xs sm:text-base font-semibold text-rose-600 dark:text-rose-400 truncate block">
						{formatRupiah(filteredExpense, true)}
					</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">
						{filteredExpenseTransactions.length} Transaksi
					</span>
				</div>
			</div>

			<!-- Col 3: Mutasi Transfer -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-blue-500/10 dark:bg-blue-500/20 text-[#007AFF] dark:text-[#0A84FF] flex items-center justify-center shrink-0">
					<ArrowLeftRight class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Mutasi Transfer</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">
						{formatRupiah(filteredTransfer, true)}
					</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">
						{filteredTransferTransactions.length} Transaksi
					</span>
				</div>
			</div>

			<!-- Col 4: Net Tabungan -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-blue-500/10 dark:bg-blue-500/20 text-[#007AFF] dark:text-[#0A84FF] flex items-center justify-center shrink-0">
					<Receipt class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">
						{authStore.isSuperuser ? 'Sisa Kas' : 'Net Tabungan'}
					</span>
					<span class="text-xs sm:text-base font-semibold text-[#007AFF] dark:text-[#0A84FF] truncate block">
						{formatRupiah(filteredIncome - filteredExpense, true)}
					</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">
						Arus Bersih
					</span>
				</div>
			</div>
		</div>
	</div>

	<!-- Minimalist Toolbar: Search Field & Button Filter Only (Unified h-9 height) -->
	<div class="flex items-center gap-2.5">
		<!-- Search Field -->
		<div class="relative flex-1">
			<Search class="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="Cari transaksi..."
				class="w-full h-9 pl-9 pr-8 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-[#131620] text-xs sm:text-sm text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:border-[#007AFF] focus:ring-1 focus:ring-[#007AFF] transition-all"
			/>
			{#if searchQuery}
				<button
					type="button"
					onclick={() => (searchQuery = '')}
					class="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1 rounded-full hover:bg-slate-100 dark:hover:bg-white/5 cursor-pointer"
					title="Hapus pencarian"
				>
					<X class="w-3 h-3" />
				</button>
			{/if}
		</div>

		<!-- Button Filter (h-9 unified) -->
		<button
			type="button"
			onclick={() => (isFilterModalOpen = true)}
			class="h-9 px-3.5 rounded-xl border {activeFilterCount > 0
				? 'border-[#007AFF]/60 bg-blue-500/10 text-[#007AFF] dark:text-[#0A84FF]'
				: 'border-slate-200/80 dark:border-white/10 bg-white dark:bg-[#131620] text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-white/5'} text-xs sm:text-sm font-medium flex items-center gap-1.5 transition-all cursor-pointer shrink-0"
		>
			<Filter class="w-3.5 h-3.5 text-[#007AFF] dark:text-[#0A84FF]" />
			<span>Filter</span>
			{#if activeFilterCount > 0}
				<span class="px-1.5 py-0.2 rounded-full bg-[#007AFF] text-white text-[10px] font-semibold leading-none">
					{activeFilterCount}
				</span>
			{/if}
		</button>
	</div>

	<!-- Active Filter Tags (Clean & dismissible) -->
	{#if activeFilterCount > 0}
		<div class="flex items-center gap-2 overflow-x-auto no-scrollbar py-0.5">
			<span class="text-[11px] font-semibold text-slate-400 shrink-0">Filter Aktif:</span>

			{#if selectedType !== 'ALL'}
				<span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-500/10 text-[#007AFF] dark:text-[#0A84FF] shrink-0">
					<span>Tipe: {selectedType === 'EXPENSE' ? 'Pengeluaran' : selectedType === 'INCOME' ? 'Pemasukan' : 'Transfer'}</span>
					<button type="button" onclick={() => (selectedType = 'ALL')} class="hover:opacity-75 cursor-pointer">
						<X class="w-3 h-3" />
					</button>
				</span>
			{/if}

			{#if selectedAccount !== 'ALL'}
				{@const acc = financialStore.accounts.find((a) => a.id === selectedAccount)}
				<span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-500/10 text-[#007AFF] dark:text-[#0A84FF] shrink-0">
					<span>Rekening: {acc?.name || selectedAccount}</span>
					<button type="button" onclick={() => (selectedAccount = 'ALL')} class="hover:opacity-75 cursor-pointer">
						<X class="w-3 h-3" />
					</button>
				</span>
			{/if}

			{#if selectedCategory !== 'ALL'}
				{@const cat = financialStore.categories.find((c) => c.id === selectedCategory)}
				<span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-500/10 text-[#007AFF] dark:text-[#0A84FF] shrink-0">
					<span>Kategori: {cat?.name || selectedCategory}</span>
					<button type="button" onclick={() => (selectedCategory = 'ALL')} class="hover:opacity-75 cursor-pointer">
						<X class="w-3 h-3" />
					</button>
				</span>
			{/if}

			{#if dateRangePreset !== 'ALL'}
				<span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-500/10 text-[#007AFF] dark:text-[#0A84FF] shrink-0">
					<span>
						Tanggal: {dateRangePreset === 'THIS_MONTH'
							? 'Bulan Ini'
							: dateRangePreset === 'LAST_7_DAYS'
								? '7 Hari Terakhir'
								: dateRangePreset === 'LAST_30_DAYS'
									? '30 Hari Terakhir'
									: `${startDate || '...'} s/d ${endDate || '...'}`}
					</span>
					<button type="button" onclick={() => (dateRangePreset = 'ALL')} class="hover:opacity-75 cursor-pointer">
						<X class="w-3 h-3" />
					</button>
				</span>
			{/if}

			<button
				type="button"
				onclick={resetFilters}
				class="text-[11px] font-semibold text-rose-500 hover:text-rose-600 hover:underline shrink-0 ml-1 cursor-pointer"
			>
				Reset Semua
			</button>
		</div>
	{/if}

	<!-- Global Reusable Table Component for Transactions -->
	<Table
		title="Tabel Transaksi & Arus Kas"
		subtitle="Daftar catatan mutasi pemasukan, pengeluaran, dan transfer terintegrasi"
		icon={Receipt}
		badge="{filteredTransactions.length} Transaksi"
		{columns}
		items={filteredTransactions}
		emptyMessage="Tidak ada transaksi yang cocok"
		emptyDescription="Coba ubah kata kunci pencarian atau sesuaikan filter di tombol Filter."
	>
		{#snippet row(transaction, index)}
			{@const isIncome = transaction.transaction_type === 'INCOME'}
			{@const isTransfer = transaction.transaction_type === 'TRANSFER'}
			{@const isExpense = transaction.transaction_type === 'EXPENSE'}
			{@const amountPrefix = isIncome ? '+ ' : isExpense ? '- ' : '⇄ '}
			{@const amountColor = isIncome ? 'text-emerald-600 dark:text-emerald-400' : isExpense ? 'text-slate-900 dark:text-white' : 'text-[#007AFF] dark:text-[#0A84FF]'}
			{@const CatIcon = getCategoryIcon(transaction.category_icon)}

			<tr class="hover:bg-slate-50/60 dark:hover:bg-white/[0.02] transition-colors group">
				<!-- Deskripsi Transaksi -->
				<td class="p-3.5">
					<div class="flex items-center gap-2.5 min-w-0">
						<div
							class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 text-white font-semibold"
							style="background-color: {isTransfer ? '#007AFF' : transaction.category_color || '#64748B'};"
						>
							{#if isTransfer}
								<ArrowLeftRight class="w-4 h-4 text-white" />
							{:else}
								<CatIcon class="w-4 h-4 text-white" />
							{/if}
						</div>
						<div class="min-w-0">
							<span class="font-semibold text-xs text-slate-900 dark:text-white block truncate">
								{transaction.description}
							</span>
							{#if transaction.source === 'TELEGRAM'}
								<span class="inline-flex items-center gap-0.5 px-1.5 py-0.2 mt-0.5 text-[9px] font-semibold rounded bg-[#007AFF]/10 text-[#007AFF] dark:text-[#0A84FF]">
									<Send class="w-2.5 h-2.5" />
									TG Bot
								</span>
							{/if}
						</div>
					</div>
				</td>

				<!-- Kategori / Pos -->
				<td class="p-3.5 whitespace-nowrap">
					{#if isTransfer}
						<span class="px-2 py-0.5 rounded-md text-[11px] font-semibold bg-blue-500/10 text-[#007AFF] dark:text-[#0A84FF] border border-blue-500/20">
							Mutasi Transfer
						</span>
					{:else}
						<span
							class="px-2 py-0.5 rounded-md text-[11px] font-semibold"
							style="background-color: {transaction.category_color ? transaction.category_color + '15' : '#64748B15'}; color: {transaction.category_color || '#64748B'};"
						>
							{transaction.category_name || 'Tanpa Kategori'}
						</span>
					{/if}
				</td>

				<!-- Rekening Sumber / Tujuan -->
				<td class="p-3.5 whitespace-nowrap text-xs text-slate-600 dark:text-slate-300">
					{#if isTransfer}
						<span class="font-medium text-slate-800 dark:text-slate-200">
							{transaction.account_name} → {transaction.destination_account_name}
						</span>
					{:else}
						<span>{transaction.account_name}</span>
					{/if}
				</td>

				<!-- Tanggal & Waktu -->
				<td class="p-3.5 whitespace-nowrap text-xs text-slate-500 dark:text-slate-400">
					{formatDateTime(transaction.transaction_date || transaction.created_at || '')}
				</td>

				<!-- Nominal -->
				<td class="p-3.5 whitespace-nowrap text-right font-semibold text-xs sm:text-sm {amountColor}">
					{amountPrefix}{formatRupiah(transaction.amount)}
				</td>

				<!-- Aksi -->
				<td class="p-3.5 whitespace-nowrap text-right">
					<button
						type="button"
						onclick={() => financialStore.deleteTransaction(transaction.id)}
						class="opacity-60 hover:opacity-100 p-1.5 rounded-lg text-slate-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-all cursor-pointer"
						aria-label="Hapus transaksi"
						title="Hapus transaksi"
					>
						<Trash2 class="w-3.5 h-3.5" />
					</button>
				</td>
			</tr>
		{/snippet}
	</Table>

	<!-- Add Transaction Modal -->
	<AddTransactionModal bind:open={isAddModalOpen} />

	<!-- Filter Modal (Accessible from Button Filter) -->
	<Modal
		bind:open={isFilterModalOpen}
		title="Filter Transaksi"
		description="Sesuaikan kriteria filter untuk menampilkan data transaksi spesifik"
	>
		<div class="space-y-5">
			<!-- 1. Rentang Waktu (Date Range) -->
			<div>
				<label class="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2 flex items-center gap-1.5">
					<Calendar class="w-3.5 h-3.5 text-[#007AFF]" />
					<span>Rentang Waktu</span>
				</label>
				<div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
					<button
						type="button"
						onclick={() => (dateRangePreset = 'ALL')}
						class="h-8 px-2.5 rounded-lg text-xs font-medium text-center border transition-all cursor-pointer {dateRangePreset === 'ALL'
							? 'bg-[#007AFF] text-white border-[#007AFF]'
							: 'bg-slate-50 dark:bg-white/5 text-slate-600 dark:text-slate-400 border-slate-200/80 dark:border-white/10 hover:border-slate-300'}"
					>
						Semua Waktu
					</button>
					<button
						type="button"
						onclick={() => (dateRangePreset = 'THIS_MONTH')}
						class="h-8 px-2.5 rounded-lg text-xs font-medium text-center border transition-all cursor-pointer {dateRangePreset === 'THIS_MONTH'
							? 'bg-[#007AFF] text-white border-[#007AFF]'
							: 'bg-slate-50 dark:bg-white/5 text-slate-600 dark:text-slate-400 border-slate-200/80 dark:border-white/10 hover:border-slate-300'}"
					>
						Bulan Ini
					</button>
					<button
						type="button"
						onclick={() => (dateRangePreset = 'LAST_7_DAYS')}
						class="h-8 px-2.5 rounded-lg text-xs font-medium text-center border transition-all cursor-pointer {dateRangePreset === 'LAST_7_DAYS'
							? 'bg-[#007AFF] text-white border-[#007AFF]'
							: 'bg-slate-50 dark:bg-white/5 text-slate-600 dark:text-slate-400 border-slate-200/80 dark:border-white/10 hover:border-slate-300'}"
					>
						7 Hari Terakhir
					</button>
					<button
						type="button"
						onclick={() => (dateRangePreset = 'LAST_30_DAYS')}
						class="h-8 px-2.5 rounded-lg text-xs font-medium text-center border transition-all cursor-pointer {dateRangePreset === 'LAST_30_DAYS'
							? 'bg-[#007AFF] text-white border-[#007AFF]'
							: 'bg-slate-50 dark:bg-white/5 text-slate-600 dark:text-slate-400 border-slate-200/80 dark:border-white/10 hover:border-slate-300'}"
					>
						30 Hari Terakhir
					</button>
					<button
						type="button"
						onclick={() => (dateRangePreset = 'CUSTOM')}
						class="col-span-2 sm:col-span-2 h-8 px-2.5 rounded-lg text-xs font-medium text-center border transition-all cursor-pointer {dateRangePreset === 'CUSTOM'
							? 'bg-[#007AFF] text-white border-[#007AFF]'
							: 'bg-slate-50 dark:bg-white/5 text-slate-600 dark:text-slate-400 border-slate-200/80 dark:border-white/10 hover:border-slate-300'}"
					>
						Pilih Tanggal Kustom
					</button>
				</div>

				{#if dateRangePreset === 'CUSTOM'}
					<div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3 pt-3 border-t border-slate-100 dark:border-white/5">
						<DatePicker label="Dari Tanggal" bind:value={startDate} />
						<DatePicker label="Sampai Tanggal" bind:value={endDate} />
					</div>
				{/if}
			</div>

			<!-- 2. Status / Tipe Transaksi -->
			<div>
				<label class="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2 flex items-center gap-1.5">
					<ArrowLeftRight class="w-3.5 h-3.5 text-[#007AFF]" />
					<span>Tipe / Status Transaksi</span>
				</label>
				<div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
					<button
						type="button"
						onclick={() => (selectedType = 'ALL')}
						class="h-8 px-2.5 rounded-lg text-xs font-medium border transition-all cursor-pointer {selectedType === 'ALL'
							? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900 border-slate-900 dark:border-white'
							: 'bg-slate-50 dark:bg-white/5 text-slate-600 dark:text-slate-400 border-slate-200/80 dark:border-white/10'}"
					>
						Semua ({financialStore.transactions.length})
					</button>
					<button
						type="button"
						onclick={() => (selectedType = 'EXPENSE')}
						class="h-8 px-2.5 rounded-lg text-xs font-medium border transition-all flex items-center justify-center gap-1.5 cursor-pointer {selectedType === 'EXPENSE'
							? 'bg-rose-500 text-white border-rose-500'
							: 'bg-slate-50 dark:bg-white/5 text-slate-600 dark:text-slate-400 border-slate-200/80 dark:border-white/10 hover:text-rose-500'}"
					>
						<ArrowUpRight class="w-3.5 h-3.5" />
						<span>Pengeluaran</span>
					</button>
					<button
						type="button"
						onclick={() => (selectedType = 'INCOME')}
						class="h-8 px-2.5 rounded-lg text-xs font-medium border transition-all flex items-center justify-center gap-1.5 cursor-pointer {selectedType === 'INCOME'
							? 'bg-emerald-500 text-white border-emerald-500'
							: 'bg-slate-50 dark:bg-white/5 text-slate-600 dark:text-slate-400 border-slate-200/80 dark:border-white/10 hover:text-emerald-500'}"
					>
						<ArrowDownLeft class="w-3.5 h-3.5" />
						<span>Pemasukan</span>
					</button>
					<button
						type="button"
						onclick={() => (selectedType = 'TRANSFER')}
						class="h-8 px-2.5 rounded-lg text-xs font-medium border transition-all flex items-center justify-center gap-1.5 cursor-pointer {selectedType === 'TRANSFER'
							? 'bg-[#007AFF] text-white border-[#007AFF]'
							: 'bg-slate-50 dark:bg-white/5 text-slate-600 dark:text-slate-400 border-slate-200/80 dark:border-white/10 hover:text-[#007AFF]'}"
					>
						<ArrowLeftRight class="w-3.5 h-3.5" />
						<span>Transfer</span>
					</button>
				</div>
			</div>

			<!-- 3. Rekening & Kategori Dropdowns -->
			<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
				<!-- Rekening -->
				<div>
					<label for="filter-account-select" class="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 block">
						Rekening
					</label>
					<select
						id="filter-account-select"
						bind:value={selectedAccount}
						class="w-full h-9 px-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-slate-50 dark:bg-[#151E2E] text-xs font-medium text-slate-700 dark:text-slate-200 focus:outline-none focus:border-[#007AFF]"
					>
						<option value="ALL">Semua Rekening</option>
						{#each financialStore.accounts as acc}
							<option value={acc.id}>{acc.name} ({acc.type.replace('_', ' ')})</option>
						{/each}
					</select>
				</div>

				<!-- Kategori -->
				<div>
					<label for="filter-category-select" class="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 block">
						Kategori
					</label>
					<select
						id="filter-category-select"
						bind:value={selectedCategory}
						class="w-full h-9 px-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-slate-50 dark:bg-[#151E2E] text-xs font-medium text-slate-700 dark:text-slate-200 focus:outline-none focus:border-[#007AFF]"
					>
						<option value="ALL">Semua Kategori</option>
						{#each financialStore.categories as cat}
							<option value={cat.id}>{cat.name}</option>
						{/each}
					</select>
				</div>
			</div>

			<!-- Filter Action Buttons -->
			<div class="flex items-center justify-between pt-3 border-t border-slate-100 dark:border-white/5">
				<button
					type="button"
					onclick={resetFilters}
					class="h-8 px-2.5 rounded-lg text-xs font-medium text-rose-500 hover:text-rose-600 flex items-center gap-1.5 cursor-pointer hover:bg-rose-500/10 transition-colors"
				>
					<RotateCcw class="w-3.5 h-3.5" />
					<span>Reset Filter</span>
				</button>

				<Button variant="primary" onclick={() => (isFilterModalOpen = false)}>
					<Check class="w-4 h-4" />
					<span>Terapkan Filter ({filteredTransactions.length})</span>
				</Button>
			</div>
		</div>
	</Modal>
</div>

