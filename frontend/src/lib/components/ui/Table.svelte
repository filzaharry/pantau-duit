<script module lang="ts">
	export interface TableColumn<T = any> {
		key?: keyof T | string;
		header: string;
		align?: 'left' | 'center' | 'right';
		class?: string;
		width?: string;
		sortable?: boolean;
		sortKey?: keyof T | string;
	}
</script>

<script lang="ts" generics="T">
	import type { Snippet } from 'svelte';
	import {
		Inbox,
		ChevronLeft,
		ChevronRight,
		ChevronsLeft,
		ChevronsRight,
		ArrowUpDown,
		ArrowUp,
		ArrowDown
	} from 'lucide-svelte';

	type SortDirection = 'asc' | 'desc' | null;

	interface Props {
		title?: string;
		subtitle?: string;
		icon?: any;
		badge?: string;
		columns: TableColumn<T>[];
		items: T[];
		emptyMessage?: string;
		emptyDescription?: string;
		class?: string;
		paginated?: boolean;
		pageSize?: number;
		pageSizeOptions?: number[];
		defaultSortKey?: string | null;
		defaultSortDirection?: 'asc' | 'desc' | null;
		headerActions?: Snippet;
		row?: Snippet<[T, number]>;
		footer?: Snippet;
	}

	let {
		title,
		subtitle,
		icon: IconComponent,
		badge,
		columns,
		items,
		emptyMessage = 'Tidak ada data ditemukan',
		emptyDescription = 'Coba ubah kata kunci pencarian atau filter Anda.',
		class: className = '',
		paginated = true,
		pageSize = $bindable(10),
		pageSizeOptions = [10, 50, 100],
		defaultSortKey = null,
		defaultSortDirection = null,
		headerActions,
		row,
		footer
	}: Props = $props();

	// State for Sorting
	let sortKey = $state<string | null>(null);
	let sortDirection = $state<SortDirection>(null);

	$effect.pre(() => {
		if (defaultSortKey && sortKey === null) {
			sortKey = defaultSortKey;
		}
		if (defaultSortDirection && sortDirection === null) {
			sortDirection = defaultSortDirection;
		}
	});

	// State for Pagination
	let currentPage = $state(1);

	function isColumnSortable(col: TableColumn<T>): boolean {
		if (col.sortable === false) return false;
		return Boolean(col.key || col.sortKey);
	}

	function getColumnSortKey(col: TableColumn<T>): string {
		return String(col.sortKey || col.key || '');
	}

	function handleSort(col: TableColumn<T>) {
		const key = getColumnSortKey(col);
		if (!key) return;

		if (sortKey === key) {
			if (sortDirection === 'asc') {
				sortDirection = 'desc';
			} else if (sortDirection === 'desc') {
				sortDirection = null;
				sortKey = null;
			} else {
				sortDirection = 'asc';
			}
		} else {
			sortKey = key;
			sortDirection = 'asc';
		}
		// Reset to first page when sort changes
		currentPage = 1;
	}

	// Sorted items derivation
	const sortedItems = $derived.by(() => {
		if (!sortKey || !sortDirection) {
			return [...items];
		}

		return [...items].sort((a, b) => {
			const aVal = (a as any)[sortKey!];
			const bVal = (b as any)[sortKey!];

			if (aVal == null && bVal == null) return 0;
			if (aVal == null) return sortDirection === 'asc' ? 1 : -1;
			if (bVal == null) return sortDirection === 'asc' ? -1 : 1;

			if (typeof aVal === 'number' && typeof bVal === 'number') {
				return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
			}

			if (typeof aVal === 'boolean' && typeof bVal === 'boolean') {
				return sortDirection === 'asc'
					? aVal === bVal
						? 0
						: aVal
							? -1
							: 1
					: aVal === bVal
						? 0
						: aVal
							? 1
							: -1;
			}

			const aStr = String(aVal).toLowerCase();
			const bStr = String(bVal).toLowerCase();

			return sortDirection === 'asc'
				? aStr.localeCompare(bStr, undefined, { numeric: true, sensitivity: 'base' })
				: bStr.localeCompare(aStr, undefined, { numeric: true, sensitivity: 'base' });
		});
	});

	// Pagination calculations
	const totalItems = $derived(sortedItems.length);
	const totalPages = $derived(Math.max(1, Math.ceil(totalItems / pageSize)));

	// Automatically clamp current page when totalPages changes
	$effect(() => {
		if (currentPage > totalPages) {
			currentPage = totalPages;
		} else if (currentPage < 1) {
			currentPage = 1;
		}
	});

	// Displayed items slice
	const displayedItems = $derived.by(() => {
		if (!paginated) return sortedItems;
		const start = (currentPage - 1) * pageSize;
		return sortedItems.slice(start, start + pageSize);
	});

	const startItemIndex = $derived(totalItems === 0 ? 0 : (currentPage - 1) * pageSize + 1);
	const endItemIndex = $derived(Math.min(currentPage * pageSize, totalItems));

	// Visible page numbers calculation for pagination buttons
	const visiblePageNumbers = $derived.by(() => {
		const pages: (number | string)[] = [];
		if (totalPages <= 5) {
			for (let i = 1; i <= totalPages; i++) {
				pages.push(i);
			}
		} else {
			if (currentPage <= 3) {
				pages.push(1, 2, 3, 4, '...', totalPages);
			} else if (currentPage >= totalPages - 2) {
				pages.push(1, '...', totalPages - 3, totalPages - 2, totalPages - 1, totalPages);
			} else {
				pages.push(1, '...', currentPage - 1, currentPage, currentPage + 1, '...', totalPages);
			}
		}
		return pages;
	});
