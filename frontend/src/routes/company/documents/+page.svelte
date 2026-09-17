<script lang="ts">
	import { formatDate, formatRupiah } from '$lib/utils/formatters';
	import {
		getDocumentStatusInfo,
		getDocumentTemplateTypeLabel
	} from '$lib/utils/status';
	import {
		DocumentTemplateType,
		DocumentStatus,
		type DocumentTemplate,
		type EmployeeDocument
	} from '$lib/types/company';
	import Button from '$lib/components/ui/Button.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Sheet from '$lib/components/ui/Sheet.svelte';
	import Table, { type TableColumn } from '$lib/components/ui/Table.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import {
		FileText,
		Plus,
		Download,
		Printer,
		CheckCircle2,
		Clock,
		Search,
		Filter,
		Eye,
		FileCheck,
		ScrollText,
		ShieldAlert,
		Building2,
		UserCheck
	} from 'lucide-svelte';

	// Templates (aligned with backend seeds)
	const templates: DocumentTemplate[] = [
		{
			id: 'tpl-1',
			tenant_id: 'ten-corp',
			title: 'Perjanjian Kerja Waktu Tertentu (PKWT)',
			type: DocumentTemplateType.KONTRAK_PKWT,
			template_body: `SURAT PERJANJIAN KERJA WAKTU TERTENTU (PKWT)
Nomor: {{letter_number}}

Pada hari ini, tanggal {{issued_date}}, bertempat di Jakarta, telah disepakati Perjanjian Kerja antara:
1. PT Pantau Duit Solusindo, beralamat di Menara Cyber Lt. 12, Jakarta Selatan, dalam hal ini diwakili oleh Reza Aditya Pratama selaku Direktur Utama, selanjutnya disebut PIHAK PERTAMA.
2. {{employee_name}}, NIK: {{employee_nik}}, selanjutnya disebut PIHAK KEDUA.

Kedua belah pihak sepakat:
- Pasal 1: PIHAK KEDUA diterima bekerja sebagai {{designation}} pada Departemen {{department}}.
- Pasal 2: Perjanjian berlaku selama 12 bulan terhitung sejak {{start_date}} hingga {{end_date}}.
- Pasal 3: PIHAK KEDUA berhak atas gaji pokok sebesar {{basic_salary}} per bulan beserta fasilitas BPJS Ketenagakerjaan dan Kesehatan sesuai hukum yang berlaku.

Demikian surat perjanjian ini dibuat untuk dipergunakan sebagaimana mestinya.`,
			is_active: true
		},
		{
			id: 'tpl-2',
			tenant_id: 'ten-corp',
			title: 'Surat Keputusan Pengangkatan Karyawan Tetap (SK Tetap)',
			type: DocumentTemplateType.SK_PENGANGKATAN,
			template_body: `SURAT KEPUTUSAN PENGANGKATAN KARYAWAN TETAP
Nomor: {{letter_number}}

Menimbang hasil evaluasi kinerja masa percobaan (probation), Manajemen PT Pantau Duit Solusindo memutuskan:
1. Mengangkat Saudara/i {{employee_name}} (NIK: {{employee_nik}}) sebagai Karyawan Tetap terhitung sejak {{effective_date}}.
2. Jabatan yang diemban adalah {{designation}} pada Departemen {{department}}.
3. Seluruh hak, tunjangan, dan fasilitas karyawan tetap berlaku efektif sejak tanggal keputusan ini.

Ditetapkan di: Jakarta
Tanggal: {{issued_date}}
Direksi PT Pantau Duit Solusindo`,
			is_active: true
		},
		{
			id: 'tpl-3',
			tenant_id: 'ten-corp',
			title: 'Surat Peringatan Pertama (SP-1)',
			type: DocumentTemplateType.SURAT_PERINGATAN,
			template_body: `SURAT PERINGATAN PERTAMA (SP-1)
Nomor: {{letter_number}}

Diberikan kepada:
- Nama: {{employee_name}}
- NIK: {{employee_nik}}
- Jabatan: {{designation}} (Departemen {{department}})

Surat Peringatan ini diterbitkan sehubungan dengan ketidakhadiran berturut-turut tanpa pemberitahuan sah. Karyawan diharapkan memperbaiki kedisiplinan dan kepatuhan terhadap SOP perusahaan dalam tempo 6 bulan ke depan.`,
			is_active: true
		},
		{
			id: 'tpl-4',
			tenant_id: 'ten-corp',
			title: 'Surat Keterangan Pengalaman Kerja (Paklaring)',
			type: DocumentTemplateType.SURAT_PAKLARING,
			template_body: `SURAT KETERANGAN KERJA (PAKLARING)
Nomor: {{letter_number}}

Dengan ini Manajemen PT Pantau Duit Solusindo menerangkan bahwa:
- Nama: {{employee_name}}
- NIK: {{employee_nik}}
- Jabatan Terakhir: {{designation}} (Departemen {{department}})
- Masa Kerja: {{start_date}} s/d {{end_date}}

Telah menyelesaikan masa baktinya dengan baik. Kami menyampaikan terima kasih atas dedikasi dan kontribusi yang telah diberikan selama masa bertugas.`,
			is_active: true
		}
	];

	// Issued Documents
	let documents = $state<EmployeeDocument[]>([
		{
			id: 'doc-1',
			tenant_id: 'ten-corp',
			employee_id: 'emp-3',
			employee_name: 'Budi Santoso',
			employee_nik: 'EMP-003',
			template_id: 'tpl-1',
			letter_number: '001/HRD-PKWT/09/2026',
			title: 'PKWT - Budi Santoso',
			content: templates[0].template_body
				.replace('{{letter_number}}', '001/HRD-PKWT/09/2026')
				.replace('{{issued_date}}', '17 September 2026')
				.replace('{{employee_name}}', 'Budi Santoso')
				.replace('{{employee_nik}}', 'EMP-003')
				.replace('{{designation}}', 'Senior Fullstack Engineer')
				.replace('{{department}}', 'Engineering & Technology')
				.replace('{{start_date}}', '01 Oktober 2026')
				.replace('{{end_date}}', '30 September 2027')
				.replace('{{basic_salary}}', 'Rp 16.000.000'),
			status: DocumentStatus.GENERATED,
			issued_date: '2026-09-17'
		},
		{
			id: 'doc-2',
			tenant_id: 'ten-corp',
			employee_id: 'emp-5',
			employee_name: 'Dimas Arya Wijaya',
			employee_nik: 'EMP-005',
			template_id: 'tpl-1',
			letter_number: '002/HRD-PKWT/09/2026',
			title: 'PKWT - Dimas Arya Wijaya',
			content: templates[0].template_body
				.replace('{{letter_number}}', '002/HRD-PKWT/09/2026')
				.replace('{{issued_date}}', '17 September 2026')
				.replace('{{employee_name}}', 'Dimas Arya Wijaya')
				.replace('{{employee_nik}}', 'EMP-005')
				.replace('{{designation}}', 'Operations Specialist')
				.replace('{{department}}', 'Operations & Warehouse')
				.replace('{{start_date}}', '01 Oktober 2026')
				.replace('{{end_date}}', '30 September 2027')
				.replace('{{basic_salary}}', 'Rp 11.000.000'),
			status: DocumentStatus.SIGNED,
			issued_date: '2026-09-17'
		}
	]);

	// Mock employee choices
	const employeeOptions = [
		{ id: 'emp-1', name: 'Reza Aditya Pratama', nik: 'EMP-001', dept: 'Engineering', title: 'Lead Software Architect', salary: 'Rp 24.000.000' },
		{ id: 'emp-2', name: 'Siti Nurhaliza Putri', nik: 'EMP-002', dept: 'Finance', title: 'Finance Operations Manager', salary: 'Rp 18.500.000' },
		{ id: 'emp-3', name: 'Budi Santoso', nik: 'EMP-003', dept: 'Engineering', title: 'Senior Fullstack Engineer', salary: 'Rp 16.000.000' },
		{ id: 'emp-4', name: 'Dewi Lestari', nik: 'EMP-004', dept: 'Human Resources', title: 'Head of People & Culture', salary: 'Rp 17.000.000' },
		{ id: 'emp-5', name: 'Dimas Arya Wijaya', nik: 'EMP-005', dept: 'Operations', title: 'Operations Specialist', salary: 'Rp 11.000.000' },
		{ id: 'emp-6', name: 'Jessica Amanda', nik: 'EMP-006', dept: 'Marketing', title: 'Growth Marketing Lead', salary: 'Rp 15.000.000' },
		{ id: 'emp-7', name: 'Fajar Hidayat', nik: 'EMP-007', dept: 'Finance', title: 'Accounting Officer', salary: 'Rp 8.500.000' },
		{ id: 'emp-8', name: 'Nadia Larasati', nik: 'EMP-008', dept: 'Human Resources', title: 'People Associate', salary: 'Rp 4.500.000' }
	];

	// Sheet States
	let isGenerateOpen = $state(false);
	let isPreviewOpen = $state(false);
	let selectedDoc = $state<EmployeeDocument | null>(null);

	let generateForm = $state({
		template_id: 'tpl-1',
		employee_id: 'emp-1',
		letter_number: '003/HRD-PKWT/09/2026',
		title: 'PKWT Baru',
		issued_date: '2026-09-17'
	});

	let searchQuery = $state('');

	function openPreview(doc: EmployeeDocument) {
		selectedDoc = doc;
		isPreviewOpen = true;
	}

	function handleGenerateDocument() {
		const template = templates.find((t) => t.id === generateForm.template_id);
		const emp = employeeOptions.find((e) => e.id === generateForm.employee_id);

		if (!template || !emp) {
			notificationStore.error('Pilih template dan karyawan terlebih dahulu!', 'Validasi Gagal');
			return;
		}

		const renderedContent = template.template_body
			.replace(/{{letter_number}}/g, generateForm.letter_number)
			.replace(/{{issued_date}}/g, formatDate(generateForm.issued_date))
			.replace(/{{employee_name}}/g, emp.name)
			.replace(/{{employee_nik}}/g, emp.nik)
			.replace(/{{designation}}/g, emp.title)
			.replace(/{{department}}/g, emp.dept)
			.replace(/{{basic_salary}}/g, emp.salary)
			.replace(/{{start_date}}/g, '01 Oktober 2026')
			.replace(/{{end_date}}/g, '30 September 2027')
			.replace(/{{effective_date}}/g, '01 Oktober 2026');

		const newDoc: EmployeeDocument = {
			id: `doc-${Date.now()}`,
			tenant_id: 'ten-corp',
			employee_id: emp.id,
			employee_name: emp.name,
			employee_nik: emp.nik,
			template_id: template.id,
			letter_number: generateForm.letter_number,
			title: `${template.title} - ${emp.name}`,
			content: renderedContent,
			status: DocumentStatus.GENERATED,
			issued_date: generateForm.issued_date
		};

		documents = [newDoc, ...documents];
		isGenerateOpen = false;
		notificationStore.success(
			`Surat nomor ${newDoc.letter_number} berhasil diterbitkan dan siap ditandatangani!`,
			'Dokumen Terbit'
		);
	}

	function signDocument() {
		if (!selectedDoc) return;
		documents = documents.map((d) =>
			d.id === selectedDoc!.id ? { ...d, status: DocumentStatus.SIGNED } : d
		);
		selectedDoc.status = DocumentStatus.SIGNED;
		notificationStore.success(
			`Dokumen ${selectedDoc.letter_number} telah ditandatangani secara digital!`,
			'Tanda Tangan Sah'
		);
	}

	function printDocument() {
		notificationStore.info(
			'Menyiapkan tampilan cetak PDF resolusi tinggi...',
			'Print / Export PDF'
		);
		setTimeout(() => {
			window.print();
		}, 300);
	}

	let isFilterModalOpen = $state(false);
	let selectedStatus = $state<string>('ALL');

	const activeFiltersCount = $derived(selectedStatus !== 'ALL' ? 1 : 0);

	function resetFilters() {
		selectedStatus = 'ALL';
		searchQuery = '';
	}

	const filteredDocuments = $derived(
		documents.filter((d) => {
			const matchesSearch =
				d.letter_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
				d.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
				(d.employee_name && d.employee_name.toLowerCase().includes(searchQuery.toLowerCase()));
			const matchesStatus = selectedStatus === 'ALL' || d.status.toString() === selectedStatus;
			return matchesSearch && matchesStatus;
		})
	);

	const selectedDocStatusInfo = $derived(
		selectedDoc ? getDocumentStatusInfo(selectedDoc.status) : null
	);

	const columns: TableColumn<EmployeeDocument>[] = [
		{ key: 'letter_number', header: 'Nomor Surat', sortable: true, width: '190px' },
		{ key: 'title', header: 'Judul Dokumen', sortable: true },
		{ key: 'employee_nik', header: 'NIK', sortable: true, width: '90px' },
		{ key: 'employee_name', header: 'Karyawan', sortable: true },
		{ key: 'issued_date', header: 'Tanggal Terbit', sortable: true, width: '130px' },
		{ key: 'status', header: 'Status', sortable: true, align: 'center', width: '120px' },
		{ key: 'id', header: 'Aksi', align: 'center', width: '70px' }
	];
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
		<div>
			<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2.5">
				<div class="p-2 rounded-2xl bg-blue-500/10 text-[#007AFF]">
					<ScrollText class="w-6 h-6" />
				</div>
				<span>Dokumen & Surat Resmi HR</span>
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
				Generator PKWT, SK Pengangkatan, Surat Peringatan (SP), dan Paklaring dengan template dinamis
			</p>
		</div>

		<div class="flex items-center gap-2">
			<Button variant="primary" size="sm" onclick={() => (isGenerateOpen = true)}>
				<Plus class="w-4 h-4 mr-1.5" />
				<span>Terbitkan Surat Baru</span>
			</Button>
		</div>
	</div>

	<!-- Template Quick Gallery Cards -->
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
		{#each templates as tpl}
			<div class="p-4 rounded-3xl bg-white/80 dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/10 backdrop-blur-xl flex flex-col justify-between">
				<div>
					<span class="text-[10px] uppercase font-bold tracking-wider text-[#007AFF]">
						{getDocumentTemplateTypeLabel(tpl.type)}
					</span>
					<h3 class="font-bold text-xs text-slate-900 dark:text-white mt-1">{tpl.title}</h3>
					<p class="text-[11px] text-slate-500 mt-1 line-clamp-2">
						Format resmi standar hukum ketenagakerjaan RI dengan variabel otomatis
					</p>
				</div>
				<div class="mt-3 pt-2 border-t border-slate-100 dark:border-white/5 flex items-center justify-between">
					<span class="text-[10px] text-emerald-600 font-semibold flex items-center gap-1">
						<CheckCircle2 class="w-3 h-3" />
						<span>Template Aktif</span>
					</span>
				</div>
			</div>
		{/each}
	</div>

	<!-- Filter & Search Toolbar -->
	<div class="p-4 rounded-3xl bg-white/80 dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/10 backdrop-blur-xl flex flex-col sm:flex-row gap-3 items-center justify-between">
		<div class="relative w-full sm:w-80">
			<Search class="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="Cari nomor surat, jenis, atau karyawan..."
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

	<!-- Documents Table (1 Value per Column) -->
	<Table items={filteredDocuments} {columns} emptyMessage="Belum ada surat yang diterbitkan yang sesuai filter">
		{#snippet row(doc)}
			{@const statusInfo = getDocumentStatusInfo(doc.status)}
			<tr class="border-b border-slate-100 dark:border-white/5 hover:bg-slate-50/50 dark:hover:bg-white/[0.02] transition-colors text-xs">
				<!-- Nomor Surat -->
				<td class="p-3.5 whitespace-nowrap font-mono font-medium text-slate-900 dark:text-white">
					{doc.letter_number}
				</td>

				<!-- Judul Dokumen -->
				<td class="p-3.5 whitespace-nowrap text-slate-800 dark:text-slate-200 font-medium">
					{doc.title}
				</td>

				<!-- NIK -->
				<td class="p-3.5 whitespace-nowrap font-mono text-slate-500 dark:text-slate-400">
					{doc.employee_nik}
				</td>

				<!-- Karyawan -->
				<td class="p-3.5 whitespace-nowrap text-slate-800 dark:text-slate-200 font-medium">
					{doc.employee_name}
				</td>

				<!-- Tanggal Terbit -->
				<td class="p-3.5 whitespace-nowrap font-mono text-slate-600 dark:text-slate-400">
					{formatDate(doc.issued_date)}
				</td>

				<!-- Status -->
				<td class="p-3.5 whitespace-nowrap text-center">
					<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-medium border {statusInfo.badgeClass}">
						{statusInfo.label}
					</span>
				</td>

				<!-- Action (Detail & Print) -->
				<td class="p-3.5 whitespace-nowrap text-center">
					<button
						type="button"
						onclick={() => openPreview(doc)}
						class="p-1.5 rounded-xl text-slate-400 hover:text-[#007AFF] hover:bg-slate-100 dark:hover:bg-white/5 transition-colors"
						title="Buka Dokumen Resmi & Cetak"
					>
						<Eye class="w-4 h-4" />
					</button>
				</td>
			</tr>
		{/snippet}
	</Table>

	<!-- Modal Filter Dokumen -->
	<Modal
		bind:open={isFilterModalOpen}
		title="Filter Dokumen & Surat HR"
		description="Saring arsip surat resmi berdasarkan status penandatanganan"
	>
		<div class="space-y-4 py-2">
			<div>
				<label for="filter-doc-status" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Status Dokumen</label>
				<select
					id="filter-doc-status"
					bind:value={selectedStatus}
					class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
				>
					<option value="ALL">Semua Status</option>
					<option value="{DocumentStatus.GENERATED}">1 - Diterbitkan (Belum TTD)</option>
					<option value="{DocumentStatus.SIGNED}">2 - Ditandatangani Sah</option>
					<option value="{DocumentStatus.ARCHIVED}">3 - Diarsipkan</option>
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

	<!-- Sheet Terbitkan Surat Baru (Right Drawer) -->
	<Sheet
		bind:open={isGenerateOpen}
		side="right"
		size="lg"
		title="Terbitkan Dokumen HR Baru"
		description="Pilih template standar dan isi variabel karyawan secara otomatis"
	>
		<div class="space-y-4 py-2">
			<div>
				<label for="doc-tpl" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Pilih Template Surat</label>
				<select
					id="doc-tpl"
					bind:value={generateForm.template_id}
					class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
				>
					{#each templates as tpl}
						<option value={tpl.id}>{tpl.title}</option>
					{/each}
				</select>
			</div>

			<div>
				<label for="doc-emp" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Pilih Karyawan Penerima</label>
				<select
					id="doc-emp"
					bind:value={generateForm.employee_id}
					class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
				>
					{#each employeeOptions as emp}
						<option value={emp.id}>{emp.nik} &bull; {emp.name} ({emp.title})</option>
					{/each}
				</select>
			</div>

			<div class="grid grid-cols-2 gap-3">
				<div>
					<label for="doc-num" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Nomor Surat Resmi</label>
					<input
						id="doc-num"
						type="text"
						bind:value={generateForm.letter_number}
						placeholder="001/HRD-PKWT/IX/2026"
						class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white font-mono"
					/>
				</div>
				<div>
					<label for="doc-date" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Tanggal Ditetapkan</label>
					<input
						id="doc-date"
						type="date"
						bind:value={generateForm.issued_date}
						class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white font-mono"
					/>
				</div>
			</div>

			<div class="p-4 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-xs text-blue-700 dark:text-blue-300 space-y-1">
				<p class="font-semibold flex items-center gap-1.5">
					<UserCheck class="w-4 h-4" />
					<span>Variabel Terisi Otomatis</span>
				</p>
				<p class="text-[11px] leading-relaxed">
					Sistem akan menginjeksi NIK, nama lengkap, departemen, jabatan, dan nominal gaji pokok karyawan ke dalam naskah perjanjian tanpa perlu input manual.
				</p>
			</div>
		</div>

		{#snippet footer()}
			<div class="flex items-center justify-end gap-2">
				<Button variant="ghost" onclick={() => (isGenerateOpen = false)}>
					Batal
				</Button>
				<Button variant="primary" onclick={handleGenerateDocument}>
					Terbitkan & Simpan Arsip
				</Button>
			</div>
		{/snippet}
	</Sheet>

	<!-- Sheet Tinjau Dokumen Resmi (Right Drawer) -->
	{#if selectedDoc}
		<Sheet
			bind:open={isPreviewOpen}
			side="right"
			size="xl"
			title={selectedDoc.letter_number}
			description={selectedDoc.title}
		>
			<div class="space-y-4 py-2">
				<!-- Action Toolbar -->
				<div class="flex items-center justify-between p-3 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200/80 dark:border-white/10">
					<div class="flex items-center gap-2">
						<span class="text-xs text-slate-500">Status:</span>
						{#if selectedDocStatusInfo}
							<span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-semibold border {selectedDocStatusInfo.badgeClass}">
								<span class="w-1.5 h-1.5 rounded-full {selectedDocStatusInfo.dotClass}"></span>
								<span>{selectedDocStatusInfo.label}</span>
							</span>
						{/if}
					</div>

					<div class="flex items-center gap-2">
						{#if selectedDoc.status === DocumentStatus.GENERATED}
							<Button variant="outline" size="sm" onclick={signDocument}>
								<FileCheck class="w-3.5 h-3.5 mr-1" />
								<span>Tandatangani</span>
							</Button>
						{/if}
						<Button variant="outline" size="sm" onclick={printDocument}>
							<Printer class="w-3.5 h-3.5 mr-1" />
							<span>Cetak PDF</span>
						</Button>
					</div>
				</div>

				<!-- Official Paper Layout (Zero Shadow & Zero Border on Print) -->
				<div class="print-content p-6 sm:p-8 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 shadow-lg print:shadow-none print:border-none print:p-0 print:m-0 print:rounded-none space-y-6 text-slate-800 dark:text-slate-100 leading-relaxed text-sm">
					<!-- Kop Surat -->
					<div class="border-b-2 border-slate-900 dark:border-white pb-4 text-center space-y-1">
						<h2 class="font-bold text-lg tracking-wider font-sans text-slate-900 dark:text-white">
							PT PANTAU DUIT SOLUSINDO
						</h2>
						<p class="text-xs text-slate-500 font-sans">
							Gedung Menara Cyber Lt. 12, Jl. HR Rasuna Said, Jakarta Selatan 12950
						</p>
						<p class="text-[10px] text-slate-400 font-sans">
							Telp: (021) 555-0199 &bull; Email: legal@pantauduit.id &bull; Web: www.pantauduit.id
						</p>
					</div>

					<!-- Naskah Surat -->
					<div class="whitespace-pre-line text-xs font-sans leading-relaxed text-slate-700 dark:text-slate-300">
						{selectedDoc.content}
					</div>

					<!-- Tanda Tangan Section -->
					<div class="grid grid-cols-2 gap-8 pt-8 text-center text-xs font-sans">
						<div>
							<p class="font-semibold text-slate-500">PIHAK PERTAMA</p>
							<p class="text-[10px] text-slate-400">PT Pantau Duit Solusindo</p>
							<div class="h-16 flex items-center justify-center">
								<span class="px-3 py-1 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 font-mono text-[10px] font-bold">
									✓ DIGITAL SIGNED
								</span>
							</div>
							<p class="font-bold underline text-slate-900 dark:text-white">Reza Aditya Pratama</p>
							<p class="text-[10px] text-slate-400">Direktur Utama</p>
						</div>

						<div>
							<p class="font-semibold text-slate-500">PIHAK KEDUA</p>
							<p class="text-[10px] text-slate-400">Karyawan Penerima</p>
							<div class="h-16 flex items-center justify-center">
								{#if selectedDoc.status === DocumentStatus.SIGNED}
									<span class="px-3 py-1 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 font-mono text-[10px] font-bold">
										✓ TTD KARYAWAN
									</span>
								{:else}
									<span class="text-[10px] text-slate-400 italic">Menunggu TTD</span>
								{/if}
							</div>
							<p class="font-bold underline text-slate-900 dark:text-white">{selectedDoc.employee_name}</p>
							<p class="text-[10px] text-slate-400">{selectedDoc.employee_nik}</p>
						</div>
					</div>
				</div>
			</div>

			{#snippet footer()}
				<div class="flex items-center justify-end">
					<Button variant="ghost" onclick={() => (isPreviewOpen = false)}>
						Tutup
					</Button>
				</div>
			{/snippet}
		</Sheet>
	{/if}
</div>

<style>
	@media print {
		:global(body *) {
			visibility: hidden !important;
		}
		.print-content,
		.print-content * {
			visibility: visible !important;
		}
		.print-content {
			position: fixed !important;
			left: 0 !important;
			top: 0 !important;
			width: 100vw !important;
			height: auto !important;
			padding: 20mm !important;
			margin: 0 !important;
			border: none !important;
			box-shadow: none !important;
			border-radius: 0 !important;
			background: white !important;
			color: black !important;
		}
	}
</style>

