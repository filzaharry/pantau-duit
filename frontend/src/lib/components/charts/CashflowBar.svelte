<script lang="ts">
	import { formatRupiah } from '$lib/utils/formatters';
	import GlassSurface from '$lib/components/ui/GlassSurface.svelte';

	interface MonthData {
		month: string;
		income: number;
		expense: number;
	}

	interface Props {
		data?: MonthData[];
		title?: string;
	}

	const defaultData: MonthData[] = [
		{ month: 'Apr', income: 11000000, expense: 4200000 },
		{ month: 'Mei', income: 11500000, expense: 5100000 },
		{ month: 'Jun', income: 12000000, expense: 3800000 },
		{ month: 'Jul', income: 12000000, expense: 4500000 },
		{ month: 'Agu', income: 13500000, expense: 4800000 },
		{ month: 'Sep', income: 12000000, expense: 2885000 }
	];

	let {
		data = defaultData,
		title = 'Tren Arus Kas 6 Bulan Terakhir'
	}: Props = $props();

	const maxVal = $derived(
		Math.max(...data.map((d) => Math.max(d.income, d.expense)), 1000000)
	);
</script>

<GlassSurface class="p-5 flex flex-col justify-between h-full">
	<div class="flex items-center justify-between mb-2">
		<h3 class="text-sm font-semibold text-slate-900 dark:text-white uppercase tracking-wider">
			{title}
		</h3>
		<!-- Chart Header Legend -->
		<div class="flex items-center gap-3 text-xs">
			<div class="flex items-center gap-1.5">
				<span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
				<span class="text-slate-600 dark:text-slate-300">Masuk</span>
			</div>
			<div class="flex items-center gap-1.5">
				<span class="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
				<span class="text-slate-600 dark:text-slate-300">Keluar</span>
			</div>
		</div>
	</div>

	<!-- Responsive Bars -->
	<div class="grid grid-cols-6 gap-2 h-44 items-end pt-4 pb-2 border-b border-slate-100 dark:border-white/5">
		{#each data as item}
			{@const incomeHeight = Math.round((item.income / maxVal) * 100)}
			{@const expenseHeight = Math.round((item.expense / maxVal) * 100)}
			<div class="flex flex-col items-center gap-1.5 h-full justify-end group">
				<div class="w-full flex items-end justify-center gap-1 h-full">
					<!-- Income Bar -->
					<div
						class="w-3 sm:w-4 rounded-t-md bg-emerald-500 transition-all duration-300 hover:opacity-90 relative cursor-pointer"
						style="height: {Math.max(incomeHeight, 4)}%;"
						title="Pemasukan {item.month}: {formatRupiah(item.income)}"
					></div>
					<!-- Expense Bar -->
					<div
						class="w-3 sm:w-4 rounded-t-md bg-rose-500 transition-all duration-300 hover:opacity-90 relative cursor-pointer"
						style="height: {Math.max(expenseHeight, 4)}%;"
						title="Pengeluaran {item.month}: {formatRupiah(item.expense)}"
					></div>
				</div>
				<span class="text-[11px] font-medium text-slate-500 dark:text-slate-400 select-none">
					{item.month}
				</span>
			</div>
		{/each}
	</div>
</GlassSurface>
