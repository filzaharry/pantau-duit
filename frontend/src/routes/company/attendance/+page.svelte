<script lang="ts">
	import { formatDate } from '$lib/utils/formatters';
	import {
		getAttendanceStatusInfo,
		getAttendanceSourceLabel
	} from '$lib/utils/status';
	import {
		AttendanceStatus,
		AttendanceSource,
		type AttendanceRecord,
		type Shift
	} from '$lib/types/company';
	import StatusBadge from '$lib/components/ui/StatusBadge.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Sheet from '$lib/components/ui/Sheet.svelte';
	import Table, { type TableColumn } from '$lib/components/ui/Table.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import {
		Clock,
		CalendarCheck2,
		AlertTriangle,
		CheckCircle2,
		TrendingUp,
		Filter,
		Search,
		Download,
		Edit3,
		Eye,
		Fingerprint,
		Smartphone,
		ShieldCheck,
		Moon,
		Sun,
		Sunset
	} from 'lucide-svelte';

	// Initial mock shifts (aligned with seed data)
	const shifts: Shift[] = [
		{
			id: 'shift-1',
			tenant_id: 'ten-corp',
			name: 'Jam Kantor Reguler',
			code: 'S-OFFICE',
			start_time: '08:30',
			end_time: '17:30',
			is_cross_day: false,
			late_tolerance_minutes: 15,
			color_code: '#3B82F6',
			status: 1
		},
		{
			id: 'shift-2',
			tenant_id: 'ten-corp',
			name: 'Shift 1 (Pagi)',
			code: 'S-PAGI',
			start_time: '07:00',
			end_time: '15:00',
			is_cross_day: false,
			late_tolerance_minutes: 10,
			color_code: '#10B981',
			status: 1
		},
		{
			id: 'shift-3',
			tenant_id: 'ten-corp',
			name: 'Shift 2 (Siang)',
			code: 'S-SIANG',
			start_time: '15:00',
			end_time: '23:00',
			is_cross_day: false,
			late_tolerance_minutes: 10,
			color_code: '#F59E0B',
			status: 1
		},
		{
			id: 'shift-4',
			tenant_id: 'ten-corp',
			name: 'Shift 3 (Malam / Cross-Day)',
			code: 'S-MALAM',
			start_time: '23:00',
			end_time: '07:00',
			is_cross_day: true,
			late_tolerance_minutes: 10,
			color_code: '#6366F1',
			status: 1
		}
	];

	// Initial attendance records for today (aligned with seed data)
	let attendanceRecords = $state<AttendanceRecord[]>([
		{
			id: 'att-1',
			tenant_id: 'ten-corp',
			employee_id: 'emp-1',
			employee_nik: 'EMP-001',
			employee_name: 'Reza Aditya Pratama',
			department_name: 'Engineering & Technology',
			shift_id: 'shift-1',
			shift_name: 'Jam Kantor Reguler',
			shift_code: 'S-OFFICE',
			date: '2026-09-17',
			check_in_time: '08:22',
			check_out_time: '17:35',
			status: AttendanceStatus.PRESENT,
			work_duration_minutes: 553,
			late_minutes: 0,
			early_leave_minutes: 0,
			overtime_minutes: 0,
			source: AttendanceSource.FINGERPRINT
		},
		{
			id: 'att-2',
			tenant_id: 'ten-corp',
			employee_id: 'emp-2',
			employee_nik: 'EMP-002',
			employee_name: 'Siti Nurhaliza Putri',
			department_name: 'Finance & Accounting',
			shift_id: 'shift-1',
			shift_name: 'Jam Kantor Reguler',
			shift_code: 'S-OFFICE',
			date: '2026-09-17',
			check_in_time: '08:28',
			check_out_time: '17:31',
			status: AttendanceStatus.PRESENT,
			work_duration_minutes: 543,
			late_minutes: 0,
			early_leave_minutes: 0,
			overtime_minutes: 0,
			source: AttendanceSource.FINGERPRINT
		},
		{
			id: 'att-3',
			tenant_id: 'ten-corp',
			employee_id: 'emp-3',
			employee_nik: 'EMP-003',
			employee_name: 'Budi Santoso',
			department_name: 'Engineering & Technology',
			shift_id: 'shift-2',
			shift_name: 'Shift 1 (Pagi)',
			shift_code: 'S-PAGI',
			date: '2026-09-17',
			check_in_time: '07:24',
			check_out_time: '15:05',
			status: AttendanceStatus.LATE,
			work_duration_minutes: 461,
			late_minutes: 14,
			early_leave_minutes: 0,
			overtime_minutes: 0,
			source: AttendanceSource.FINGERPRINT,
			correction_notes: 'Antrian verifikasi gerbang pintu 1'
		},
		{
			id: 'att-4',
			tenant_id: 'ten-corp',
			employee_id: 'emp-4',
			employee_nik: 'EMP-004',
			employee_name: 'Dewi Lestari',
			department_name: 'Human Resources & GA',
			shift_id: 'shift-3',
			shift_name: 'Shift 2 (Siang)',
			shift_code: 'S-SIANG',
			date: '2026-09-17',
			check_in_time: '14:55',
			check_out_time: null,
			status: AttendanceStatus.PRESENT,
			work_duration_minutes: 240,
			late_minutes: 0,
			early_leave_minutes: 0,
			overtime_minutes: 0,
			source: AttendanceSource.FINGERPRINT
		},
		{
			id: 'att-5',
			tenant_id: 'ten-corp',
			employee_id: 'emp-5',
			employee_nik: 'EMP-005',
			employee_name: 'Dimas Arya Wijaya',
			department_name: 'Operations & Warehouse',
			shift_id: 'shift-2',
			shift_name: 'Shift 1 (Pagi)',
			shift_code: 'S-PAGI',
			date: '2026-09-17',
			check_in_time: '06:52',
			check_out_time: '17:15',
			status: AttendanceStatus.PRESENT,
			work_duration_minutes: 623,
			late_minutes: 0,
			early_leave_minutes: 0,
			overtime_minutes: 120,
			source: AttendanceSource.FINGERPRINT,
			correction_notes: 'Lembur 2 jam maintenance mesin conveyor'
		},
		{
			id: 'att-6',
			tenant_id: 'ten-corp',
			employee_id: 'emp-6',
			employee_nik: 'EMP-006',
			employee_name: 'Jessica Amanda',
			department_name: 'Marketing & Growth',
			shift_id: 'shift-1',
			shift_name: 'Jam Kantor Reguler',
			shift_code: 'S-OFFICE',
			date: '2026-09-17',
			check_in_time: null,
			check_out_time: null,
			status: AttendanceStatus.ON_LEAVE,
			work_duration_minutes: 0,
			late_minutes: 0,
			early_leave_minutes: 0,
			overtime_minutes: 0,
			source: AttendanceSource.MANUAL_HR,
			correction_notes: 'Cuti tahunan disetujui HRD'
		}
	]);

	// Filter states
	let searchQuery = $state('');
	let selectedShift = $state('ALL');
	let selectedStatus = $state<string>('ALL');
	let selectedDate = $state('2026-09-17');
	let isFilterModalOpen = $state(false);

	// Detail & Correction Sheet states
	let isDetailSheetOpen = $state(false);
	let selectedRecord = $state<AttendanceRecord | null>(null);
	let isCorrectionOpen = $state(false);
	let editingRecord = $state<AttendanceRecord | null>(null);
	let correctionForm = $state<{
		check_in_time: string;
		check_out_time: string;
		status: AttendanceStatus;
		notes: string;
	}>({
		check_in_time: '',
		check_out_time: '',
		status: AttendanceStatus.PRESENT,
		notes: ''
	});

	const activeFiltersCount = $derived(
		(selectedShift !== 'ALL' ? 1 : 0) +
		(selectedStatus !== 'ALL' ? 1 : 0) +
		(selectedDate !== '2026-09-17' ? 1 : 0)
	);

	function resetFilters() {
		selectedShift = 'ALL';
		selectedStatus = 'ALL';
		selectedDate = '2026-09-17';
	}

	function openDetail(record: AttendanceRecord) {
		selectedRecord = record;
		isDetailSheetOpen = true;
	}

	// Metrics
	const metrics = $derived.by(() => {
		const total = attendanceRecords.length;
		const present = attendanceRecords.filter((r) => r.status === AttendanceStatus.PRESENT).length;
		const late = attendanceRecords.filter((r) => r.status === AttendanceStatus.LATE).length;
		const overtime = attendanceRecords.filter((r) => r.overtime_minutes > 0).length;
		const absent = attendanceRecords.filter((r) => r.status === AttendanceStatus.ABSENT).length;
		return { total, present, late, overtime, absent };
	});

	// Filtered records
	const filteredRecords = $derived(
		attendanceRecords.filter((rec) => {
			const matchesSearch =
				rec.employee_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
				rec.employee_nik?.toLowerCase().includes(searchQuery.toLowerCase()) ||
				rec.department_name?.toLowerCase().includes(searchQuery.toLowerCase());

			const matchesShift = selectedShift === 'ALL' || rec.shift_code === selectedShift;
			const matchesStatus =
				selectedStatus === 'ALL' || rec.status.toString() === selectedStatus;

			return matchesSearch && matchesShift && matchesStatus;
		})
	);

	function openCorrection(record: AttendanceRecord) {
		editingRecord = record;
		correctionForm = {
			check_in_time: record.check_in_time || '',
			check_out_time: record.check_out_time || '',
			status: record.status,
			notes: record.correction_notes || ''
		};
		isCorrectionOpen = true;
	}

	function saveCorrection() {
		if (!editingRecord) return;

		attendanceRecords = attendanceRecords.map((r) => {
			if (r.id === editingRecord!.id) {
				return {
					...r,
					check_in_time: correctionForm.check_in_time || null,
					check_out_time: correctionForm.check_out_time || null,
					status: Number(correctionForm.status) as AttendanceStatus,
					source: AttendanceSource.MANUAL_HR,
					correction_notes: correctionForm.notes,
					corrected_by_name: 'HR Superadmin'
				};
			}
			return r;
		});

		isCorrectionOpen = false;
		notificationStore.success(
			`Presensi ${editingRecord.employee_name} berhasil dikoreksi manual oleh HR`,
			'Audit Log Tercatat'
		);
	}

	function exportAttendance() {
		notificationStore.success(
			'Laporan rekap presensi harian shift berhasil diexport ke CSV/Excel',
			'Export Selesai'
		);
	}

	const columns: TableColumn<AttendanceRecord>[] = [
		{ key: 'employee_nik', header: 'NIK', sortable: true, width: '90px' },
		{ key: 'employee_name', header: 'Nama Karyawan', sortable: true },
		{ key: 'department_name', header: 'Departemen', sortable: true },
		{ key: 'shift_code', header: 'Shift', sortable: true },
		{ key: 'check_in_time', header: 'Check In', sortable: true, align: 'center' },
		{ key: 'check_out_time', header: 'Check Out', sortable: true, align: 'center' },
		{ key: 'work_duration_minutes', header: 'Durasi', sortable: true, align: 'right' },
		{ key: 'overtime_minutes', header: 'Lembur', sortable: true, align: 'right' },
		{ key: 'status', header: 'Status', sortable: true, align: 'center' },
		{ key: 'id', header: 'Aksi', align: 'center', width: '90px' }
	];
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
		<div>
			<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2.5">
				<div class="p-2 rounded-2xl bg-blue-500/10 text-[#007AFF]">
					<Clock class="w-6 h-6" />
				</div>
				<span>Presensi & Monitoring Shift</span>
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
				Pemantauan kehadiran real-time, toleransi keterlambatan shift, dan audit trail koreksi manual
			</p>
		</div>

		<div class="flex items-center gap-2">
			<Button variant="outline" size="sm" onclick={exportAttendance}>
				<Download class="w-4 h-4 mr-1.5" />
				<span>Export Rekap</span>
			</Button>
		</div>
	</div>

	<!-- Shift Presets Pill Bar -->
	<div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
		{#each shifts as s}
			<div
				class="p-3.5 rounded-2xl border bg-white/60 dark:bg-white/[0.02] backdrop-blur-xl transition-all hover:border-slate-300 dark:hover:border-white/20 border-slate-200/80 dark:border-white/10 flex flex-col justify-between"
			>
				<div class="flex items-center justify-between mb-2">
					<span
						class="px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase text-white"
						style="background-color: {s.color_code};"
					>
						{s.code}
					</span>
					{#if s.is_cross_day}
						<span class="flex items-center gap-1 text-[10px] text-purple-600 dark:text-purple-400 font-semibold">
							<Moon class="w-3 h-3" />
							<span>Lintas Hari</span>
						</span>
					{:else if s.code === 'S-PAGI'}
						<Sun class="w-3.5 h-3.5 text-amber-500" />
					{:else if s.code === 'S-SIANG'}
						<Sunset class="w-3.5 h-3.5 text-orange-500" />
					{/if}
				</div>
				<div>
					<p class="font-semibold text-xs text-slate-900 dark:text-white">{s.name}</p>
					<p class="text-[11px] font-mono text-slate-500 mt-0.5">
						{s.start_time} - {s.end_time} &bull; Tol: {s.late_tolerance_minutes}m
					</p>
				</div>
			</div>
		{/each}
	</div>

	<!-- KPI Metric Cards -->
	<div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
		<div class="p-4 rounded-3xl bg-white/80 dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/10 backdrop-blur-xl">
			<div class="flex items-center justify-between">
				<span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Hadir Tepat Waktu</span>
				<div class="p-2 rounded-xl bg-emerald-500/10 text-emerald-600">
					<CheckCircle2 class="w-4 h-4" />
				</div>
			</div>
			<div class="mt-2 flex items-baseline gap-2">
				<span class="text-2xl font-bold text-slate-900 dark:text-white">{metrics.present}</span>
				<span class="text-xs text-slate-400">/ {metrics.total} staf</span>
			</div>
			<p class="text-[10px] text-emerald-600 mt-1 font-medium">Sesuai toleransi shift</p>
		</div>

		<div class="p-4 rounded-3xl bg-white/80 dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/10 backdrop-blur-xl">
			<div class="flex items-center justify-between">
				<span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Terlambat</span>
				<div class="p-2 rounded-xl bg-amber-500/10 text-amber-600">
					<AlertTriangle class="w-4 h-4" />
				</div>
			</div>
			<div class="mt-2 flex items-baseline gap-2">
				<span class="text-2xl font-bold text-amber-600 dark:text-amber-400">{metrics.late}</span>
				<span class="text-xs text-slate-400">orang</span>
			</div>
			<p class="text-[10px] text-amber-600 mt-1 font-medium">Melebihi toleransi shift</p>
		</div>

		<div class="p-4 rounded-3xl bg-white/80 dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/10 backdrop-blur-xl">
			<div class="flex items-center justify-between">
				<span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Lembur (Overtime)</span>
				<div class="p-2 rounded-xl bg-blue-500/10 text-blue-600">
					<TrendingUp class="w-4 h-4" />
				</div>
			</div>
			<div class="mt-2 flex items-baseline gap-2">
				<span class="text-2xl font-bold text-blue-600 dark:text-blue-400">{metrics.overtime}</span>
				<span class="text-xs text-slate-400">orang</span>
			</div>
			<p class="text-[10px] text-blue-600 mt-1 font-medium">Masuk kalkulasi payroll</p>
		</div>

		<div class="p-4 rounded-3xl bg-white/80 dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/10 backdrop-blur-xl">
			<div class="flex items-center justify-between">
				<span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Izin / Cuti / Alpa</span>
				<div class="p-2 rounded-xl bg-purple-500/10 text-purple-600">
					<CalendarCheck2 class="w-4 h-4" />
				</div>
			</div>
			<div class="mt-2 flex items-baseline gap-2">
				<span class="text-2xl font-bold text-purple-600 dark:text-purple-400">
					{attendanceRecords.filter((r) => r.status === AttendanceStatus.ON_LEAVE || r.status === AttendanceStatus.SICK).length}
				</span>
				<span class="text-xs text-slate-400">orang</span>
			</div>
			<p class="text-[10px] text-purple-600 mt-1 font-medium">Tercatat izin HR</p>
		</div>
	</div>

	<!-- Filter & Search Toolbar -->
	<div class="flex flex-col sm:flex-row gap-3 items-center justify-between p-4 rounded-3xl bg-white/80 dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/10 backdrop-blur-xl">
		<div class="relative w-full sm:w-80">
			<Search class="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="Cari karyawan, NIK, atau departemen..."
				class="w-full pl-9 pr-4 py-2 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#007AFF]/30"
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

	<!-- Attendance Table (1 Value per Column) -->
	<Table items={filteredRecords} {columns} emptyMessage="Tidak ada catatan presensi yang sesuai">
		{#snippet row(rec)}
			{@const statusInfo = getAttendanceStatusInfo(rec.status)}
			<tr class="border-b border-slate-100 dark:border-white/5 hover:bg-slate-50/50 dark:hover:bg-white/[0.02] transition-colors text-xs">
				<!-- NIK -->
				<td class="p-3.5 whitespace-nowrap font-mono text-slate-500 dark:text-slate-400">
					{rec.employee_nik}
				</td>

				<!-- Nama Karyawan -->
				<td class="p-3.5 whitespace-nowrap font-medium text-slate-900 dark:text-white">
					{rec.employee_name}
				</td>

				<!-- Departemen -->
				<td class="p-3.5 whitespace-nowrap text-slate-600 dark:text-slate-300">
					{rec.department_name}
				</td>

				<!-- Shift -->
				<td class="p-3.5 whitespace-nowrap text-slate-700 dark:text-slate-300 font-medium">
					{rec.shift_code || 'S-OFFICE'}
				</td>

				<!-- Check In -->
				<td class="p-3.5 whitespace-nowrap text-center font-mono text-slate-800 dark:text-slate-200">
					{rec.check_in_time || '-'}
				</td>

				<!-- Check Out -->
				<td class="p-3.5 whitespace-nowrap text-center font-mono text-slate-800 dark:text-slate-200">
					{rec.check_out_time || '-'}
				</td>

				<!-- Durasi Kerja -->
				<td class="p-3.5 whitespace-nowrap text-right font-mono text-slate-900 dark:text-white">
					{Math.floor(rec.work_duration_minutes / 60)}j {rec.work_duration_minutes % 60}m
				</td>

				<!-- Lembur -->
				<td class="p-3.5 whitespace-nowrap text-right font-mono text-slate-800 dark:text-slate-200">
					{rec.overtime_minutes > 0 ? `${rec.overtime_minutes / 60} Jam` : '-'}
				</td>

				<!-- Status -->
				<td class="p-3.5 whitespace-nowrap text-center">
					<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-medium border {statusInfo.badgeClass}">
						{statusInfo.label}
					</span>
				</td>

				<!-- Action (Detail & Edit) -->
				<td class="p-3.5 whitespace-nowrap text-center">
					<div class="flex items-center justify-center gap-1">
						<button
							type="button"
							onclick={() => openDetail(rec)}
							class="p-1.5 rounded-xl text-slate-400 hover:text-[#007AFF] hover:bg-slate-100 dark:hover:bg-white/5 transition-colors"
							title="Lihat Detail Presensi"
						>
							<Eye class="w-4 h-4" />
						</button>
						<button
							type="button"
							onclick={() => openCorrection(rec)}
							class="p-1.5 rounded-xl text-slate-400 hover:text-[#007AFF] hover:bg-slate-100 dark:hover:bg-white/5 transition-colors"
							title="Koreksi Presensi Manual HR"
						>
							<Edit3 class="w-4 h-4" />
						</button>
					</div>
				</td>
			</tr>
		{/snippet}
	</Table>

	<!-- Modal Filter Presensi -->
	<Modal
		bind:open={isFilterModalOpen}
		title="Filter Presensi Karyawan"
		description="Saring catatan presensi berdasarkan tanggal, jadwal shift, dan status kehadiran"
	>
		<div class="space-y-4 py-2">
			<div>
				<label for="filter-date" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Tanggal Presensi</label>
				<input
					id="filter-date"
					type="date"
					bind:value={selectedDate}
					class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white font-mono"
				/>
			</div>

			<div>
				<label for="filter-shift" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Shift Kerja</label>
				<select
					id="filter-shift"
					bind:value={selectedShift}
					class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
				>
					<option value="ALL">Semua Shift</option>
					<option value="S-OFFICE">Office (08:30 - 17:30)</option>
					<option value="S-PAGI">Shift 1 (07:00 - 15:00)</option>
					<option value="S-SIANG">Shift 2 (15:00 - 23:00)</option>
					<option value="S-MALAM">Shift 3 (23:00 - 07:00)</option>
				</select>
			</div>

			<div>
				<label for="filter-status" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Status Kehadiran</label>
				<select
					id="filter-status"
					bind:value={selectedStatus}
					class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
				>
					<option value="ALL">Semua Status</option>
					<option value={AttendanceStatus.PRESENT.toString()}>Hadir Tepat</option>
					<option value={AttendanceStatus.LATE.toString()}>Terlambat</option>
					<option value={AttendanceStatus.ON_LEAVE.toString()}>Cuti</option>
					<option value={AttendanceStatus.SICK.toString()}>Sakit</option>
					<option value={AttendanceStatus.ABSENT.toString()}>Alpa</option>
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

	<!-- Sheet Detail Presensi Karyawan -->
	{#if selectedRecord}
		{@const statusInfo = getAttendanceStatusInfo(selectedRecord.status)}
		<Sheet
			bind:open={isDetailSheetOpen}
			side="right"
			size="md"
			title="Detail Presensi Karyawan"
			description="Informasi audit kehadiran, waktu tap fingerprint, dan rekonsiliasi kerja"
		>
			<div class="space-y-4 py-2">
				<div class="p-4 rounded-2xl bg-slate-100 dark:bg-white/5 space-y-1">
					<div class="flex items-center justify-between">
						<span class="text-xs font-mono font-bold text-[#007AFF]">{selectedRecord.employee_nik}</span>
						<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold border {statusInfo.badgeClass}">
							{statusInfo.label}
						</span>
					</div>
					<h3 class="font-bold text-sm text-slate-900 dark:text-white">{selectedRecord.employee_name}</h3>
					<p class="text-xs text-slate-500">{selectedRecord.department_name}</p>
				</div>

				<div class="grid grid-cols-2 gap-3 text-xs">
					<div class="p-3 rounded-2xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/5">
						<span class="text-slate-400 text-[10px] uppercase font-semibold">Jadwal Shift</span>
						<p class="font-bold text-slate-900 dark:text-white mt-0.5">{selectedRecord.shift_name}</p>
						<p class="text-[11px] font-mono text-slate-500">{selectedRecord.shift_code}</p>
					</div>
					<div class="p-3 rounded-2xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/5">
						<span class="text-slate-400 text-[10px] uppercase font-semibold">Tanggal</span>
						<p class="font-bold text-slate-900 dark:text-white mt-0.5">{formatDate(selectedRecord.date)}</p>
					</div>
				</div>

				<div class="grid grid-cols-2 gap-3 text-xs">
					<div class="p-3 rounded-2xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/5">
						<span class="text-slate-400 text-[10px] uppercase font-semibold">Jam Check In</span>
						<p class="font-mono font-bold text-sm text-slate-900 dark:text-white mt-0.5">
							{selectedRecord.check_in_time || '-'}
						</p>
						{#if selectedRecord.late_minutes > 0}
							<p class="text-amber-500 font-medium text-[11px] mt-0.5">+{selectedRecord.late_minutes} Menit Terlambat</p>
						{:else}
							<p class="text-emerald-500 font-medium text-[11px] mt-0.5">Tepat Waktu</p>
						{/if}
					</div>
					<div class="p-3 rounded-2xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/5">
						<span class="text-slate-400 text-[10px] uppercase font-semibold">Jam Check Out</span>
						<p class="font-mono font-bold text-sm text-slate-900 dark:text-white mt-0.5">
							{selectedRecord.check_out_time || '-'}
						</p>
						{#if selectedRecord.overtime_minutes > 0}
							<p class="text-blue-500 font-medium text-[11px] mt-0.5">+{selectedRecord.overtime_minutes / 60} Jam Lembur</p>
						{/if}
					</div>
				</div>

				<div class="p-3 rounded-2xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/5 text-xs space-y-1">
					<span class="text-slate-400 text-[10px] uppercase font-semibold">Sumber Rekam Presensi</span>
					<div class="flex items-center gap-2 pt-1 text-slate-700 dark:text-slate-300">
						{#if selectedRecord.source === AttendanceSource.FINGERPRINT}
							<Fingerprint class="w-4 h-4 text-blue-500" />
							<span class="font-medium">Mesin Terminal Fingerprint (ZKTeco Hardware)</span>
						{:else if selectedRecord.source === AttendanceSource.MANUAL_HR}
							<ShieldCheck class="w-4 h-4 text-purple-500" />
							<span class="font-medium">Koreksi Manual oleh Administrator HR</span>
						{:else}
							<Smartphone class="w-4 h-4 text-emerald-500" />
							<span class="font-medium">Aplikasi Mobile GPS Karyawan</span>
						{/if}
					</div>
				</div>

				{#if selectedRecord.correction_notes}
					<div class="p-3 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-xs space-y-1">
						<span class="text-amber-700 dark:text-amber-400 text-[10px] uppercase font-bold">Catatan Audit Trail</span>
						<p class="text-slate-700 dark:text-slate-200">{selectedRecord.correction_notes}</p>
					</div>
				{/if}
			</div>

			{#snippet footer()}
				<div class="flex items-center justify-between w-full">
					<Button variant="ghost" onclick={() => (isDetailSheetOpen = false)}>
						Tutup
					</Button>
					<Button
						variant="outline"
						onclick={() => {
							isDetailSheetOpen = false;
							openCorrection(selectedRecord!);
						}}
					>
						<Edit3 class="w-4 h-4 mr-1.5" />
						<span>Koreksi Presensi</span>
					</Button>
				</div>
			{/snippet}
		</Sheet>
	{/if}

	<!-- Sheet Koreksi Presensi Manual (Right Drawer) -->
	{#if editingRecord}
		<Sheet
			bind:open={isCorrectionOpen}
			side="right"
			size="md"
			title="Koreksi Presensi Manual HR"
			description="Audit trail perubahan jam kerja dan status presensi karyawan"
		>
			<div class="space-y-4 py-2">
				<div class="p-4 rounded-2xl bg-slate-100 dark:bg-white/5 space-y-1">
					<p class="font-bold text-sm text-slate-900 dark:text-white">{editingRecord.employee_name}</p>
					<p class="text-xs text-slate-500 font-mono">
						{editingRecord.employee_nik} &bull; {editingRecord.shift_name} ({editingRecord.shift_code})
					</p>
					<p class="text-[11px] text-slate-400">Tanggal: {formatDate(editingRecord.date)}</p>
				</div>

				<div class="grid grid-cols-2 gap-3">
					<div>
						<label for="corr-checkin" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Jam Check In</label>
						<input
							id="corr-checkin"
							type="time"
							bind:value={correctionForm.check_in_time}
							class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white font-mono"
						/>
					</div>
					<div>
						<label for="corr-checkout" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Jam Check Out</label>
						<input
							id="corr-checkout"
							type="time"
							bind:value={correctionForm.check_out_time}
							class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white font-mono"
						/>
					</div>
				</div>

				<div>
					<label for="corr-status" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Status Kehadiran</label>
					<select
						id="corr-status"
						bind:value={correctionForm.status}
						class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
					>
						<option value={AttendanceStatus.PRESENT}>1 - Hadir Tepat Waktu</option>
						<option value={AttendanceStatus.LATE}>2 - Terlambat</option>
						<option value={AttendanceStatus.EARLY_LEAVE}>3 - Pulang Cepat</option>
						<option value={AttendanceStatus.SICK}>4 - Sakit (Surat Dokter)</option>
						<option value={AttendanceStatus.ON_LEAVE}>5 - Cuti Resmi</option>
						<option value={AttendanceStatus.ABSENT}>0 - Alpa / Mangkir</option>
					</select>
				</div>

				<div>
					<label for="corr-notes" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Catatan Koreksi (Audit Trail Wajib)</label>
					<textarea
						id="corr-notes"
						bind:value={correctionForm.notes}
						rows="3"
						placeholder="Contoh: Lupa tap karena fingerprint gerbang antre, diverifikasi SPV"
						class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
					></textarea>
				</div>
			</div>

			{#snippet footer()}
				<div class="flex items-center justify-end gap-2">
					<Button variant="ghost" onclick={() => (isCorrectionOpen = false)}>
						Batal
					</Button>
					<Button variant="primary" onclick={saveCorrection}>
						Simpan Koreksi HR
					</Button>
				</div>
			{/snippet}
		</Sheet>
	{/if}
</div>
