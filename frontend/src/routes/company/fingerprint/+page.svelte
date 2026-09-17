<script lang="ts">
	import { formatDate } from '$lib/utils/formatters';
	import {
		getFingerprintDeviceStatusInfo,
		getFingerprintSyncStatusInfo
	} from '$lib/utils/status';
	import {
		FingerprintDeviceStatus,
		FingerprintSyncStatus,
		type FingerprintDevice,
		type FingerprintRawLog,
		type FingerprintEmployeeMapping
	} from '$lib/types/company';
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Sheet from '$lib/components/ui/Sheet.svelte';
	import Table, { type TableColumn } from '$lib/components/ui/Table.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import {
		Fingerprint,
		Cpu,
		RefreshCw,
		Plus,
		Server,
		Activity,
		CheckCircle2,
		AlertTriangle,
		Clock,
		Search,
		Filter,
		Eye,
		Link as LinkIcon,
		Layers,
		Check,
		Wifi,
		WifiOff,
		MapPin
	} from 'lucide-svelte';

	// Registered Devices (aligned with seed data)
	let devices = $state<FingerprintDevice[]>([
		{
			id: 'dev-1',
			tenant_id: 'ten-corp',
			device_name: 'Lobby Utama & Turnstile Gerbang',
			device_sn: 'ZK-GATE-01',
			brand: 'ZKTeco iClock 680',
			ip_address: '192.168.1.201',
			port: 4370,
			location: 'Gerbang Depan Pabrik & Lobby Utama',
			status: FingerprintDeviceStatus.ONLINE,
			last_sync_at: '2026-09-17T03:45:00Z'
		},
		{
			id: 'dev-2',
			tenant_id: 'ten-corp',
			device_name: 'Pintu Masuk Gudang & Line 2',
			device_sn: 'ZK-WH-02',
			brand: 'ZKTeco K40',
			ip_address: '192.168.1.202',
			port: 4370,
			location: 'Gudang Logistik & Area Perakitan',
			status: FingerprintDeviceStatus.ONLINE,
			last_sync_at: '2026-09-17T03:40:00Z'
		}
	]);

	// PIN Mappings (PIN on device -> Employee)
	let mappings = $state<FingerprintEmployeeMapping[]>([
		{ id: 'map-1', tenant_id: 'ten-corp', device_user_id: '1001', employee_id: 'emp-1', employee_name: 'Reza Aditya Pratama', employee_nik: 'EMP-001' },
		{ id: 'map-2', tenant_id: 'ten-corp', device_user_id: '1002', employee_id: 'emp-2', employee_name: 'Siti Nurhaliza Putri', employee_nik: 'EMP-002' },
		{ id: 'map-3', tenant_id: 'ten-corp', device_user_id: '1003', employee_id: 'emp-3', employee_name: 'Budi Santoso', employee_nik: 'EMP-003' },
		{ id: 'map-4', tenant_id: 'ten-corp', device_user_id: '1004', employee_id: 'emp-4', employee_name: 'Dewi Lestari', employee_nik: 'EMP-004' },
		{ id: 'map-5', tenant_id: 'ten-corp', device_user_id: '1005', employee_id: 'emp-5', employee_name: 'Dimas Arya Wijaya', employee_nik: 'EMP-005' },
		{ id: 'map-6', tenant_id: 'ten-corp', device_user_id: '1006', employee_id: 'emp-6', employee_name: 'Jessica Amanda', employee_nik: 'EMP-006' },
		{ id: 'map-7', tenant_id: 'ten-corp', device_user_id: '1007', employee_id: 'emp-7', employee_name: 'Fajar Hidayat', employee_nik: 'EMP-007' },
		{ id: 'map-8', tenant_id: 'ten-corp', device_user_id: '1008', employee_id: 'emp-8', employee_name: 'Nadia Larasati', employee_nik: 'EMP-008' }
	]);

	// Raw Punch Logs
	let rawLogs = $state<FingerprintRawLog[]>([
		{
			id: 'log-1',
			tenant_id: 'ten-corp',
			device_id: 'dev-1',
			device_name: 'Lobby Utama & Turnstile Gerbang',
			device_user_id: '1001',
			timestamp: '2026-09-17 08:22:15',
			verify_mode: 1, // Fingerprint
			sync_status: FingerprintSyncStatus.PROCESSED,
			matched_employee_name: 'Reza Aditya Pratama',
			created_at: '2026-09-17 08:22:16'
		},
		{
			id: 'log-2',
			tenant_id: 'ten-corp',
			device_id: 'dev-1',
			device_name: 'Lobby Utama & Turnstile Gerbang',
			device_user_id: '1002',
			timestamp: '2026-09-17 08:28:44',
			verify_mode: 1,
			sync_status: FingerprintSyncStatus.PROCESSED,
			matched_employee_name: 'Siti Nurhaliza Putri',
			created_at: '2026-09-17 08:28:45'
		},
		{
			id: 'log-3',
			tenant_id: 'ten-corp',
			device_id: 'dev-2',
			device_name: 'Pintu Masuk Gudang & Line 2',
			device_user_id: '1003',
			timestamp: '2026-09-17 07:24:02',
			verify_mode: 1,
			sync_status: FingerprintSyncStatus.PROCESSED,
			matched_employee_name: 'Budi Santoso',
			created_at: '2026-09-17 07:24:03'
		},
		{
			id: 'log-4',
			tenant_id: 'ten-corp',
			device_id: 'dev-2',
			device_name: 'Pintu Masuk Gudang & Line 2',
			device_user_id: '1005',
			timestamp: '2026-09-17 06:52:19',
			verify_mode: 1,
			sync_status: FingerprintSyncStatus.PROCESSED,
			matched_employee_name: 'Dimas Arya Wijaya',
			created_at: '2026-09-17 06:52:20'
		},
		{
			id: 'log-5',
			tenant_id: 'ten-corp',
			device_id: 'dev-2',
			device_name: 'Pintu Masuk Gudang & Line 2',
			device_user_id: '1005',
			timestamp: '2026-09-17 06:52:35',
			verify_mode: 1,
			sync_status: FingerprintSyncStatus.DUPLICATE,
			matched_employee_name: 'Dimas Arya Wijaya',
			error_message: 'Double tap terdeteksi dalam 16 detik (diabaikan)',
			created_at: '2026-09-17 06:52:36'
		},
		{
			id: 'log-6',
			tenant_id: 'ten-corp',
			device_id: 'dev-1',
			device_name: 'Lobby Utama & Turnstile Gerbang',
			device_user_id: '9999',
			timestamp: '2026-09-17 08:45:10',
			verify_mode: 3, // RFID
			sync_status: FingerprintSyncStatus.UNMATCHED,
			matched_employee_name: null,
			error_message: 'PIN 9999 belum terdaftar ke karyawan',
			created_at: '2026-09-17 08:45:11'
		}
	]);

	let isSyncing = $state(false);
	let activeTab = $state<'devices' | 'logs' | 'mappings'>('logs');
	let logSearch = $state('');

	// Sheet States
	let isAddDeviceOpen = $state(false);
	let newDevice = $state({
		device_name: '',
		device_sn: '',
		brand: 'ZKTeco',
		ip_address: '',
		port: 4370,
		location: ''
	});

	let isMappingOpen = $state(false);
	let newMapping = $state({
		device_user_id: '',
		employee_id: 'emp-1',
		employee_name: 'Reza Aditya Pratama'
	});

	// Trigger manual pull from devices
	function triggerDeviceSync() {
		isSyncing = true;
		notificationStore.info('Menghubungi socket port 4370 perangkat ZKTeco...', 'Sinkronisasi Dimulai');

		setTimeout(() => {
			isSyncing = false;
			// Add a newly synced punch
			const newLog: FingerprintRawLog = {
				id: `log-${Date.now()}`,
				tenant_id: 'ten-corp',
				device_id: 'dev-1',
				device_name: 'Lobby Utama & Turnstile Gerbang',
				device_user_id: '1004',
				timestamp: '2026-09-17 14:55:00',
				verify_mode: 1,
				sync_status: FingerprintSyncStatus.PROCESSED,
				matched_employee_name: 'Dewi Lestari',
				created_at: new Date().toISOString()
			};
			rawLogs = [newLog, ...rawLogs];
			notificationStore.success(
				'Berhasil menarik 1 log baru dari mesin Lobby & Warehouse. Presensi terekonsiliasi!',
				'Sinkronisasi Selesai'
			);
		}, 1500);
	}

	function handleAddDevice() {
		if (!newDevice.device_name || !newDevice.ip_address || !newDevice.device_sn) {
			notificationStore.error('Nama, Serial Number, dan IP Address wajib diisi!', 'Form Belum Lengkap');
			return;
		}

		const created: FingerprintDevice = {
			id: `dev-${Date.now()}`,
			tenant_id: 'ten-corp',
			device_name: newDevice.device_name,
			device_sn: newDevice.device_sn,
			brand: newDevice.brand,
			ip_address: newDevice.ip_address,
			port: Number(newDevice.port),
			location: newDevice.location || 'Area Produksi',
			status: FingerprintDeviceStatus.ONLINE,
			last_sync_at: new Date().toISOString()
		};

		devices = [...devices, created];
		isAddDeviceOpen = false;
		notificationStore.success(`Mesin ${created.device_name} terdaftar dan terhubung!`, 'Perangkat Terhubung');
	}

	function handleAddMapping() {
		if (!newMapping.device_user_id) {
			notificationStore.error('PIN mesin wajib diisi!', 'Validasi Gagal');
			return;
		}

		const created: FingerprintEmployeeMapping = {
			id: `map-${Date.now()}`,
			tenant_id: 'ten-corp',
			device_user_id: newMapping.device_user_id,
			employee_id: newMapping.employee_id,
			employee_name: 'Reza Aditya Pratama',
			employee_nik: 'EMP-001'
		};

		mappings = [...mappings, created];
		isMappingOpen = false;
		notificationStore.success(`PIN ${created.device_user_id} berhasil dipetakan!`, 'Pemetaan Tersimpan');
	}

	let isFilterModalOpen = $state(false);
	let selectedDeviceFilter = $state('ALL');
	let selectedSyncStatus = $state<string>('ALL');
	let isLogDetailOpen = $state(false);
	let selectedLog = $state<FingerprintRawLog | null>(null);

	const activeFiltersCount = $derived(
		(selectedDeviceFilter !== 'ALL' ? 1 : 0) +
		(selectedSyncStatus !== 'ALL' ? 1 : 0)
	);

	function resetLogFilters() {
		selectedDeviceFilter = 'ALL';
		selectedSyncStatus = 'ALL';
		logSearch = '';
	}

	function openLogDetail(log: FingerprintRawLog) {
		selectedLog = log;
		isLogDetailOpen = true;
	}

	const filteredLogs = $derived(
		rawLogs.filter((log) => {
			const matchesSearch =
				log.device_user_id.includes(logSearch) ||
				(log.matched_employee_name && log.matched_employee_name.toLowerCase().includes(logSearch.toLowerCase())) ||
				(log.device_name && log.device_name.toLowerCase().includes(logSearch.toLowerCase()));
			const matchesDevice = selectedDeviceFilter === 'ALL' || (Boolean(log.device_name) && log.device_name!.includes(selectedDeviceFilter));
			const matchesStatus = selectedSyncStatus === 'ALL' || log.sync_status.toString() === selectedSyncStatus;
			return matchesSearch && matchesDevice && matchesStatus;
		})
	);

	const logColumns: TableColumn<FingerprintRawLog>[] = [
		{ key: 'timestamp', header: 'Waktu Tap', sortable: true, width: '160px' },
		{ key: 'device_name', header: 'Perangkat', sortable: true },
		{ key: 'device_user_id', header: 'PIN Mesin', sortable: true, align: 'center', width: '90px' },
		{ key: 'matched_employee_name', header: 'Karyawan', sortable: true },
		{ key: 'verify_mode', header: 'Metode', sortable: true, align: 'center', width: '110px' },
		{ key: 'sync_status', header: 'Status', sortable: true, align: 'center', width: '130px' },
		{ key: 'id', header: 'Aksi', align: 'center', width: '70px' }
	];
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
		<div>
			<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2.5">
				<div class="p-2 rounded-2xl bg-blue-500/10 text-[#007AFF]">
					<Fingerprint class="w-6 h-6" />
				</div>
				<span>Integrasi Mesin Fingerprint</span>
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
				Koneksi hardware ZKTeco/Standalone, log mentah presensi, deduplikasi double-tap, dan pemetaan PIN
			</p>
		</div>

		<div class="flex items-center gap-2">
			<Button variant="outline" size="sm" onclick={() => (isAddDeviceOpen = true)}>
				<Plus class="w-4 h-4 mr-1.5" />
				<span>Tambah Mesin</span>
			</Button>

			<Button variant="primary" size="sm" onclick={triggerDeviceSync} disabled={isSyncing}>
				<RefreshCw class="w-4 h-4 mr-1.5 {isSyncing ? 'animate-spin' : ''}" />
				<span>{isSyncing ? 'Menarik Data...' : 'Sync Mesin Sekarang'}</span>
			</Button>
		</div>
	</div>

	<!-- Device Status Cards -->
	<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
		{#each devices as dev}
			{@const statusInfo = getFingerprintDeviceStatusInfo(dev.status)}
			<div class="p-5 rounded-3xl bg-white/80 dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/10 backdrop-blur-xl space-y-4">
				<div class="flex items-start justify-between">
					<div class="flex items-center gap-3">
						<div class="p-3 rounded-2xl bg-[#007AFF]/10 text-[#007AFF]">
							<Cpu class="w-6 h-6" />
						</div>
						<div>
							<h3 class="font-bold text-sm text-slate-900 dark:text-white">{dev.device_name}</h3>
							<p class="text-xs text-slate-500 font-mono">SN: {dev.device_sn} &bull; {dev.brand}</p>
						</div>
					</div>
					<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium border {statusInfo.badgeClass}">
						<span class="w-1.5 h-1.5 rounded-full {statusInfo.dotClass}"></span>
						<span>{statusInfo.label}</span>
					</span>
				</div>

				<div class="grid grid-cols-3 gap-2 text-xs pt-2 border-t border-slate-100 dark:border-white/5">
					<div>
						<span class="text-[10px] text-slate-400 font-semibold uppercase">IP / Socket</span>
						<p class="font-mono font-semibold text-slate-800 dark:text-slate-200 mt-0.5">
							{dev.ip_address}:{dev.port}
						</p>
					</div>
					<div>
						<span class="text-[10px] text-slate-400 font-semibold uppercase">Lokasi Pasang</span>
						<p class="text-slate-800 dark:text-slate-200 mt-0.5 truncate" title={dev.location}>
							{dev.location}
						</p>
					</div>
					<div>
						<span class="text-[10px] text-slate-400 font-semibold uppercase">Sync Terakhir</span>
						<p class="text-slate-800 dark:text-slate-200 mt-0.5 font-mono">
							Baru saja
						</p>
					</div>
				</div>
			</div>
		{/each}
	</div>

	<!-- Navigation Tabs for Logs vs PIN Mappings -->
	<div class="flex items-center justify-between border-b border-slate-200/80 dark:border-white/10 pb-2">
		<div class="flex items-center gap-2">
			<button
				type="button"
				onclick={() => (activeTab = 'logs')}
				class="px-4 py-2 rounded-2xl text-xs font-semibold transition-all {activeTab === 'logs' ? 'bg-[#007AFF] text-white shadow-sm' : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'}"
			>
				Raw Attendance Logs ({rawLogs.length})
			</button>
			<button
				type="button"
				onclick={() => (activeTab = 'mappings')}
				class="px-4 py-2 rounded-2xl text-xs font-semibold transition-all {activeTab === 'mappings' ? 'bg-[#007AFF] text-white shadow-sm' : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'}"
			>
				Pemetaan PIN Karyawan ({mappings.length})
			</button>
		</div>

		{#if activeTab === 'mappings'}
			<Button variant="outline" size="sm" onclick={() => (isMappingOpen = true)}>
				<LinkIcon class="w-3.5 h-3.5 mr-1" />
				<span>Petakan PIN Baru</span>
			</Button>
		{/if}
	</div>

	{#if activeTab === 'logs'}
		<!-- Raw Logs Tab -->
		<div class="space-y-4">
			<div class="flex flex-col sm:flex-row gap-3 items-center justify-between p-4 rounded-3xl bg-white/80 dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/10 backdrop-blur-xl">
				<div class="relative w-full sm:w-80">
					<Search class="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
					<input
						type="text"
						bind:value={logSearch}
						placeholder="Cari PIN atau nama karyawan..."
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

					{#if activeFiltersCount > 0 || logSearch}
						<Button variant="ghost" size="sm" onclick={resetLogFilters}>
							Reset
						</Button>
					{/if}
				</div>
			</div>

			<Table items={filteredLogs} columns={logColumns} emptyMessage="Tidak ada log presensi yang sesuai filter">
				{#snippet row(log)}
					{@const syncInfo = getFingerprintSyncStatusInfo(log.sync_status)}
					<tr class="border-b border-slate-100 dark:border-white/5 hover:bg-slate-50/50 dark:hover:bg-white/[0.02] transition-colors text-xs">
						<!-- Waktu Tap -->
						<td class="p-3.5 whitespace-nowrap font-mono text-slate-800 dark:text-slate-200 font-semibold">
							{log.timestamp}
						</td>

						<!-- Perangkat -->
						<td class="p-3.5 whitespace-nowrap text-slate-600 dark:text-slate-400">
							{log.device_name}
						</td>

						<!-- PIN Mesin -->
						<td class="p-3.5 whitespace-nowrap text-center font-mono text-slate-800 dark:text-slate-200">
							{log.device_user_id}
						</td>

						<!-- Karyawan -->
						<td class="p-3.5 whitespace-nowrap font-medium text-slate-900 dark:text-white">
							{log.matched_employee_name || 'Tidak Dikenal'}
						</td>

						<!-- Metode -->
						<td class="p-3.5 whitespace-nowrap text-center text-slate-500">
							{log.verify_mode === 1 ? 'Fingerprint' : log.verify_mode === 2 ? 'Face Recognition' : 'RFID Card'}
						</td>

						<!-- Status -->
						<td class="p-3.5 whitespace-nowrap text-center">
							<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-medium border {syncInfo.badgeClass}">
								{syncInfo.label}
							</span>
						</td>

						<!-- Action (Detail Log) -->
						<td class="p-3.5 whitespace-nowrap text-center">
							<button
								type="button"
								onclick={() => openLogDetail(log)}
								class="p-1.5 rounded-xl text-slate-400 hover:text-[#007AFF] hover:bg-slate-100 dark:hover:bg-white/5 transition-colors"
								title="Lihat Detail Log Mesin"
							>
								<Eye class="w-4 h-4" />
							</button>
						</td>
					</tr>
				{/snippet}
			</Table>

			<!-- Modal Filter Log -->
			<Modal
				bind:open={isFilterModalOpen}
				title="Filter Log Presensi Mesin"
				description="Saring log mentah mesin berdasarkan status sinkronisasi dan terminal"
			>
				<div class="space-y-4 py-2">
					<div>
						<label for="filter-log-status" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Status Sinkronisasi</label>
						<select
							id="filter-log-status"
							bind:value={selectedSyncStatus}
							class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
						>
							<option value="ALL">Semua Status</option>
							<option value="{FingerprintSyncStatus.PROCESSED}">1 - Sukses Terekonsiliasi</option>
							<option value="{FingerprintSyncStatus.DUPLICATE}">2 - Duplikat (Double-Tap Diabaikan)</option>
							<option value="{FingerprintSyncStatus.UNMATCHED}">3 - PIN Belum Terdaftar</option>
						</select>
					</div>

					<div>
						<label for="filter-log-dev" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Terminal Mesin</label>
						<select
							id="filter-log-dev"
							bind:value={selectedDeviceFilter}
							class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
						>
							<option value="ALL">Semua Perangkat</option>
							<option value="Lobby Utama">Lobby Utama & Turnstile Gerbang</option>
							<option value="Gudang">Pintu Masuk Gudang & Line 2</option>
						</select>
					</div>
				</div>

				{#snippet footer()}
					<div class="flex items-center justify-between w-full">
						<Button variant="ghost" size="sm" onclick={resetLogFilters}>
							Reset Filter
						</Button>
						<Button variant="primary" size="sm" onclick={() => (isFilterModalOpen = false)}>
							Terapkan Filter
						</Button>
					</div>
				{/snippet}
			</Modal>

			<!-- Modal Detail Log -->
			{#if selectedLog}
				{@const syncInfo = getFingerprintSyncStatusInfo(selectedLog.sync_status)}
				<Modal
					bind:open={isLogDetailOpen}
					title="Detail Log Presensi Mesin"
					description="Audit rekaman mentah sinyal punch dari terminal fisik"
				>
					<div class="space-y-4 py-2 text-xs">
						<div class="p-4 rounded-2xl bg-slate-100 dark:bg-white/5 space-y-1">
							<div class="flex items-center justify-between">
								<span class="font-mono text-slate-500">PIN #{selectedLog.device_user_id}</span>
								<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold border {syncInfo.badgeClass}">
									{syncInfo.label}
								</span>
							</div>
							<h3 class="font-bold text-sm text-slate-900 dark:text-white">
								{selectedLog.matched_employee_name || 'Karyawan Belum Dipetakan'}
							</h3>
							<p class="text-slate-500">{selectedLog.device_name}</p>
						</div>

						<div class="grid grid-cols-2 gap-3">
							<div class="p-3 rounded-2xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/5">
								<span class="text-slate-400 text-[10px] uppercase font-semibold">Waktu Tap Fisik</span>
								<p class="font-mono font-bold text-slate-900 dark:text-white mt-0.5">{selectedLog.timestamp}</p>
							</div>
							<div class="p-3 rounded-2xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/5">
								<span class="text-slate-400 text-[10px] uppercase font-semibold">Metode Verifikasi</span>
								<p class="font-bold text-slate-900 dark:text-white mt-0.5">
									{selectedLog.verify_mode === 1 ? 'Biometrik Fingerprint' : selectedLog.verify_mode === 2 ? 'Face Recognition' : 'RFID Card'}
								</p>
							</div>
						</div>

						{#if selectedLog.error_message}
							<div class="p-3 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-700 dark:text-rose-400 text-xs">
								<span class="font-bold block mb-0.5">Peringatan Rekonsiliasi:</span>
								<span>{selectedLog.error_message}</span>
							</div>
						{/if}
					</div>

					{#snippet footer()}
						<div class="flex items-center justify-end w-full">
							<Button variant="primary" size="sm" onclick={() => (isLogDetailOpen = false)}>
								Tutup
							</Button>
						</div>
					{/snippet}
				</Modal>
			{/if}
		</div>
	{:else}
		<!-- PIN Mappings Tab -->
		<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
			{#each mappings as map}
				<div class="p-4 rounded-2xl bg-white/80 dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/10 flex items-center justify-between">
					<div>
						<span class="text-[10px] text-slate-400 uppercase font-semibold">PIN Mesin #{map.device_user_id}</span>
						<h4 class="font-bold text-xs text-slate-900 dark:text-white mt-0.5">{map.employee_name}</h4>
						<p class="text-[11px] font-mono text-slate-500">{map.employee_nik}</p>
					</div>
					<div class="p-2 rounded-xl bg-emerald-500/10 text-emerald-600">
						<CheckCircle2 class="w-4 h-4" />
					</div>
				</div>
			{/each}
		</div>
	{/if}

	<!-- Sheet Tambah Mesin Fingerprint (Right Drawer) -->
	<Sheet
		bind:open={isAddDeviceOpen}
		side="right"
		size="md"
		title="Registrasi Mesin Fingerprint"
		description="Hubungkan terminal mesin absen fisik melalui koneksi TCP/IP"
	>
		<div class="space-y-4 py-2">
			<div>
				<label for="dev-name" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Nama Perangkat</label>
				<input
					id="dev-name"
					type="text"
					bind:value={newDevice.device_name}
					placeholder="Contoh: Mesin Pintu Depan Lobby"
					class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
				/>
			</div>

			<div class="grid grid-cols-2 gap-3">
				<div>
					<label for="dev-sn" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Serial Number (SN)</label>
					<input
						id="dev-sn"
						type="text"
						bind:value={newDevice.device_sn}
						placeholder="ZK-GATE-03"
						class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white font-mono"
					/>
				</div>
				<div>
					<label for="dev-brand" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Merk / Tipe</label>
					<input
						id="dev-brand"
						type="text"
						bind:value={newDevice.brand}
						placeholder="ZKTeco iClock"
						class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
					/>
				</div>
			</div>

			<div class="grid grid-cols-2 gap-3">
				<div>
					<label for="dev-ip" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">IP Address</label>
					<input
						id="dev-ip"
						type="text"
						bind:value={newDevice.ip_address}
						placeholder="192.168.1.203"
						class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white font-mono"
					/>
				</div>
				<div>
					<label for="dev-port" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Port Komunikasi</label>
					<input
						id="dev-port"
						type="number"
						bind:value={newDevice.port}
						placeholder="4370"
						class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white font-mono"
					/>
				</div>
			</div>

			<div>
				<label for="dev-loc" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Lokasi Fisik Mesin</label>
				<input
					id="dev-loc"
					type="text"
					bind:value={newDevice.location}
					placeholder="Contoh: Gedung B - Pintu Masuk Staff"
					class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
				/>
			</div>
		</div>

		{#snippet footer()}
			<div class="flex items-center justify-end gap-2">
				<Button variant="ghost" onclick={() => (isAddDeviceOpen = false)}>
					Batal
				</Button>
				<Button variant="primary" onclick={handleAddDevice}>
					Daftarkan Mesin
				</Button>
			</div>
		{/snippet}
	</Sheet>

	<!-- Sheet Petakan PIN (Right Drawer) -->
	<Sheet
		bind:open={isMappingOpen}
		side="right"
		size="md"
		title="Petakan PIN Mesin ke Karyawan"
		description="Hubungkan nomor identitas pada mesin fingerprint dengan profil karyawan"
	>
		<div class="space-y-4 py-2">
			<div>
				<label for="map-pin" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Nomor PIN Mesin (User ID)</label>
				<input
					id="map-pin"
					type="text"
					bind:value={newMapping.device_user_id}
					placeholder="Contoh: 1009 atau 9999"
					class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white font-mono"
				/>
			</div>

			<div>
				<label for="map-emp" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Pilih Karyawan</label>
				<select
					id="map-emp"
					bind:value={newMapping.employee_id}
					class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
				>
					<option value="emp-1">Reza Aditya Pratama (EMP-001)</option>
					<option value="emp-2">Siti Nurhaliza Putri (EMP-002)</option>
					<option value="emp-3">Budi Santoso (EMP-003)</option>
					<option value="emp-4">Dewi Lestari (EMP-004)</option>
					<option value="emp-5">Dimas Arya Wijaya (EMP-005)</option>
					<option value="emp-6">Jessica Amanda (EMP-006)</option>
					<option value="emp-7">Fajar Hidayat (EMP-007)</option>
					<option value="emp-8">Nadia Larasati (EMP-008)</option>
				</select>
			</div>
		</div>

		{#snippet footer()}
			<div class="flex items-center justify-end gap-2">
				<Button variant="ghost" onclick={() => (isMappingOpen = false)}>
					Batal
				</Button>
				<Button variant="primary" onclick={handleAddMapping}>
					Simpan Pemetaan
				</Button>
			</div>
		{/snippet}
	</Sheet>
</div>
