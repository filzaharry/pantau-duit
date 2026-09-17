<script lang="ts">
	import { formatRupiah, formatDate } from '$lib/utils/formatters';
	import {
		PayrollStatus,
		PayrollItemStatus,
		type PayrollRun,
		type PayrollItem
	} from '$lib/types/company';
	import StatusBadge from '$lib/components/ui/StatusBadge.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Sheet from '$lib/components/ui/Sheet.svelte';
	import Table, { type TableColumn } from '$lib/components/ui/Table.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import {
		Briefcase,
		Play,
		CheckCircle2,
		Download,
		Printer,
		FileText,
		ShieldCheck,
		CreditCard,
		Building2,
		ArrowDownRight,
		TrendingUp,
		Layers,
		Check,
		AlertCircle,
		Filter,
		Search,
		Eye
	} from 'lucide-svelte';

	// Active Payroll Period
	let currentRun = $state<PayrollRun>({
		id: 'pr-2026-08',
		tenant_id: 'ten-corp',
		period_month: 8,
		period_year: 2026,
		title: 'Payroll Rutin Karyawan - Agustus 2026',
		total_gross: 118500000,
		total_deductions: 9325000,
		total_net: 109175000,
		status: PayrollStatus.PAID,
		paid_at: '2026-08-28T10:00:00Z',
		payment_account_id: 'acc-bca-biz',
		notes: 'Ditransfer via batch payroll BCA Corporate.',
		items_count: 8
	});

	// Items (Individual Salary Slips)
	let items = $state<PayrollItem[]>([
		{
			id: 'item-1',
			payroll_run_id: 'pr-2026-08',
			employee_id: 'emp-1',
			employee_nik: 'EMP-001',
			employee_name: 'Reza Aditya Pratama',
			employee_dept: 'Engineering',
			employee_bank: 'BCA',
			employee_account: '8830192811',
			basic_salary: 24000000,
			allowances: 1500000,
			overtime: 0,
			deductions: 0,
			bpjs_tk_employee: 720000,
			bpjs_tk_company: 1497600,
			bpjs_kes_employee: 240000,
			bpjs_kes_company: 960000,
			pph21: 1200000,
			gross_salary: 25500000,
			net_salary: 23340000,
			status: PayrollItemStatus.PAID
		},
		{
			id: 'item-2',
			payroll_run_id: 'pr-2026-08',
			employee_id: 'emp-2',
			employee_nik: 'EMP-002',
			employee_name: 'Siti Nurhaliza Putri',
			employee_dept: 'Finance & Accounting',
			employee_bank: 'Bank Mandiri',
			employee_account: '1370018293847',
			basic_salary: 18500000,
			allowances: 1500000,
			overtime: 0,
			deductions: 0,
			bpjs_tk_employee: 555000,
			bpjs_tk_company: 1154400,
			bpjs_kes_employee: 185000,
			bpjs_kes_company: 740000,
			pph21: 925000,
			gross_salary: 20000000,
			net_salary: 18335000,
			status: PayrollItemStatus.PAID
		},
		{
			id: 'item-3',
			payroll_run_id: 'pr-2026-08',
			employee_id: 'emp-3',
			employee_nik: 'EMP-003',
			employee_name: 'Budi Santoso',
			employee_dept: 'Engineering',
			employee_bank: 'BCA',
			employee_account: '8830492812',
			basic_salary: 16000000,
			allowances: 1500000,
			overtime: 500000,
			deductions: 0,
			bpjs_tk_employee: 480000,
			bpjs_tk_company: 998400,
			bpjs_kes_employee: 160000,
			bpjs_kes_company: 640000,
			pph21: 800000,
			gross_salary: 18000000,
			net_salary: 16560000,
			status: PayrollItemStatus.PAID
		},
		{
			id: 'item-4',
			payroll_run_id: 'pr-2026-08',
			employee_id: 'emp-4',
			employee_nik: 'EMP-004',
			employee_name: 'Anindya Kirana',
			employee_dept: 'Human Resources',
			employee_bank: 'BSI',
			employee_account: '7182938491',
			basic_salary: 17000000,
			allowances: 1500000,
			overtime: 0,
			deductions: 0,
			bpjs_tk_employee: 510000,
			bpjs_tk_company: 1060800,
			bpjs_kes_employee: 170000,
			bpjs_kes_company: 680000,
			pph21: 850000,
			gross_salary: 18500000,
			net_salary: 16970000,
			status: PayrollItemStatus.PAID
		},
		{
			id: 'item-5',
			payroll_run_id: 'pr-2026-08',
			employee_id: 'emp-5',
			employee_nik: 'EMP-005',
			employee_name: 'Dimas Arya Wijaya',
			employee_dept: 'Engineering',
			employee_bank: 'Bank Jago',
			employee_account: '109283746519',
			basic_salary: 11000000,
			allowances: 750000,
			overtime: 500000,
			deductions: 0,
			bpjs_tk_employee: 330000,
			bpjs_tk_company: 686400,
			bpjs_kes_employee: 110000,
			bpjs_kes_company: 440000,
			pph21: 550000,
			gross_salary: 12250000,
			net_salary: 11260000,
			status: PayrollItemStatus.PAID
		},
		{
			id: 'item-6',
			payroll_run_id: 'pr-2026-08',
			employee_id: 'emp-6',
			employee_nik: 'EMP-006',
			employee_name: 'Jessica Amanda',
			employee_dept: 'Marketing',
			employee_bank: 'BCA',
			employee_account: '8830918273',
			basic_salary: 15000000,
			allowances: 1500000,
			overtime: 0,
			deductions: 0,
			bpjs_tk_employee: 450000,
			bpjs_tk_company: 936000,
			bpjs_kes_employee: 150000,
			bpjs_kes_company: 600000,
			pph21: 750000,
			gross_salary: 16500000,
			net_salary: 15150000,
			status: PayrollItemStatus.PAID
		},
		{
			id: 'item-7',
			payroll_run_id: 'pr-2026-08',
			employee_id: 'emp-7',
			employee_nik: 'EMP-007',
			employee_name: 'Fajar Hidayat',
			employee_dept: 'Finance & Accounting',
			employee_bank: 'BCA',
			employee_account: '8830112233',
			basic_salary: 8500000,
			allowances: 750000,
			overtime: 0,
			deductions: 0,
			bpjs_tk_employee: 255000,
			bpjs_tk_company: 530400,
			bpjs_kes_employee: 85000,
			bpjs_kes_company: 340000,
			pph21: 0,
			gross_salary: 9250000,
			net_salary: 8910000,
			status: PayrollItemStatus.PAID
		},
		{
			id: 'item-8',
			payroll_run_id: 'pr-2026-08',
			employee_id: 'emp-8',
			employee_nik: 'EMP-008',
			employee_name: 'Nadia Larasati',
			employee_dept: 'Human Resources',
			employee_bank: 'BNI',
			employee_account: '0891827364',
			basic_salary: 4500000,
			allowances: 500000,
			overtime: 0,
			deductions: 0,
			bpjs_tk_employee: 135000,
			bpjs_tk_company: 280800,
			bpjs_kes_employee: 45000,
			bpjs_kes_company: 180000,
			pph21: 0,
			gross_salary: 5000000,
			net_salary: 4820000,
			status: PayrollItemStatus.PAID
		}
	]);

	// Filter States
	let searchQuery = $state('');
	let selectedDept = $state('ALL');
	let selectedStatus = $state<string>('ALL');
	let isFilterModalOpen = $state(false);

	const activeFiltersCount = $derived(
		(selectedDept !== 'ALL' ? 1 : 0) +
		(selectedStatus !== 'ALL' ? 1 : 0)
	);

	function resetFilters() {
		selectedDept = 'ALL';
		selectedStatus = 'ALL';
		searchQuery = '';
	}

	const filteredItems = $derived(
		items.filter((it) => {
			const matchesSearch =
				(it.employee_name && it.employee_name.toLowerCase().includes(searchQuery.toLowerCase())) ||
				(it.employee_nik && it.employee_nik.toLowerCase().includes(searchQuery.toLowerCase())) ||
				(it.employee_dept && it.employee_dept.toLowerCase().includes(searchQuery.toLowerCase()));
			const matchesDept = selectedDept === 'ALL' || (it.employee_dept && it.employee_dept.toLowerCase().includes(selectedDept.toLowerCase()));
			const matchesStatus = selectedStatus === 'ALL' || it.status.toString() === selectedStatus;
			return Boolean(matchesSearch && matchesDept && matchesStatus);
		})
	);

	// Modal States
	let isProcessModalOpen = $state(false);
	let selectedSlip = $state<PayrollItem | null>(null);
	let isSlipModalOpen = $state(false);

	let selectedAccountDebit = $state('BCA Operasional Utama (Rp 450.000.000)');

	function openSlip(item: PayrollItem) {
		selectedSlip = item;
		isSlipModalOpen = true;
	}

	function handleRunPayroll() {
		notificationStore.info(
			'Menghitung rekonsiliasi absensi, BPJS TK, BPJS Kesehatan & PPh 21...',
			'Proses Payroll Dimulai'
		);
		setTimeout(() => {
			currentRun.status = PayrollStatus.PAID;
			currentRun.paid_at = new Date().toISOString();
			isProcessModalOpen = false;
			notificationStore.success(
				`Siklus payroll berhasil dibayarkan! Pengeluaran ${formatRupiah(currentRun.total_net)} otomatis terjurnal ke kas perusahaan.`,
				'Payroll Selesai & Kas Terdebet'
			);
		}, 1200);
	}

	const columns: TableColumn<PayrollItem>[] = [
		{ key: 'employee_nik', header: 'NIK', sortable: true, width: '90px' },
		{ key: 'employee_name', header: 'Nama Karyawan', sortable: true },
		{ key: 'employee_dept', header: 'Departemen', sortable: true },
		{ key: 'basic_salary', header: 'Gaji Pokok', sortable: true, align: 'right' },
		{ key: 'allowances', header: 'Tunjangan', sortable: true, align: 'right' },
		{ key: 'overtime', header: 'Lembur', sortable: true, align: 'right' },
		{ key: 'bpjs_tk_employee', header: 'Potongan', sortable: true, align: 'right' },
		{ key: 'net_salary', header: 'Gaji Bersih', sortable: true, align: 'right' },
		{ key: 'status', header: 'Status', sortable: true, align: 'center' },
		{ key: 'id', header: 'Aksi', align: 'center', width: '80px' }
	];
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
		<div>
			<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2.5">
				<div class="p-2 rounded-2xl bg-purple-500/10 text-purple-600 dark:text-purple-400">
					<Briefcase class="w-6 h-6" />
				</div>
				<span>Penggajian & Payroll Karyawan</span>
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
				Kalkulasi otomatis BPJS Ketenagakerjaan, BPJS Kesehatan, PPh 21, dan integrasi pengeluaran kas
			</p>
		</div>

		<div class="flex items-center gap-2 self-start sm:self-auto">
			<Button variant="primary" onclick={() => (isProcessModalOpen = true)}>
				<Play class="w-4 h-4 mr-1.5" />
				<span>Jalankan Payroll Bulan Ini</span>
			</Button>
		</div>
	</div>

	<!-- Active Payroll Period Status Card -->
	<div class="p-6 sm:p-7 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
		<div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
			<div class="flex items-center gap-4">
				<div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-600 to-indigo-600 text-white flex items-center justify-center font-semibold">
					<Briefcase class="w-6 h-6" />
				</div>
				<div>
					<div class="flex items-center gap-2.5">
						<h2 class="text-base font-semibold text-slate-900 dark:text-white">
							{currentRun.title}
						</h2>
						<StatusBadge status={currentRun.status} type="payroll" size="sm" />
					</div>
					<p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
						Periode Bulan ke-{currentRun.period_month} Tahun {currentRun.period_year} &bull; Total {currentRun.items_count} Penerima Slip
					</p>
				</div>
			</div>

			<div class="flex items-center gap-6">
				<div class="text-right">
					<span class="text-[11px] text-slate-400 uppercase font-semibold tracking-wider">Total Gaji Dibayarkan</span>
					<p class="text-lg sm:text-xl font-semibold font-mono text-emerald-600 dark:text-emerald-400 mt-0.5">
						{formatRupiah(currentRun.total_net)}
					</p>
				</div>
			</div>
		</div>
	</div>

	<!-- 4 Financial Breakdown KPI Cards -->
	<div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
		<div class="p-5 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
			<span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Gaji Bruto</span>
			<div class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white font-mono mt-2">
				{formatRupiah(currentRun.total_gross, true)}
			</div>
			<p class="text-[11px] text-slate-500 mt-1">Gaji pokok + tunjangan + lembur</p>
		</div>

		<div class="p-5 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
			<span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Potongan Karyawan</span>
			<div class="text-xl sm:text-2xl font-semibold text-rose-600 dark:text-rose-400 font-mono mt-2">
				{formatRupiah(currentRun.total_deductions, true)}
			</div>
			<p class="text-[11px] text-slate-500 mt-1">BPJS TK 3%, Kes 1% & PPh 21</p>
		</div>

		<div class="p-5 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
			<span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Kontribusi BPJS Kantor</span>
			<div class="text-xl sm:text-2xl font-semibold text-purple-600 dark:text-purple-400 font-mono mt-2">
				Rp 11,2 M
			</div>
			<p class="text-[11px] text-slate-500 mt-1">Beban tambahan BPJS perusahaan</p>
		</div>

		<div class="p-5 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
			<span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Bersih (Take Home)</span>
			<div class="text-xl sm:text-2xl font-semibold text-emerald-600 dark:text-emerald-400 font-mono mt-2">
				{formatRupiah(currentRun.total_net, true)}
			</div>
			<p class="text-[11px] text-slate-500 mt-1">Ditransfer langsung ke rekening staf</p>
		</div>
	</div>

	<!-- Filter & Search Controls -->
	<div class="p-4 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] flex flex-col sm:flex-row gap-3 items-center justify-between">
		<div class="w-full sm:w-80 relative">
			<Search class="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="Cari nama karyawan, NIK, atau divisi..."
				class="w-full pl-9 pr-4 py-2 rounded-2xl bg-slate-100/80 dark:bg-white/5 border border-slate-200/80 dark:border-white/10 text-xs text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-hidden focus:ring-2 focus:ring-[#007AFF]"
			/>
		</div>

		<div class="flex items-center gap-2 w-full sm:w-auto justify-end">
			<Button variant="outline" size="sm" onclick={() => (isFilterModalOpen = true)}>
				<Filter class="w-4 h-4 mr-1.5" />
				<span>Filter</span>
				{#if activeFiltersCount > 0}
					<span class="ml-1.5 px-1.5 py-0.5 rounded-full bg-[#007AFF] text-white text-[10px] font-bold">
						{activeFiltersCount}
					</span>
				{/if}
			</Button>

			{#if activeFiltersCount > 0 || searchQuery}
				<Button variant="ghost" size="sm" onclick={resetFilters}>
					Reset
				</Button>
			{/if}
		</div>
	</div>

	<!-- Payroll Items Table (1 Value per Column) -->
	<Table
		title="Rincian Slip Gaji Karyawan"
		subtitle="Daftar slip gaji per individu lengkap dengan kalkulasi potongan dan gaji bersih"
		icon={FileText}
		badge="{filteredItems.length} Penerima Gaji"
		columns={columns}
		items={filteredItems}
		emptyMessage="Belum ada item penggajian yang sesuai filter"
		emptyDescription="Ubah kata kunci pencarian atau reset filter untuk melihat data lainnya."
	>
		{#snippet row(it, index)}
			<tr class="hover:bg-slate-50/60 dark:hover:bg-white/[0.02] transition-colors border-b border-slate-100 dark:border-white/5 text-xs">
				<!-- NIK -->
				<td class="p-3.5 whitespace-nowrap font-mono text-slate-500 dark:text-slate-400">
					{it.employee_nik}
				</td>

				<!-- Nama Karyawan -->
				<td class="p-3.5 whitespace-nowrap font-medium text-slate-900 dark:text-white">
					{it.employee_name}
				</td>

				<!-- Departemen -->
				<td class="p-3.5 whitespace-nowrap text-slate-600 dark:text-slate-300">
					{it.employee_dept}
				</td>

				<!-- Gaji Pokok -->
				<td class="p-3.5 whitespace-nowrap text-right font-mono text-slate-900 dark:text-white">
					{formatRupiah(it.basic_salary)}
				</td>

				<!-- Tunjangan -->
				<td class="p-3.5 whitespace-nowrap text-right font-mono text-slate-600 dark:text-slate-300">
					{it.allowances > 0 ? formatRupiah(it.allowances) : '-'}
				</td>

				<!-- Lembur -->
				<td class="p-3.5 whitespace-nowrap text-right font-mono text-slate-600 dark:text-slate-300">
					{it.overtime > 0 ? formatRupiah(it.overtime) : '-'}
				</td>

				<!-- Total Potongan -->
				<td class="p-3.5 whitespace-nowrap text-right font-mono text-rose-500">
					-{formatRupiah(it.bpjs_tk_employee + it.bpjs_kes_employee + it.pph21 + it.deductions)}
				</td>

				<!-- Gaji Bersih -->
				<td class="p-3.5 whitespace-nowrap text-right font-mono font-semibold text-emerald-600 dark:text-emerald-400">
					{formatRupiah(it.net_salary)}
				</td>

				<!-- Status -->
				<td class="p-3.5 whitespace-nowrap text-center">
					<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-600 border border-emerald-500/20">
						{it.status === PayrollItemStatus.PAID ? 'Dibayar' : 'Draf'}
					</span>
				</td>

				<!-- Action (Detail Slip) -->
				<td class="p-3.5 whitespace-nowrap text-center">
					<button
						type="button"
						onclick={() => openSlip(it)}
						class="p-1.5 rounded-xl text-slate-400 hover:text-[#007AFF] hover:bg-slate-100 dark:hover:bg-white/5 transition-colors"
						title="Buka Lembar Slip Gaji"
					>
						<Eye class="w-4 h-4" />
					</button>
				</td>
			</tr>
		{/snippet}
	</Table>

	<!-- Modal Filter Payroll -->
	<Modal
		bind:open={isFilterModalOpen}
		title="Filter Rincian Slip Gaji"
		description="Saring rincian slip gaji berdasarkan divisi dan status pembayaran"
	>
		<div class="space-y-4 py-2">
			<div>
				<label for="filter-payroll-dept" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Departemen / Divisi</label>
				<select
					id="filter-payroll-dept"
					bind:value={selectedDept}
					class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
				>
					<option value="ALL">Semua Departemen</option>
					<option value="Engineering">Engineering</option>
					<option value="Finance">Finance & Accounting</option>
					<option value="Human Resources">Human Resources & GA</option>
					<option value="Marketing">Marketing & Growth</option>
				</select>
			</div>

			<div>
				<label for="filter-payroll-status" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Status Pembayaran</label>
				<select
					id="filter-payroll-status"
					bind:value={selectedStatus}
					class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
				>
					<option value="ALL">Semua Status</option>
					<option value="{PayrollItemStatus.PAID}">1 - Dibayar (Lunas)</option>
					<option value="{PayrollItemStatus.UNPAID}">0 - Belum Dibayar</option>
				</select>
			</div>
		</div>

		{#snippet footer()}
			<div class="flex items-center justify-between w-full">
				<Button variant="ghost" size="sm" onclick={resetFilters}>
					Reset Filter
				</Button>
				<Button variant="primary" size="sm" onclick={() => (isFilterModalOpen = false)}>
					Terapkan Filter
				</Button>
			</div>
		{/snippet}
	</Modal>

	<!-- Sheet Jalankan Payroll (Drawer Kanan) -->
	<Sheet
		bind:open={isProcessModalOpen}
		side="right"
		size="md"
		title="Jalankan Siklus Payroll Perusahaan"
		description="Hitung otomatis gaji seluruh karyawan dan jurnal pengeluaran ke kas perusahaan"
	>
		<div class="space-y-4 py-2">
			<div class="p-4 rounded-2xl bg-purple-500/10 border border-purple-500/20 text-xs text-purple-700 dark:text-purple-300 space-y-1.5">
				<div class="font-semibold flex items-center gap-1.5">
					<ShieldCheck class="w-4 h-4" />
					<span>Kalkulasi Pajak & Jaminan Sosial Indonesia</span>
				</div>
				<p class="leading-relaxed text-[11px]">
					Sistem akan mengkalkulasi tarif resmi BPJS TK (JKK, JKM, JHT, JP), BPJS Kesehatan (1% karyawan, 4% perusahaan), potongan presensi/keterlambatan, serta estimasi PPh 21.
				</p>
			</div>

			<div>
				<label for="payroll-debit-acc" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Pilih Rekening Bank Debet Perusahaan</label>
				<select
					id="payroll-debit-acc"
					bind:value={selectedAccountDebit}
					class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
				>
					<option value="BCA Operasional Utama (Rp 450.000.000)">BCA Operasional Utama (Saldo: Rp 450.000.000)</option>
					<option value="Bank Mandiri Payroll Batch (Rp 220.000.000)">Bank Mandiri Payroll Batch (Saldo: Rp 220.000.000)</option>
				</select>
			</div>

			<div class="p-3 rounded-2xl border border-slate-200/80 dark:border-white/10 space-y-2 text-xs">
				<div class="flex justify-between text-slate-500">
					<span>Total Karyawan Diproses:</span>
					<strong class="text-slate-900 dark:text-white">8 Orang</strong>
				</div>
				<div class="flex justify-between text-slate-500">
					<span>Estimasi Gaji Bersih Terdebet:</span>
					<strong class="text-emerald-600 dark:text-emerald-400 font-mono">{formatRupiah(currentRun.total_net)}</strong>
				</div>
			</div>
		</div>

		{#snippet footer()}
			<div class="flex items-center justify-end gap-2">
				<Button variant="ghost" onclick={() => (isProcessModalOpen = false)}>
					Batal
				</Button>
				<Button variant="primary" onclick={handleRunPayroll}>
					<Check class="w-4 h-4 mr-1.5" />
					<span>Setujui & Debet Kas Sekarang</span>
				</Button>
			</div>
		{/snippet}
	</Sheet>

	<!-- Sheet Tampilan Slip Gaji (Digital Salary Slip - Drawer Kanan) -->
	{#if selectedSlip}
		<Sheet
			bind:open={isSlipModalOpen}
			side="right"
			size="2xl"
			title="Slip Gaji Karyawan"
			description="Dokumen resmi rincian penghasilan, rekonsiliasi presensi & potongan"
		>
			<div class="p-5 rounded-3xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200/80 dark:border-white/10 space-y-4">
				<!-- Slip Header -->
				<div class="flex items-center justify-between border-b border-slate-200 dark:border-white/10 pb-4">
					<div>
						<h3 class="font-bold text-sm text-slate-900 dark:text-white tracking-wide">
							PT PANTAU DUIT SOLUSINDO
						</h3>
						<p class="text-[10px] text-slate-500">
							Menara Cyber Lt. 12, Jakarta Selatan &bull; NPWP: 01.234.567.8-012.000
						</p>
					</div>
					<div class="text-right">
						<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-600 border border-emerald-500/20">
							LUNAS / DIBAYAR
						</span>
						<p class="text-[10px] font-mono text-slate-400 mt-1">Periode: Agustus 2026</p>
					</div>
				</div>

				<!-- Employee Details -->
				<div class="grid grid-cols-2 gap-3 text-xs">
					<div>
						<span class="text-[10px] text-slate-400 uppercase font-semibold">Nama Karyawan</span>
						<p class="font-semibold text-slate-900 dark:text-white">{selectedSlip.employee_name}</p>
					</div>
					<div>
						<span class="text-[10px] text-slate-400 uppercase font-semibold">NIK & Departemen</span>
						<p class="font-semibold text-slate-900 dark:text-white font-mono">{selectedSlip.employee_nik} ({selectedSlip.employee_dept})</p>
					</div>
					<div>
						<span class="text-[10px] text-slate-400 uppercase font-semibold">Bank Penerima</span>
						<p class="font-semibold text-slate-900 dark:text-white font-mono">{selectedSlip.employee_bank} - {selectedSlip.employee_account}</p>
					</div>
					<div>
						<span class="text-[10px] text-slate-400 uppercase font-semibold">Waktu Transfer</span>
						<p class="font-semibold text-slate-900 dark:text-white">28 Agu 2026, 10:00 WIB</p>
					</div>
				</div>

				<!-- Attendance Summary in Slip -->
				<div class="p-3 rounded-2xl bg-blue-500/5 border border-blue-500/15 grid grid-cols-4 gap-2 text-center text-xs">
					<div>
						<span class="text-[10px] text-slate-400 font-medium">Hari Kerja</span>
						<p class="font-bold text-slate-800 dark:text-slate-200">22 Hari</p>
					</div>
					<div>
						<span class="text-[10px] text-slate-400 font-medium">Hadir Tepat</span>
						<p class="font-bold text-emerald-600 dark:text-emerald-400">22 Hari</p>
					</div>
					<div>
						<span class="text-[10px] text-slate-400 font-medium">Lembur</span>
						<p class="font-bold text-blue-600 dark:text-blue-400">
							{selectedSlip.overtime > 0 ? '4 Jam' : '0 Jam'}
						</p>
					</div>
					<div>
						<span class="text-[10px] text-slate-400 font-medium">Keterlambatan</span>
						<p class="font-bold text-slate-500">0 Menit</p>
					</div>
				</div>

				<!-- Salary Breakdown (Penerimaan vs Potongan) -->
				<div class="grid grid-cols-2 gap-4 pt-2 border-t border-slate-200 dark:border-white/10 text-xs">
					<!-- Penerimaan -->
					<div class="space-y-1.5">
						<h4 class="text-[11px] font-semibold text-emerald-600 uppercase tracking-wider">A. Penerimaan (Gross)</h4>
						<div class="flex justify-between">
							<span class="text-slate-500">Gaji Pokok:</span>
							<span class="font-mono text-slate-900 dark:text-white">{formatRupiah(selectedSlip.basic_salary)}</span>
						</div>
						<div class="flex justify-between">
							<span class="text-slate-500">Tunjangan Operasional:</span>
							<span class="font-mono text-slate-900 dark:text-white">{formatRupiah(selectedSlip.allowances)}</span>
						</div>
						{#if selectedSlip.overtime > 0}
							<div class="flex justify-between">
								<span class="text-slate-500">Upah Lembur:</span>
								<span class="font-mono text-slate-900 dark:text-white">{formatRupiah(selectedSlip.overtime)}</span>
							</div>
						{/if}
						<div class="flex justify-between pt-1 border-t border-slate-200 dark:border-white/10 font-semibold">
							<span>Total Penerimaan:</span>
							<span class="font-mono text-slate-900 dark:text-white">{formatRupiah(selectedSlip.gross_salary)}</span>
						</div>
					</div>

					<!-- Potongan -->
					<div class="space-y-1.5">
						<h4 class="text-[11px] font-semibold text-rose-600 uppercase tracking-wider">B. Potongan Wajib</h4>
						<div class="flex justify-between">
							<span class="text-slate-500">BPJS Ketenagakerjaan (3%):</span>
							<span class="font-mono text-rose-500">-{formatRupiah(selectedSlip.bpjs_tk_employee)}</span>
						</div>
						<div class="flex justify-between">
							<span class="text-slate-500">BPJS Kesehatan (1%):</span>
							<span class="font-mono text-rose-500">-{formatRupiah(selectedSlip.bpjs_kes_employee)}</span>
						</div>
						<div class="flex justify-between">
							<span class="text-slate-500">Estimasi PPh 21:</span>
							<span class="font-mono text-rose-500">-{formatRupiah(selectedSlip.pph21)}</span>
						</div>
						<div class="flex justify-between pt-1 border-t border-slate-200 dark:border-white/10 font-semibold">
							<span>Total Potongan:</span>
							<span class="font-mono text-rose-500">-{formatRupiah(selectedSlip.bpjs_tk_employee + selectedSlip.bpjs_kes_employee + selectedSlip.pph21)}</span>
						</div>
					</div>
				</div>

				<!-- Net Take Home Pay Highlight -->
				<div class="p-3.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-between">
					<div>
						<span class="text-[10px] font-semibold text-emerald-600 uppercase tracking-wider">Gaji Bersih Diterima (Take Home Pay)</span>
						<p class="text-xs text-slate-500">Telah ditransfer ke rekening {selectedSlip.employee_bank}</p>
					</div>
					<div class="text-xl font-bold font-mono text-emerald-600 dark:text-emerald-400">
						{formatRupiah(selectedSlip.net_salary)}
					</div>
				</div>
			</div>

			{#snippet footer()}
				<div class="flex items-center justify-between">
					<Button variant="outline" size="sm" onclick={() => notificationStore.success('Slip gaji berhasil diunduh dalam format PDF!', 'Dokumen Siap')}>
						<Download class="w-3.5 h-3.5 mr-1" />
						<span>Unduh PDF</span>
					</Button>
					<Button variant="ghost" onclick={() => (isSlipModalOpen = false)}>
						Tutup
					</Button>
				</div>
			{/snippet}
		</Sheet>
	{/if}
</div>
