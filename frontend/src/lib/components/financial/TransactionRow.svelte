<script lang="ts">
	import type { Transaction } from '$lib/types';
	import { formatRupiah, formatDateTime } from '$lib/utils/formatters';
	import {
		Utensils,
		Car,
		ShoppingBag,
		Film,
		Bolt,
		Banknote,
		Laptop,
		ArrowLeftRight,
		Send,
		Receipt,
		Trash2,
		Crown,
		Sparkles,
		Server,
		Globe,
		Database,
		Shield,
		Cpu,
		Users
	} from 'lucide-svelte';

	interface Props {
		transaction: Transaction;
		ondelete?: (id: string) => void;
	}

	let { transaction, ondelete }: Props = $props();

	// Map category icon
	function getIcon(iconName?: string) {
		switch (iconName) {
			case 'crown':
				return Crown;
			case 'sparkles':
				return Sparkles;
			case 'server':
				return Server;
			case 'globe':
				return Globe;
			case 'database':
				return Database;
			case 'shield':
				return Shield;
			case 'cpu':
				return Cpu;
			case 'users':
				return Users;
			case 'utensils':
				return Utensils;
			case 'car':
				return Car;
			case 'shopping-cart':
				return ShoppingBag;
			case 'film':
				return Film;
			case 'bolt':
				return Bolt;
			case 'money-bill-wave':
				return Banknote;
			case 'laptop-code':
				return Laptop;
			default:
				return Receipt;
		}
	}

	const isIncome = $derived(transaction.transaction_type === 'INCOME');
	const isTransfer = $derived(transaction.transaction_type === 'TRANSFER');
	const isExpense = $derived(transaction.transaction_type === 'EXPENSE');

	const amountPrefix = $derived(isIncome ? '+ ' : isExpense ? '- ' : '⇄ ');
	const amountColor = $derived(
		isIncome
			? 'text-emerald-600 dark:text-emerald-400'
			: isExpense
				? 'text-slate-900 dark:text-white'
				: 'text-[#007AFF] dark:text-[#0A84FF]'
	);

	const CategoryIcon = $derived(getIcon(transaction.category_icon));
</script>

<div
	class="flex items-center justify-between px-3.5 py-2.5 sm:px-5 sm:py-3.5 hover:bg-slate-50/80 dark:hover:bg-white/[0.02] transition-colors duration-150 group"
>
	<!-- Left: Category Icon & Details -->
	<div class="flex items-center gap-2.5 sm:gap-3 min-w-0 flex-1 mr-2">
		<div
			class="w-8 h-8 sm:w-9 sm:h-9 rounded-lg sm:rounded-xl flex items-center justify-center shrink-0 text-white font-semibold"
			style="background-color: {isTransfer ? '#007AFF' : transaction.category_color || '#64748B'};"
		>
			{#if isTransfer}
				<ArrowLeftRight class="w-3.5 h-3.5 sm:w-4 sm:h-4 text-white" />
			{:else}
				<CategoryIcon class="w-3.5 h-3.5 sm:w-4 sm:h-4 text-white" />
			{/if}
		</div>

		<div class="flex flex-col min-w-0 flex-1">
			<span class="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white truncate tracking-tight">
				{transaction.description}
			</span>

			<div class="flex items-center gap-1.5 text-[11px] sm:text-xs text-slate-500 dark:text-slate-400 mt-0.5 min-w-0">
				<span class="truncate">
					{isTransfer
						? `${transaction.account_name} → ${transaction.destination_account_name}`
						: transaction.category_name || transaction.account_name}
				</span>
				<span class="shrink-0">•</span>
				<span class="shrink-0">{formatDateTime(transaction.transaction_date)}</span>

				{#if transaction.source === 'TELEGRAM'}
					<span
						class="inline-flex items-center gap-0.5 px-1.5 py-0.2 text-[9px] sm:text-[10px] font-semibold rounded bg-[#007AFF]/10 text-[#007AFF] dark:text-[#0A84FF] shrink-0"
					>
						<Send class="w-2.5 h-2.5" />
						TG
					</span>
				{/if}
			</div>
		</div>
	</div>

	<!-- Right: Amount & Delete Button -->
	<div class="flex items-center gap-1.5 sm:gap-3 shrink-0">
		<span class="text-xs sm:text-base font-semibold tracking-tight {amountColor} text-right">
			{amountPrefix}{formatRupiah(transaction.amount)}
		</span>

		{#if ondelete}
			<button
				type="button"
				onclick={() => ondelete(transaction.id)}
				class="opacity-30 sm:opacity-0 sm:group-hover:opacity-100 hover:opacity-100 transition-opacity p-1 sm:p-1.5 rounded-lg text-slate-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/30 cursor-pointer"
				aria-label="Hapus transaksi"
			>
				<Trash2 class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
			</button>
		{/if}
	</div>
</div>