</script>

<div
	class="rounded-2xl border border-slate-200/70 dark:border-white/[0.06] bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] overflow-hidden {className}"
>
	<!-- Header Bar (if title, icon, badge, or headerActions provided) -->
	{#if title || headerActions || badge}
		<div class="p-4 border-b border-slate-100 dark:border-white/5 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
			<div>
				{#if title}
					<h3 class="text-xs font-semibold text-slate-900 dark:text-white uppercase tracking-wider flex items-center gap-2">
						{#if IconComponent}
							<IconComponent class="w-4 h-4 text-[#007AFF] dark:text-[#0A84FF] shrink-0" />
						{/if}
						<span>{title}</span>
					</h3>
				{/if}
				{#if subtitle}
					<p class="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
						{subtitle}
					</p>
				{/if}
			</div>

			<div class="flex items-center gap-2 self-start sm:self-auto">
				{#if badge}
					<span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-100 dark:bg-white/5 text-slate-500 dark:text-slate-400 border border-slate-200/60 dark:border-white/10">
						{badge}
					</span>
				{/if}
				{#if headerActions}
					{@render headerActions()}
				{/if}
			</div>
		</div>
	{/if}

	<!-- Responsive Table Container -->
	<div class="overflow-x-auto">
		<table class="w-full text-xs text-left">
			<thead>
				<tr class="border-b border-slate-100 dark:border-white/5 text-slate-400 font-semibold bg-slate-50/50 dark:bg-white/[0.02]">
					{#each columns as col}
						{@const sortable = isColumnSortable(col)}
						{@const isSorted = sortKey === getColumnSortKey(col)}
						<th
							class="p-3.5 whitespace-nowrap {col.class || ''} {col.align === 'center'
								? 'text-center'
								: col.align === 'right'
									? 'text-right'
									: 'text-left'}"
							style={col.width ? `width: ${col.width}` : undefined}
						>
							{#if sortable}
								<button
									type="button"
									onclick={() => handleSort(col)}
									class="inline-flex items-center gap-1.5 group select-none cursor-pointer font-semibold text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors {col.align === 'center' ? 'mx-auto' : col.align === 'right' ? 'ml-auto' : ''}"
									title={`Urutkan berdasarkan ${col.header}`}
								>
									<span>{col.header}</span>
									<span class="inline-flex shrink-0 transition-transform">
										{#if isSorted && sortDirection === 'asc'}
											<ArrowUp class="w-3.5 h-3.5 text-[#007AFF] dark:text-[#0A84FF]" />
										{:else if isSorted && sortDirection === 'desc'}
											<ArrowDown class="w-3.5 h-3.5 text-[#007AFF] dark:text-[#0A84FF]" />
										{:else}
											<ArrowUpDown class="w-3 h-3 text-slate-300 dark:text-white/20 group-hover:text-slate-500 dark:group-hover:text-slate-300 transition-colors" />
										{/if}
									</span>
								</button>
							{:else}
								<span>{col.header}</span>
							{/if}
						</th>
					{/each}
				</tr>
			</thead>
			<tbody class="divide-y divide-slate-100 dark:divide-white/5">
				{#if displayedItems.length > 0}
					{#each displayedItems as item, index}
						{@const absoluteIndex = (currentPage - 1) * pageSize + index}
						{#if row}
							{@render row(item, absoluteIndex)}
						{:else}
							<tr class="hover:bg-slate-50/60 dark:hover:bg-white/[0.02] transition-colors">
								{#each columns as col}
									<td
										class="p-3.5 {col.align === 'center'
											? 'text-center'
											: col.align === 'right'
												? 'text-right'
												: 'text-left'}"
									>
										{col.key ? (item as any)[col.key] : ''}
									</td>
								{/each}
							</tr>
						{/if}
					{/each}
				{:else}
					<tr>
						<td colspan={columns.length} class="p-8 text-center">
							<div class="flex flex-col items-center justify-center gap-2 max-w-sm mx-auto">
								<div class="w-10 h-10 rounded-2xl bg-slate-100 dark:bg-white/5 text-slate-400 flex items-center justify-center">
									<Inbox class="w-5 h-5" />
								</div>
								<p class="text-xs font-semibold text-slate-700 dark:text-slate-200">
									{emptyMessage}
								</p>
								<p class="text-[11px] text-slate-400">
									{emptyDescription}
								</p>
							</div>
						</td>
					</tr>
				{/if}
			</tbody>
		</table>
	</div>

	<!-- Optional Supplementary Footer Slot (e.g. legends) -->
	{#if footer}
		<div class="p-3 border-t border-slate-100 dark:border-white/5 bg-slate-50/40 dark:bg-white/[0.01]">
			{@render footer()}
		</div>
	{/if}

	<!-- Built-in Pagination Bar -->
	{#if paginated}
		<div class="p-3 border-t border-slate-100 dark:border-white/5 bg-slate-50/50 dark:bg-white/[0.015] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
			<!-- Left: Page Size Selector (10, 50, 100) & Showing Info -->
			<div class="flex items-center gap-2.5">
				<div class="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
					<label for="table-page-size" class="font-medium whitespace-nowrap">
						Tampilkan:
					</label>
					<select
						id="table-page-size"
						bind:value={pageSize}
						onchange={() => (currentPage = 1)}
						class="h-8 px-2.5 rounded-lg border border-slate-200/80 dark:border-white/10 bg-white dark:bg-[#151926] text-xs font-semibold text-slate-700 dark:text-slate-200 focus:outline-none focus:border-[#007AFF] transition-colors cursor-pointer"
					>
						{#each pageSizeOptions as opt}
							<option value={opt}>{opt}</option>
						{/each}
					</select>
					<span class="text-slate-400 whitespace-nowrap">baris per halaman</span>
				</div>

				<span class="hidden md:inline-block text-slate-300 dark:text-white/10">|</span>

				<div class="hidden md:block text-xs text-slate-400">
					{#if totalItems > 0}
						Menampilkan <span class="font-semibold text-slate-700 dark:text-slate-200">{startItemIndex}-{endItemIndex}</span> dari <span class="font-semibold text-slate-700 dark:text-slate-200">{totalItems}</span> data
					{:else}
						0 data
					{/if}
				</div>
			</div>

			<!-- Right: Pagination System -->
			<div class="flex items-center justify-between sm:justify-end gap-2 text-xs self-stretch sm:self-auto">
				<!-- Mobile showing counter -->
				<div class="block md:hidden text-[11px] text-slate-400 font-medium">
					{totalItems > 0 ? `${startItemIndex}-${endItemIndex} dari ${totalItems}` : '0 data'}
				</div>

				<div class="flex items-center gap-1">
					<!-- First page button -->
					<button
						type="button"
						onclick={() => (currentPage = 1)}
						disabled={currentPage === 1 || totalItems === 0}
						class="w-8 h-8 rounded-lg flex items-center justify-center text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white hover:bg-slate-200/60 dark:hover:bg-white/10 disabled:opacity-30 disabled:pointer-events-none transition-colors cursor-pointer"
						title="Halaman Pertama"
					>
						<ChevronsLeft class="w-4 h-4" />
					</button>

					<!-- Prev page button -->
					<button
						type="button"
						onclick={() => (currentPage = Math.max(1, currentPage - 1))}
						disabled={currentPage === 1 || totalItems === 0}
						class="w-8 h-8 rounded-lg flex items-center justify-center text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white hover:bg-slate-200/60 dark:hover:bg-white/10 disabled:opacity-30 disabled:pointer-events-none transition-colors cursor-pointer"
						title="Halaman Sebelumnya"
					>
						<ChevronLeft class="w-4 h-4" />
					</button>

					<!-- Page Numbers -->
					<div class="flex items-center gap-1 px-0.5">
						{#each visiblePageNumbers as p}
							{#if typeof p === 'number'}
								<button
									type="button"
									onclick={() => (currentPage = p)}
									class="min-w-8 h-8 px-2 rounded-lg text-xs font-semibold transition-colors cursor-pointer {currentPage === p
										? 'bg-[#007AFF] text-white shadow-xs'
										: 'text-slate-600 dark:text-slate-400 hover:bg-slate-200/60 dark:hover:bg-white/10'}"
								>
									{p}
								</button>
							{:else}
								<span class="px-1 text-slate-400 select-none">...</span>
							{/if}
						{/each}
					</div>

					<!-- Next page button -->
					<button
						type="button"
						onclick={() => (currentPage = Math.min(totalPages, currentPage + 1))}
						disabled={currentPage >= totalPages || totalItems === 0}
						class="w-8 h-8 rounded-lg flex items-center justify-center text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white hover:bg-slate-200/60 dark:hover:bg-white/10 disabled:opacity-30 disabled:pointer-events-none transition-colors cursor-pointer"
						title="Halaman Berikutnya"
					>
						<ChevronRight class="w-4 h-4" />
					</button>

					<!-- Last page button -->
					<button
						type="button"
						onclick={() => (currentPage = totalPages)}
						disabled={currentPage >= totalPages || totalItems === 0}
						class="w-8 h-8 rounded-lg flex items-center justify-center text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white hover:bg-slate-200/60 dark:hover:bg-white/10 disabled:opacity-30 disabled:pointer-events-none transition-colors cursor-pointer"
						title="Halaman Terakhir"
					>
						<ChevronsRight class="w-4 h-4" />
					</button>
				</div>
			</div>
		</div>
	{/if}
</div>

