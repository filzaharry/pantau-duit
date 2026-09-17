<script lang="ts">
	import { authStore } from '$lib/stores/auth.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import { formatRupiah } from '$lib/utils/formatters';
	import GlassSurface from '$lib/components/ui/GlassSurface.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Table, { type TableColumn } from '$lib/components/ui/Table.svelte';
	import {
		Crown,
		Check,
		Sparkles,
		ShieldCheck,
		CreditCard,
		Receipt,
		ArrowRight
	} from 'lucide-svelte';

	let billingCycle = $state<'monthly' | 'yearly'>('monthly');

	function handleUpgrade(tierName: string) {
		notificationStore.toast(`Menghubungkan ke gateway pembayaran untuk paket ${tierName}...`, 'info');
		setTimeout(() => {
			notificationStore.toast(`Selamat! Akun Anda telah ditingkatkan ke ${tierName}!`, 'success');
		}, 1500);
	}

	const plans = [
		{
			id: 'free',
			name: 'Starter (Gratis)',
			priceMonthly: 0,
			priceYearly: 0,
			description: 'Cocok untuk mencoba pencatatan keuangan pribadi dasar.',
			features: [
				'Maksimal 2 Rekening / Dompet',
				'Maksimal 50 pesan Telegram / bulan',
				'Pencatatan Pemasukan & Pengeluaran',
				'Laporan ringkas bulanan',
				'Dukungan komunitas'
			],
			current: authStore.subscription?.tier === 'free',
			highlight: false
		},
		{
			id: 'pro',
			name: 'Pro Member',
			priceMonthly: 49000,
			priceYearly: 470000,
			description: 'Paling populer untuk profesional yang mengutamakan kecepatan Telegram.',
			features: [
				'Pesan Telegram Tanpa Batas (Unlimited)',
				'Hingga 20 Rekening & E-Wallet',
				'Transfer Antar Akun Lengkap',
				'AI Natural Language Parser',
				'Anggaran & Target Tak Terbatas',
				'Ekspor Excel & PDF Laporan',
				'Dukungan Prioritas 24/7'
			],
			current: authStore.subscription?.tier === 'pro',
			highlight: true
		},
		{
			id: 'enterprise',
			name: 'Family & Bisnis',
			priceMonthly: 149000,
			priceYearly: 1430000,
			description: 'Untuk keluarga atau UMKM yang membutuhkan multi-user dan kolaborasi tim.',
			features: [
				'Semua fitur Pro tanpa batas',
				'Multi-User RBAC (Role Based Access)',
				'Dedicated Telegram Bot Instance',
				'Audit Trail Keuangan Lengkap',
				'Webhook & API Access',
				'Konsultasi Perencana Keuangan'
			],
			current: authStore.subscription?.tier === 'enterprise',
			highlight: false
		}
	];

	const invoices = [
		{
			id: 'inv-1',
			invoiceNumber: '#INV-2026-0815',
			date: '15 Agu 2026',
			plan: 'PantauDuit Pro (1 Bulan)',
			amount: 49000,
			status: 'Lunas'
		},
		{
			id: 'inv-2',
			invoiceNumber: '#INV-2026-0715',
			date: '15 Jul 2026',
			plan: 'PantauDuit Pro (1 Bulan)',
			amount: 49000,
			status: 'Lunas'
		},
		{
			id: 'inv-3',
			invoiceNumber: '#INV-2026-0615',
			date: '15 Jun 2026',
			plan: 'PantauDuit Pro (1 Bulan)',
			amount: 49000,
			status: 'Lunas'
		}
	];

	const invoiceColumns: TableColumn<any>[] = [
		{ key: 'invoiceNumber', header: 'No. Faktur', sortable: true },
		{ key: 'date', header: 'Tanggal', sortable: true },
		{ key: 'plan', header: 'Paket', sortable: true },
		{ key: 'amount', header: 'Jumlah', sortable: true, align: 'right' },
		{ key: 'status', header: 'Status', sortable: true, align: 'right' }
	];
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
		<div>
			<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
				<Crown class="w-6 h-6 text-amber-500" />
				<span>Paket Langganan & Kuota SaaS</span>
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
				Kelola paket langganan aktif, kuota akun, dan riwayat pembayaran faktur
			</p>
		</div>

		<!-- Billing Cycle Toggle -->
		<div class="p-1 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200/70 dark:border-white/10 flex items-center gap-1 self-start sm:self-auto">
			<button
				type="button"
				onclick={() => (billingCycle = 'monthly')}
				class="px-3 py-1.5 rounded-xl text-xs font-semibold transition-all {billingCycle === 'monthly'
					? 'bg-white dark:bg-[#131B2A] text-slate-900 dark:text-white'
					: 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'}"
			>
				Bulanan
			</button>
			<button
				type="button"
				onclick={() => (billingCycle = 'yearly')}
				class="px-3 py-1.5 rounded-xl text-xs font-semibold transition-all flex items-center gap-1 {billingCycle === 'yearly'
					? 'bg-white dark:bg-[#131B2A] text-slate-900 dark:text-white'
					: 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'}"
			>
				<span>Tahunan</span>
				<span class="px-1.5 py-0.2 rounded text-[9px] font-semibold bg-emerald-500 text-white">Hemat 20%</span>
			</button>
		</div>
	</div>

	<!-- Current Active Plan Banner -->
	<div class="p-6 sm:p-7 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
		<div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
			<div class="flex items-center gap-4">
				<div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-[#007AFF] to-[#0055B3] text-white flex items-center justify-center font-semibold text-xl">
					<Crown class="w-6 h-6" />
				</div>
				<div>
					<div class="flex items-center gap-2">
						<h2 class="text-base font-semibold text-slate-900 dark:text-white">
							Paket Saat Ini: {authStore.subscription?.tier?.toUpperCase() || 'PRO'}
						</h2>
						<span class="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
							Aktif
						</span>
					</div>
					<p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
						Periode tagihan aktif &bull; Berakhir pada <strong>15 Oktober 2026</strong>
					</p>
				</div>
			</div>

			<!-- Quick Limits Usage Bar -->
			<div class="flex items-center gap-6">
				<div class="text-right">
					<span class="text-[11px] text-slate-400 uppercase font-semibold tracking-wider">Telegram Sync</span>
					<p class="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white mt-0.5">Unlimited</p>
				</div>
				<div class="text-right">
					<span class="text-[11px] text-slate-400 uppercase font-semibold tracking-wider">Slot Rekening</span>
					<p class="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white mt-0.5">4 / 20 Akun</p>
				</div>
			</div>
		</div>
	</div>

	<!-- Plans Comparison Cards -->
	<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
		{#each plans as plan}
			{@const price = billingCycle === 'monthly' ? plan.priceMonthly : plan.priceYearly}
			<div
				class="p-6 sm:p-7 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] flex flex-col justify-between relative transition-all duration-200 hover:-translate-y-1 {plan.highlight
					? 'ring-2 ring-[#007AFF]'
					: ''}"
			>
				{#if plan.highlight}
					<div class="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-gradient-to-r from-[#007AFF] to-[#0055B3] text-white text-[10px] font-semibold tracking-wider uppercase">
						Pilihan Utama
					</div>
				{/if}

				<div>
					<h3 class="text-base font-semibold text-slate-900 dark:text-white">
						{plan.name}
					</h3>
					<p class="text-xs text-slate-500 dark:text-slate-400 mt-1 min-h-[32px]">
						{plan.description}
					</p>

					<div class="mt-4 mb-6">
						<span class="text-3xl font-semibold text-slate-900 dark:text-white tracking-tight">
							{price === 0 ? 'Gratis' : formatRupiah(price)}
						</span>
						{#if price > 0}
							<span class="text-xs text-slate-400 font-semibold">
								/{billingCycle === 'monthly' ? 'bulan' : 'tahun'}
							</span>
						{/if}
					</div>

					<!-- Features List -->
					<div class="space-y-2.5 mb-6">
						{#each plan.features as feat}
							<div class="flex items-start gap-2.5 text-xs text-slate-600 dark:text-slate-300">
								<Check class="w-4 h-4 text-[#007AFF] dark:text-[#0A84FF] shrink-0 mt-0.5" />
								<span>{feat}</span>
							</div>
						{/each}
					</div>
				</div>

				<div>
					{#if plan.current}
						<button
							type="button"
							disabled
							class="w-full py-3 rounded-2xl bg-slate-100 dark:bg-white/5 text-slate-400 dark:text-slate-500 text-xs font-semibold cursor-default"
						>
							Paket Aktif Anda
						</button>
					{:else}
						<Button
							variant={plan.highlight ? 'primary' : 'outline'}
							class="w-full"
							onclick={() => handleUpgrade(plan.name)}
						>
							<span>Pilih Paket {plan.name}</span>
						</Button>
					{/if}
				</div>
			</div>
		{/each}
	</div>

	<!-- Billing History Section -->
	<Table
		title="Riwayat Pembayaran & Faktur"
		subtitle="Daftar faktur tagihan dan mutasi pembayaran paket langganan"
		icon={Receipt}
		badge="{invoices.length} Faktur"
		columns={invoiceColumns}
		items={invoices}
		emptyMessage="Belum ada riwayat faktur"
		emptyDescription="Faktur pembayaran akan tercatat otomatis saat Anda berlangganan."
	>
		{#snippet row(inv, index)}
			<tr class="hover:bg-slate-50/60 dark:hover:bg-white/[0.02] transition-colors">
				<td class="p-3.5 whitespace-nowrap font-mono font-semibold text-slate-900 dark:text-white">
					{inv.invoiceNumber}
				</td>
				<td class="p-3.5 whitespace-nowrap text-xs text-slate-500">
					{inv.date}
				</td>
				<td class="p-3.5 whitespace-nowrap text-xs font-semibold text-slate-900 dark:text-white">
					{inv.plan}
				</td>
				<td class="p-3.5 whitespace-nowrap text-right font-semibold text-xs text-slate-900 dark:text-white">
					{formatRupiah(inv.amount)}
				</td>
				<td class="p-3.5 whitespace-nowrap text-right">
					<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-600 border border-emerald-500/20">
						{inv.status}
					</span>
				</td>
			</tr>
		{/snippet}
	</Table>
</div>
