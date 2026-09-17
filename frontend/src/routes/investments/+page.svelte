<script lang="ts">
	import { financialStore } from '$lib/stores/financial.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import { formatRupiah } from '$lib/utils/formatters';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import EmptyState from '$lib/components/ui/EmptyState.svelte';
	import TradingViewPortfolioChart from '$lib/components/charts/TradingViewPortfolioChart.svelte';
	import type { AssetClass } from '$lib/types';
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
		Layers
	} from 'lucide-svelte';

	let isAddModalOpen = $state(false);
	let selectedFilter = $state<string>('ALL');

	// Form State
	let assetClass = $state<AssetClass>('STOCK');
	let name = $state('');
	let symbol = $state('');
	let calculationMode = $state<'UNIT_PRICE' | 'LUMP_SUM'>('UNIT_PRICE');
	let unitLabel = $state('lembar');

	// Unit Price inputs
	let quantity = $state<number>(1000);
	let buyPrice = $state<number>(4800);
	let currentPrice = $state<number>(5200);

	// Lump Sum inputs (for Real Estate, Deposits, Businesses, etc.)
	let totalCostInput = $state<number>(50000000);
	let totalCurrentValInput = $state<number>(55000000);
	let customNotes = $state('');

	let formError = $state('');

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

	// When user selects a new asset class, intelligently adapt defaults
	function handleClassChange(newClass: AssetClass) {
		assetClass = newClass;
		const cfg = assetCategories[newClass];
		if (cfg) {
			unitLabel = cfg.defaultUnit;
			calculationMode = cfg.defaultMode;
		}
	}

	// Dynamic config for current selection
	const currentMeta = $derived(assetCategories[assetClass] || assetCategories.STOCK);

	// Portfolio Calculations
	const totalInvested = $derived(
		financialStore.investments.reduce((acc, h) => acc + h.quantity * h.buy_price_avg, 0)
	);

	const totalMarketValue = $derived(
		financialStore.investments.reduce((acc, h) => acc + h.quantity * h.current_price, 0)
	);

	const totalPnL = $derived(totalMarketValue - totalInvested);

	const totalPnLPercent = $derived(
		totalInvested > 0 ? ((totalPnL / totalInvested) * 100).toFixed(2) : '0.00'
	);

	// Filtered Holdings
	const filteredHoldings = $derived(
		selectedFilter === 'ALL'
			? financialStore.investments
			: financialStore.investments.filter((item) => item.asset_class === selectedFilter)
	);

	// Simulation for Add Modal
	const simTotalCost = $derived.by(() => {
		if (calculationMode === 'LUMP_SUM') {
			return totalCostInput || 0;
		}
		return (quantity || 0) * (buyPrice || 0);
	});

	const simCurrentVal = $derived.by(() => {
		if (calculationMode === 'LUMP_SUM') {
			return totalCurrentValInput || 0;
		}
		return (quantity || 0) * (currentPrice || 0);
	});

	const simPnL = $derived(simCurrentVal - simTotalCost);
	const simPnLPercent = $derived(
		simTotalCost > 0 ? ((simPnL / simTotalCost) * 100).toFixed(2) : '0.00'
	);

	function openAddModal(preselectedClass?: AssetClass) {
		if (preselectedClass) {
			handleClassChange(preselectedClass);
		}
		name = '';
		symbol = '';
		customNotes = '';
		formError = '';
		isAddModalOpen = true;
	}

	function handleAddHolding() {
		formError = '';
		if (!name.trim()) {
			formError = 'Nama instrumen investasi wajib diisi.';
			return;
		}

		if (simTotalCost <= 0) {
			formError = 'Modal awal investasi harus lebih dari 0.';
			return;
		}

		// Auto-generate clean symbol if empty
		let finalSymbol = symbol.trim().toUpperCase();
		if (!finalSymbol) {
			const clean = name.trim().replace(/[^a-zA-Z0-9\s]/g, '');
			const words = clean.split(/\s+/).filter(Boolean);
			if (words.length >= 2) {
				finalSymbol = (words[0].slice(0, 2) + words[1].slice(0, 2)).toUpperCase();
			} else if (words.length === 1) {
				finalSymbol = words[0].slice(0, 4).toUpperCase();
			} else {
				finalSymbol = currentMeta.shortLabel.slice(0, 3).toUpperCase();
			}
		}

		let finalQty = 1;
		let finalBuyPrice = 0;
		let finalCurrentPrice = 0;

		if (calculationMode === 'LUMP_SUM') {
			finalQty = quantity > 0 ? quantity : 1;
			finalBuyPrice = totalCostInput / finalQty;
			finalCurrentPrice = totalCurrentValInput / finalQty;
		} else {
			finalQty = quantity > 0 ? quantity : 1;
			finalBuyPrice = buyPrice || 0;
			finalCurrentPrice = currentPrice || 0;
		}

		financialStore.investments.push({
			id: `inv-${Date.now()}`,
			tenant_id: 'tenant-demo-uuid-001',
			symbol: finalSymbol,
			name: name.trim(),
			asset_class: assetClass,
			quantity: finalQty,
			buy_price_avg: finalBuyPrice,
			current_price: finalCurrentPrice,
			unit_label: unitLabel.trim() || undefined,
			notes: customNotes.trim() || undefined,
			currency: 'IDR',
			updated_at: new Date().toISOString()
		});

		notificationStore.toast(`Aset ${name.trim()} (${finalSymbol}) berhasil ditambahkan!`, 'success');
		isAddModalOpen = false;
	}
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full pb-24 lg:pb-10">
	<!-- Page Header: Universal Multi-Asset Heading -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
		<div>
			<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
				<TrendingUp class="w-6 h-6 text-[#007AFF] dark:text-[#0A84FF]" />
				<span>Portofolio Investasi</span>
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
				Pantau pertumbuhan modal saham, kripto, emas, deposito, tanah, dan aset lainnya dalam satu dasbor
			</p>
		</div>

		<Button variant="primary" onclick={() => openAddModal()}>
			<Plus class="w-4 h-4" />
			<span>Tambah Aset</span>
		</Button>
	</div>

	<!-- TradingView-Style Interactive Portfolio Chart -->
	<TradingViewPortfolioChart
		{totalMarketValue}
		{totalInvested}
		{totalPnL}
		{totalPnLPercent}
		assetCount={financialStore.investments.length}
	/>

	<!-- Holdings Section: Filter Pills & Cards List -->
	<div class="space-y-3">
		<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
			<h3 class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
				Daftar Aset Investasi ({filteredHoldings.length})
			</h3>

			<!-- Quick Category Filter Pills -->
			<div class="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0 scrollbar-none">
				<button
					type="button"
					onclick={() => (selectedFilter = 'ALL')}
					class="px-2.5 py-1 rounded-xl text-xs font-semibold whitespace-nowrap transition-all cursor-pointer {selectedFilter === 'ALL'
						? 'bg-[#007AFF] text-white'
						: 'bg-slate-100 dark:bg-white/5 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
				>
					Semua ({financialStore.investments.length})
				</button>
				{#each (['STOCK', 'CRYPTO', 'GOLD', 'REAL_ESTATE', 'DEPOSIT'] as AssetClass[]) as catKey}
					{@const count = financialStore.investments.filter(i => i.asset_class === catKey).length}
					{#if count > 0}
						<button
							type="button"
							onclick={() => (selectedFilter = catKey)}
							class="px-2.5 py-1 rounded-xl text-xs font-semibold whitespace-nowrap transition-all cursor-pointer {selectedFilter === catKey
								? 'bg-[#007AFF] text-white'
								: 'bg-slate-100 dark:bg-white/5 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
						>
							{assetCategories[catKey]?.shortLabel} ({count})
						</button>
					{/if}
				{/each}
			</div>
		</div>

		<!-- Holdings Card -->
		<div class="rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] overflow-hidden">
			{#if filteredHoldings.length > 0}
				<div class="divide-y divide-slate-100 dark:divide-white/5">
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

							<!-- Value & PnL Metrics -->
							<div class="flex items-center justify-between sm:justify-end gap-6 shrink-0 pt-2 sm:pt-0 border-t sm:border-t-0 border-slate-100 dark:border-white/5">
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

	<!-- Add Multi-Asset Modal (Universal Form) -->
	<Modal
		bind:open={isAddModalOpen}
		title="Tambah Aset Portofolio"
		description="Catat instrumen investasi: saham, kripto, emas, deposito, tanah & properti, hingga bisnis."
	>
		<div class="space-y-4">
			<!-- Row 1: Instrumen & Kode -->
			<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
				<!-- Asset Class Selection -->
				<div class="flex flex-col gap-1.5 w-full">
					<label for="inv-class" class="text-xs font-medium text-slate-600 dark:text-slate-300">
						Kategori Instrumen Investasi
					</label>
					<select
						id="inv-class"
						value={assetClass}
						onchange={(e) => handleClassChange((e.target as HTMLSelectElement).value as AssetClass)}
						class="w-full h-9 px-3 text-xs sm:text-sm font-medium rounded-xl border border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-[#151E2E]/80 focus:border-[#007AFF] focus:ring-1 focus:ring-[#007AFF]/15 text-slate-900 dark:text-white outline-none cursor-pointer transition-all"
					>
						{#each assetClassSelectOptions as opt}
							<option value={opt.value}>{opt.label}</option>
						{/each}
					</select>
				</div>

				<!-- Ticker / Code (Optional) -->
				<div class="flex flex-col gap-1.5 w-full">
					<label for="inv-symbol" class="text-xs font-medium text-slate-600 dark:text-slate-300 flex items-center justify-between">
						<span>Kode / Ticker</span>
						<span class="text-[10px] text-slate-400 font-normal">Opsional</span>
					</label>
					<input
						id="inv-symbol"
						type="text"
						bind:value={symbol}
						oninput={(e) => {
							symbol = (e.target as HTMLInputElement).value.toUpperCase();
						}}
						placeholder={`Contoh: ${currentMeta.symbolPlaceholder}`}
						class="w-full h-9 px-3 text-xs sm:text-sm font-semibold uppercase rounded-xl border border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-[#151E2E]/80 focus:border-[#007AFF] focus:ring-1 focus:ring-[#007AFF]/15 text-slate-900 dark:text-white outline-none transition-all"
					/>
				</div>
			</div>

			<!-- Row 2: Nama Aset / Properti Lengkap (Wajib) -->
			<div class="flex flex-col gap-1.5 w-full">
				<label for="inv-name" class="text-xs font-medium text-slate-600 dark:text-slate-300">
					Nama Aset / Properti / Instrumen <span class="text-rose-500">*</span>
				</label>
				<input
					id="inv-name"
					type="text"
					bind:value={name}
					placeholder={currentMeta.namePlaceholder}
					class="w-full h-9 px-3 text-xs sm:text-sm rounded-xl border border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-[#151E2E]/80 focus:border-[#007AFF] focus:ring-1 focus:ring-[#007AFF]/15 text-slate-900 dark:text-white outline-none transition-all"
				/>
			</div>

			<!-- Calculation Mode Switcher: Satuan Unit vs Total Nilai (Lump Sum) -->
			<div class="p-1 rounded-xl bg-slate-100 dark:bg-white/5 border border-slate-200/60 dark:border-white/5 flex items-center">
				<button
					type="button"
					onclick={() => (calculationMode = 'UNIT_PRICE')}
					class="flex-1 h-8 rounded-lg text-xs font-semibold transition-all cursor-pointer {calculationMode === 'UNIT_PRICE'
						? 'bg-[#007AFF] text-white shadow-sm'
						: 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
				>
					Hitung per Satuan ({unitLabel || 'Unit'})
				</button>
				<button
					type="button"
					onclick={() => (calculationMode = 'LUMP_SUM')}
					class="flex-1 h-8 rounded-lg text-xs font-semibold transition-all cursor-pointer {calculationMode === 'LUMP_SUM'
						? 'bg-[#007AFF] text-white shadow-sm'
						: 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
				>
					Langsung Total Modal & Nilai
				</button>
			</div>

			<!-- Conditional Inputs based on Calculation Mode -->
			{#if calculationMode === 'UNIT_PRICE'}
				<!-- MODE A: Satuan, Harga Beli Satuan, Harga Pasar Satuan -->
				<div class="space-y-3">
					<div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
						<!-- Jumlah Satuan & Pilihan Unit -->
						<div class="flex flex-col gap-1.5 w-full">
							<label for="inv-quantity" class="text-xs font-medium text-slate-600 dark:text-slate-300 flex items-center justify-between">
								<span>Jumlah</span>
								<div class="flex items-center gap-1">
									{#each currentMeta.unitOptions as u}
										<button
											type="button"
											onclick={() => (unitLabel = u)}
											class="text-[10px] px-1.5 py-0.5 rounded transition-colors {unitLabel === u
												? 'bg-[#007AFF]/15 text-[#007AFF] font-semibold'
												: 'text-slate-400 hover:text-slate-600'}"
										>
											{u}
										</button>
									{/each}
								</div>
							</label>
							<div class="relative flex items-center">
								<input
									id="inv-quantity"
									type="text"
									inputmode="decimal"
									value={quantity > 0 ? quantity : ''}
									oninput={(e) => {
										const raw = (e.target as HTMLInputElement).value.replace(/[^0-9.]/g, '');
										quantity = raw ? parseFloat(raw) : 0;
									}}
									placeholder={currentMeta.unitPlaceholder}
									class="w-full h-9 pl-3 pr-14 text-xs sm:text-sm font-medium rounded-xl border border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-[#151E2E]/80 focus:border-[#007AFF] focus:ring-1 focus:ring-[#007AFF]/15 text-slate-900 dark:text-white outline-none transition-all"
								/>
								<span class="absolute right-3 text-[11px] font-medium text-slate-400 pointer-events-none select-none">
									{unitLabel}
								</span>
							</div>
						</div>

						<!-- Harga Beli per Unit -->
						<div class="flex flex-col gap-1.5 w-full">
							<label for="inv-buy-price" class="text-xs font-medium text-slate-600 dark:text-slate-300">
								Harga Beli / {unitLabel}
							</label>
							<div class="relative flex items-center">
								<span class="absolute left-3 text-xs font-semibold text-slate-400 select-none pointer-events-none">Rp</span>
								<input
									id="inv-buy-price"
									type="text"
									inputmode="numeric"
									value={buyPrice > 0 ? new Intl.NumberFormat('id-ID').format(buyPrice) : ''}
									oninput={(e) => {
										const raw = (e.target as HTMLInputElement).value.replace(/\D/g, '');
										buyPrice = raw ? parseInt(raw, 10) : 0;
									}}
									placeholder="0"
									class="w-full h-9 pl-9 pr-3 text-xs sm:text-sm font-medium rounded-xl border border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-[#151E2E]/80 focus:border-[#007AFF] focus:ring-1 focus:ring-[#007AFF]/15 text-slate-900 dark:text-white outline-none transition-all"
								/>
							</div>
						</div>

						<!-- Harga Pasar Sekarang per Unit -->
						<div class="flex flex-col gap-1.5 w-full">
							<label for="inv-current-price" class="text-xs font-medium text-slate-600 dark:text-slate-300">
								Harga Pasar / {unitLabel}
							</label>
							<div class="relative flex items-center">
								<span class="absolute left-3 text-xs font-semibold text-slate-400 select-none pointer-events-none">Rp</span>
								<input
									id="inv-current-price"
									type="text"
									inputmode="numeric"
									value={currentPrice > 0 ? new Intl.NumberFormat('id-ID').format(currentPrice) : ''}
									oninput={(e) => {
										const raw = (e.target as HTMLInputElement).value.replace(/\D/g, '');
										currentPrice = raw ? parseInt(raw, 10) : 0;
									}}
									placeholder="0"
									class="w-full h-9 pl-9 pr-3 text-xs sm:text-sm font-medium rounded-xl border border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-[#151E2E]/80 focus:border-[#007AFF] focus:ring-1 focus:ring-[#007AFF]/15 text-slate-900 dark:text-white outline-none transition-all"
								/>
							</div>
						</div>
					</div>
				</div>
			{:else}
				<!-- MODE B: Total Modal Pembelian & Taksiran Nilai Sekarang Langsung -->
				<div class="space-y-3">
					<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
						<!-- Total Modal Beli / Setor -->
						<div class="flex flex-col gap-1.5 w-full">
							<label for="inv-lump-cost" class="text-xs font-medium text-slate-600 dark:text-slate-300">
								Total Modal Awal Beli / Setor <span class="text-rose-500">*</span>
							</label>
							<div class="relative flex items-center">
								<span class="absolute left-3 text-xs font-semibold text-slate-400 select-none pointer-events-none">Rp</span>
								<input
									id="inv-lump-cost"
									type="text"
									inputmode="numeric"
									value={totalCostInput > 0 ? new Intl.NumberFormat('id-ID').format(totalCostInput) : ''}
									oninput={(e) => {
										const raw = (e.target as HTMLInputElement).value.replace(/\D/g, '');
										totalCostInput = raw ? parseInt(raw, 10) : 0;
									}}
									placeholder="0"
									class="w-full h-9 pl-9 pr-3 text-xs sm:text-sm font-medium rounded-xl border border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-[#151E2E]/80 focus:border-[#007AFF] focus:ring-1 focus:ring-[#007AFF]/15 text-slate-900 dark:text-white outline-none transition-all"
								/>
							</div>
						</div>

						<!-- Taksiran Nilai Pasar / Saldo Sekarang -->
						<div class="flex flex-col gap-1.5 w-full">
							<label for="inv-lump-val" class="text-xs font-medium text-slate-600 dark:text-slate-300">
								Taksiran Nilai Pasar / Saldo Sekarang <span class="text-rose-500">*</span>
							</label>
							<div class="relative flex items-center">
								<span class="absolute left-3 text-xs font-semibold text-slate-400 select-none pointer-events-none">Rp</span>
								<input
									id="inv-lump-val"
									type="text"
									inputmode="numeric"
									value={totalCurrentValInput > 0 ? new Intl.NumberFormat('id-ID').format(totalCurrentValInput) : ''}
									oninput={(e) => {
										const raw = (e.target as HTMLInputElement).value.replace(/\D/g, '');
										totalCurrentValInput = raw ? parseInt(raw, 10) : 0;
									}}
									placeholder="0"
									class="w-full h-9 pl-9 pr-3 text-xs sm:text-sm font-medium rounded-xl border border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-[#151E2E]/80 focus:border-[#007AFF] focus:ring-1 focus:ring-[#007AFF]/15 text-slate-900 dark:text-white outline-none transition-all"
								/>
							</div>
						</div>
					</div>

					<!-- Optional Volume / Unit Context for Real Estate / Deposits -->
					<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
						<div class="flex flex-col gap-1.5 w-full">
							<label for="inv-lump-qty" class="text-xs font-medium text-slate-600 dark:text-slate-300">
								Luas / Volume / Jumlah (Opsional)
							</label>
							<div class="relative flex items-center">
								<input
									id="inv-lump-qty"
									type="text"
									inputmode="numeric"
									value={quantity > 0 ? quantity : ''}
									oninput={(e) => {
										const raw = (e.target as HTMLInputElement).value.replace(/\D/g, '');
										quantity = raw ? parseInt(raw, 10) : 1;
									}}
									placeholder={currentMeta.unitPlaceholder}
									class="w-full h-9 pl-3 pr-14 text-xs sm:text-sm font-medium rounded-xl border border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-[#151E2E]/80 focus:border-[#007AFF] focus:ring-1 focus:ring-[#007AFF]/15 text-slate-900 dark:text-white outline-none transition-all"
								/>
								<span class="absolute right-3 text-[11px] font-medium text-slate-400 pointer-events-none select-none">
									{unitLabel}
								</span>
							</div>
						</div>

						<div class="flex flex-col gap-1.5 w-full">
							<label for="inv-lump-notes" class="text-xs font-medium text-slate-600 dark:text-slate-300">
								Catatan / Tenor (Opsional)
							</label>
							<input
								id="inv-lump-notes"
								type="text"
								bind:value={customNotes}
								placeholder="Contoh: Sertifikat SHM / Bunga 5% p.a."
								class="w-full h-9 px-3 text-xs sm:text-sm rounded-xl border border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-[#151E2E]/80 focus:border-[#007AFF] focus:ring-1 focus:ring-[#007AFF]/15 text-slate-900 dark:text-white outline-none transition-all"
							/>
						</div>
					</div>
				</div>
			{/if}

			<!-- Row 4: Live Calculation / Simulation Card -->
			<div class="p-3.5 rounded-2xl bg-slate-50 dark:bg-white/[0.03] border border-slate-200/70 dark:border-white/5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
				<div class="flex items-center gap-4">
					<div>
						<span class="text-[10px] uppercase text-slate-400 font-semibold block">Total Modal</span>
						<span class="font-semibold text-slate-900 dark:text-white">{formatRupiah(simTotalCost)}</span>
					</div>
					<div class="border-l border-slate-200 dark:border-white/10 pl-4">
						<span class="text-[10px] uppercase text-slate-400 font-semibold block">Nilai Sekarang</span>
						<span class="font-semibold text-slate-900 dark:text-white">{formatRupiah(simCurrentVal)}</span>
					</div>
				</div>

				<div class="flex items-center gap-1.5 self-end sm:self-auto px-2.5 py-1 rounded-xl {simPnL >= 0
					? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
					: 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20'} font-semibold">
					{#if simPnL >= 0}
						<TrendingUp class="w-3.5 h-3.5" />
					{:else}
						<TrendingDown class="w-3.5 h-3.5" />
					{/if}
					<span>{simPnL >= 0 ? '+' : ''}{formatRupiah(simPnL)} ({simPnL >= 0 ? '+' : ''}{simPnLPercent}%)</span>
				</div>
			</div>

			{#if formError}
				<p class="text-xs font-medium text-rose-500 bg-rose-50 dark:bg-rose-950/30 p-2.5 rounded-xl border border-rose-200 dark:border-rose-900/50">
					{formError}
				</p>
			{/if}
		</div>

		{#snippet footer()}
			<Button variant="ghost" onclick={() => (isAddModalOpen = false)}>Batal</Button>
			<Button variant="primary" onclick={handleAddHolding}>Simpan Aset</Button>
		{/snippet}
	</Modal>
</div>
