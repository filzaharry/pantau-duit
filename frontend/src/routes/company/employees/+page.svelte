<script lang="ts">
	import { formatRupiah, formatDate } from '$lib/utils/formatters';
	import { getEmploymentTypeInfo } from '$lib/utils/status';
	import {
		EmployeeStatus,
		EmploymentType,
		Gender,
		type Employee
	} from '$lib/types/company';
	import StatusBadge from '$lib/components/ui/StatusBadge.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Sheet from '$lib/components/ui/Sheet.svelte';
	import Table, { type TableColumn } from '$lib/components/ui/Table.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import {
		Users,
		UserPlus,
		Search,
		Filter,
		Briefcase,
		Building2,
		CreditCard,
		ShieldCheck,
		FileText,
		CheckCircle2,
		Clock,
		AlertCircle,
		Phone,
		Mail,
		Eye,
		Edit3
	} from 'lucide-svelte';

	// Sample data initial (aligned with seed data)
	let employees = $state<Employee[]>([
		{
			id: 'emp-1',
			tenant_id: 'ten-corp',
			nik: 'EMP-001',
			full_name: 'Reza Aditya Pratama',
			email: 'reza.aditya@pantauduit.id',
			phone: '+6281298760001',
			gender: Gender.MALE,
			department_name: 'Engineering & Technology',
			designation_title: 'Lead Software Architect',
			employment_type: EmploymentType.PERMANENT,
			status: EmployeeStatus.ACTIVE,
			join_date: '2023-01-15',
			basic_salary: 24000000,
			bank_name: 'BCA',
			bank_account_number: '8830192811',
			bank_account_holder: 'Reza Aditya Pratama',
			npwp: '81.234.567.8-012.000',
			bpjs_tk_number: '19028374651',
			bpjs_kes_number: '000182938475'
		},
		{
			id: 'emp-2',
			tenant_id: 'ten-corp',
			nik: 'EMP-002',
			full_name: 'Siti Nurhaliza Putri',
			email: 'siti.putri@pantauduit.id',
			phone: '+6281298760002',
			gender: Gender.FEMALE,
			department_name: 'Finance & Accounting',
			designation_title: 'Finance Operations Manager',
			employment_type: EmploymentType.PERMANENT,
			status: EmployeeStatus.ACTIVE,
			join_date: '2023-03-01',
			basic_salary: 18500000,
			bank_name: 'Bank Mandiri',
			bank_account_number: '1370018293847',
			bank_account_holder: 'Siti Nurhaliza Putri',
			npwp: '82.918.273.6-013.000',
			bpjs_tk_number: '19028374652',
			bpjs_kes_number: '000182938476'
		},
		{
			id: 'emp-3',
			tenant_id: 'ten-corp',
			nik: 'EMP-003',
			full_name: 'Budi Santoso',
			email: 'budi.santoso@pantauduit.id',
			phone: '+6281298760003',
			gender: Gender.MALE,
			department_name: 'Engineering & Technology',
			designation_title: 'Senior Fullstack Engineer',
			employment_type: EmploymentType.PERMANENT,
			status: EmployeeStatus.ACTIVE,
			join_date: '2023-06-10',
			basic_salary: 16000000,
			bank_name: 'BCA',
			bank_account_number: '8830492812',
			bank_account_holder: 'Budi Santoso',
			npwp: '83.123.456.7-014.000',
			bpjs_tk_number: '19028374653',
			bpjs_kes_number: '000182938477'
		},
		{
			id: 'emp-4',
			tenant_id: 'ten-corp',
			nik: 'EMP-004',
			full_name: 'Anindya Kirana',
			email: 'anindya.k@pantauduit.id',
			phone: '+6281298760004',
			gender: Gender.FEMALE,
			department_name: 'Human Resources & GA',
			designation_title: 'Head of People & Culture',
			employment_type: EmploymentType.PERMANENT,
			status: EmployeeStatus.ACTIVE,
			join_date: '2023-04-15',
			basic_salary: 17000000,
			bank_name: 'BSI',
			bank_account_number: '7182938491',
			bank_account_holder: 'Anindya Kirana',
			npwp: '84.345.678.9-015.000',
			bpjs_tk_number: '19028374654',
			bpjs_kes_number: '000182938478'
		},
		{
			id: 'emp-5',
			tenant_id: 'ten-corp',
			nik: 'EMP-005',
			full_name: 'Dimas Arya Wijaya',
			email: 'dimas.arya@pantauduit.id',
			phone: '+6281298760005',
			gender: Gender.MALE,
			department_name: 'Engineering & Technology',
			designation_title: 'Frontend Svelte Specialist',
			employment_type: EmploymentType.CONTRACT,
			status: EmployeeStatus.ACTIVE,
			join_date: '2024-01-10',
			basic_salary: 11000000,
			bank_name: 'Bank Jago',
			bank_account_number: '109283746519',
			bank_account_holder: 'Dimas Arya Wijaya',
			npwp: '85.456.789.0-016.000',
			bpjs_tk_number: '19028374655',
			bpjs_kes_number: '000182938479'
		},
		{
			id: 'emp-6',
			tenant_id: 'ten-corp',
			nik: 'EMP-006',
			full_name: 'Jessica Amanda',
			email: 'jessica.m@pantauduit.id',
			phone: '+6281298760006',
			gender: Gender.FEMALE,
			department_name: 'Marketing & Growth',
			designation_title: 'Growth Marketing Lead',
			employment_type: EmploymentType.PERMANENT,
			status: EmployeeStatus.ACTIVE,
			join_date: '2023-08-20',
			basic_salary: 15000000,
			bank_name: 'BCA',
			bank_account_number: '8830918273',
			bank_account_holder: 'Jessica Amanda',
			npwp: '86.567.890.1-017.000',
			bpjs_tk_number: '19028374656',
			bpjs_kes_number: '000182938480'
		},
		{
			id: 'emp-7',
			tenant_id: 'ten-corp',
			nik: 'EMP-007',
			full_name: 'Fajar Hidayat',
			email: 'fajar.h@pantauduit.id',
			phone: '+6281298760007',
			gender: Gender.MALE,
			department_name: 'Finance & Accounting',
			designation_title: 'Accounting & Tax Officer',
			employment_type: EmploymentType.CONTRACT,
			status: EmployeeStatus.PROBATION,
			join_date: '2026-07-01',
			basic_salary: 8500000,
			bank_name: 'BCA',
			bank_account_number: '8830112233',
			bank_account_holder: 'Fajar Hidayat',
			npwp: '87.678.901.2-018.000',
			bpjs_tk_number: '19028374657',
			bpjs_kes_number: '000182938481'
		},
		{
			id: 'emp-8',
			tenant_id: 'ten-corp',
			nik: 'EMP-008',
			full_name: 'Nadia Larasati',
			email: 'nadia.larasati@pantauduit.id',
			phone: '+6281298760008',
			gender: Gender.FEMALE,
			department_name: 'Human Resources & GA',
			designation_title: 'People Operations Associate',
			employment_type: EmploymentType.INTERN,
			status: EmployeeStatus.ACTIVE,
			join_date: '2026-06-01',
			basic_salary: 4500000,
			bank_name: 'BNI',
			bank_account_number: '0891827364',
			bank_account_holder: 'Nadia Larasati',
			npwp: '88.789.012.3-019.000',
			bpjs_tk_number: '19028374658',
			bpjs_kes_number: '000182938482'
		}
	]);

	// Filter states
	let searchQuery = $state('');
	let selectedDept = $state('ALL');
	let selectedStatus = $state<string>('ALL');
	let isFilterModalOpen = $state(false);

	// Modal states
	let isAddModalOpen = $state(false);
	let selectedEmployee = $state<Employee | null>(null);
	let isDetailModalOpen = $state(false);

	const activeFiltersCount = $derived(
		(selectedDept !== 'ALL' ? 1 : 0) +
		(selectedStatus !== 'ALL' ? 1 : 0)
	);

	function resetFilters() {
		selectedDept = 'ALL';
		selectedStatus = 'ALL';
		searchQuery = '';
	}

	// New employee form
	let newEmp = $state({
		nik: '',
		full_name: '',
		email: '',
		phone: '',
		department_name: 'Engineering & Technology',
		designation_title: 'Junior Engineer',
		employment_type: EmploymentType.PERMANENT,
		basic_salary: 8000000,
		bank_name: 'BCA',
		bank_account_number: '',
		join_date: '2026-09-17'
	});

	// Filtered list
	const filteredEmployees = $derived(
		employees.filter((emp) => {
			const matchesSearch =
				emp.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
				emp.nik.toLowerCase().includes(searchQuery.toLowerCase()) ||
				(emp.email && emp.email.toLowerCase().includes(searchQuery.toLowerCase()));

			const matchesDept = selectedDept === 'ALL' || emp.department_name === selectedDept;
			const matchesStatus =
				selectedStatus === 'ALL' || emp.status.toString() === selectedStatus;

			return matchesSearch && matchesDept && matchesStatus;
		})
	);

	// Summary statistics
	const stats = $derived.by(() => {
		const total = employees.length;
		const active = employees.filter((e) => e.status === EmployeeStatus.ACTIVE).length;
		const probation = employees.filter((e) => e.status === EmployeeStatus.PROBATION).length;
		const totalPayrollBase = employees.reduce((acc, curr) => acc + curr.basic_salary, 0);
		return { total, active, probation, totalPayrollBase };
	});

	function handleAddEmployee() {
		if (!newEmp.full_name || !newEmp.nik) {
			notificationStore.error('Nama dan NIK wajib diisi!', 'Validasi Data Gagal');
			return;
		}

		const created: Employee = {
			id: `emp-${Date.now()}`,
			tenant_id: 'ten-corp',
			nik: newEmp.nik,
			full_name: newEmp.full_name,
			email: newEmp.email,
			phone: newEmp.phone,
			gender: Gender.UNSPECIFIED,
			department_name: newEmp.department_name,
			designation_title: newEmp.designation_title,
			employment_type: Number(newEmp.employment_type) as EmploymentType,
			status: EmployeeStatus.ACTIVE,
			join_date: newEmp.join_date,
			basic_salary: Number(newEmp.basic_salary),
			bank_name: newEmp.bank_name,
			bank_account_number: newEmp.bank_account_number,
			bank_account_holder: newEmp.full_name
		};

		employees = [created, ...employees];
		isAddModalOpen = false;
		notificationStore.success(`Karyawan ${created.full_name} berhasil ditambahkan!`, 'Data Tersimpan');
	}

	function openDetail(emp: Employee) {
		selectedEmployee = emp;
		isDetailModalOpen = true;
	}

	const columns: TableColumn<Employee>[] = [
		{ key: 'nik', header: 'NIK', sortable: true, width: '90px' },
		{ key: 'full_name', header: 'Nama Karyawan', sortable: true },
		{ key: 'department_name', header: 'Departemen', sortable: true },
		{ key: 'designation_title', header: 'Jabatan', sortable: true },
		{ key: 'employment_type', header: 'Ikatan Kerja', sortable: true },
		{ key: 'basic_salary', header: 'Gaji Pokok', sortable: true, align: 'right' },
		{ key: 'status', header: 'Status', sortable: true, align: 'center' },
		{ key: 'id', header: 'Aksi', align: 'center', width: '90px' }
	];
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
		<div>
			<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2.5">
				<div class="p-2 rounded-2xl bg-purple-500/10 text-purple-600 dark:text-purple-400">
					<Users class="w-6 h-6" />
				</div>
				<span>Direktori SDM & Karyawan</span>
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
				Kelola data personel, penempatan divisi, status kepegawaian, dan informasi rekening payroll
			</p>
		</div>

		<div class="flex items-center gap-2 self-start sm:self-auto">
			<Button variant="primary" onclick={() => (isAddModalOpen = true)}>
				<UserPlus class="w-4 h-4 mr-1.5" />
				<span>Tambah Karyawan</span>
			</Button>
		</div>
	</div>

	<!-- Statistics KPI Cards -->
	<div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
		<div class="p-5 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
			<div class="flex items-center justify-between text-slate-400 mb-2">
				<span class="text-xs font-semibold uppercase tracking-wider">Total Karyawan</span>
				<Users class="w-4 h-4 text-purple-500" />
			</div>
			<div class="text-2xl sm:text-3xl font-semibold text-slate-900 dark:text-white">
				{stats.total} <span class="text-xs font-normal text-slate-400">Orang</span>
			</div>
			<p class="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
				Tersebar di 4 departemen aktif
			</p>
		</div>

		<div class="p-5 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
			<div class="flex items-center justify-between text-slate-400 mb-2">
				<span class="text-xs font-semibold uppercase tracking-wider">Staf Aktif</span>
				<CheckCircle2 class="w-4 h-4 text-emerald-500" />
			</div>
			<div class="text-2xl sm:text-3xl font-semibold text-emerald-600 dark:text-emerald-400">
				{stats.active} <span class="text-xs font-normal text-slate-400">Karyawan</span>
			</div>
			<p class="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
				Eligible untuk siklus payroll bulanan
			</p>
		</div>

		<div class="p-5 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
			<div class="flex items-center justify-between text-slate-400 mb-2">
				<span class="text-xs font-semibold uppercase tracking-wider">Masa Percobaan</span>
				<Clock class="w-4 h-4 text-amber-500" />
			</div>
			<div class="text-2xl sm:text-3xl font-semibold text-amber-600 dark:text-amber-400">
				{stats.probation} <span class="text-xs font-normal text-slate-400">Orang</span>
			</div>
			<p class="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
				Status evaluasi berkala (probation)
			</p>
		</div>

		<div class="p-5 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
			<div class="flex items-center justify-between text-slate-400 mb-2">
				<span class="text-xs font-semibold uppercase tracking-wider">Total Beban Gaji</span>
				<CreditCard class="w-4 h-4 text-[#007AFF]" />
			</div>
			<div class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white truncate">
				{formatRupiah(stats.totalPayrollBase, true)}
			</div>
			<p class="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
				Estimasi beban gaji pokok / bulan
			</p>
		</div>
	</div>

	<!-- Filter & Search Controls -->
	<div class="p-4 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] flex flex-col sm:flex-row gap-3 items-center justify-between">
		<div class="w-full sm:w-80 relative">
			<Search class="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="Cari nama, NIK, atau email..."
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

	<!-- Employees Data Table (1 Value per Column) -->
	<Table
		title="Daftar Karyawan"
		subtitle="Data lengkap personel perusahaan beserta nomor identitas dan informasi kerja"
		icon={Users}
		badge="{filteredEmployees.length} Karyawan"
		columns={columns}
		items={filteredEmployees}
		emptyMessage="Tidak ada karyawan yang sesuai filter"
		emptyDescription="Ubah kata kunci pencarian atau reset filter untuk melihat data lainnya."
	>
		{#snippet row(emp, index)}
			{@const typeMeta = getEmploymentTypeInfo(emp.employment_type)}
			<tr class="hover:bg-slate-50/60 dark:hover:bg-white/[0.02] transition-colors border-b border-slate-100 dark:border-white/5 text-xs">
				<!-- NIK -->
				<td class="p-3.5 whitespace-nowrap font-mono text-slate-500 dark:text-slate-400">
					{emp.nik}
				</td>

				<!-- Nama Karyawan -->
				<td class="p-3.5 whitespace-nowrap font-medium text-slate-900 dark:text-white">
					{emp.full_name}
				</td>

				<!-- Departemen -->
				<td class="p-3.5 whitespace-nowrap text-slate-600 dark:text-slate-300">
					{emp.department_name}
				</td>

				<!-- Jabatan -->
				<td class="p-3.5 whitespace-nowrap text-slate-700 dark:text-slate-300">
					{emp.designation_title}
				</td>

				<!-- Ikatan Kerja -->
				<td class="p-3.5 whitespace-nowrap text-slate-700 dark:text-slate-300 font-medium">
					{typeMeta.label}
				</td>

				<!-- Gaji Pokok -->
				<td class="p-3.5 whitespace-nowrap text-right font-mono font-medium text-slate-900 dark:text-white">
					{formatRupiah(emp.basic_salary)}
				</td>

				<!-- Status -->
				<td class="p-3.5 whitespace-nowrap text-center">
					<StatusBadge status={emp.status} type="employee" size="sm" />
				</td>

				<!-- Action (Detail & Edit) -->
				<td class="p-3.5 whitespace-nowrap text-center">
					<div class="flex items-center justify-center gap-1">
						<button
							type="button"
							onclick={() => openDetail(emp)}
							class="p-1.5 rounded-xl text-slate-400 hover:text-[#007AFF] hover:bg-slate-100 dark:hover:bg-white/5 transition-colors"
							title="Lihat Detail Profil & Payroll"
						>
							<Eye class="w-4 h-4" />
						</button>
						<button
							type="button"
							onclick={() => openDetail(emp)}
							class="p-1.5 rounded-xl text-slate-400 hover:text-[#007AFF] hover:bg-slate-100 dark:hover:bg-white/5 transition-colors"
							title="Edit Data Karyawan"
						>
							<Edit3 class="w-4 h-4" />
						</button>
					</div>
				</td>
			</tr>
		{/snippet}
	</Table>

	<!-- Modal Filter Karyawan -->
	<Modal
		bind:open={isFilterModalOpen}
		title="Filter Direktori Karyawan"
		description="Saring karyawan berdasarkan penempatan divisi dan status kepegawaian"
	>
		<div class="space-y-4 py-2">
			<div>
				<label for="filter-dept" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Departemen / Divisi</label>
				<select
					id="filter-dept"
					bind:value={selectedDept}
					class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
				>
					<option value="ALL">Semua Departemen</option>
					<option value="Engineering & Technology">Engineering & Technology</option>
					<option value="Finance & Accounting">Finance & Accounting</option>
					<option value="Human Resources & GA">Human Resources & GA</option>
					<option value="Marketing & Growth">Marketing & Growth</option>
				</select>
			</div>

			<div>
				<label for="filter-status" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Status Kepegawaian</label>
				<select
					id="filter-status"
					bind:value={selectedStatus}
					class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
				>
					<option value="ALL">Semua Status</option>
					<option value="{EmployeeStatus.ACTIVE}">1 - Aktif</option>
					<option value="{EmployeeStatus.PROBATION}">2 - Probation</option>
					<option value="{EmployeeStatus.INACTIVE}">0 - Non-Aktif</option>
					<option value="{EmployeeStatus.RESIGNED}">3 - Resigned</option>
					<option value="{EmployeeStatus.TERMINATED}">4 - Terminated</option>
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

	<!-- Sheet Tambah Karyawan Baru (Drawer Kanan) -->
	<Sheet
		bind:open={isAddModalOpen}
		side="right"
		size="lg"
		title="Tambah Karyawan Baru"
		description="Masukkan data profil, penempatan departemen, dan rekening gaji"
	>
		<div class="space-y-4 py-2">
			<div class="grid grid-cols-2 gap-3">
				<div>
					<label for="emp-nik" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">NIK Perusahaan</label>
					<input
						id="emp-nik"
						type="text"
						bind:value={newEmp.nik}
						placeholder="Contoh: EMP-009"
						class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
					/>
				</div>
				<div>
					<label for="emp-join-date" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Tanggal Bergabung</label>
					<input
						id="emp-join-date"
						type="date"
						bind:value={newEmp.join_date}
						class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
					/>
				</div>
			</div>

			<div>
				<label for="emp-name" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Nama Lengkap Karyawan</label>
				<input
					id="emp-name"
					type="text"
					bind:value={newEmp.full_name}
					placeholder="Nama sesuai KTP"
					class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
				/>
			</div>

			<div class="grid grid-cols-2 gap-3">
				<div>
					<label for="emp-email" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Email Kantor</label>
					<input
						id="emp-email"
						type="email"
						bind:value={newEmp.email}
						placeholder="nama@pantauduit.id"
						class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
					/>
				</div>
				<div>
					<label for="emp-phone" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">No. WhatsApp / Telepon</label>
					<input
						id="emp-phone"
						type="tel"
						bind:value={newEmp.phone}
						placeholder="+6281..."
						class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
					/>
				</div>
			</div>

			<div class="grid grid-cols-2 gap-3">
				<div>
					<label for="emp-dept" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Departemen</label>
					<select
						id="emp-dept"
						bind:value={newEmp.department_name}
						class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
					>
						<option value="Engineering & Technology">Engineering & Technology</option>
						<option value="Finance & Accounting">Finance & Accounting</option>
						<option value="Human Resources & GA">Human Resources & GA</option>
						<option value="Marketing & Growth">Marketing & Growth</option>
					</select>
				</div>
				<div>
					<label for="emp-title" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Jabatan / Posisi</label>
					<input
						id="emp-title"
						type="text"
						bind:value={newEmp.designation_title}
						placeholder="Contoh: Frontend Engineer"
						class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
					/>
				</div>
			</div>

			<div class="grid grid-cols-2 gap-3">
				<div>
					<label for="emp-type" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Ikatan Kerja (Opsi Angka)</label>
					<select
						id="emp-type"
						bind:value={newEmp.employment_type}
						class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
					>
						<option value={EmploymentType.PERMANENT}>1 - Tetap (PKWTT)</option>
						<option value={EmploymentType.CONTRACT}>2 - Kontrak (PKWT)</option>
						<option value={EmploymentType.INTERN}>3 - Magang</option>
						<option value={EmploymentType.FREELANCE}>4 - Freelance</option>
					</select>
				</div>
				<div>
					<label for="emp-salary" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Gaji Pokok (IDR)</label>
					<input
						id="emp-salary"
						type="number"
						bind:value={newEmp.basic_salary}
						class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white font-mono"
					/>
				</div>
			</div>

			<div class="grid grid-cols-2 gap-3">
				<div>
					<label for="emp-bank" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Bank Penerima</label>
					<select
						id="emp-bank"
						bind:value={newEmp.bank_name}
						class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
					>
						<option value="BCA">BCA (Bank Central Asia)</option>
						<option value="Bank Mandiri">Bank Mandiri</option>
						<option value="BNI">BNI</option>
						<option value="BRI">BRI</option>
						<option value="BSI">BSI (Syariah)</option>
						<option value="Bank Jago">Bank Jago</option>
					</select>
				</div>
				<div>
					<label for="emp-acc-num" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Nomor Rekening</label>
					<input
						id="emp-acc-num"
						type="text"
						bind:value={newEmp.bank_account_number}
						placeholder="Contoh: 8830192811"
						class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white font-mono"
					/>
				</div>
			</div>
		</div>

		{#snippet footer()}
			<div class="flex items-center justify-end gap-2">
				<Button variant="ghost" onclick={() => (isAddModalOpen = false)}>
					Batal
				</Button>
				<Button variant="primary" onclick={handleAddEmployee}>
					Simpan Data Karyawan
				</Button>
			</div>
		{/snippet}
	</Sheet>

	<!-- Sheet Detail Karyawan (Drawer Kanan) -->
	{#if selectedEmployee}
		<Sheet
			bind:open={isDetailModalOpen}
			side="right"
			size="lg"
			title="Profil Karyawan & Payroll"
			description="Informasi kompensasi dan administrasi kepegawaian"
		>
			<div class="space-y-4 py-2">
				<div class="p-4 rounded-2xl bg-slate-100/80 dark:bg-white/5 flex items-center justify-between">
					<div class="flex items-center gap-3">
						<div class="w-12 h-12 rounded-2xl bg-[#007AFF] text-white flex items-center justify-center font-semibold text-lg">
							{selectedEmployee.full_name.charAt(0)}
						</div>
						<div>
							<h3 class="font-semibold text-sm text-slate-900 dark:text-white">
								{selectedEmployee.full_name}
							</h3>
							<p class="text-xs text-slate-500 font-mono">
								{selectedEmployee.nik} &bull; {selectedEmployee.designation_title}
							</p>
						</div>
					</div>
					<StatusBadge status={selectedEmployee.status} type="employee" size="md" />
				</div>

				<div class="grid grid-cols-2 gap-3 text-xs">
					<div class="p-3 rounded-2xl border border-slate-200/80 dark:border-white/10 space-y-1">
						<span class="text-slate-400 font-semibold uppercase text-[10px]">Departemen</span>
						<p class="font-semibold text-slate-900 dark:text-white">{selectedEmployee.department_name}</p>
					</div>

					<div class="p-3 rounded-2xl border border-slate-200/80 dark:border-white/10 space-y-1">
						<span class="text-slate-400 font-semibold uppercase text-[10px]">Tanggal Bergabung</span>
						<p class="font-semibold text-slate-900 dark:text-white">{formatDate(selectedEmployee.join_date)}</p>
					</div>

					<div class="p-3 rounded-2xl border border-slate-200/80 dark:border-white/10 space-y-1">
						<span class="text-slate-400 font-semibold uppercase text-[10px]">Gaji Pokok</span>
						<p class="font-semibold text-slate-900 dark:text-white font-mono">{formatRupiah(selectedEmployee.basic_salary)}</p>
					</div>

					<div class="p-3 rounded-2xl border border-slate-200/80 dark:border-white/10 space-y-1">
						<span class="text-slate-400 font-semibold uppercase text-[10px]">Rekening Bank</span>
						<p class="font-semibold text-slate-900 dark:text-white font-mono">{selectedEmployee.bank_name} - {selectedEmployee.bank_account_number || '-'}</p>
					</div>

					<div class="p-3 rounded-2xl border border-slate-200/80 dark:border-white/10 space-y-1">
						<span class="text-slate-400 font-semibold uppercase text-[10px]">Nomor NPWP</span>
						<p class="font-semibold text-slate-900 dark:text-white font-mono">{selectedEmployee.npwp || '-'}</p>
					</div>

					<div class="p-3 rounded-2xl border border-slate-200/80 dark:border-white/10 space-y-1">
						<span class="text-slate-400 font-semibold uppercase text-[10px]">BPJS Ketenagakerjaan</span>
						<p class="font-semibold text-slate-900 dark:text-white font-mono">{selectedEmployee.bpjs_tk_number || '-'}</p>
					</div>
				</div>
			</div>

			{#snippet footer()}
				<div class="flex items-center justify-end">
					<Button variant="ghost" onclick={() => (isDetailModalOpen = false)}>
						Tutup
					</Button>
				</div>
			{/snippet}
		</Sheet>
	{/if}
</div>
