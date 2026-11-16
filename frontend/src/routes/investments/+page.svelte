<script lang="ts">
	import { financialStore } from '$lib/stores/financial.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import { formatRupiah, formatDate, formatDateTime, formatRelativeTime } from '$lib/utils/formatters';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Select from '$lib/components/ui/Select.svelte';
	import AmountInput from '$lib/components/ui/AmountInput.svelte';
	import EmptyState from '$lib/components/ui/EmptyState.svelte';
	import TradingViewPortfolioChart from '$lib/components/charts/TradingViewPortfolioChart.svelte';
	import type { AssetClass, Transaction } from '$lib/types';
	import {
		TrendingUp,
		TrendingDown,
		Plus,
		Coins,
		Sparkles,
		Building2,
		Landmark,
		PieChart,
		FileText,
		Briefcase,
		Layers,
		Search,
		Filter,
		Trash2,
		Pencil,
		Wallet,
		Calendar,
		ArrowDownLeft,
		ArrowUpRight
	} from 'lucide-svelte';

	let isAddModalOpen = $state(false);
	let activeViewTab = $state<'ASSETS' | 'CASHFLOW'>('ASSETS');
	let selectedFilter = $state<string>('ALL');
	let searchQuery = $state('');
	let isFilterOpen = $state(false);
	let selectedAccountId = $state(financialStore.accounts[0]?.id || '');
	let isSubmitting = $state(false);

	const selectedInvAccount = $derived(financialStore.accounts.find((a) => a.id === selectedAccountId));

	const accountOptions = $derived(
		financialStore.accounts.map((a) => ({
			value: a.id,
			label: `${a.name} (Saldo: ${formatRupiah(a.current_balance)})`,
			sublabel: a.type.replace('_', ' ')
		}))
	);

	// Form State for Add Investment Modal
	let assetClass = $state<AssetClass>('STOCK');
	let name = $state('');
	let investmentAmount = $state<number>(0);
	let formError = $state('');

	const namePlaceholder = $derived.by(() => {
		switch (assetClass) {
			case 'STOCK':
				return 'Contoh: BBRI, BBCA, TLKM';
			case 'CRYPTO':
				return 'Contoh: Bitcoin, Ethereum, Solana';
			case 'GOLD':
				return 'Contoh: Emas Antam, Emas UBS';
			case 'MUTUAL_FUND':
				return 'Contoh: Sucorinvest Money Market';
			case 'DEPOSIT':
				return 'Contoh: Deposito BCA 6 Bulan';
			case 'REAL_ESTATE':
				return 'Contoh: Tanah Kavling Sentul';
			default:
				return 'Contoh: BBRI, Bitcoin, Emas Antam';
		}
	});

	// Universal Asset Categories Config
	interface AssetCategoryConfig {
		label: string;
		shortLabel: string;
		defaultUnit: string;
		defaultMode: 'UNIT_PRICE' | 'LUMP_SUM';
		namePlaceholder: string;
		symbolPlaceholder: string;
		unitPlaceholder: string;
		unitOptions: string[];
		color: string;
		bgLight: string;
		icon: any;
	}

	const assetCategories: Record<AssetClass, AssetCategoryConfig> = {
		STOCK: {
			label: 'Saham (IHSG / Luar Negeri)',
			shortLabel: 'Saham',
			defaultUnit: 'lembar',
			defaultMode: 'UNIT_PRICE',
			namePlaceholder: 'Contoh: Bank Central Asia Tbk',
			symbolPlaceholder: 'BBCA',
			unitPlaceholder: '1.000',
			unitOptions: ['lembar', 'lot'],
			color: 'text-blue-600 dark:text-blue-400 border-blue-500/20 bg-blue-500/10',
			bgLight: 'bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400',
			icon: TrendingUp
		},
		CRYPTO: {
			label: 'Aset Kripto (BTC, ETH, Solana)',
			shortLabel: 'Kripto',
			defaultUnit: 'koin',
			defaultMode: 'UNIT_PRICE',
			namePlaceholder: 'Contoh: Bitcoin',
			symbolPlaceholder: 'BTC',
			unitPlaceholder: '0.05',
			unitOptions: ['koin', 'token', 'unit'],
			color: 'text-amber-600 dark:text-amber-400 border-amber-500/20 bg-amber-500/10',
			bgLight: 'bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400',
			icon: Coins
		},
		GOLD: {
			label: 'Emas & Logam Mulia',
			shortLabel: 'Emas',
			defaultUnit: 'gram',
			defaultMode: 'UNIT_PRICE',
			namePlaceholder: 'Contoh: Logam Mulia Antam CertiEye',
			symbolPlaceholder: 'ANTM',
			unitPlaceholder: '10',
			unitOptions: ['gram', 'batang', 'ons'],
			color: 'text-yellow-600 dark:text-yellow-400 border-yellow-500/20 bg-yellow-500/10',
			bgLight: 'bg-yellow-50 dark:bg-yellow-950/40 text-yellow-600 dark:text-yellow-400',
			icon: Sparkles
		},
		DEPOSIT: {
			label: 'Deposito & Kas Berjangka',
			shortLabel: 'Deposito',
			defaultUnit: 'bilyet',
			defaultMode: 'LUMP_SUM',
			namePlaceholder: 'Contoh: Deposito Berjangka BCA 6 Bulan',
			symbolPlaceholder: 'DEP-BCA',
			unitPlaceholder: '1',
			unitOptions: ['bilyet', 'rekening', 'paket'],
			color: 'text-cyan-600 dark:text-cyan-400 border-cyan-500/20 bg-cyan-500/10',
			bgLight: 'bg-cyan-50 dark:bg-cyan-950/40 text-cyan-600 dark:text-cyan-400',
			icon: Landmark
		},
		REAL_ESTATE: {
			label: 'Tanah & Properti',
			shortLabel: 'Tanah/Properti',
			defaultUnit: 'm²',
			defaultMode: 'LUMP_SUM',
			namePlaceholder: 'Contoh: Tanah Kavling Sentul Highland',
			symbolPlaceholder: 'TNH-BGR',
			unitPlaceholder: '200',
			unitOptions: ['m²', 'kavling', 'hektar', 'unit'],
			color: 'text-emerald-600 dark:text-emerald-400 border-emerald-500/20 bg-emerald-500/10',
			bgLight: 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400',
			icon: Building2
		},
		MUTUAL_FUND: {
			label: 'Reksadana',
			shortLabel: 'Reksadana',
			defaultUnit: 'unit',
			defaultMode: 'UNIT_PRICE',
			namePlaceholder: 'Contoh: Sucorinvest Sharia Money Market',
			symbolPlaceholder: 'SUCOR',
			unitPlaceholder: '10.000',
			unitOptions: ['unit', 'lembar'],
			color: 'text-violet-600 dark:text-violet-400 border-violet-500/20 bg-violet-500/10',
			bgLight: 'bg-violet-50 dark:bg-violet-950/40 text-violet-600 dark:text-violet-400',
			icon: PieChart
		},
		BOND: {
			label: 'Obligasi / SBN (Surat Berharga Negara)',
			shortLabel: 'Obligasi/SBN',
			defaultUnit: 'unit',
			defaultMode: 'LUMP_SUM',
			namePlaceholder: 'Contoh: Obligasi Negara Ritel ORI024',
			symbolPlaceholder: 'ORI024',
			unitPlaceholder: '1',
			unitOptions: ['unit', 'lembar'],
			color: 'text-indigo-600 dark:text-indigo-400 border-indigo-500/20 bg-indigo-500/10',
			bgLight: 'bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400',
			icon: FileText
		},
		COMMODITY: {
			label: 'Komoditas Fisik',
			shortLabel: 'Komoditas',
			defaultUnit: 'unit',
			defaultMode: 'UNIT_PRICE',
			namePlaceholder: 'Contoh: Minyak Kelapa Sawit (CPO)',
			symbolPlaceholder: 'CPO',
			unitPlaceholder: '10',
			unitOptions: ['unit', 'ton', 'barel'],
			color: 'text-orange-600 dark:text-orange-400 border-orange-500/20 bg-orange-500/10',
			bgLight: 'bg-orange-50 dark:bg-orange-950/40 text-orange-600 dark:text-orange-400',
			icon: Layers
		},
		OTHER: {
			label: 'Bisnis, P2P & Instrumen Lainnya',
			shortLabel: 'Bisnis/Lainnya',
			defaultUnit: 'unit',
			defaultMode: 'LUMP_SUM',
			namePlaceholder: 'Contoh: Kemitraan Franchise Kopi Kenangan',
			symbolPlaceholder: 'KOPI',
			unitPlaceholder: '1',
			unitOptions: ['unit', 'porsi', 'lot'],
			color: 'text-rose-600 dark:text-rose-400 border-rose-500/20 bg-rose-500/10',
			bgLight: 'bg-rose-50 dark:bg-rose-950/40 text-rose-600 dark:text-rose-400',
			icon: Briefcase
		}
	};

	const assetClassSelectOptions = Object.entries(assetCategories).map(([key, cfg]) => ({
		value: key,
		label: cfg.label
	}));

	// When user selects a new asset class
	function handleClassChange(newClass: AssetClass) {
		assetClass = newClass;
	}

	// Portfolio Calculations: Seamlessly accounts for Liquid Cash & Invested Assets
	const totalLiquidCash = $derived(financialStore.totalBalance);

	const totalInvestedAssets = $derived(
		financialStore.investments.reduce((acc, h) => acc + h.quantity * h.buy_price_avg, 0)
	);

	const totalMarketAssets = $derived(
		financialStore.investments.reduce((acc, h) => acc + h.quantity * h.current_price, 0)
	);

	// Total Portfolio Value (Net Worth: Cash in Rekening + Invested Assets)
	const totalPortfolioValue = $derived(totalLiquidCash + totalMarketAssets);

	// Total Capital (Liquid Cash + Cost of Bought Assets)
	const totalInvestedCapital = $derived(totalLiquidCash + totalInvestedAssets);

	// PnL from Investments
	const totalPnL = $derived(totalMarketAssets - totalInvestedAssets);

	const totalPnLPercent = $derived(
		totalInvestedAssets > 0 ? ((totalPnL / totalInvestedAssets) * 100).toFixed(2) : '0.00'
	);

	const totalAssetItemsCount = $derived(
		financialStore.investments.length + financialStore.accounts.length
	);

	// Filtered Holdings
	const filteredHoldings = $derived(
		financialStore.investments.filter((item) => {
			if (selectedFilter !== 'ALL' && item.asset_class !== selectedFilter) return false;
			if (searchQuery.trim()) {
				const q = searchQuery.toLowerCase();
				return item.name.toLowerCase().includes(q) || item.symbol.toLowerCase().includes(q);
			}
			return true;
		})
	);

	// Filtered Cash Accounts
	const filteredCashAccounts = $derived(
		financialStore.accounts.filter((acc) => {
			if (selectedFilter !== 'ALL' && selectedFilter !== 'CASH') return false;
			if (searchQuery.trim()) {
				const q = searchQuery.toLowerCase();
				return acc.name.toLowerCase().includes(q) || acc.type.toLowerCase().includes(q);
			}
			return true;
		})
	);

	interface EnrichedTransaction extends Transaction {
		runningBalance: number;
	}

	// Chronological transaction ledger with running balance
	const chronologicalTransactions = $derived.by(() => {
		const sorted = [...financialStore.transactions].sort((a, b) => {
			return new Date(a.transaction_date).getTime() - new Date(b.transaction_date).getTime();
		});

		const totalTxNet = sorted.reduce((sum, t) => {
			if (t.transaction_type === 'INCOME') return sum + Number(t.amount);
			if (t.transaction_type === 'EXPENSE') return sum - Number(t.amount);
			return sum;
		}, 0);

		let currentRunning = Math.max(0, totalPortfolioValue - totalTxNet);
		const enriched: EnrichedTransaction[] = sorted.map((t) => {
			if (t.transaction_type === 'INCOME') {
				currentRunning += Number(t.amount);
			} else if (t.transaction_type === 'EXPENSE') {
				currentRunning -= Number(t.amount);
			}
			return {
				...t,
				runningBalance: currentRunning
			};
		});

		if (searchQuery.trim()) {
			const q = searchQuery.toLowerCase();
			return enriched.filter(
				(t) =>
					t.description.toLowerCase().includes(q) ||
					(t.account_name && t.account_name.toLowerCase().includes(q))
			).reverse();
		}

		return enriched.reverse();
	});

	async function handleDeleteHolding(item: any) {
		await financialStore.deleteInvestment(item.id);
	}

	function openAddModal(preselectedClass?: AssetClass) {
		if (preselectedClass) {
			handleClassChange(preselectedClass);
		}
		name = '';
		investmentAmount = 0;
		formError = '';
		if (!selectedAccountId && financialStore.accounts[0]) {
			selectedAccountId = financialStore.accounts[0].id;
		}
		isAddModalOpen = true;
	}

	async function handleAddHolding() {
		formError = '';
		if (!name.trim()) {
			formError = 'Nama instrumen atau aset investasi wajib diisi (misal: BBRI, Bitcoin, Emas Antam).';
			return;
		}

		if (!selectedAccountId) {
			formError = 'Pilih dompet/rekening pembayaran untuk membeli aset ini.';
			return;
		}

		if (!investmentAmount || investmentAmount <= 0) {
			formError = 'Nominal investasi harus lebih dari Rp 0.';
			return;
		}

		const acc = financialStore.accounts.find((a) => a.id === selectedAccountId);
		if (acc && acc.current_balance < investmentAmount) {
			formError = `Saldo di ${acc.name} tidak cukup (${formatRupiah(acc.current_balance)}). Kurangi nominal atau pilih dompet lain.`;
			return;
		}

		// Auto-generate clean symbol if name is short or extract initials
		let finalSymbol = name.trim().toUpperCase();
		if (finalSymbol.length > 8) {
			const clean = name.trim().replace(/[^a-zA-Z0-9\s]/g, '');
			const words = clean.split(/\s+/).filter(Boolean);
			if (words.length >= 2) {
				finalSymbol = (words[0].slice(0, 3) + words[1].slice(0, 3)).toUpperCase();
			} else if (words.length === 1) {
				finalSymbol = words[0].slice(0, 6).toUpperCase();
			} else {
				finalSymbol = (assetCategories[assetClass]?.shortLabel || 'INV').slice(0, 4).toUpperCase();
			}
		}

		isSubmitting = true;
		try {
			const res = await financialStore.addInvestment({
				account_id: selectedAccountId,
				name: name.trim(),
				symbol: finalSymbol,
				asset_class: assetClass,
				quantity: 1,
				buy_price: investmentAmount,
				current_price: investmentAmount,
				notes: `Alokasi dana dari ${acc?.name || 'rekening'}`
			});

			if (res) {
				isAddModalOpen = false;
				name = '';
				investmentAmount = 0;
				formError = '';
			}
		} finally {
			isSubmitting = false;
		}
	}
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full pb-24 lg:pb-10">
	<!-- Page Header: Universal Multi-Asset Heading -->
	<div class="pb-2 border-b border-slate-200/80 dark:border-white/10">
		<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
			<TrendingUp class="w-6 h-6 text-[#007AFF] dark:text-[#0A84FF]" />
			<span>Portofolio Investasi</span>
		</h1>
		<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
			Pantau pertumbuhan modal saham, kripto, emas, deposito, tanah, dan aset lainnya dalam satu dasbor
		</p>
	</div>

	<!-- TradingView-Style Interactive Portfolio Chart -->
	<TradingViewPortfolioChart
		totalMarketValue={totalPortfolioValue}
		totalInvested={totalInvestedCapital}
		{totalPnL}
		{totalPnLPercent}
		assetCount={totalAssetItemsCount}
		liquidCash={totalLiquidCash}
		investedAssetsValue={totalMarketAssets}
		transactions={financialStore.transactions}
	/>

	<!-- Section View Tabs: Daftar Aset & Rekening vs Riwayat Keluar & Masuk Arus Kas -->
	<div class="space-y-4">
		<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
			<div class="flex items-center p-1 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200/60 dark:border-white/5">
				<button
					type="button"
					onclick={() => (activeViewTab = 'ASSETS')}
					class="py-2 px-3.5 rounded-xl text-xs font-semibold transition-all flex items-center gap-2 cursor-pointer {activeViewTab === 'ASSETS'
						? 'bg-[#007AFF] text-white shadow-sm'
						: 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
				>
					<Coins class="w-4 h-4" />
					<span>Daftar Aset & Rekening ({totalAssetItemsCount})</span>
				</button>
				<button
					type="button"
					onclick={() => (activeViewTab = 'CASHFLOW')}
					class="py-2 px-3.5 rounded-xl text-xs font-semibold transition-all flex items-center gap-2 cursor-pointer {activeViewTab === 'CASHFLOW'
						? 'bg-[#007AFF] text-white shadow-sm'
						: 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
				>
					<Calendar class="w-4 h-4" />
					<span>Riwayat Keluar & Masuk ({financialStore.transactions.length})</span>
				</button>
			</div>

			{#if activeViewTab === 'ASSETS'}
				<Button variant="primary" onclick={() => openAddModal()} class="h-9 px-3.5 text-xs self-start sm:self-auto">
					<Plus class="w-4 h-4 mr-1.5" />
					<span>Tambah Aset</span>
				</Button>
			{/if}
		</div>

		{#if activeViewTab === 'ASSETS'}
			<!-- Holdings Section: Unified Toolbar & Cards List -->
			<div class="space-y-4">
				<!-- Unified Action Toolbar: Search (Max 40%) & Quick Filters -->
				<div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
					<!-- Search Field (Max 40% Width) -->
					<div class="relative w-full sm:w-[40%] sm:max-w-[40%]">
						<Search class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
						<input
							type="text"
							bind:value={searchQuery}
							placeholder="Cari aset saham, kripto, emas..."
							class="w-full h-9 pl-9 pr-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:border-[#007AFF] transition-colors"
						/>
					</div>

					<!-- Category Filter Pills -->
					<div class="flex items-center gap-1.5 overflow-x-auto scrollbar-none">
						<button
							type="button"
							onclick={() => (selectedFilter = 'ALL')}
							class="h-9 px-3 rounded-xl text-xs font-semibold whitespace-nowrap transition-all cursor-pointer {selectedFilter === 'ALL'
								? 'bg-[#007AFF] text-white'
								: 'bg-white dark:bg-white/5 border border-slate-200/80 dark:border-white/10 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
						>
							Semua ({totalAssetItemsCount})
						</button>

						{#if financialStore.accounts.length > 0}
							<button
								type="button"
								onclick={() => (selectedFilter = 'CASH')}
								class="h-9 px-3 rounded-xl text-xs font-semibold whitespace-nowrap transition-all cursor-pointer {selectedFilter === 'CASH'
									? 'bg-[#007AFF] text-white'
									: 'bg-white dark:bg-white/5 border border-slate-200/80 dark:border-white/10 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
							>
								Kas & Rekening ({financialStore.accounts.length})
							</button>
						{/if}

						{#each (['STOCK', 'CRYPTO', 'GOLD', 'REAL_ESTATE', 'DEPOSIT'] as AssetClass[]) as catKey}
							{@const count = financialStore.investments.filter(i => i.asset_class === catKey).length}
							{#if count > 0}
								<button
									type="button"
									onclick={() => (selectedFilter = catKey)}
									class="h-9 px-3 rounded-xl text-xs font-semibold whitespace-nowrap transition-all cursor-pointer {selectedFilter === catKey
										? 'bg-[#007AFF] text-white'
										: 'bg-white dark:bg-white/5 border border-slate-200/80 dark:border-white/10 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
								>
									{assetCategories[catKey]?.shortLabel}
								</button>
							{/if}
						{/each}
					</div>
				</div>

				<!-- Holdings Card -->
				<div class="rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] overflow-hidden">
					{#if filteredCashAccounts.length > 0 || filteredHoldings.length > 0}
						<div class="divide-y divide-slate-100 dark:divide-white/5">
							<!-- 1. Liquid Cash in Bank/E-Wallets -->
							{#each filteredCashAccounts as acc}
								<div class="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-50/50 dark:hover:bg-white/[0.02] transition-colors">
									<!-- Asset Info & Badge -->
									<div class="flex items-center gap-3.5 min-w-0">
										<div class="w-11 h-11 rounded-2xl flex items-center justify-center shrink-0 bg-blue-50 dark:bg-blue-950/40 text-[#007AFF] dark:text-[#0A84FF] border border-blue-500/20">
											<Landmark class="w-5 h-5" />
										</div>
										<div class="min-w-0">
											<div class="flex flex-wrap items-center gap-2">
												<h4 class="text-sm font-semibold text-slate-900 dark:text-white">
													{acc.name}
												</h4>
												<span class="px-2 py-0.5 rounded text-[10px] font-semibold border text-blue-600 dark:text-blue-400 border-blue-500/20 bg-blue-500/10">
													Kas & Rekening
												</span>
											</div>
											<p class="text-xs text-slate-600 dark:text-slate-300 mt-0.5 truncate">
												<span class="font-medium text-slate-900 dark:text-white">{acc.type.replace('_', ' ')}</span>
												<span class="text-slate-400 ml-1">&bull; Saldo kas likuid siap dialokasikan ke investasi</span>
											</p>
										</div>
									</div>

									<!-- Value & PnL Metrics + Actions -->
									<div class="flex items-center justify-between sm:justify-end gap-5 shrink-0 pt-2 sm:pt-0 border-t sm:border-t-0 border-slate-100 dark:border-white/5">
										<div class="text-left sm:text-right">
											<span class="text-[11px] text-slate-400">Saldo Kas</span>
											<p class="text-sm font-semibold text-slate-900 dark:text-white">
												{formatRupiah(acc.current_balance)}
											</p>
										</div>

										<div class="text-right min-w-[110px]">
											<span class="text-[11px] text-slate-400">Status</span>
											<p class="text-sm font-semibold text-emerald-600 dark:text-emerald-400">
												Likuid 100%
											</p>
										</div>

										<a
											href="/accounts"
											class="p-1.5 rounded-xl text-slate-400 hover:text-[#007AFF] hover:bg-blue-50 dark:hover:bg-blue-950/30 transition-colors"
											title="Kelola Rekening"
										>
											<Pencil class="w-4 h-4" />
										</a>
									</div>
								</div>
							{/each}

							<!-- 2. Invested Assets (Stocks, Crypto, Gold, Real Estate, etc.) -->
							{#each filteredHoldings as item}
								{@const holdingValue = item.quantity * item.current_price}
								{@const holdingCost = item.quantity * item.buy_price_avg}
								{@const holdingPnL = holdingValue - holdingCost}
								{@const holdingPnLPercent = holdingCost > 0 ? ((holdingPnL / holdingCost) * 100).toFixed(1) : '0'}
								{@const cat = assetCategories[item.asset_class] || assetCategories.OTHER}
								{@const CatIcon = cat.icon}

								<div class="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-50/50 dark:hover:bg-white/[0.02] transition-colors">
									<!-- Asset Info & Badge -->
									<div class="flex items-center gap-3.5 min-w-0">
										<div class="w-11 h-11 rounded-2xl flex items-center justify-center shrink-0 {cat.bgLight} border border-current/15">
											<CatIcon class="w-5 h-5" />
										</div>
										<div class="min-w-0">
											<div class="flex flex-wrap items-center gap-2">
												<h4 class="text-sm font-semibold text-slate-900 dark:text-white">
													{item.symbol}
												</h4>
												<span class="px-2 py-0.5 rounded text-[10px] font-semibold border {cat.color}">
													{cat.shortLabel}
												</span>
											</div>
											<p class="text-xs text-slate-600 dark:text-slate-300 mt-0.5 truncate">
												<span class="font-medium text-slate-900 dark:text-white">{item.name}</span>
												{#if item.quantity > 1 || item.unit_label}
													<span class="text-slate-400 ml-1">&bull; {item.quantity.toLocaleString('id-ID')} {item.unit_label || 'unit'} @ {formatRupiah(item.buy_price_avg)}</span>
												{:else}
													<span class="text-slate-400 ml-1">&bull; Modal {formatRupiah(holdingCost)}</span>
												{/if}
											</p>
											{#if item.notes}
												<p class="text-[11px] text-slate-400 italic mt-0.5 truncate">
													{item.notes}
												</p>
											{/if}
										</div>
									</div>

									<!-- Value & PnL Metrics + Actions -->
									<div class="flex items-center justify-between sm:justify-end gap-5 shrink-0 pt-2 sm:pt-0 border-t sm:border-t-0 border-slate-100 dark:border-white/5">
										<div class="text-left sm:text-right">
											<span class="text-[11px] text-slate-400">Nilai Sekarang</span>
											<p class="text-sm font-semibold text-slate-900 dark:text-white">
												{formatRupiah(holdingValue)}
											</p>
										</div>

										<div class="text-right min-w-[110px]">
											<span class="text-[11px] text-slate-400">Keuntungan</span>
											<p class="text-sm font-semibold {holdingPnL >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}">
												{holdingPnL >= 0 ? '+' : ''}{formatRupiah(holdingPnL)}
												<span class="text-xs font-semibold">({holdingPnL >= 0 ? '+' : ''}{holdingPnLPercent}%)</span>
											</p>
										</div>

										<!-- Action Delete -->
										<button
											type="button"
											onclick={() => handleDeleteHolding(item)}
											class="p-1.5 rounded-xl text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-colors cursor-pointer"
											title="Hapus Aset Investasi"
										>
											<Trash2 class="w-4 h-4" />
										</button>
									</div>
								</div>
							{/each}
						</div>
					{:else}
						<EmptyState
							title="Belum ada aset dalam kategori ini"
							description="Tambahkan instrumen investasi seperti saham, kripto, emas, deposito, atau tanah."
						/>
					{/if}
				</div>
			</div>
		{:else}
			<!-- Riwayat Keluar & Masuk Portofolio (Arus Kas Nyata) -->
			<div class="space-y-4">
				<!-- Search Field -->
				<div class="relative w-full sm:w-[40%] sm:max-w-[40%]">
					<Search class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
					<input
						type="text"
						bind:value={searchQuery}
						placeholder="Cari transaksi keluar / masuk..."
						class="w-full h-9 pl-9 pr-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:border-[#007AFF] transition-colors"
					/>
				</div>

				<!-- Ledger Card -->
				<div class="rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] overflow-hidden">
					{#if chronologicalTransactions.length > 0}
						<div class="divide-y divide-slate-100 dark:divide-white/5">
							{#each chronologicalTransactions as tx}
								{@const isIncome = tx.transaction_type === 'INCOME'}
								{@const isExpense = tx.transaction_type === 'EXPENSE'}
								{@const isTransfer = tx.transaction_type === 'TRANSFER'}

								<div class="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-50/50 dark:hover:bg-white/[0.02] transition-colors">
									<!-- Left: Icon & Description -->
									<div class="flex items-center gap-3.5 min-w-0">
										<div class="w-11 h-11 rounded-2xl flex items-center justify-center shrink-0 {isIncome ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20' : isExpense ? 'bg-rose-50 dark:bg-rose-950/40 text-rose-600 dark:text-rose-400 border border-rose-500/20' : 'bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 border border-blue-500/20'}">
											{#if isIncome}
												<ArrowDownLeft class="w-5 h-5" />
											{:else if isExpense}
												<ArrowUpRight class="w-5 h-5" />
											{:else}
												<Landmark class="w-5 h-5" />
											{/if}
										</div>

										<div class="min-w-0">
											<div class="flex flex-wrap items-center gap-2">
												<h4 class="text-sm font-semibold text-slate-900 dark:text-white truncate">
													{tx.description || (isIncome ? 'Pemasukan' : 'Pengeluaran')}
												</h4>
												<span class="px-2 py-0.5 rounded text-[10px] font-semibold border {isIncome ? 'text-emerald-600 dark:text-emerald-400 border-emerald-500/20 bg-emerald-500/10' : isExpense ? 'text-rose-600 dark:text-rose-400 border-rose-500/20 bg-rose-500/10' : 'text-blue-600 dark:text-blue-400 border-blue-500/20 bg-blue-500/10'}">
													{isIncome ? 'Uang Masuk' : isExpense ? 'Uang Keluar' : 'Pindah Saldo'}
												</span>
											</div>

											<div class="flex flex-wrap items-center gap-2 text-xs text-slate-500 dark:text-slate-400 mt-0.5">
												<span class="flex items-center gap-1 font-medium text-slate-700 dark:text-slate-300">
													<Calendar class="w-3 h-3 text-[#007AFF]" />
													{formatDateTime(tx.transaction_date)}
												</span>
												<span>&bull;</span>
												<span>{formatRelativeTime(tx.transaction_date)}</span>
												{#if tx.account_name}
													<span>&bull;</span>
													<span class="text-slate-600 dark:text-slate-300 font-medium">{tx.account_name}</span>
												{/if}
											</div>
										</div>
									</div>

									<!-- Right: Mutation Amount & Running Balance -->
									<div class="flex items-center justify-between sm:justify-end gap-6 shrink-0 pt-2 sm:pt-0 border-t sm:border-t-0 border-slate-100 dark:border-white/5">
										<div class="text-left sm:text-right">
											<span class="text-[11px] text-slate-400">Nominal Mutasi</span>
											<p class="text-sm sm:text-base font-bold {isIncome ? 'text-emerald-600 dark:text-emerald-400' : isExpense ? 'text-rose-600 dark:text-rose-400' : 'text-blue-600 dark:text-blue-400'}">
												{isIncome ? '+' : isExpense ? '-' : ''}{formatRupiah(tx.amount)}
											</p>
										</div>

										<div class="text-right min-w-[120px]">
											<span class="text-[11px] text-slate-400">Saldo Portofolio</span>
											<p class="text-sm font-semibold text-slate-900 dark:text-white">
												{formatRupiah(tx.runningBalance)}
											</p>
										</div>
									</div>
								</div>
							{/each}
						</div>
					{:else}
						<EmptyState
							title="Belum ada riwayat mutasi"
							description="Setiap uang masuk atau keluar akan tercatat otomatis lengkap dengan tanggal dan jamnya di sini."
						/>
					{/if}
				</div>
			</div>
		{/if}
	</div>

	<!-- Add Multi-Asset Modal (Simplified Form) -->
	<Modal
		bind:open={isAddModalOpen}
		title="Pindahkan ke Instrumen Investasi"
		description="Catat aset investasi yang dibeli dari saldo dompet atau rekening Anda."
	>
		<form
			onsubmit={(e) => {
				e.preventDefault();
				handleAddHolding();
			}}
			class="space-y-4"
		>
			<!-- 1. Kategori Instrumen (Saham, Crypto, Emas, dll) -->
			<div class="flex flex-col gap-1.5 w-full">
				<label for="inv-class" class="text-xs font-semibold text-slate-700 dark:text-slate-300">
					1. Jenis / Kategori Instrumen
				</label>
				<select
					id="inv-class"
					bind:value={assetClass}
					class="w-full h-10 px-3 text-xs sm:text-sm font-medium rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-[#151E2E] focus:border-[#007AFF] focus:ring-1 focus:ring-[#007AFF]/20 text-slate-900 dark:text-white outline-none cursor-pointer transition-all"
				>
					{#each assetClassSelectOptions as opt}
						<option value={opt.value}>{opt.label}</option>
					{/each}
				</select>
			</div>

			<!-- 2. Nama Instrumen (BBRI, Bitcoin, dll) -->
			<div class="flex flex-col gap-1.5 w-full">
				<label for="inv-name" class="text-xs font-semibold text-slate-700 dark:text-slate-300">
					2. Nama Instrumen / Aset <span class="text-rose-500">*</span>
				</label>
				<input
					id="inv-name"
					type="text"
					bind:value={name}
					placeholder={namePlaceholder}
					class="w-full h-10 px-3 text-xs sm:text-sm rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-[#151E2E] focus:border-[#007AFF] focus:ring-1 focus:ring-[#007AFF]/20 text-slate-900 dark:text-white outline-none transition-all placeholder:text-slate-400"
				/>
			</div>

			<!-- 3. Pilih mau ambil dari dompet mana -->
			<Select
				bind:value={selectedAccountId}
				options={accountOptions}
				label="3. Ambil dari Dompet / Rekening Mana?"
				placeholder="Pilih rekening sumber dana..."
			/>

			<!-- 4. Nominal berapa -->
			<AmountInput
				bind:value={investmentAmount}
				label="4. Nominal Yang Mau Dipindahkan"
				referenceBalance={selectedInvAccount?.current_balance}
			/>

			{#if formError}
				<p class="text-xs font-medium text-rose-500 bg-rose-50 dark:bg-rose-950/30 p-2.5 rounded-xl border border-rose-200 dark:border-rose-900/50">
					{formError}
				</p>
			{/if}

			<button type="submit" class="hidden" aria-hidden="true"></button>
		</form>

		{#snippet footer()}
			<Button variant="ghost" onclick={() => (isAddModalOpen = false)}>Batal</Button>
			<Button variant="primary" onclick={handleAddHolding} disabled={isSubmitting}>
				{isSubmitting ? 'Memproses...' : 'Pindahkan ke Investasi'}
			</Button>
		{/snippet}
	</Modal>
</div>
