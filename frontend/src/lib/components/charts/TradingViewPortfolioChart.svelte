<script lang="ts">
	import { formatRupiah } from '$lib/utils/formatters';
	import {
		TrendingUp,
		TrendingDown,
		Wallet,
		Coins,
		ArrowUpRight,
		Layers
	} from 'lucide-svelte';

	interface Props {
		totalMarketValue: number;
		totalInvested: number;
		totalPnL: number;
		totalPnLPercent: string;
		assetCount: number;
	}

	let {
		totalMarketValue = 104625000,
		totalInvested = 94925000,
		totalPnL = 9700000,
		totalPnLPercent = '10.22',
		assetCount = 2
	}: Props = $props();

	type Timeframe = '1D' | '1W' | '1M' | '1Y' | 'ALL';
	let activeTimeframe = $state<Timeframe>('1M');

	interface TimePoint {
		timeLabel: string;
		dateFormatted: string;
		value: number;
	}

	// Generate realistic time-series data without overly technical clutter
	function generateTimeSeries(tf: Timeframe, curVal: number, costVal: number): TimePoint[] {
		const points: TimePoint[] = [];

		if (tf === '1D') {
			const hours = 24;
			const base = curVal * 0.985;
			for (let i = 0; i < hours; i++) {
				const hourStr = String(i).padStart(2, '0') + ':00';
				const progress = i / (hours - 1);
				const target = base + (curVal - base) * progress;
				const noise = (Math.sin(i * 1.3) + Math.cos(i * 0.7)) * curVal * 0.003;
				const value = i === hours - 1 ? curVal : Math.round(target + noise);
				points.push({
					timeLabel: hourStr,
					dateFormatted: `Hari ini, pukul ${hourStr}`,
					value
				});
			}
		} else if (tf === '1W') {
			const days = ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min'];
			const base = curVal * 0.96;
			for (let i = 0; i < days.length; i++) {
				const day = days[i];
				const progress = i / (days.length - 1);
				const target = base + (curVal - base) * progress;
				const noise = Math.sin(i * 1.5) * curVal * 0.008;
				const value = i === days.length - 1 ? curVal : Math.round(target + noise);
				points.push({
					timeLabel: day,
					dateFormatted: `${day}, Sep 2026`,
					value
				});
			}
		} else if (tf === '1M') {
			const count = 30;
			const base = costVal * 0.99;
			for (let i = 0; i < count; i++) {
				const day = i + 1;
				const progress = i / (count - 1);
				const dip = i > 7 && i < 16 ? -curVal * 0.022 : curVal * 0.004;
				const target = base + (curVal - base) * Math.pow(progress, 1.15) + dip;
				const noise = (Math.sin(i * 0.9) * 0.6 + Math.cos(i * 1.3) * 0.4) * curVal * 0.01;
				const value = i === count - 1 ? curVal : Math.round(target + noise);
				points.push({
					timeLabel: `${day} Sep`,
					dateFormatted: `${day} September 2026`,
					value
				});
			}
		} else if (tf === '1Y') {
			const months = ['Okt', 'Nov', 'Des', 'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep'];
			const base = costVal * 0.88;
			for (let i = 0; i < months.length; i++) {
				const month = months[i];
				const progress = i / (months.length - 1);
				const target = base + (curVal - base) * Math.pow(progress, 0.9);
				const noise = Math.sin(i * 1.1) * curVal * 0.015;
				const value = i === months.length - 1 ? curVal : Math.round(target + noise);
				points.push({
					timeLabel: month,
					dateFormatted: `Bulan ${month} 2026`,
					value
				});
			}
		} else {
			// ALL
			const quarters = ['Q1 23', 'Q2 23', 'Q3 23', 'Q4 23', 'Q1 24', 'Q2 24', 'Q3 24', 'Q4 24', 'Q1 25', 'Q2 25', 'Q3 25', 'Q4 25', 'Q1 26', 'Q2 26', 'Q3 26'];
			const base = costVal * 0.72;
			for (let i = 0; i < quarters.length; i++) {
				const q = quarters[i];
				const progress = i / (quarters.length - 1);
				const target = base + (curVal - base) * Math.pow(progress, 1.1);
				const noise = Math.sin(i * 0.8) * curVal * 0.02;
				const value = i === quarters.length - 1 ? curVal : Math.round(target + noise);
				points.push({
					timeLabel: q,
					dateFormatted: `Kuartal ${q}`,
					value
				});
			}
		}

		return points;
	}

	const data = $derived(generateTimeSeries(activeTimeframe, totalMarketValue, totalInvested));

	// Min & Max calculations
	const minVal = $derived(Math.min(...data.map((d) => d.value)) * 0.99);
	const maxVal = $derived(Math.max(...data.map((d) => d.value)) * 1.01);
	const range = $derived(maxVal - minVal || 1);

	// Full-width SVG Dimensions (Edge-to-edge: 0 padding on left and right)
	const svgWidth = 1000;
	const svgHeight = 220;
	const padTop = 20;
	const padBottom = 20;
	const usableH = $derived(svgHeight - padTop - padBottom);

	function getY(val: number): number {
		return padTop + usableH - ((val - minVal) / range) * usableH;
	}

	function getX(index: number): number {
		return (index / (data.length - 1)) * svgWidth;
	}

	// Interactive Crosshair & Tooltip
	let hoverIndex = $state<number | null>(null);
	let isHovered = $derived(hoverIndex !== null && hoverIndex >= 0 && hoverIndex < data.length);
	let activePoint = $derived(
		isHovered && hoverIndex !== null ? data[hoverIndex] : data[data.length - 1]
	);

	// Displayed Value & Gain (Updates live when hovering over the chart)
	const displayValue = $derived(activePoint?.value || totalMarketValue);
	const displayPnL = $derived(displayValue - totalInvested);
	const displayPnLPercent = $derived(
		totalInvested > 0 ? ((displayPnL / totalInvested) * 100).toFixed(2) : '0.00'
	);
	const isProfit = $derived(displayPnL >= 0);

	// Human-readable timeframe explanation
	const timeframeSubtitle = $derived.by(() => {
		if (isHovered && activePoint) {
			return activePoint.dateFormatted;
		}
		switch (activeTimeframe) {
			case '1D':
				return 'Pertumbuhan dalam 24 jam terakhir';
			case '1W':
				return 'Pertumbuhan 7 hari terakhir';
			case '1M':
				return 'Pertumbuhan 30 hari terakhir';
			case '1Y':
				return 'Pertumbuhan 1 tahun terakhir';
			default:
				return 'Total keuntungan sejak awal investasi';
		}
	});

	// Smooth Catmull-Rom / Bezier Edge-to-Edge Area Path
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
		if (!areaPath) return '';
		return `${areaPath} L ${svgWidth} ${svgHeight} L 0 ${svgHeight} Z`;
	});

	// Derived coordinates for the current latest value marker
	const latestY = $derived(getY(data[data.length - 1]?.value || totalMarketValue));

	// Mouse / Touch Event Handlers for edge-to-edge crosshair
	function handleMouseMove(e: MouseEvent) {
		const target = e.currentTarget as HTMLElement;
		const rect = target.getBoundingClientRect();
		const clientX = e.clientX - rect.left;
		const ratio = Math.max(0, Math.min(1, clientX / rect.width));
		const rawIndex = Math.round(ratio * (data.length - 1));
		hoverIndex = Math.max(0, Math.min(data.length - 1, rawIndex));
	}

	function handleTouchMove(e: TouchEvent) {
		if (!e.touches.length) return;
		const target = e.currentTarget as HTMLElement;
		const rect = target.getBoundingClientRect();
		const touch = e.touches[0];
		const clientX = touch.clientX - rect.left;
		const ratio = Math.max(0, Math.min(1, clientX / rect.width));
		const rawIndex = Math.round(ratio * (data.length - 1));
		hoverIndex = Math.max(0, Math.min(data.length - 1, rawIndex));
	}

	function handleMouseLeave() {
		hoverIndex = null;
	}
