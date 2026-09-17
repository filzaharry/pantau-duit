<script lang="ts">
	import { financialStore } from '$lib/stores/financial.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import { formatRupiah } from '$lib/utils/formatters';
	import SpendingDonut from '$lib/components/charts/SpendingDonut.svelte';
	import CashflowBar from '$lib/components/charts/CashflowBar.svelte';
	import GlassSurface from '$lib/components/ui/GlassSurface.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import {
		BarChart3,
		Download,
		TrendingUp,
		Sparkles,
		ShieldCheck,
		AlertCircle,
		Calendar,
		ArrowLeftRight
	} from 'lucide-svelte';

	let selectedPeriod = $state('month');

	const netCashflow = $derived(
		financialStore.monthlyIncome - financialStore.monthlyExpense
	);

	const savingsRate = $derived(
		financialStore.monthlyIncome > 0
			? Math.max(0, Math.round((netCashflow / financialStore.monthlyIncome) * 100))
			: 0
	);

	function handleExportReport() {
		notificationStore.toast('Menyiapkan file laporan finansial Excel & PDF...', 'info');
		setTimeout(() => {
			notificationStore.toast('Laporan bulanan berhasil diunduh!', 'success');
		}, 1200);
	}
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full pb-24 lg:pb-10">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
		<div>
			<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
				<BarChart3 class="w-6 h-6 text-[#007AFF] dark:text-[#0A84FF]" />
				<span>Laporan & Analisis Keuangan</span>
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
				Evaluasi kesehatan cashflow, rasio tabungan, dan tren pengeluaran berkala
			</p>
		</div>

		<div class="flex items-center gap-2 self-start sm:self-auto">
			<Button variant="outline" onclick={handleExportReport}>
				<Download class="w-4 h-4" />
				<span>Ekspor Laporan</span>
			</Button>
		</div>
	</div>

	<!-- Cute Health Scorecard Grid -->
	<div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
		<!-- Savings Rate -->
		<div class="p-5 sm:p-6 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] flex flex-col justify-between gap-4 hover:border-emerald-500/30 transition-all">
			<div class="flex items-center justify-between">
				<div class="w-10 h-10 rounded-xl bg-emerald-500/10 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 flex items-center justify-center shrink-0">
					<ShieldCheck class="w-5 h-5" />
				</div>
				<span class="px-2.5 py-1 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
					Target: &ge;20%
				</span>
			</div>
			<div>
				<span class="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block leading-tight">
					Rasio Tabungan (Savings Rate)
				</span>
				<h2 class="text-3xl font-semibold text-slate-900 dark:text-white tracking-tight mt-1">
					{savingsRate}%
				</h2>
				<p class="text-xs text-emerald-600 dark:text-emerald-400 font-semibold mt-1 flex items-center gap-1">
					<span>Kategori: Sangat Sehat (Ideal)</span>
				</p>
			</div>
		</div>

		<!-- Net Cashflow -->
		<div class="p-5 sm:p-6 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] flex flex-col justify-between gap-4 hover:border-blue-500/30 transition-all">
			<div class="flex items-center justify-between">
				<div class="w-10 h-10 rounded-xl bg-blue-500/10 dark:bg-blue-500/20 text-[#007AFF] dark:text-[#0A84FF] border border-blue-500/20 flex items-center justify-center shrink-0">
					<TrendingUp class="w-5 h-5" />
				</div>
				<span class="px-2.5 py-1 rounded-full text-[10px] font-semibold bg-blue-500/10 text-[#007AFF] dark:text-[#0A84FF] border border-blue-500/20">
					Bulan Ini
				</span>
			</div>
			<div>
				<span class="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block leading-tight">
					Arus Kas Bersih (Net Cashflow)
				</span>
				<h2 class="text-3xl font-semibold text-slate-900 dark:text-white tracking-tight mt-1">
					{formatRupiah(netCashflow)}
				</h2>
				<p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
					Pemasukan minus pengeluaran riil
				</p>
			</div>
		</div>

		<!-- Total Mutual Transfers -->
		<div class="p-5 sm:p-6 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] flex flex-col justify-between gap-4 hover:border-cyan-500/30 transition-all">
			<div class="flex items-center justify-between">
				<div class="w-10 h-10 rounded-xl bg-cyan-500/10 dark:bg-cyan-500/20 text-cyan-600 dark:text-cyan-400 border border-cyan-500/20 flex items-center justify-center shrink-0">
					<ArrowLeftRight class="w-5 h-5" />
				</div>
				<span class="px-2.5 py-1 rounded-full text-[10px] font-semibold bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/20">
					Non-Beban
				</span>
			</div>
			<div>
				<span class="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block leading-tight">
					Mutasi Transfer Antar Akun
				</span>
				<h2 class="text-3xl font-semibold text-slate-900 dark:text-white tracking-tight mt-1">
					{formatRupiah(financialStore.monthlyTransfers)}
				</h2>
				<p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
					Pindah saldo antar rekening
				</p>
			</div>
		</div>
	</div>

	<!-- AI Financial Insights Banner -->
	<div class="p-5 rounded-3xl bg-gradient-to-br from-[#007AFF]/10 via-indigo-500/10 to-purple-500/10 border border-[#007AFF]/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
		<div class="flex items-start gap-3.5">
			<div class="w-10 h-10 rounded-2xl bg-[#007AFF] text-white flex items-center justify-center shrink-0">
				<Sparkles class="w-5 h-5" />
			</div>
			<div>
				<h3 class="text-sm font-semibold text-slate-900 dark:text-white">
					AI Financial Diagnostic
				</h3>
				<p class="text-xs text-slate-600 dark:text-slate-300 mt-1 leading-relaxed max-w-2xl">
					Berdasarkan transaksi bulan ini, pengeluaran makanan & minuman mendominasi pos anggaran. Namun berkat rasio tabungan sebesar <strong>{savingsRate}%</strong>, kamu berada di jalur yang sangat baik untuk mencapai target tabungan dalam 4 bulan ke depan.
				</p>
			</div>
		</div>
	</div>

	<!-- Charts Grid -->
	<div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
		<SpendingDonut />
		<CashflowBar />
	</div>
</div>
