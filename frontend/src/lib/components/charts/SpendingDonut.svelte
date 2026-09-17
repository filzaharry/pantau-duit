<script lang="ts">
	import { formatRupiah } from '$lib/utils/formatters';
	import GlassSurface from '$lib/components/ui/GlassSurface.svelte';

	interface Slice {
		label: string;
		value: number;
		color: string;
	}

	interface Props {
		slices?: Slice[];
		total?: number;
		title?: string;
	}

	const defaultSlices: Slice[] = [
		{ label: 'Makanan & Minuman', value: 1615000, color: '#EF4444' },
		{ label: 'Transportasi', value: 320000, color: '#F97316' },
		{ label: 'Tagihan & WiFi', value: 450000, color: '#EAB308' },
		{ label: 'Belanja & Lainnya', value: 500000, color: '#007AFF' }
	];

	let {
		slices = defaultSlices,
		total = 2885000,
		title = 'Distribusi Pos Pengeluaran'
	}: Props = $props();

	// Calculate SVG donut stroke-dasharray and stroke-dashoffset
	const radius = 64;
	const circumference = 2 * Math.PI * radius;

	const calculatedSlices = $derived.by(() => {
		let accumulated = 0;
		if (total <= 0) return [];

		return slices.map((slice) => {
			const percent = slice.value / total;
			const dashLength = percent * circumference;
			const offset = -accumulated;
			accumulated += dashLength;
			return {
				...slice,
				percent: Math.round(percent * 100),
				dasharray: `${dashLength} ${circumference}`,
				offset
			};
		});
	});
</script>

<GlassSurface class="p-5 flex flex-col justify-between h-full">
	<div class="flex items-center justify-between mb-4">
		<h3 class="text-sm font-semibold text-slate-900 dark:text-white uppercase tracking-wider">
			{title}
		</h3>
		<span class="text-xs text-slate-400">Bulan Ini</span>
	</div>

	<div class="flex flex-col sm:flex-row items-center gap-6 w-full">
		<!-- Donut Circle SVG -->
		<div class="relative w-44 h-44 shrink-0 flex items-center justify-center">
			<svg class="w-full h-full -rotate-90 transform" viewBox="0 0 160 160">
				<!-- Background Track -->
				<circle
					cx="80"
					cy="80"
					r={radius}
					fill="none"
					stroke="currentColor"
					class="text-slate-100 dark:text-white/5"
					stroke-width="18"
				/>

				<!-- Slices -->
				{#each calculatedSlices as slice}
					<circle
						cx="80"
						cy="80"
						r={radius}
						fill="none"
						stroke={slice.color}
						stroke-width="18"
						stroke-dasharray={slice.dasharray}
						stroke-dashoffset={slice.offset}
						stroke-linecap="round"
						class="transition-all duration-500 hover:opacity-90"
					/>
				{/each}
			</svg>

			<!-- Donut Center Label -->
			<div class="absolute inset-0 flex flex-col items-center justify-center text-center pointer-events-none p-2">
				<span class="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Total</span>
				<span class="text-sm font-semibold text-slate-900 dark:text-white tracking-tight leading-tight mt-0.5">
					{formatRupiah(total, true)}
				</span>
			</div>
		</div>

		<!-- Legend List -->
		<div class="flex flex-col gap-2.5 w-full flex-1 min-w-0">
			{#each calculatedSlices as slice}
				<div class="flex items-center justify-between text-xs">
					<div class="flex items-center gap-2 min-w-0">
						<span class="w-2.5 h-2.5 rounded-full shrink-0" style="background-color: {slice.color};"></span>
						<span class="font-medium text-slate-700 dark:text-slate-200 truncate">{slice.label}</span>
					</div>
					<div class="flex items-center gap-2 shrink-0 ml-2">
						<span class="font-semibold text-slate-900 dark:text-white">{formatRupiah(slice.value, true)}</span>
						<span class="text-[10px] text-slate-400 font-semibold w-7 text-right">{slice.percent}%</span>
					</div>
				</div>
			{/each}
		</div>
	</div>
</GlassSurface>