</script>

<div
	class="rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#131722] dark:via-[#101420] dark:to-[#0c0f18] border border-slate-200/70 dark:border-white/[0.08] overflow-hidden select-none transition-colors"
>
	<!-- 1. Header Bar: Clear Investment & Trading Information -->
	<div class="p-5 sm:p-6 pb-2">
		<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
			<!-- Portfolio Value & Return -->
			<div>
				<span class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 block">
					Total Nilai Investasi
				</span>

				<div class="flex flex-wrap items-baseline gap-2.5 sm:gap-3 mt-1">
					<span class="text-2xl sm:text-4xl font-bold tracking-tight text-slate-900 dark:text-white">
						{formatRupiah(displayValue)}
					</span>

					<!-- PnL Badge -->
					<div
						class="inline-flex items-center gap-1 px-2.5 py-1 rounded-xl text-xs font-semibold {isProfit
							? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
							: 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20'}"
					>
						{#if isProfit}
							<TrendingUp class="w-3.5 h-3.5" />
						{:else}
							<TrendingDown class="w-3.5 h-3.5" />
						{/if}
						<span>{isProfit ? '+' : ''}{formatRupiah(displayPnL)} ({isProfit ? '+' : ''}{displayPnLPercent}%)</span>
					</div>
				</div>

				<!-- Easy-to-understand explanation text -->
				<p class="text-xs text-slate-500 dark:text-slate-400 mt-1 flex items-center gap-1.5">
					<span>{timeframeSubtitle}</span>
					{#if isHovered}
						<span class="text-[10px] px-1.5 py-0.2 rounded bg-[#007AFF]/10 text-[#007AFF] font-medium">Titik Dipilih</span>
					{/if}
				</p>
			</div>

			<!-- Timeframe Selector Tabs (Clean & Intuitive) -->
			<div class="flex items-center p-0.5 rounded-xl bg-slate-100 dark:bg-white/5 border border-slate-200/60 dark:border-white/5 self-start sm:self-auto">
				{#each (['1D', '1W', '1M', '1Y', 'ALL'] as Timeframe[]) as tf}
					<button
						type="button"
						onclick={() => (activeTimeframe = tf)}
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

	<!-- 2. Full-Width Edge-to-Edge Interactive Chart (0 Left/Right Padding) -->
	<div
		class="relative w-full overflow-hidden cursor-crosshair"
		onmousemove={handleMouseMove}
		ontouchmove={handleTouchMove}
		onmouseleave={handleMouseLeave}
		role="region"
		aria-label="Grafik Tren Investasi"
	>
		<svg
			viewBox="0 0 {svgWidth} {svgHeight}"
			class="w-full h-44 sm:h-64 block"
			preserveAspectRatio="none"
		>
			<defs>
				<!-- Full-width Radiant Emerald Gradient -->
				<linearGradient id="edgePortfolioGrad" x1="0" y1="0" x2="0" y2="1">
					<stop offset="0%" stop-color="#10B981" stop-opacity="0.30" />
					<stop offset="60%" stop-color="#10B981" stop-opacity="0.08" />
					<stop offset="100%" stop-color="#10B981" stop-opacity="0.0" />
				</linearGradient>
			</defs>

			<!-- Faint Horizontal Guide Lines (Full width 0 to 1000) -->
			<line
				x1="0"
				y1={padTop + usableH * 0.25}
				x2={svgWidth}
				y2={padTop + usableH * 0.25}
				stroke="currentColor"
				stroke-width="1"
				stroke-dasharray="4 4"
				class="text-slate-200/70 dark:text-white/[0.04]"
			/>
			<line
				x1="0"
				y1={padTop + usableH * 0.5}
				x2={svgWidth}
				y2={padTop + usableH * 0.5}
				stroke="currentColor"
				stroke-width="1"
				stroke-dasharray="4 4"
				class="text-slate-200/70 dark:text-white/[0.04]"
			/>
			<line
				x1="0"
				y1={padTop + usableH * 0.75}
				x2={svgWidth}
				y2={padTop + usableH * 0.75}
				stroke="currentColor"
				stroke-width="1"
				stroke-dasharray="4 4"
				class="text-slate-200/70 dark:text-white/[0.04]"
			/>

			<!-- Edge-to-Edge Area Gradient Fill -->
			<path d={areaFillPath} fill="url(#edgePortfolioGrad)" />

			<!-- Edge-to-Edge Smooth Curve Line -->
			<path
				d={areaPath}
				fill="none"
				stroke="#10B981"
				stroke-width="2.5"
				stroke-linecap="round"
				stroke-linejoin="round"
			/>

			<!-- End-point Radar Pulse Indicator at the edge -->
			<g transform="translate({svgWidth - 6}, {latestY})">
				<circle r="8" fill="#10B981" opacity="0.35" class="animate-ping" />
				<circle r="4" fill="#10B981" stroke="#ffffff" stroke-width="1.5" />
			</g>

			<!-- Interactive Crosshair & Tooltip Dot -->
			{#if isHovered && hoverIndex !== null}
				{@const hX = getX(hoverIndex)}
				{@const hY = getY(activePoint.value)}

				<!-- Vertical Crosshair Line -->
				<line
					x1={hX}
					y1="0"
					x2={hX}
					y2={svgHeight}
					stroke="currentColor"
					stroke-width="1"
					stroke-dasharray="3 3"
					class="text-slate-400 dark:text-slate-300"
				/>

				<!-- Horizontal Crosshair Line -->
				<line
					x1="0"
					y1={hY}
					x2={svgWidth}
					y2={hY}
					stroke="currentColor"
					stroke-width="1"
					stroke-dasharray="3 3"
					class="text-slate-400 dark:text-slate-300"
				/>

				<!-- Glowing Data Point Dot -->
				<circle cx={hX} cy={hY} r="6" fill="#10B981" stroke="#ffffff" stroke-width="2.5" />
			{/if}
		</svg>
	</div>

	<!-- 3. Bottom Summary Strip: Jelas, Bahasa Investor Santai & Mudah Dipahami -->
	<div class="p-4 sm:p-5 bg-slate-50/70 dark:bg-white/[0.02] border-t border-slate-100 dark:border-white/5">
		<div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 divide-y sm:divide-y-0 lg:divide-x divide-slate-100 dark:divide-white/5">
			<!-- Col 1: Modal Awal -->
			<div class="flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-9 h-9 rounded-xl bg-blue-500/10 text-[#007AFF] dark:text-[#0A84FF] flex items-center justify-center shrink-0">
					<Layers class="w-4 h-4" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Modal Awal Disetor</span>
					<span class="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white truncate block">{formatRupiah(totalInvested)}</span>
				</div>
			</div>

			<!-- Col 2: Keuntungan Bersih -->
			<div class="pt-2 sm:pt-0 lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-9 h-9 rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
					<TrendingUp class="w-4 h-4" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Keuntungan Bersih</span>
					<span class="text-xs sm:text-sm font-semibold text-emerald-600 dark:text-emerald-400 truncate block">+{formatRupiah(totalPnL)} ({totalPnLPercent}%)</span>
				</div>
			</div>

			<!-- Col 3: Nilai Tertinggi -->
			<div class="pt-2 sm:pt-0 lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-9 h-9 rounded-xl bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 flex items-center justify-center shrink-0">
					<ArrowUpRight class="w-4 h-4" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Nilai Tertinggi ({activeTimeframe === 'ALL' ? 'Semua' : activeTimeframe})</span>
					<span class="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white truncate block">{formatRupiah(Math.max(...data.map(d => d.value)))}</span>
				</div>
			</div>

			<!-- Col 4: Total Aset -->
			<div class="pt-2 sm:pt-0 lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-9 h-9 rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400 flex items-center justify-center shrink-0">
					<Coins class="w-4 h-4" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Total Aset Terdaftar</span>
					<span class="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white truncate block">{assetCount} Aset Aktif</span>
				</div>
			</div>
		</div>
	</div>
</div>
