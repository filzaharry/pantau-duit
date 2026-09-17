<script lang="ts">
	import { financialStore } from '$lib/stores/financial.svelte';
	import { formatRupiah } from '$lib/utils/formatters';
	import GlassSurface from '$lib/components/ui/GlassSurface.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import { TrendingUp, ArrowDownLeft, ArrowUpRight, ArrowLeftRight, Plus, Send } from 'lucide-svelte';

	interface Props {
		onAddExpense?: () => void;
		onAddTransfer?: () => void;
		onOpenTelegram?: () => void;
	}

	let { onAddExpense, onAddTransfer, onOpenTelegram }: Props = $props();
</script>

<GlassSurface elevated class="p-5 sm:p-6 overflow-hidden relative">
	<!-- Subtle ambient glow background -->
	<div
		class="absolute -top-16 -right-16 w-48 h-48 rounded-full bg-[#007AFF]/10 dark:bg-[#0A84FF]/10 blur-3xl pointer-events-none"
	></div>

	<div class="flex flex-col gap-4">
		<!-- Title & Workspace Tag -->
		<div class="flex items-center justify-between">
			<span class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
				Total Saldo Tersedia
			</span>
			<span
				class="inline-flex items-center gap-1 text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
			>
				<TrendingUp class="w-3 h-3" />
				+8.4% bln ini
			</span>
		</div>

		<!-- Big Prominent Financial Number -->
		<div class="flex items-baseline gap-2">
			<h1 class="text-3xl sm:text-4xl font-semibold text-slate-900 dark:text-white tracking-tight">
				{formatRupiah(financialStore.totalBalance)}
			</h1>
		</div>

		<!-- Cashflow Summary Pills -->
		<div class="grid grid-cols-2 sm:grid-cols-3 gap-2.5 pt-1">
			<!-- Pemasukan -->
			<div class="flex items-center gap-2.5 p-3 rounded-xl bg-slate-50 dark:bg-white/[0.03] border border-slate-100 dark:border-white/5">
				<div class="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
					<ArrowDownLeft class="w-4 h-4" />
				</div>
				<div class="flex flex-col min-w-0">
					<span class="text-[11px] text-slate-500 dark:text-slate-400 leading-none">Pemasukan</span>
					<span class="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white truncate mt-0.5">
						{formatRupiah(financialStore.monthlyIncome, true)}
					</span>
				</div>
			</div>

			<!-- Pengeluaran (Transfers excluded!) -->
			<div class="flex items-center gap-2.5 p-3 rounded-xl bg-slate-50 dark:bg-white/[0.03] border border-slate-100 dark:border-white/5">
				<div class="w-8 h-8 rounded-lg bg-rose-500/10 text-rose-600 dark:text-rose-400 flex items-center justify-center shrink-0">
					<ArrowUpRight class="w-4 h-4" />
				</div>
				<div class="flex flex-col min-w-0">
					<span class="text-[11px] text-slate-500 dark:text-slate-400 leading-none">Pengeluaran</span>
					<span class="text-xs sm:text-sm font-semibold text-rose-600 dark:text-rose-400 truncate mt-0.5">
						{formatRupiah(financialStore.monthlyExpense, true)}
					</span>
				</div>
			</div>

			<!-- Transfer / Portofolio -->
			<div class="col-span-2 sm:col-span-1 flex items-center gap-2.5 p-3 rounded-xl bg-slate-50 dark:bg-white/[0.03] border border-slate-100 dark:border-white/5">
				<div class="w-8 h-8 rounded-lg bg-[#007AFF]/10 text-[#007AFF] dark:text-[#0A84FF] flex items-center justify-center shrink-0">
					<ArrowLeftRight class="w-4 h-4" />
				</div>
				<div class="flex flex-col min-w-0">
					<span class="text-[11px] text-slate-500 dark:text-slate-400 leading-none">Transfer Antar Akun</span>
					<span class="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white truncate mt-0.5">
						{formatRupiah(financialStore.monthlyTransfers, true)}
					</span>
				</div>
			</div>
		</div>

		<!-- Quick Action Buttons -->
		<div class="flex items-center gap-2 pt-2">
			<Button variant="primary" class="flex-1" onclick={onAddExpense}>
				<Plus class="w-4 h-4" />
				<span>Catat Transaksi</span>
			</Button>

			<Button variant="outline" class="flex-1" onclick={onAddTransfer}>
				<ArrowLeftRight class="w-4 h-4" />
				<span>Transfer</span>
			</Button>

			<Button variant="ghost" class="shrink-0 text-[#007AFF] dark:text-[#0A84FF] border border-[#007AFF]/20" onclick={onOpenTelegram}>
				<Send class="w-4 h-4" />
				<span class="hidden sm:inline text-xs font-semibold">Telegram Bot</span>
			</Button>
		</div>
	</div>
</GlassSurface>
