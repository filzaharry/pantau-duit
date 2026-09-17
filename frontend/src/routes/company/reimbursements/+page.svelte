<script lang="ts">
	import { formatRupiah, formatDate } from '$lib/utils/formatters';
	import {
		ReimbursementStatus,
		type Reimbursement
	} from '$lib/types/company';
	import StatusBadge from '$lib/components/ui/StatusBadge.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Sheet from '$lib/components/ui/Sheet.svelte';
	import Table, { type TableColumn } from '$lib/components/ui/Table.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import {
		Receipt,
		Plus,
		CheckCircle2,
		Clock,
		AlertCircle,
		Check,
		X,
		FileText,
		CreditCard,
		Search,
		Filter,
		Eye
	} from 'lucide-svelte';

	let reimbursements = $state<Reimbursement[]>([
		{
			id: 'rm-1',
			tenant_id: 'ten-corp',
			employee_id: 'emp-1',
			employee_nik: 'EMP-001',
			employee_name: 'Reza Aditya Pratama',
			title: 'Langganan Cloud Staging Server & Domain',
			description: 'Pembayaran tagihan infrastructure staging development via CC pribadi',
			amount: 1250000,
			status: ReimbursementStatus.PAID,
			paid_at: '2026-09-02T14:30:00Z'
		},
		{
			id: 'rm-2',
			tenant_id: 'ten-corp',
			employee_id: 'emp-6',
			employee_nik: 'EMP-006',
			employee_name: 'Jessica Amanda',
			title: 'Jamuan Makan Meeting Klien Partnership',
			description: 'Lunch meeting bersama prospective enterprise client di Grand Indonesia',
			amount: 875000,
			status: ReimbursementStatus.APPROVED
		},
		{
			id: 'rm-3',
			tenant_id: 'ten-corp',
			employee_id: 'emp-5',
			employee_nik: 'EMP-005',
			employee_name: 'Dimas Arya Wijaya',
			title: 'Pembelian Kabel Adaptor & Monitor Hub',
			description: 'Perlengkapan display testing monitor kantor',
			amount: 450000,
			status: ReimbursementStatus.SUBMITTED
		}
	]);

	// Filter states
	let searchQuery = $state('');
	let selectedStatus = $state<string>('ALL');
	let isFilterModalOpen = $state(false);

	let selectedClaim = $state<Reimbursement | null>(null);
	let isDetailModalOpen = $state(false);

	const activeFiltersCount = $derived(selectedStatus !== 'ALL' ? 1 : 0);

	function resetFilters() {
		selectedStatus = 'ALL';
		searchQuery = '';
	}

	function openDetail(rm: Reimbursement) {
		selectedClaim = rm;
		isDetailModalOpen = true;
	}

	const filteredClaims = $derived(
		reimbursements.filter((rm) => {
			const matchesSearch =
				Boolean(rm.title && rm.title.toLowerCase().includes(searchQuery.toLowerCase())) ||
				Boolean(rm.employee_name && rm.employee_name.toLowerCase().includes(searchQuery.toLowerCase())) ||
				Boolean(rm.employee_nik && rm.employee_nik.toLowerCase().includes(searchQuery.toLowerCase()));
			const matchesStatus = selectedStatus === 'ALL' || rm.status.toString() === selectedStatus;
			return matchesSearch && matchesStatus;
		})
	);

	let isAddModalOpen = $state(false);
	let newClaim = $state({
		title: '',
		amount: 250000,
		description: '',
		receipt_url: ''
	});

	function handleAddClaim() {
		if (!newClaim.title || newClaim.amount <= 0) {
			notificationStore.toast('Judul dan nominal klaim valid wajib diisi!', 'error');
			return;
		}

		const created: Reimbursement = {
			id: `rm-${Date.now()}`,
			tenant_id: 'ten-corp',
			employee_id: 'emp-1',
			employee_name: 'Reza Aditya Pratama',
			employee_nik: 'EMP-001',
			title: newClaim.title,
			amount: Number(newClaim.amount),
			description: newClaim.description,
			receipt_url: newClaim.receipt_url,
			status: ReimbursementStatus.SUBMITTED
		};

		reimbursements = [created, ...reimbursements];
		isAddModalOpen = false;
		notificationStore.success('Klaim pengeluaran berhasil diajukan!', 'Klaim Terkirim');
	}

	function approveClaim(id: string) {
		reimbursements = reimbursements.map((r) =>
			r.id === id ? { ...r, status: ReimbursementStatus.APPROVED } : r
		);
		notificationStore.success('Klaim biaya disetujui! Siap untuk dicairkan oleh Finance.', 'Persetujuan Selesai');
	}

	function payClaim(id: string) {
		reimbursements = reimbursements.map((r) =>
			r.id === id ? { ...r, status: ReimbursementStatus.PAID, paid_at: new Date().toISOString() } : r
		);
		notificationStore.success('Dana berhasil dicairkan dan otomatis terjurnal ke pengeluaran kas!', 'Kas Terdebet');
	}

	const columns: TableColumn<Reimbursement>[] = [
		{ key: 'employee_nik', header: 'NIK', sortable: true, width: '90px' },
		{ key: 'employee_name', header: 'Nama Pemohon', sortable: true },
		{ key: 'title', header: 'Judul Klaim', sortable: true },
		{ key: 'amount', header: 'Nominal', sortable: true, align: 'right' },
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
					<Receipt class="w-6 h-6" />
				</div>
				<span>Klaim Biaya & Reimbursement</span>
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
				Pengajuan biaya operasional karyawan, persetujuan atasan, dan pencairan otomatis kas perusahaan
			</p>
		</div>

		<Button variant="primary" onclick={() => (isAddModalOpen = true)}>
			<Plus class="w-4 h-4 mr-1.5" />
			<span>Ajukan Klaim Biaya</span>
		</Button>
	</div>

	<!-- Stats Cards -->
	<div class="grid grid-cols-3 gap-4">
		<div class="p-5 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
			<span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Menunggu Approval</span>
			<div class="text-2xl font-semibold text-amber-600 dark:text-amber-400 mt-1">
				{reimbursements.filter((r) => r.status === ReimbursementStatus.SUBMITTED).length} Klaim
			</div>
			<p class="text-[11px] text-slate-500 mt-1">Memerlukan verifikasi nota struk</p>
		</div>

		<div class="p-5 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
			<span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Disetujui (Siap Cair)</span>
			<div class="text-2xl font-semibold text-[#007AFF] mt-1">
				{reimbursements.filter((r) => r.status === ReimbursementStatus.APPROVED).length} Klaim
			</div>
			<p class="text-[11px] text-slate-500 mt-1">Menunggu eksekusi transfer kasir</p>
		</div>

		<div class="p-5 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
			<span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Dicairkan Bulan Ini</span>
			<div class="text-2xl font-semibold font-mono text-emerald-600 dark:text-emerald-400 mt-1">
				{formatRupiah(
					reimbursements
						.filter((r) => r.status === ReimbursementStatus.PAID)
						.reduce((acc, curr) => acc + curr.amount, 0)
				)}
			</div>
			<p class="text-[11px] text-slate-500 mt-1">Telah terjurnal ke buku pengeluaran</p>
		</div>
	</div>

	<!-- Filter & Search Controls -->
	<div class="p-4 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] flex flex-col sm:flex-row gap-3 items-center justify-between">
		<div class="w-full sm:w-80 relative">
			<Search class="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="Cari judul klaim, NIK, atau nama..."
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

	<!-- Reimbursements Table (1 Value per Column) -->
	<Table
		title="Daftar Klaim Reimbursement"
		subtitle="Data pengajuan klaim biaya staf beserta bukti struk dan status persetujuan"
		icon={Receipt}
		badge="{filteredClaims.length} Klaim"
		columns={columns}
		items={filteredClaims}
		emptyMessage="Tidak ada klaim reimbursement yang sesuai filter"
		emptyDescription="Ubah kata kunci pencarian atau reset filter untuk melihat data lainnya."
	>
		{#snippet row(rm, index)}
			<tr class="hover:bg-slate-50/60 dark:hover:bg-white/[0.02] transition-colors border-b border-slate-100 dark:border-white/5 text-xs">
				<!-- NIK -->
				<td class="p-3.5 whitespace-nowrap font-mono text-slate-500 dark:text-slate-400">
					{rm.employee_nik}
				</td>

				<!-- Nama Pemohon -->
				<td class="p-3.5 whitespace-nowrap font-medium text-slate-900 dark:text-white">
					{rm.employee_name}
				</td>

				<!-- Judul Klaim -->
				<td class="p-3.5 whitespace-nowrap text-slate-800 dark:text-slate-200">
					{rm.title}
				</td>

				<!-- Nominal -->
				<td class="p-3.5 whitespace-nowrap text-right font-mono font-medium text-slate-900 dark:text-white">
					{formatRupiah(rm.amount)}
				</td>

				<!-- Status -->
				<td class="p-3.5 whitespace-nowrap text-center">
					<StatusBadge status={rm.status} type="reimbursement" size="sm" />
				</td>

				<!-- Action (Detail) -->
				<td class="p-3.5 whitespace-nowrap text-center">
					<button
						type="button"
						onclick={() => openDetail(rm)}
						class="p-1.5 rounded-xl text-slate-400 hover:text-[#007AFF] hover:bg-slate-100 dark:hover:bg-white/5 transition-colors"
						title="Lihat Detail & Persetujuan Biaya"
					>
						<Eye class="w-4 h-4" />
					</button>
				</td>
			</tr>
		{/snippet}
	</Table>

	<!-- Modal Filter Reimbursement -->
	<Modal
		bind:open={isFilterModalOpen}
		title="Filter Klaim Reimbursement"
		description="Saring data klaim biaya berdasarkan tahapan persetujuan dan pencairan kas"
	>
		<div class="space-y-4 py-2">
			<div>
				<label for="filter-rm-status" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Status Klaim Biaya</label>
				<select
					id="filter-rm-status"
					bind:value={selectedStatus}
					class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
				>
					<option value="ALL">Semua Status</option>
					<option value="{ReimbursementStatus.SUBMITTED}">1 - Diajukan (Menunggu Approval)</option>
					<option value="{ReimbursementStatus.APPROVED}">2 - Disetujui (Siap Dicairkan)</option>
					<option value="{ReimbursementStatus.PAID}">3 - Dicairkan (Terjurnal Kas)</option>
					<option value="{ReimbursementStatus.REJECTED}">4 - Ditolak</option>
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

	<!-- Modal Detail Reimbursement -->
	{#if selectedClaim}
		<Modal
			bind:open={isDetailModalOpen}
			title="Detail Klaim Biaya (Reimbursement)"
			description="Informasi bukti nota struk dan otorisasi pencairan kas keuangan"
		>
			<div class="space-y-4 py-2 text-xs">
				<div class="p-4 rounded-2xl bg-slate-100 dark:bg-white/5 space-y-1">
					<div class="flex items-center justify-between">
						<span class="font-mono text-slate-500">{selectedClaim.employee_nik}</span>
						<StatusBadge status={selectedClaim.status} type="reimbursement" size="sm" />
					</div>
					<h3 class="font-bold text-sm text-slate-900 dark:text-white">{selectedClaim.employee_name}</h3>
					<p class="font-semibold text-base font-mono text-[#007AFF]">{formatRupiah(selectedClaim.amount)}</p>
				</div>

				<div class="p-3 rounded-2xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/5 space-y-1">
					<span class="text-slate-400 text-[10px] uppercase font-semibold">Judul Klaim</span>
					<p class="font-bold text-slate-900 dark:text-white">{selectedClaim.title}</p>
				</div>

				{#if selectedClaim.description}
					<div class="p-3 rounded-2xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/5 space-y-1">
						<span class="text-slate-400 text-[10px] uppercase font-semibold">Deskripsi / Keperluan</span>
						<p class="text-slate-700 dark:text-slate-300 leading-relaxed">{selectedClaim.description}</p>
					</div>
				{/if}
			</div>

			{#snippet footer()}
				<div class="flex items-center justify-between w-full">
					<Button variant="ghost" size="sm" onclick={() => (isDetailModalOpen = false)}>
						Tutup
					</Button>
					<div class="flex items-center gap-2">
						{#if selectedClaim?.status === ReimbursementStatus.SUBMITTED}
							<Button
								variant="primary"
								size="sm"
								onclick={() => {
									if (selectedClaim) {
										approveClaim(selectedClaim.id);
										isDetailModalOpen = false;
									}
								}}
							>
								<Check class="w-3.5 h-3.5 mr-1 text-emerald-300" />
								<span>Setujui Klaim</span>
							</Button>
						{:else if selectedClaim?.status === ReimbursementStatus.APPROVED}
							<Button
								variant="primary"
								size="sm"
								onclick={() => {
									if (selectedClaim) {
										payClaim(selectedClaim.id);
										isDetailModalOpen = false;
									}
								}}
							>
								<CreditCard class="w-3.5 h-3.5 mr-1" />
								<span>Cairkan Kas Sekarang</span>
							</Button>
						{/if}
					</div>
				</div>
			{/snippet}
		</Modal>
	{/if}

	<!-- Sheet Ajukan Klaim (Drawer Kanan) -->
	<Sheet
		bind:open={isAddModalOpen}
		side="right"
		size="md"
		title="Ajukan Klaim Biaya (Reimbursement)"
		description="Masukkan judul pengeluaran, nominal, dan keterangan nota struk"
	>
		<div class="space-y-4 py-2">
			<div>
				<label for="claim-title" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Judul Klaim Pengeluaran</label>
				<input
					id="claim-title"
					type="text"
					bind:value={newClaim.title}
					placeholder="Contoh: Jamuan Makan Klien / Beli Peralatan Kantor"
					class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
				/>
			</div>

			<div>
				<label for="claim-amount" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Nominal Klaim (IDR)</label>
				<input
					id="claim-amount"
					type="number"
					bind:value={newClaim.amount}
					class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white font-mono"
				/>
			</div>

			<div>
				<label for="claim-desc" class="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Keterangan / Keperluan Bisnis</label>
				<textarea
					id="claim-desc"
					bind:value={newClaim.description}
					rows="3"
					placeholder="Jelaskan tujuan pengeluaran..."
					class="w-full p-2.5 rounded-2xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white"
				></textarea>
			</div>
		</div>

		{#snippet footer()}
			<div class="flex items-center justify-end gap-2">
				<Button variant="ghost" onclick={() => (isAddModalOpen = false)}>
					Batal
				</Button>
				<Button variant="primary" onclick={handleAddClaim}>
					Kirim Pengajuan Klaim
				</Button>
			</div>
		{/snippet}
	</Sheet>
</div>
