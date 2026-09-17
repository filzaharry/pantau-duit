<script lang="ts">
	import { Calendar as CalendarIcon, ChevronLeft, ChevronRight } from 'lucide-svelte';

	interface Props {
		value?: string; // YYYY-MM-DD
		label?: string;
		error?: string;
		disabled?: boolean;
	}

	let {
		value = $bindable(new Date().toISOString().split('T')[0]),
		label,
		error,
		disabled = false
	}: Props = $props();

	let isOpen = $state(false);

	// Parse initial value or fallback to today
	let activeDate = $derived(() => {
		const parts = (value || '').split('-');
		if (parts.length === 3) {
			const y = parseInt(parts[0], 10);
			const m = parseInt(parts[1], 10) - 1;
			const d = parseInt(parts[2], 10);
			return new Date(y, m, d);
		}
		return new Date();
	});

	let currentYear = $state(new Date().getFullYear());
	let currentMonth = $state(new Date().getMonth());

	$effect(() => {
		const d = activeDate();
		if (!isNaN(d.getTime())) {
			currentYear = d.getFullYear();
			currentMonth = d.getMonth();
		}
	});

	const indonesianMonths = [
		'Januari',
		'Februari',
		'Maret',
		'April',
		'Mei',
		'Juni',
		'Juli',
		'Agustus',
		'September',
		'Oktober',
		'November',
		'Desember'
	];

	const daysOfWeek = ['Min', 'Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab'];

	// Formatted display value in Indonesian e.g. "12 September 2026"
	const formattedDisplay = $derived(() => {
		const d = activeDate();
		if (isNaN(d.getTime())) return value || 'Pilih tanggal';
		return `${d.getDate()} ${indonesianMonths[d.getMonth()]} ${d.getFullYear()}`;
	});

	// Grid generation for calendar
	const calendarDays = $derived(() => {
		const firstDayIndex = new Date(currentYear, currentMonth, 1).getDay();
		const daysInCurrentMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
		const daysInPrevMonth = new Date(currentYear, currentMonth, 0).getDate();

		const days: Array<{
			date: number;
			month: number;
			year: number;
			isCurrentMonth: boolean;
			dateString: string;
		}> = [];

		// Previous month's trailing days
		for (let i = firstDayIndex - 1; i >= 0; i--) {
			const d = daysInPrevMonth - i;
			const m = currentMonth === 0 ? 11 : currentMonth - 1;
			const y = currentMonth === 0 ? currentYear - 1 : currentYear;
			const dateStr = `${y}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
			days.push({
				date: d,
				month: m,
				year: y,
				isCurrentMonth: false,
				dateString: dateStr
			});
		}

		// Current month days
		for (let i = 1; i <= daysInCurrentMonth; i++) {
			const dateStr = `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
			days.push({
				date: i,
				month: currentMonth,
				year: currentYear,
				isCurrentMonth: true,
				dateString: dateStr
			});
		}

		// Next month leading days to complete grid to 35 or 42
		const totalCells = days.length > 35 ? 42 : 35;
		const nextDaysNeeded = totalCells - days.length;
		for (let i = 1; i <= nextDaysNeeded; i++) {
			const m = currentMonth === 11 ? 0 : currentMonth + 1;
			const y = currentMonth === 11 ? currentYear + 1 : currentYear;
			const dateStr = `${y}-${String(m + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
			days.push({
				date: i,
				month: m,
				year: y,
				isCurrentMonth: false,
				dateString: dateStr
			});
		}

		return days;
	});

	function prevMonth() {
		if (currentMonth === 0) {
			currentMonth = 11;
			currentYear -= 1;
		} else {
			currentMonth -= 1;
		}
	}

	function nextMonth() {
		if (currentMonth === 11) {
			currentMonth = 0;
			currentYear += 1;
		} else {
			currentMonth += 1;
		}
	}

	function selectDate(dateString: string) {
		value = dateString;
		isOpen = false;
	}

	function selectToday() {
		const now = new Date();
		const y = now.getFullYear();
		const m = String(now.getMonth() + 1).padStart(2, '0');
		const d = String(now.getDate()).padStart(2, '0');
		currentYear = y;
		currentMonth = now.getMonth();
		value = `${y}-${m}-${d}`;
		isOpen = false;
	}

	let containerEl: HTMLElement | null = $state(null);
	let openUpwards = $state(false);

	function toggleOpen() {
		if (disabled) return;
		isOpen = !isOpen;
		if (isOpen && containerEl) {
			const dialogEl = containerEl.closest('[role="dialog"]');
			const bottomBoundary = dialogEl
				? dialogEl.getBoundingClientRect().bottom
				: window.innerHeight;
			const spaceBelow = bottomBoundary - containerEl.getBoundingClientRect().bottom;
			openUpwards = spaceBelow < 200;
		}
	}

	function handleClickOutside(event: MouseEvent) {
		if (containerEl && !containerEl.contains(event.target as Node)) {
			isOpen = false;
		}
	}
</script>

<svelte:window onclick={handleClickOutside} />

<div class="relative w-full" bind:this={containerEl}>
	{#if label}
		<span class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
			{label}
		</span>
	{/if}

	<!-- Custom Trigger Box -->
	<button
		type="button"
		{disabled}
		onclick={toggleOpen}
		class="w-full h-9 flex items-center justify-between px-3 rounded-xl text-xs sm:text-sm bg-white dark:bg-[#151E2E] border border-slate-200/80 dark:border-white/10 hover:border-[#007AFF] text-slate-800 dark:text-slate-100 transition-colors focus:outline-none focus:ring-1 focus:ring-[#007AFF]/20 disabled:opacity-50 disabled:cursor-not-allowed"
	>
		<span class="font-medium text-slate-900 dark:text-white">
			{formattedDisplay()}
		</span>
		<CalendarIcon class="w-4 h-4 text-slate-400 dark:text-slate-500" />
	</button>

	<!-- Calendar Popover Menu -->
	{#if isOpen}
		<div
			class="absolute left-0 {openUpwards ? 'bottom-full mb-2' : 'top-full mt-2'} z-50 w-72 sm:w-80 p-3.5 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/90 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200 dark:border-white/10 animate-in fade-in zoom-in-95 duration-150"
		>
			<!-- Month / Year Nav Header -->
			<div class="flex items-center justify-between mb-3 pb-2 border-b border-slate-100 dark:border-white/5">
				<button
					type="button"
					onclick={prevMonth}
					class="p-1.5 rounded-lg text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/5 transition-colors"
					aria-label="Bulan Sebelumnya"
				>
					<ChevronLeft class="w-4 h-4" />
				</button>

				<div class="flex items-center gap-1.5">
					<span class="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white">
						{indonesianMonths[currentMonth]} {currentYear}
					</span>
				</div>

				<button
					type="button"
					onclick={nextMonth}
					class="p-1.5 rounded-lg text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/5 transition-colors"
					aria-label="Bulan Berikutnya"
				>
					<ChevronRight class="w-4 h-4" />
				</button>
			</div>

			<!-- Days of Week Header -->
			<div class="grid grid-cols-7 gap-1 text-center mb-1.5">
				{#each daysOfWeek as day}
					<span class="text-[11px] font-semibold text-slate-400 py-1">
						{day}
					</span>
				{/each}
			</div>

			<!-- Days Grid -->
			<div class="grid grid-cols-7 gap-1 text-center">
				{#each calendarDays() as dayItem}
					{@const isSelected = value === dayItem.dateString}
					{@const isToday =
						dayItem.dateString === new Date().toISOString().split('T')[0]}

					<button
						type="button"
						onclick={() => selectDate(dayItem.dateString)}
						class="h-8 w-8 mx-auto flex items-center justify-center rounded-xl text-xs transition-all {isSelected
							? 'bg-[#007AFF] text-white font-semibold'
							: isToday
								? 'border border-[#007AFF] text-[#007AFF] font-semibold hover:bg-[#007AFF]/10'
								: dayItem.isCurrentMonth
									? 'text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-white/5 font-medium'
									: 'text-slate-300 dark:text-slate-600 hover:bg-slate-50 dark:hover:bg-white/[0.02]'}"
					>
						{dayItem.date}
					</button>
				{/each}
			</div>

			<!-- Footer: Quick "Hari Ini" button -->
			<div class="mt-3 pt-2 border-t border-slate-100 dark:border-white/5 flex items-center justify-between">
				<span class="text-[11px] text-slate-400">Pilih cepat</span>
				<button
					type="button"
					onclick={selectToday}
					class="text-xs font-semibold text-[#007AFF] dark:text-[#0A84FF] hover:underline"
				>
					Hari Ini
				</button>
			</div>
		</div>
	{/if}

	{#if error}
		<p class="text-xs text-rose-500 mt-1">{error}</p>
	{/if}
</div>
