<script lang="ts">
	import { formatRupiah, formatDate, formatDateTime } from '$lib/utils/formatters';
	import type { Transaction, TransactionType } from '$lib/types';
	import {
		TrendingUp,
		TrendingDown,
		Wallet,
		Coins,
		ArrowUpRight,
		ArrowDownLeft,
		Layers,
		CheckCircle2,
		Calendar,
		X
	} from 'lucide-svelte';

	interface Props {
		totalMarketValue: number;
		totalInvested: number;
		totalPnL: number;
		totalPnLPercent: string;
		assetCount: number;
		liquidCash?: number;
		investedAssetsValue?: number;
		transactions?: Transaction[];
	}

	let {
		totalMarketValue = 0,
		totalInvested = 0,
		totalPnL = 0,
		totalPnLPercent = '0.00',
		assetCount = 0,
		liquidCash = 0,
		investedAssetsValue = 0,
		transactions = []
	}: Props = $props();

	type Timeframe = '1D' | '1W' | '1M' | '1Y' | 'ALL';
	let activeTimeframe = $state<Timeframe>('1M');

	export interface TxEvent {
		id: string;
		type: TransactionType;
		amount: number;
		description: string;
		date: string;
	}

	export interface TimePoint {
		timeLabel: string;
		dateFormatted: string;
		value: number;
		events: TxEvent[];
		netChange: number;
	}

	// Calculate historical time-series from real database transactions
	function generateTimeSeries(
		tf: Timeframe,
		curVal: number,
		txs: Transaction[] = [],
		investedVal: number = 0
	): TimePoint[] {
		if (curVal <= 0 && txs.length === 0) {
			return [];
		}

		const now = new Date();

		// Normalize and sort transactions ascending by timestamp
		const sortedTxs = [...txs].sort((a, b) => {
			const da = new Date(a.transaction_date).getTime();
			const db = new Date(b.transaction_date).getTime();
			return da - db;
		});

		// Calculate total net transaction cashflow
		const totalTxNet = sortedTxs.reduce((sum, t) => {
			if (t.transaction_type === 'INCOME') return sum + Number(t.amount);
			if (t.transaction_type === 'EXPENSE') return sum - Number(t.amount);
			return sum;
		}, 0);

		// Opening cash balance before any recorded transaction in database
		const openingCash = Math.max(0, curVal - totalTxNet);

		// Compute balance and events at a given end-time
		function getBalanceAt(d: Date, bucketStart?: Date): { balance: number; events: TxEvent[]; netChange: number } {
			const dTime = d.getTime();
			const txsUpTo = sortedTxs.filter((t) => new Date(t.transaction_date).getTime() <= dTime);
			const cashAtD = openingCash + txsUpTo.reduce((sum, t) => {
				if (t.transaction_type === 'INCOME') return sum + Number(t.amount);
				if (t.transaction_type === 'EXPENSE') return sum - Number(t.amount);
				return sum;
			}, 0);

			const bStart = bucketStart ? bucketStart.getTime() : new Date(d.getFullYear(), d.getMonth(), d.getDate(), 0, 0, 0).getTime();
			const bEnd = dTime;

			const bucketTxs = sortedTxs.filter((t) => {
				const tt = new Date(t.transaction_date).getTime();
				return tt >= bStart && tt <= bEnd;
			});

			const events: TxEvent[] = bucketTxs.map((t) => ({
				id: t.id,
				type: t.transaction_type,
				amount: Number(t.amount),
				description: t.description || (t.transaction_type === 'INCOME' ? 'Pemasukan' : 'Pengeluaran'),
				date: t.transaction_date
			}));

			const netChange = bucketTxs.reduce((sum, t) => {
				if (t.transaction_type === 'INCOME') return sum + Number(t.amount);
				if (t.transaction_type === 'EXPENSE') return sum - Number(t.amount);
				return sum;
			}, 0);

			const finalBal = dTime > now.getTime() ? curVal : Math.max(0, cashAtD);
			return { balance: finalBal, events, netChange };
		}

		const points: TimePoint[] = [];

		if (tf === '1D') {
			for (let h = 0; h < 24; h++) {
				const bucketStart = new Date(now.getFullYear(), now.getMonth(), now.getDate(), h, 0, 0);
				const targetDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), h, 59, 59);
				const hourStr = String(h).padStart(2, '0') + ':00';
				const res = getBalanceAt(targetDate, bucketStart);
				points.push({
					timeLabel: hourStr,
					dateFormatted: `Hari ini, ${hourStr}`,
					value: targetDate.getTime() > now.getTime() ? curVal : res.balance,
					events: res.events,
					netChange: res.netChange
				});
			}
		} else if (tf === '1W') {
			for (let i = 6; i >= 0; i--) {
				const d = new Date(now.getFullYear(), now.getMonth(), now.getDate() - i, 23, 59, 59);
				const bStart = new Date(now.getFullYear(), now.getMonth(), now.getDate() - i, 0, 0, 0);
				const dayName = new Intl.DateTimeFormat('id-ID', { weekday: 'short' }).format(d);
				const dayDate = d.getDate();
				const monthShort = new Intl.DateTimeFormat('id-ID', { month: 'short' }).format(d);
				const monthLong = new Intl.DateTimeFormat('id-ID', { month: 'long' }).format(d);
				const res = getBalanceAt(d, bStart);
				points.push({
					timeLabel: `${dayDate} ${monthShort}`,
					dateFormatted: `${dayName}, ${dayDate} ${monthLong} ${d.getFullYear()}`,
					value: res.balance,
					events: res.events,
					netChange: res.netChange
				});
			}
		} else if (tf === '1M') {
			const totalDays = 30;
			for (let i = totalDays - 1; i >= 0; i--) {
				const d = new Date(now.getFullYear(), now.getMonth(), now.getDate() - i, 23, 59, 59);
				const bStart = new Date(now.getFullYear(), now.getMonth(), now.getDate() - i, 0, 0, 0);
				const dayNum = d.getDate();
				const monthShort = new Intl.DateTimeFormat('id-ID', { month: 'short' }).format(d);
				const monthLong = new Intl.DateTimeFormat('id-ID', { month: 'long' }).format(d);
				const res = getBalanceAt(d, bStart);
				points.push({
					timeLabel: `${dayNum} ${monthShort}`,
					dateFormatted: `${dayNum} ${monthLong} ${d.getFullYear()}`,
					value: res.balance,
					events: res.events,
					netChange: res.netChange
				});
			}
		} else if (tf === '1Y') {
			for (let i = 11; i >= 0; i--) {
				const d = new Date(now.getFullYear(), now.getMonth() - i + 1, 0, 23, 59, 59);
				const bStart = new Date(now.getFullYear(), now.getMonth() - i, 1, 0, 0, 0);
				const monthShort = new Intl.DateTimeFormat('id-ID', { month: 'short' }).format(d);
				const monthLong = new Intl.DateTimeFormat('id-ID', { month: 'long' }).format(d);
				const res = getBalanceAt(d, bStart);
				points.push({
					timeLabel: monthShort,
					dateFormatted: `Bulan ${monthLong} ${d.getFullYear()}`,
					value: res.balance,
					events: res.events,
					netChange: res.netChange
				});
			}
		} else {
			// ALL (Historical from first transaction)
			if (sortedTxs.length > 0) {
				const firstTxDate = new Date(sortedTxs[0].transaction_date);
				const startDate = new Date(firstTxDate.getFullYear(), firstTxDate.getMonth(), firstTxDate.getDate() - 1, 0, 0, 0);
				const diffDays = Math.max(7, Math.ceil((now.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)));
				for (let i = diffDays; i >= 0; i--) {
					const d = new Date(now.getFullYear(), now.getMonth(), now.getDate() - i, 23, 59, 59);
					const bStart = new Date(now.getFullYear(), now.getMonth(), now.getDate() - i, 0, 0, 0);
					const dayNum = d.getDate();
					const monthShort = new Intl.DateTimeFormat('id-ID', { month: 'short' }).format(d);
					const monthLong = new Intl.DateTimeFormat('id-ID', { month: 'long' }).format(d);
					const res = getBalanceAt(d, bStart);
					points.push({
						timeLabel: `${dayNum} ${monthShort}`,
						dateFormatted: `${dayNum} ${monthLong} ${d.getFullYear()}`,
						value: res.balance,
						events: res.events,
						netChange: res.netChange
					});
				}
			} else {
				points.push({
					timeLabel: 'Hari ini',
					dateFormatted: 'Hari ini',
					value: curVal,
					events: [],
					netChange: 0
				});
			}
		}

		return points;
	}

	const hasInvestments = $derived(investedAssetsValue > 0);
	const data = $derived(generateTimeSeries(activeTimeframe, totalMarketValue, transactions, investedAssetsValue));

	// Min & Max calculations for clean, intuitive grid levels
	const rawMin = $derived(data.length > 0 ? Math.min(...data.map((d) => d.value)) : 0);
	const rawMax = $derived(data.length > 0 ? Math.max(...data.map((d) => d.value)) : 1);
	const isStepUp = $derived(rawMax > rawMin);

	// Grid starting at 0 if min <= 0; max scaled appropriately
	const minVal = $derived(rawMin <= 0 ? 0 : Math.max(0, rawMin * 0.85));
	const maxVal = $derived(rawMax > 0 ? (rawMax === minVal ? rawMax * 1.25 : rawMax) : 1000000);
	const range = $derived(maxVal - minVal || 1);

	// Precise Grid Dimensions with dedicated gutters for axes
	const svgWidth = 1000;
	const svgHeight = 250;
	const marginLeft = 95; // Dedicated left gutter for nominal currency labels
	const marginRight = 25;
	const marginTop = 20;
	const marginBottom = 40; // Dedicated bottom gutter for date labels

	const usableW = $derived(svgWidth - marginLeft - marginRight);
	const usableH = $derived(svgHeight - marginTop - marginBottom);

	function getY(val: number): number {
		if (range <= 0) return marginTop + usableH * 0.5;
		return marginTop + usableH - ((val - minVal) / range) * usableH;
	}

	function getX(index: number): number {
		if (data.length <= 1) return marginLeft + usableW / 2;
		return marginLeft + (index / (data.length - 1)) * usableW;
	}

	// Format nominal value for left Y-axis ticks
	function formatAxisNominal(num: number): string {
		const rounded = Math.round(num);
		if (rounded <= 0) return 'Rp 0';
		if (rounded >= 1_000_000_000) {
			const val = rounded / 1_000_000_000;
			return `Rp ${val % 1 === 0 ? val.toFixed(0) : val.toFixed(1).replace('.', ',')} M`;
		}
		if (rounded >= 1_000_000) {
			const val = rounded / 1_000_000;
			return `Rp ${val % 1 === 0 ? val.toFixed(0) : val.toFixed(1).replace('.', ',')} jt`;
		}
		if (rounded >= 1_000) {
			const val = rounded / 1_000;
			return `Rp ${val % 1 === 0 ? val.toFixed(0) : val.toFixed(0)} rb`;
		}
		return `Rp ${rounded}`;
	}

	// 5 Ticks on Y-axis (Nominal on the Left)
	const yTicks = $derived.by(() => {
		const fractions = [1, 0.75, 0.5, 0.25, 0];
		return fractions.map((f) => {
			const val = minVal + f * range;
			const y = marginTop + usableH * (1 - f);
			return {
				fraction: f,
				value: val,
				y,
				label: formatAxisNominal(val)
			};
		});
	});

	// Evenly spaced Ticks on X-axis (Dates on the Bottom)
	interface AxisXTick {
		index: number;
		label: string;
	}

	const xTicks = $derived.by(() => {
		if (data.length === 0) return [];
		if (data.length <= 6) {
			return data.map((d, i) => ({ index: i, label: d.timeLabel }));
		}
		const count = 6;
		const step = (data.length - 1) / (count - 1);
		const ticks: AxisXTick[] = [];
		const usedIndices = new Set<number>();

		for (let i = 0; i < count; i++) {
			const idx = Math.min(data.length - 1, Math.round(i * step));
			if (!usedIndices.has(idx)) {
				usedIndices.add(idx);
				ticks.push({ index: idx, label: data[idx].timeLabel });
			}
		}
		return ticks;
	});

	// Smooth Catmull-Rom / Bezier Area Path
	const areaPath = $derived.by(() => {
		if (data.length === 0) return '';
		const pts = data.map((d, i) => ({ x: getX(i), y: getY(d.value) }));
		let path = `M ${pts[0].x} ${pts[0].y}`;

		for (let i = 0; i < pts.length - 1; i++) {
			const p0 = pts[Math.max(0, i - 1)];
			const p1 = pts[i];
			const p2 = pts[i + 1];
			const p3 = pts[Math.min(pts.length - 1, i + 2)];

			const cp1x = p1.x + (p2.x - p0.x) / 6;
			const cp1y = p1.y + (p2.y - p0.y) / 6;
			const cp2x = p2.x - (p3.x - p1.x) / 6;
			const cp2y = p2.y - (p3.y - p1.y) / 6;

			path += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${p2.x} ${p2.y}`;
		}
		return path;
	});

	const areaFillPath = $derived.by(() => {
		if (!areaPath || data.length === 0) return '';
		const firstX = getX(0);
		const lastX = getX(data.length - 1);
		const bottomY = marginTop + usableH;
		return `${areaPath} L ${lastX} ${bottomY} L ${firstX} ${bottomY} Z`;
	});

	// Click-to-Inspect Interactive Tooltip State
	// (No changing header nominals on hover; tooltip only opens on explicit click)
	let selectedPointIndex = $state<number | null>(null);
	const selectedPoint = $derived(
		selectedPointIndex !== null && data[selectedPointIndex] ? data[selectedPointIndex] : null
	);

	function handleChartClick(e: MouseEvent) {
		if (data.length === 0) return;
		const target = e.currentTarget as HTMLElement;
		const rect = target.getBoundingClientRect();
		const clientX = e.clientX - rect.left;

		// Convert to SVG x
		const svgX = (clientX / rect.width) * svgWidth;

		// If clicked outside chart area, ignore
		if (svgX < marginLeft - 20 || svgX > svgWidth - marginRight + 20) {
			return;
		}

		// Find closest data point
		let closestIdx = 0;
		let minDiff = Infinity;
		for (let i = 0; i < data.length; i++) {
			const px = getX(i);
			const diff = Math.abs(px - svgX);
			if (diff < minDiff) {
				minDiff = diff;
				closestIdx = i;
			}
		}

		selectedPointIndex = closestIdx;
	}
</script>

<div
	class="rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#131722] dark:via-[#101420] dark:to-[#0c0f18] border border-slate-200/70 dark:border-white/[0.08] overflow-hidden select-none transition-colors"
>
	<!-- 1. Header Bar: Bersih, Rapi, Nominal Tetap / Static (Tidak Fluktuatif Saat Hover) -->
	<div class="p-5 sm:p-6 pb-2">
		<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
			<!-- Portfolio Value & Static Growth Tag -->
			<div>
				<div class="flex items-center gap-2">
					<span class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 block">
						Total Nilai Portofolio (Kas + Investasi)
					</span>
				</div>

				<div class="flex flex-wrap items-baseline gap-2.5 sm:gap-3 mt-1">
					<!-- Static Header Nominal: Selalu menampilkan total real saat ini -->
					<span class="text-2xl sm:text-4xl font-bold tracking-tight text-slate-900 dark:text-white">
						{formatRupiah(totalMarketValue)}
					</span>

					<!-- Growth / Step-up Badge -->
					{#if isStepUp}
						<div class="inline-flex items-center gap-1 px-2.5 py-1 rounded-xl text-xs font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
							<TrendingUp class="w-3.5 h-3.5" />
							<span>+{formatRupiah(rawMax - rawMin)} (Saldo Tumbuh)</span>
						</div>
					{:else if hasInvestments}
						<div
							class="inline-flex items-center gap-1 px-2.5 py-1 rounded-xl text-xs font-semibold {totalPnL >= 0
								? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
								: 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20'}"
						>
							{#if totalPnL >= 0}
								<TrendingUp class="w-3.5 h-3.5" />
							{:else}
								<TrendingDown class="w-3.5 h-3.5" />
							{/if}
							<span>{totalPnL >= 0 ? '+' : ''}{formatRupiah(totalPnL)} ({totalPnLPercent}%)</span>
						</div>
					{:else}
						<div class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-xl text-xs font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
							<CheckCircle2 class="w-3.5 h-3.5 text-emerald-500" />
							<span>Kas Likuid 100% (Aman & Stabil)</span>
						</div>
					{/if}
				</div>

				<p class="text-xs text-slate-500 dark:text-slate-400 mt-1.5">
					Saldo kas tersimpan aman di rekening dan siap dialokasikan untuk investasi. Klik titik pada kurva untuk melihat rincian tanggal dan mutasi.
				</p>
			</div>

			<!-- Timeframe Selector Tabs -->
			<div class="flex items-center p-0.5 rounded-xl bg-slate-100 dark:bg-white/5 border border-slate-200/60 dark:border-white/5 self-start sm:self-auto">
				{#each (['1D', '1W', '1M', '1Y', 'ALL'] as Timeframe[]) as tf}
					<button
						type="button"
						onclick={() => {
							activeTimeframe = tf;
							selectedPointIndex = null;
						}}
						class="h-8 px-3 rounded-lg text-xs font-semibold transition-all cursor-pointer {activeTimeframe === tf
							? 'bg-[#007AFF] text-white shadow-sm'
							: 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
					>
						{tf === 'ALL' ? 'Semua' : tf}
					</button>
				{/each}
			</div>
		</div>
	</div>

	<!-- 2. Chart Grid: Sisi Kiri = Angka Nominal, Sisi Bawah = Tanggal, Titik Diklik = Tooltip Muncul -->
	<div
		class="relative w-full overflow-hidden cursor-pointer"
		onclick={handleChartClick}
		onkeydown={(e) => {
			if (e.key === 'Escape' || e.key === 'Enter' || e.key === ' ') selectedPointIndex = null;
		}}
		tabindex="0"
		role="button"
		aria-label="Grafik Tren Portofolio & Mutasi Saldo"
	>
		<svg
			viewBox="0 0 {svgWidth} {svgHeight}"
			class="w-full h-56 sm:h-72 block"
			preserveAspectRatio="none"
		>
			<defs>
				<!-- Emerald Area Gradient Fill -->
				<linearGradient id="portfolioAreaGrad" x1="0" y1="0" x2="0" y2="1">
					<stop offset="0%" stop-color="#10B981" stop-opacity="0.25" />
					<stop offset="70%" stop-color="#10B981" stop-opacity="0.05" />
					<stop offset="100%" stop-color="#10B981" stop-opacity="0.0" />
				</linearGradient>
			</defs>

			<!-- ================= LEFT Y-AXIS (ANGKA NOMINAL) & HORIZONTAL GRID ================= -->
			{#each yTicks as tick}
				<!-- Horizontal Grid Line -->
				<line
					x1={marginLeft}
					y1={tick.y}
					x2={svgWidth - marginRight}
					y2={tick.y}
					stroke="currentColor"
					stroke-width="1"
					stroke-dasharray="3 3"
					class="text-slate-200/70 dark:text-white/[0.05]"
				/>

				<!-- Left Nominal Text Label -->
				<text
					x={marginLeft - 12}
					y={tick.y + 4}
					text-anchor="end"
					class="fill-slate-400 dark:fill-slate-500 text-[11px] font-medium tracking-tight select-none"
				>
					{tick.label}
				</text>
			{/each}

			<!-- ================= BOTTOM X-AXIS (TANGGAL) & VERTICAL TICKS ================= -->
			<!-- X-Axis Baseline -->
			<line
				x1={marginLeft}
				y1={marginTop + usableH}
				x2={svgWidth - marginRight}
				y2={marginTop + usableH}
				stroke="currentColor"
				stroke-width="1"
				class="text-slate-200 dark:text-white/10"
			/>

			{#each xTicks as tick}
				{@const xPos = getX(tick.index)}
				<!-- Vertical Tick Notch -->
				<line
					x1={xPos}
					y1={marginTop + usableH}
					x2={xPos}
					y2={marginTop + usableH + 5}
					stroke="currentColor"
					stroke-width="1"
					class="text-slate-300 dark:text-white/20"
				/>

				<!-- Bottom Date Text Label -->
				<text
					x={xPos}
					y={marginTop + usableH + 22}
					text-anchor="middle"
					class="fill-slate-400 dark:fill-slate-500 text-[11px] font-medium tracking-tight select-none"
				>
					{tick.label}
				</text>
			{/each}

			<!-- ================= DATA CURVE & AREA FILL ================= -->
			{#if data.length > 0}
				<!-- Gradient Area Fill under the line -->
				<path d={areaFillPath} fill="url(#portfolioAreaGrad)" />

				<!-- Smooth Trend Line -->
				<path
					d={areaPath}
					fill="none"
					stroke="#10B981"
					stroke-width="2.5"
					stroke-linecap="round"
					stroke-linejoin="round"
				/>

				<!-- Visible Event Markers where Cash In/Out Occurred -->
				{#each data as pt, i}
					{#if pt.events && pt.events.length > 0}
						{@const pX = getX(i)}
						{@const pY = getY(pt.value)}
						<g transform="translate({pX}, {pY})">
							<circle r="9" fill="#10B981" opacity="0.3" class="animate-ping" />
							<circle
								r="6"
								fill="#10B981"
								stroke="#ffffff"
								stroke-width="2"
								class="hover:scale-125 transition-transform"
							/>
							<circle r="2" fill="#ffffff" />
						</g>
					{/if}
				{/each}

				<!-- Latest Current Point Pulse Marker at the end -->
				{@const lastX = getX(data.length - 1)}
				{@const lastY = getY(data[data.length - 1]?.value ?? totalMarketValue)}
				<g transform="translate({lastX}, {lastY})">
					<circle r="7" fill="#10B981" opacity="0.35" class="animate-ping" />
					<circle r="4" fill="#10B981" stroke="#ffffff" stroke-width="1.5" />
				</g>
			{/if}

			<!-- ================= SELECTED POINT HIGHLIGHT ON CLICK ================= -->
			{#if selectedPointIndex !== null && selectedPoint !== null}
				{@const sX = getX(selectedPointIndex)}
				{@const sY = getY(selectedPoint.value)}

				<!-- Vertical Guideline to Bottom Date -->
				<line
					x1={sX}
					y1={marginTop}
					x2={sX}
					y2={marginTop + usableH}
					stroke="#10B981"
					stroke-width="1.5"
					stroke-dasharray="3 3"
					class="opacity-70"
				/>

				<!-- Active Point Ring -->
				<g transform="translate({sX}, {sY})">
					<circle r="12" fill="#10B981" opacity="0.25" class="animate-ping" />
					<circle r="7" fill="#10B981" stroke="#ffffff" stroke-width="2.5" />
					<circle r="2.5" fill="#ffffff" />
				</g>
			{/if}
		</svg>

		<!-- ================= FLOATING TOOLTIP ON POINT CLICK ================= -->
		{#if selectedPoint !== null && selectedPointIndex !== null}
			{@const posX = getX(selectedPointIndex)}
			{@const posY = getY(selectedPoint.value)}
			{@const leftPercent = (posX / svgWidth) * 100}
			{@const topPercent = (posY / svgHeight) * 100}
			{@const isNearRight = leftPercent > 65}
			{@const isNearLeft = leftPercent < 35}
			{@const isNearTop = topPercent < 45}

			<div
				class="absolute z-30 pointer-events-auto transition-all duration-150 animate-in fade-in zoom-in-95"
				style="
					left: {leftPercent}%;
					top: {topPercent}%;
					transform: translate({isNearRight ? '-88%' : isNearLeft ? '-12%' : '-50%'}, {isNearTop ? '15%' : '-115%'});
				"
			>
				<div
					class="w-72 max-w-[88vw] rounded-2xl bg-white/95 dark:bg-[#181d2a]/95 backdrop-blur-md p-3.5 shadow-2xl border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white"
				>
					<!-- Tooltip Header -->
					<div class="flex items-center justify-between pb-2 mb-2 border-b border-slate-100 dark:border-white/10">
						<div class="flex items-center gap-1.5 text-xs font-semibold text-slate-700 dark:text-slate-200">
							<Calendar class="w-3.5 h-3.5 text-[#007AFF]" />
							<span>{selectedPoint.dateFormatted}</span>
						</div>
						<button
							type="button"
							onclick={(e) => {
								e.stopPropagation();
								selectedPointIndex = null;
							}}
							class="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-white/10 text-slate-400 hover:text-slate-600 dark:hover:text-white transition-colors cursor-pointer"
							title="Tutup"
						>
							<X class="w-3.5 h-3.5" />
						</button>
					</div>

					<!-- Saldo Pada Tanggal Ini -->
					<div class="space-y-0.5">
						<span class="text-[10px] font-medium text-slate-400 uppercase tracking-wider block">Saldo Portofolio</span>
						<span class="text-base font-bold text-slate-900 dark:text-white block">
							{formatRupiah(selectedPoint.value)}
						</span>
					</div>

					<!-- Mutasi Tanggal Ini -->
					<div class="mt-2.5 pt-2 border-t border-slate-100 dark:border-white/10">
						{#if selectedPoint.events && selectedPoint.events.length > 0}
							<span class="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
								Mutasi Transaksi ({selectedPoint.events.length})
							</span>
							<div class="space-y-1.5 max-h-36 overflow-y-auto pr-1">
								{#each selectedPoint.events as ev}
									<div
										class="flex items-center justify-between gap-2 p-1.5 rounded-lg text-xs font-medium {ev.type === 'INCOME'
											? 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border border-emerald-500/15'
											: 'bg-rose-500/10 text-rose-700 dark:text-rose-300 border border-rose-500/15'}"
									>
										<div class="flex items-center gap-1.5 min-w-0">
											{#if ev.type === 'INCOME'}
												<ArrowDownLeft class="w-3.5 h-3.5 text-emerald-600 shrink-0" />
											{:else}
												<ArrowUpRight class="w-3.5 h-3.5 text-rose-600 shrink-0" />
											{/if}
											<span class="truncate">{ev.description}</span>
										</div>
										<span class="font-bold shrink-0">
											{ev.type === 'INCOME' ? '+' : '-'}{formatRupiah(ev.amount)}
										</span>
									</div>
								{/each}
							</div>
						{:else}
							<p class="text-[11px] text-slate-400 flex items-center gap-1.5 py-0.5">
								<CheckCircle2 class="w-3.5 h-3.5 text-slate-400 shrink-0" />
								<span>Tidak ada mutasi transaksi pada tanggal ini.</span>
							</p>
						{/if}
					</div>
				</div>
			</div>
		{/if}
	</div>

	<!-- 3. Bottom Summary Strip: Jelas, Bahasa Investor Santai & Mudah Dipahami -->
	<div class="p-4 sm:p-5 bg-slate-50/70 dark:bg-white/[0.02] border-t border-slate-100 dark:border-white/5">
		<div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 divide-y sm:divide-y-0 lg:divide-x divide-slate-100 dark:divide-white/5">
			<!-- Col 1: Saldo Kas di Rekening -->
			<div class="flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-9 h-9 rounded-xl bg-blue-500/10 text-[#007AFF] dark:text-[#0A84FF] flex items-center justify-center shrink-0">
					<Wallet class="w-4 h-4" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Kas di Rekening</span>
					<span class="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white truncate block">{formatRupiah(liquidCash)}</span>
				</div>
			</div>

			<!-- Col 2: Aset Investasi -->
			<div class="pt-2 sm:pt-0 lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-9 h-9 rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400 flex items-center justify-center shrink-0">
					<Layers class="w-4 h-4" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Aset Pasar Terinvestasi</span>
					<span class="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white truncate block">{formatRupiah(investedAssetsValue)}</span>
				</div>
			</div>

			<!-- Col 3: Kenaikan Saldo / Keuntungan -->
			<div class="pt-2 sm:pt-0 lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-9 h-9 rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
					<TrendingUp class="w-4 h-4" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">
						{isStepUp ? 'Pertumbuhan Saldo' : 'Keuntungan Aset'}
					</span>
					<span class="text-xs sm:text-sm font-semibold text-emerald-600 dark:text-emerald-400 truncate block">
						{isStepUp ? `+${formatRupiah(rawMax - rawMin)}` : `${totalPnL >= 0 ? '+' : ''}${formatRupiah(totalPnL)} (${totalPnLPercent}%)`}
					</span>
				</div>
			</div>

			<!-- Col 4: Total Aset & Rekening Terdaftar -->
			<div class="pt-2 sm:pt-0 lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-9 h-9 rounded-xl bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 flex items-center justify-center shrink-0">
					<Coins class="w-4 h-4" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Total Simpanan & Rekening</span>
					<span class="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white truncate block">{assetCount} Terdaftar</span>
				</div>
			</div>
		</div>
	</div>
</div>
