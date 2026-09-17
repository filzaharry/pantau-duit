<script lang="ts">
	import { formatDate } from '$lib/utils/formatters';
	import { getLeaveTypeLabel } from '$lib/utils/status';
	import {
		LeaveType,
		LeaveStatus,
		type LeaveRequest
	} from '$lib/types/company';
	import StatusBadge from '$lib/components/ui/StatusBadge.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Sheet from '$lib/components/ui/Sheet.svelte';
	import Table, { type TableColumn } from '$lib/components/ui/Table.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import {
		CalendarCheck,
		CalendarPlus,
		CheckCircle2,
		Clock,
		AlertCircle,
		Check,
		X,
		Search,
		Filter,
		Eye
	} from 'lucide-svelte';

	let leaves = $state<LeaveRequest[]>([
		{
			id: 'lv-1',
			tenant_id: 'ten-corp',
			employee_id: 'emp-1',
			employee_nik: 'EMP-001',
			employee_name: 'Reza Aditya Pratama',
			leave_type: LeaveType.ANNUAL,
			start_date: '2026-09-21',
			end_date: '2026-09-23',
			total_days: 3,
			reason: 'Liburan tahunan bersama keluarga',
			status: LeaveStatus.APPROVED
		},
		{
			id: 'lv-2',
			tenant_id: 'ten-corp',
			employee_id: 'emp-3',
			employee_nik: 'EMP-003',
			employee_name: 'Budi Santoso',
			leave_type: LeaveType.SICK,
			start_date: '2026-09-15',
			end_date: '2026-09-16',
			total_days: 2,
			reason: 'Demam dan flu (disertai surat dokter)',
			status: LeaveStatus.APPROVED
		},
		{
			id: 'lv-3',
			tenant_id: 'ten-corp',
			employee_id: 'emp-5',
			employee_nik: 'EMP-005',
			employee_name: 'Dimas Arya Wijaya',
			leave_type: LeaveType.SPECIAL,
			start_date: '2026-09-28',
			end_date: '2026-09-30',
			total_days: 3,
			reason: 'Menikah (Cuti pernikahan)',
			status: LeaveStatus.PENDING
		},
		{
			id: 'lv-4',
			tenant_id: 'ten-corp',
			employee_id: 'emp-8',
			employee_nik: 'EMP-008',
			employee_name: 'Nadia Larasati',
			leave_type: LeaveType.ANNUAL,
			start_date: '2026-10-05',
			end_date: '2026-10-06',
			total_days: 2,
			reason: 'Keperluan wisuda sarjana',
			status: LeaveStatus.PENDING
		}
	]);

	// Filter states
	let searchQuery = $state('');
	let selectedStatus = $state<string>('ALL');
	let selectedType = $state<string>('ALL');
	let isFilterModalOpen = $state(false);

	let selectedLeave = $state<LeaveRequest | null>(null);
	let isDetailModalOpen = $state(false);

	const activeFiltersCount = $derived(
		(selectedStatus !== 'ALL' ? 1 : 0) +
		(selectedType !== 'ALL' ? 1 : 0)
	);

	function resetFilters() {
		selectedStatus = 'ALL';
		selectedType = 'ALL';
		searchQuery = '';
	}

	function openDetail(l: LeaveRequest) {
		selectedLeave = l;
		isDetailModalOpen = true;
	}

	const filteredLeaves = $derived(
		leaves.filter((l) => {
			const matchesSearch =
				(l.employee_name && l.employee_name.toLowerCase().includes(searchQuery.toLowerCase())) ||
				(l.employee_nik && l.employee_nik.toLowerCase().includes(searchQuery.toLowerCase())) ||
				(l.reason && l.reason.toLowerCase().includes(searchQuery.toLowerCase()));
			const matchesStatus = selectedStatus === 'ALL' || l.status.toString() === selectedStatus;
			const matchesType = selectedType === 'ALL' || l.leave_type.toString() === selectedType;
			return Boolean(matchesSearch && matchesStatus && matchesType);
		})
	);

	let isAddModalOpen = $state(false);
	let newLeave = $state({
		employee_name: 'Reza Aditya Pratama',
		employee_nik: 'EMP-001',
		leave_type: LeaveType.ANNUAL,
		start_date: '2026-10-12',
		end_date: '2026-10-14',
		total_days: 3,
		reason: ''
	});

	function handleAddLeave() {
		const created: LeaveRequest = {
			id: `lv-${Date.now()}`,
			tenant_id: 'ten-corp',
			employee_id: 'emp-1',
			employee_name: newLeave.employee_name,
			employee_nik: newLeave.employee_nik,
			leave_type: Number(newLeave.leave_type) as LeaveType,
			start_date: newLeave.start_date,
			end_date: newLeave.end_date,
			total_days: Number(newLeave.total_days),
			reason: newLeave.reason,
			status: LeaveStatus.PENDING
		};

		leaves = [created, ...leaves];
		isAddModalOpen = false;
		notificationStore.success('Pengajuan cuti berhasil dikirim ke atasan!', 'Pengajuan Terkirim');
	}

	function approveLeave(id: string) {
		leaves = leaves.map((l) => (l.id === id ? { ...l, status: LeaveStatus.APPROVED } : l));
		notificationStore.success('Pengajuan cuti berhasil disetujui!', 'Status Diperbarui');
	}

	function rejectLeave(id: string) {
		leaves = leaves.map((l) => (l.id === id ? { ...l, status: LeaveStatus.REJECTED } : l));
		notificationStore.info('Pengajuan cuti ditolak.', 'Status Diperbarui');
	}

	const columns: TableColumn<LeaveRequest>[] = [
		{ key: 'employee_nik', header: 'NIK', sortable: true, width: '90px' },
		{ key: 'employee_name', header: 'Nama Karyawan', sortable: true },
		{ key: 'leave_type', header: 'Jenis Cuti', sortable: true },
		{ key: 'start_date', header: 'Mulai', sortable: true },
		{ key: 'end_date', header: 'Selesai', sortable: true },
		{ key: 'total_days', header: 'Durasi', sortable: true, align: 'center' },
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
					<CalendarCheck class="w-6 h-6" />
				</div>
				<span>Presensi & Pengajuan Cuti</span>
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
				Kelola persetujuan cuti tahunan, izin sakit, dan jadwal ketersediaan kerja tim
			</p>
		</div>

		<Button variant="primary" onclick={() => (isAddModalOpen = true)}>
			<CalendarPlus class="w-4 h-4 mr-1.5" />
			<span>Ajukan Cuti Baru</span>
		</Button>
	</div>

	<!-- Stats Cards -->
	<div class="grid grid-cols-3 gap-4">
		<div class="p-5 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
			<span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Menunggu Review</span>
			<div class="text-2xl font-semibold text-amber-600 dark:text-amber-400 mt-1">
				{leaves.filter((l) => l.status === LeaveStatus.PENDING).length} Pengajuan
			</div>
		</div>
		<div class="p-5 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
			<span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Disetujui Bulan Ini</span>
			<div class="text-2xl font-semibold text-emerald-600 dark:text-emerald-400 mt-1">
				{leaves.filter((l) => l.status === LeaveStatus.APPROVED).length} Disetujui
			</div>
		</div>
		<div class="p-5 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
			<span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Sedang Cuti Hari Ini</span>
			<div class="text-2xl font-semibold text-[#007AFF] mt-1">
				0 Karyawan
			</div>
		</div>
	</div>

	<!-- Filter & Search Controls -->
	<div class="p-4 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] flex flex-col sm:flex-row gap-3 items-center justify-between">
		<div class="w-full sm:w-80 relative">
			<Search class="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="Cari nama karyawan, NIK, atau alasan..."
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

	<!-- Leaves Table (1 Value per Column) -->
	<Table
		title="Daftar Pengajuan Cuti"
		subtitle="Riwayat pengajuan izin dan cuti karyawan beserta status persetujuan"
		icon={CalendarCheck}
		badge="{filteredLeaves.length} Pengajuan"
		columns={columns}
		items={filteredLeaves}
		emptyMessage="Tidak ada pengajuan cuti yang sesuai filter"
		emptyDescription="Ubah kata kunci pencarian atau reset filter untuk melihat data lainnya."
	>
		{#snippet row(l, index)}
			<tr class="hover:bg-slate-50/60 dark:hover:bg-white/[0.02] transition-colors border-b border-slate-100 dark:border-white/5 text-xs">
				<!-- NIK -->
				<td class="p-3.5 whitespace-nowrap font-mono text-slate-500 dark:text-slate-400">
					{l.employee_nik}
				</td>

				<!-- Nama Karyawan -->
				<td class="p-3.5 whitespace-nowrap font-medium text-slate-900 dark:text-white">
					{l.employee_name}
				</td>

				<!-- Jenis Cuti -->
				<td class="p-3.5 whitespace-nowrap text-slate-700 dark:text-slate-300">
					{getLeaveTypeLabel(l.leave_type)}
				</td>

				<!-- Mulai -->
				<td class="p-3.5 whitespace-nowrap font-mono text-slate-600 dark:text-slate-300">
					{formatDate(l.start_date)}
				</td>

				<!-- Selesai -->
				<td class="p-3.5 whitespace-nowrap font-mono text-slate-600 dark:text-slate-300">
					{formatDate(l.end_date)}
				</td>

				<!-- Durasi -->
				<td class="p-3.5 whitespace-nowrap text-center font-medium text-slate-900 dark:text-white">
					{l.total_days} Hari
				</td>

				<!-- Status -->
				<td class="p-3.5 whitespace-nowrap text-center">
					<StatusBadge status={l.status} type="leave" size="sm" />
				</td>

				<!-- Action (Detail) -->
				<td class="p-3.5 whitespace-nowrap text-center">
					<button
						type="button"
						onclick={() => openDetail(l)}
						class="p-1.5 rounded-xl text-slate-400 hover:text-[#007AFF] hover:bg-slate-100 dark:hover:bg-white/5 transition-colors"
						title="Lihat Detail & Keputusan Cuti"
					>
						<Eye class="w-4 h-4" />
					</button>
				</td>
			</tr>
		{/snippet}
	</Table>

	<!-- Modal Filter Cuti -->
	<Modal
		bind:open={isFilterModalOpen}
		title="Filter Pengajuan Cuti"
		description="Saring data cuti berdasarkan status persetujuan dan jenis cuti"
	>
		<div class="space-y-4 py-2">
			<div>
				<label for="filter-leave-status" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Status Persetujuan</label>
				<select
					id="filter-leave-status"
					bind:value={selectedStatus}
					class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
				>
					<option value="ALL">Semua Status</option>
					<option value="{LeaveStatus.PENDING}">0 - Menunggu Review</option>
					<option value="{LeaveStatus.APPROVED}">1 - Disetujui</option>
					<option value="{LeaveStatus.REJECTED}">2 - Ditolak</option>
				</select>
			</div>

			<div>
				<label for="filter-leave-type" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Jenis Cuti</label>
				<select
					id="filter-leave-type"
					bind:value={selectedType}
					class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
				>
					<option value="ALL">Semua Jenis</option>
					<option value="{LeaveType.ANNUAL}">1 - Cuti Tahunan</option>
					<option value="{LeaveType.SICK}">2 - Izin Sakit</option>
					<option value="{LeaveType.MATERNITY}">3 - Cuti Melahirkan</option>
					<option value="{LeaveType.SPECIAL}">5 - Izin Khusus</option>
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

	<!-- Modal Detail Cuti -->
	{#if selectedLeave}
		<Modal
			bind:open={isDetailModalOpen}
			title="Detail Pengajuan Cuti"
			description="Informasi alasan pengajuan izin dan keputusan atasan"
		>
			<div class="space-y-4 py-2 text-xs">
				<div class="p-4 rounded-2xl bg-slate-100 dark:bg-white/5 space-y-1">
					<div class="flex items-center justify-between">
						<span class="font-mono text-slate-500">{selectedLeave.employee_nik}</span>
						<StatusBadge status={selectedLeave.status} type="leave" size="sm" />
					</div>
					<h3 class="font-bold text-sm text-slate-900 dark:text-white">{selectedLeave.employee_name}</h3>
					<p class="text-[#007AFF] font-medium">{getLeaveTypeLabel(selectedLeave.leave_type)}</p>
				</div>

				<div class="grid grid-cols-2 gap-3">
					<div class="p-3 rounded-2xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/5">
						<span class="text-slate-400 text-[10px] uppercase font-semibold">Periode Cuti</span>
						<p class="font-mono font-bold text-slate-900 dark:text-white mt-0.5">
							{formatDate(selectedLeave.start_date)}
						</p>
						<p class="font-mono text-slate-500 text-[11px]">s/d {formatDate(selectedLeave.end_date)}</p>
					</div>
					<div class="p-3 rounded-2xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/5">
						<span class="text-slate-400 text-[10px] uppercase font-semibold">Durasi Izin</span>
						<p class="font-bold text-slate-900 dark:text-white mt-0.5 text-base">{selectedLeave.total_days} Hari Kerja</p>
					</div>
				</div>

				<div class="p-3 rounded-2xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/5 space-y-1">
					<span class="text-slate-400 text-[10px] uppercase font-semibold">Alasan / Keterangan</span>
					<p class="text-slate-800 dark:text-slate-200 leading-relaxed">{selectedLeave.reason || '-'}</p>
				</div>
			</div>

			{#snippet footer()}
				<div class="flex items-center justify-between w-full">
					<Button variant="ghost" size="sm" onclick={() => (isDetailModalOpen = false)}>
						Tutup
					</Button>
					{#if selectedLeave && selectedLeave.status === LeaveStatus.PENDING}
						<div class="flex items-center gap-2">
							<Button
								variant="outline"
								size="sm"
								onclick={() => {
									if (selectedLeave) rejectLeave(selectedLeave.id);
									isDetailModalOpen = false;
								}}
							>
								<X class="w-4 h-4 mr-1 text-rose-500" />
								<span>Tolak</span>
							</Button>
							<Button
								variant="primary"
								size="sm"
								onclick={() => {
									if (selectedLeave) approveLeave(selectedLeave.id);
									isDetailModalOpen = false;
								}}
							>
								<Check class="w-4 h-4 mr-1" />
								<span>Setujui Cuti</span>
							</Button>
						</div>
					{/if}
				</div>
			{/snippet}
		</Modal>
	{/if}

	<!-- Sheet Ajukan Cuti (Drawer Kanan) -->
	<Sheet
		bind:open={isAddModalOpen}
		side="right"
		size="md"
		title="Formulir Pengajuan Cuti"
		description="Kirim pengajuan izin kerja atau cuti ke manajer dan HR"
	>
		<div class="space-y-4 py-2">
			<div>
				<label for="leave-type-select" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Jenis Cuti (Opsi Angka)</label>
				<select
					id="leave-type-select"
					bind:value={newLeave.leave_type}
					class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
				>
					<option value={LeaveType.ANNUAL}>1 - Cuti Tahunan</option>
					<option value={LeaveType.SICK}>2 - Izin Sakit (Surat Dokter)</option>
					<option value={LeaveType.MATERNITY}>3 - Cuti Melahirkan / Ayah</option>
					<option value={LeaveType.UNPAID}>4 - Cuti di Luar Tanggungan</option>
					<option value={LeaveType.SPECIAL}>5 - Izin Khusus</option>
				</select>
			</div>

			<div class="grid grid-cols-2 gap-3">
				<div>
					<label for="leave-start-date" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Mulai Tanggal</label>
					<input
						id="leave-start-date"
						type="date"
						bind:value={newLeave.start_date}
						class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
					/>
				</div>
				<div>
					<label for="leave-end-date" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Selesai Tanggal</label>
					<input
						id="leave-end-date"
						type="date"
						bind:value={newLeave.end_date}
						class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
					/>
				</div>
			</div>

			<div>
				<label for="leave-total-days" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Total Hari Kerja</label>
				<input
					id="leave-total-days"
					type="number"
					bind:value={newLeave.total_days}
					class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
				/>
			</div>

			<div>
				<label for="leave-reason" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Alasan Pengajuan</label>
				<textarea
					id="leave-reason"
					bind:value={newLeave.reason}
					rows="3"
					placeholder="Tulis alasan keperluan izin/cuti..."
					class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
				></textarea>
			</div>
		</div>

		{#snippet footer()}
			<div class="flex items-center justify-end gap-2">
				<Button variant="ghost" onclick={() => (isAddModalOpen = false)}>
					Batal
				</Button>
				<Button variant="primary" onclick={handleAddLeave}>
					Kirim Pengajuan
				</Button>
			</div>
		{/snippet}
	</Sheet>
</div>
