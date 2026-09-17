<script lang="ts">
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Table, { type TableColumn } from '$lib/components/ui/Table.svelte';
	import {
		Shield,
		ShieldCheck,
		KeyRound,
		Lock,
		Plus,
		Check,
		CheckCircle2,
		X,
		AlertCircle,
		Users,
		Layers,
		Save,
		RotateCcw,
		Search,
		SlidersHorizontal,
		Trash2,
		Eye,
		HelpCircle
	} from 'lucide-svelte';

	// System Modules matching backend RBAC seed
	const modulesList = [
		{ id: 'dashboard', name: 'Dashboard & Ringkasan', desc: 'Akses metrik visual dan overview keuangan' },
		{ id: 'transactions', name: 'Riwayat Transaksi', desc: 'Pencatatan pengeluaran, pemasukan, dan mutasi' },
		{ id: 'accounts', name: 'Dompet & Rekening', desc: 'Pengelolaan saldo bank, e-wallet, dan kas' },
		{ id: 'budgets', name: 'Batas Belanja (Budgets)', desc: 'Anggaran belanja bulanan dan peringatan overbudget' },
		{ id: 'investments', name: 'Portofolio Investasi', desc: 'Pencatatan instrumen emas, saham, reksa dana, crypto' },
		{ id: 'goals', name: 'Target Tabungan (Goals)', desc: 'Sasaran tabungan dan pencapaian finansial' },
		{ id: 'reports', name: 'Laporan Finansial & Audit', desc: 'Rekapitulasi laba rugi, arus kas, dan ekspor PDF/Excel' },
		{ id: 'telegram', name: 'Integrasi Bot Telegram', desc: 'Konfigurasi bot token, webhook, dan auto-capture chat' },
		{ id: 'notifications', name: 'Pusat Notifikasi & Alert', desc: 'Pengaturan alert pengeluaran dan pesan pengingat' },
		{ id: 'subscription', name: 'Billing & Langganan SaaS', desc: 'Manajemen paket Pro/Enterprise dan tagihan' },
		{ id: 'users', name: 'Manajemen Pengguna (Users)', desc: 'Pendaftaran anggota ruang kerja dan kontrol akun' },
		{ id: 'roles', name: 'Hak Akses & Role (RBAC)', desc: 'Matriks izin otorisasi peran dan penugasan akses' },
		{ id: 'settings', name: 'Pengaturan Ruang Kerja', desc: 'Konfigurasi mata uang, tema, dan preferensi umum' }
	];

	const actionTypes = [
		{ id: 'view', label: 'View (Lihat)' },
		{ id: 'create', label: 'Create (Tambah)' },
		{ id: 'update', label: 'Update (Ubah)' },
		{ id: 'delete', label: 'Delete (Hapus)' },
		{ id: 'export', label: 'Export (Unduh)' },
		{ id: 'manage', label: 'Manage (Penuh)' }
	];

	interface RoleItem {
		id: string;
		slug: string;
		name: string;
		description: string;
		isSystem: boolean;
		usersCount: number;
		badgeBg: string;
		permissions: Record<string, boolean>;
	}

	// Roles State (B2C Personal Budgeting Platform)
	const roles = $state<RoleItem[]>([
		{
			id: 'role-superadmin',
			slug: 'superadmin',
			name: 'Superadmin',
			description: 'Pengelola penuh platform PantauDuit. Mengontrol direktori user, hak akses fitur, parameter sistem, dan telemetri bot.',
			isSystem: true,
			usersCount: 2,
			badgeBg: 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20',
			permissions: {}
		},
		{
			id: 'role-pro',
			slug: 'pro',
			name: 'Pro Subscriber',
			description: 'Pengguna personal berbayar. Akses tanpa batas ke seluruh dompet, transaksi, portofolio investasi multi-aset, dan bot Telegram AI.',
			isSystem: true,
			usersCount: 42,
			badgeBg: 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20',
			permissions: {}
		},
		{
			id: 'role-free',
			slug: 'free',
			name: 'Free User',
			description: 'Pengguna personal gratis standar. Akses pencatatan transaksi dasar, maksimal 3 dompet, 5 budget, dan kuota bot standar.',
			isSystem: true,
			usersCount: 242,
			badgeBg: 'bg-slate-500/10 text-slate-600 dark:text-slate-400 border-slate-500/20',
			permissions: {}
		},
		{
			id: 'role-support',
			slug: 'support',
			name: 'Support & Helpdesk',
			description: 'Staf layanan pelanggan untuk verifikasi status webhook bot Telegram dan troubleshooting sesi akun pengguna.',
			isSystem: false,
			usersCount: 3,
			badgeBg: 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20',
			permissions: {}
		}
	]);

	// Initialize default permissions
	for (const role of roles) {
		for (const mod of modulesList) {
			for (const act of actionTypes) {
				const key = `${mod.id}.${act.id}`;
				if (role.slug === 'superadmin') {
					role.permissions[key] = true;
				} else if (role.slug === 'pro') {
					const isFinanceMod = ['dashboard', 'transactions', 'accounts', 'budgets', 'investments', 'goals', 'reports', 'telegram', 'notifications', 'settings'].includes(mod.id);
					role.permissions[key] = isFinanceMod;
				} else if (role.slug === 'free') {
					const isCoreMod = ['dashboard', 'transactions', 'accounts', 'budgets', 'goals', 'telegram', 'notifications'].includes(mod.id);
					role.permissions[key] = isCoreMod && ['view', 'create', 'update'].includes(act.id);
				} else if (role.slug === 'support') {
					role.permissions[key] = ['telegram', 'notifications', 'users'].includes(mod.id) && ['view'].includes(act.id);
				}
			}
		}
	}

	// Filter & Search
	let searchQuery = $state('');

	const filteredRoles = $derived(
		roles.filter((r) => {
			const query = searchQuery.toLowerCase().trim();
			if (!query) return true;
			return (
				r.name.toLowerCase().includes(query) ||
				r.slug.toLowerCase().includes(query) ||
				r.description.toLowerCase().includes(query)
			);
		})
	);

	// Table Columns Definition
	const columns: TableColumn<RoleItem>[] = [
		{ header: 'Peran / Role', key: 'name', width: '220px' },
		{ header: 'Deskripsi Wewenang', key: 'description' },
		{ header: 'Cakupan Izin', key: 'slug', align: 'center', width: '160px' },
		{ header: 'Pengguna', key: 'usersCount', align: 'center', width: '120px' },
		{ header: 'Tipe', key: 'isSystem', align: 'center', width: '110px' },
		{ header: 'Aksi', align: 'right', width: '140px', sortable: false }
	];

	// Permissions Modal State
	let isPermissionsModalOpen = $state(false);
	let activeRole = $state<RoleItem>(roles[0]);

	function openPermissionsModal(role: RoleItem) {
		activeRole = role;
		isPermissionsModalOpen = true;
	}

	function handleTogglePermission(modId: string, actId: string) {
		if (activeRole.isSystem && activeRole.slug === 'superadmin') {
			notificationStore.toast('Izin Superadmin tidak dapat dibatasi karena merupakan peran sistem tertinggi.', 'warning');
			return;
		}

		const key = `${modId}.${actId}`;
		activeRole.permissions[key] = !activeRole.permissions[key];
	}

	function handleToggleModuleAll(modId: string) {
		if (activeRole.isSystem && activeRole.slug === 'superadmin') return;

		const allChecked = actionTypes.every((act) => activeRole.permissions[`${modId}.${act.id}`]);
		for (const act of actionTypes) {
			activeRole.permissions[`${modId}.${act.id}`] = !allChecked;
		}
	}

	function handleSelectAllPermissions() {
		if (activeRole.isSystem && activeRole.slug === 'superadmin') return;
		for (const mod of modulesList) {
			for (const act of actionTypes) {
				activeRole.permissions[`${mod.id}.${act.id}`] = true;
			}
		}
		notificationStore.toast('Semua izin berhasil dicentang.', 'info');
	}

	function handleSelectViewOnly() {
		if (activeRole.isSystem && activeRole.slug === 'superadmin') return;
		for (const mod of modulesList) {
			for (const act of actionTypes) {
				activeRole.permissions[`${mod.id}.${act.id}`] = act.id === 'view';
			}
		}
		notificationStore.toast('Izin diset ke mode Lihat Saja (View Only).', 'info');
	}

	function handleResetPermissions() {
		if (activeRole.isSystem && activeRole.slug === 'superadmin') return;
		for (const mod of modulesList) {
			for (const act of actionTypes) {
				activeRole.permissions[`${mod.id}.${act.id}`] = false;
			}
		}
		notificationStore.toast('Seluruh izin peran telah dikosongkan.', 'info');
	}

	function savePermissions() {
		isPermissionsModalOpen = false;
		notificationStore.toast(`Matriks hak akses untuk peran "${activeRole.name}" berhasil disimpan!`, 'success');
	}

	// Helper to calculate granted permissions count for any role
	function getGrantedCount(role: RoleItem): number {
		return Object.values(role.permissions).filter(Boolean).length;
	}

	const totalPermissionsCount = modulesList.length * actionTypes.length;

	// Modal New Custom Role
	let isNewRoleModalOpen = $state(false);
	let newRoleName = $state('');
	let newRoleSlug = $state('');
	let newRoleDescription = $state('');

	function createNewRole() {
		if (!newRoleName.trim() || !newRoleSlug.trim()) {
			notificationStore.toast('Nama role dan slug wajib diisi.', 'error');
			return;
		}

		const newRoleObj: RoleItem = {
			id: `role-${Date.now()}`,
			slug: newRoleSlug.trim().toLowerCase().replace(/\s+/g, '-'),
			name: newRoleName.trim(),
			description: newRoleDescription.trim() || 'Peran kustom ruang kerja baru',
			isSystem: false,
			usersCount: 0,
			badgeBg: 'bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border-indigo-500/20',
			permissions: {}
		};

		// Default view only on core finance
		for (const mod of modulesList) {
			for (const act of actionTypes) {
				newRoleObj.permissions[`${mod.id}.${act.id}`] = act.id === 'view';
			}
		}

		roles.push(newRoleObj);
		isNewRoleModalOpen = false;
		newRoleName = '';
		newRoleSlug = '';
		newRoleDescription = '';
		notificationStore.toast(`Role kustom "${newRoleObj.name}" berhasil dibuat. Silakan atur izinnya.`, 'success');

		// Open permission modal immediately for convenient setup
		openPermissionsModal(newRoleObj);
	}

	function handleDeleteRole(role: RoleItem) {
		if (role.isSystem) {
			notificationStore.toast('Peran bawaan sistem tidak dapat dihapus.', 'error');
			return;
		}

		const idx = roles.findIndex((r) => r.id === role.id);
		if (idx !== -1) {
			const deletedName = roles[idx].name;
			roles.splice(idx, 1);
			notificationStore.toast(`Role "${deletedName}" berhasil dihapus.`, 'info');
		}
	}
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full pb-24 lg:pb-10">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
		<div>
			<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
				<KeyRound class="w-6 h-6 text-[#007AFF] dark:text-[#0A84FF]" />
				<span>Manajemen Hak Akses & Role (RBAC)</span>
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
				Kelola daftar peran pengguna ruang kerja, wewenang otorisasi, dan matriks izin granular sistem
			</p>
		</div>

		<div class="flex items-center gap-2 self-start sm:self-auto">
			<Button variant="primary" onclick={() => (isNewRoleModalOpen = true)} class="h-9 px-4">
				<Plus class="w-4 h-4" />
				<span>Buat Role Kustom</span>
			</Button>
		</div>
	</div>

	<!-- Top Metric Ribbon Strip (4 Columns) -->
	<div class="p-3 sm:p-5 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
		<div class="grid grid-cols-2 lg:grid-cols-4 gap-2.5 sm:gap-4 lg:divide-x divide-slate-100 dark:divide-white/5">
			<!-- Col 1: Roles Count -->
			<div class="flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400 flex items-center justify-center shrink-0">
					<ShieldCheck class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Total Peran (Roles)</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">{roles.length} Role Terdaftar</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">3 Bawaan &bull; {roles.length - 3} Kustom</span>
				</div>
			</div>

			<!-- Col 2: Granular Permissions -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-[#007AFF]/10 text-[#007AFF] dark:text-[#0A84FF] flex items-center justify-center shrink-0">
					<KeyRound class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Izin Granular</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">{totalPermissionsCount} Titik Izin</span>
					<span class="text-[10px] sm:text-[11px] text-emerald-500 font-medium truncate block">Matriks 13 Modul x 6 Aksi</span>
				</div>
			</div>

			<!-- Col 3: Enforced Users -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
					<Users class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Pengguna Ditegakkan</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">
						{roles.reduce((acc, r) => acc + r.usersCount, 0)} Pengguna
					</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">100% Menggunakan RBAC</span>
				</div>
			</div>

			<!-- Col 4: Security Mode -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-blue-500/10 text-blue-500 flex items-center justify-center shrink-0">
					<Lock class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Penegakan Izin</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">Strict RBAC</span>
					<span class="text-[10px] sm:text-[11px] text-emerald-500 font-medium truncate block">JWT + Scope Claims</span>
				</div>
			</div>
		</div>
	</div>

	<!-- Search Toolbar -->
	<div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2.5">
		<div class="relative flex-1 max-w-md">
			<Search class="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="Cari peran berdasarkan nama, slug, atau deskripsi..."
				class="w-full h-9 pl-9 pr-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-[#007AFF] transition-colors"
			/>
		</div>

		<div class="text-[11px] text-slate-400 self-end sm:self-auto font-medium">
			Menampilkan <strong class="text-slate-900 dark:text-white">{filteredRoles.length}</strong> dari {roles.length} Peran
		</div>
	</div>

	<!-- Reusable Global Table Component for Roles -->
	<Table
		title="Daftar Peran & Hak Akses Ruang Kerja"
		subtitle="Konfigurasi izin pengguna PantauDuit dengan otorisasi berbasis peran (Role-Based Access Control)"
		icon={Shield}
		badge="{filteredRoles.length} Peran"
		{columns}
		items={filteredRoles}
		emptyMessage="Tidak ada peran yang cocok"
		emptyDescription="Ubah kata kunci pencarian peran Anda di kolom pencarian di atas."
	>
		{#snippet row(role, index)}
			{@const granted = getGrantedCount(role)}
			{@const percentage = Math.round((granted / totalPermissionsCount) * 100)}
			<tr class="hover:bg-slate-50/60 dark:hover:bg-white/[0.02] transition-colors">
				<!-- Role Name & Slug -->
				<td class="p-3.5 whitespace-nowrap">
					<div class="flex items-center gap-3">
						<div class="w-8 h-8 rounded-xl flex items-center justify-center shrink-0 {role.slug === 'superadmin' ? 'bg-purple-500/10 text-purple-600 dark:text-purple-400' : role.slug === 'pro' ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400' : role.slug === 'free' ? 'bg-slate-500/10 text-slate-600 dark:text-slate-400' : 'bg-blue-500/10 text-blue-500'}">
							<Shield class="w-4 h-4" />
						</div>
						<div>
							<span class="font-semibold text-xs text-slate-900 dark:text-white block">
								{role.name}
							</span>
							<span class="text-[10px] font-mono text-slate-400 block">
								slug: {role.slug}
							</span>
						</div>
					</div>
				</td>

				<!-- Description -->
				<td class="p-3.5">
					<p class="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-2 leading-relaxed max-w-md">
						{role.description}
					</p>
				</td>

				<!-- Permissions Coverage Progress -->
				<td class="p-3.5 whitespace-nowrap text-center">
					<div class="inline-flex flex-col items-center gap-1 min-w-[110px]">
						<div class="flex items-center gap-1.5 text-[11px] font-semibold text-slate-800 dark:text-slate-200">
							<span>{granted} / {totalPermissionsCount}</span>
							<span class="text-[10px] text-slate-400 font-normal">({percentage}%)</span>
						</div>
						<div class="w-24 h-1.5 rounded-full bg-slate-100 dark:bg-white/10 overflow-hidden">
							<div
								class="h-full rounded-full transition-all duration-300 {percentage === 100 ? 'bg-purple-500' : percentage > 50 ? 'bg-[#007AFF]' : 'bg-amber-500'}"
								style="width: {percentage}%"
							></div>
						</div>
					</div>
				</td>

				<!-- User Count -->
				<td class="p-3.5 whitespace-nowrap text-center">
					<span class="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-700 dark:text-slate-300 px-2.5 py-1 rounded-lg bg-slate-100/80 dark:bg-white/5">
						<Users class="w-3.5 h-3.5 text-slate-400" />
						<span>{role.usersCount}</span>
					</span>
				</td>

				<!-- Type Badge (System / Custom) -->
				<td class="p-3.5 whitespace-nowrap text-center">
					{#if role.isSystem}
						<span class="px-2 py-0.5 rounded-full text-[9px] font-semibold tracking-wider bg-slate-100 dark:bg-white/5 text-slate-500 dark:text-slate-400 border border-slate-200/60 dark:border-white/10">
							SISTEM
						</span>
					{:else}
						<span class="px-2 py-0.5 rounded-full text-[9px] font-semibold tracking-wider bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20">
							KUSTOM
						</span>
					{/if}
				</td>

				<!-- Actions -->
				<td class="p-3.5 whitespace-nowrap text-right">
					<div class="flex items-center justify-end gap-1.5">
						<Button
							variant="outline"
							onclick={() => openPermissionsModal(role)}
							class="h-8 px-2.5 text-xs border-slate-200/80 dark:border-white/10 hover:border-[#007AFF]"
							title="Buka Matriks Izin Akses"
						>
							<SlidersHorizontal class="w-3.5 h-3.5 text-[#007AFF] dark:text-[#0A84FF]" />
							<span class="hidden sm:inline">Atur Izin</span>
						</Button>

						{#if !role.isSystem}
							<Button
								variant="ghost"
								onclick={() => handleDeleteRole(role)}
								class="h-8 w-8 p-0 text-rose-500 hover:bg-rose-500/10"
								title="Hapus Role Kustom"
							>
								<Trash2 class="w-3.5 h-3.5" />
							</Button>
						{/if}
					</div>
				</td>
			</tr>
		{/snippet}

		{#snippet footer()}
			<div class="flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-slate-500 dark:text-slate-400 px-2 py-1">
				<span class="text-[11px]">
					Peran sistem bawaan terkunci untuk keamanan operasional inti PantauDuit.
				</span>
				<div class="flex items-center gap-3 text-[11px]">
					<span class="flex items-center gap-1.5">
						<span class="w-2 h-2 rounded-full bg-purple-500"></span> Superadmin (Penuh)
					</span>
					<span class="flex items-center gap-1.5">
						<span class="w-2 h-2 rounded-full bg-[#007AFF]"></span> Pro Subscriber
					</span>
					<span class="flex items-center gap-1.5">
						<span class="w-2 h-2 rounded-full bg-slate-400"></span> Free User
					</span>
				</div>
			</div>
		{/snippet}
	</Table>
</div>

<!-- Modal Matriks Hak Akses & Perizinan (RBAC) -->
<Modal
	bind:open={isPermissionsModalOpen}
	title="Matriks Hak Akses: {activeRole.name}"
	description="Konfigurasi izin granular 13 modul sistem untuk peran {activeRole.name} (slug: {activeRole.slug})"
>
	<div class="space-y-4 text-xs">
		<!-- Role Info Banner -->
		<div class="p-3.5 rounded-xl bg-slate-50 dark:bg-white/[0.02] border border-slate-100 dark:border-white/5 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
			<div>
				<div class="flex items-center gap-2">
					<span class="font-semibold text-slate-900 dark:text-white text-xs">
						{activeRole.name}
					</span>
					<span class="px-1.5 py-0.2 rounded text-[9px] font-mono font-semibold {activeRole.badgeBg}">
						{activeRole.slug}
					</span>
					{#if activeRole.isSystem}
						<span class="px-1.5 py-0.2 rounded text-[9px] font-semibold bg-slate-100 dark:bg-white/5 text-slate-400">
							BAWAAN SISTEM
						</span>
					{/if}
				</div>
				<p class="text-[11px] text-slate-400 mt-0.5">
					{activeRole.description}
				</p>
			</div>

			<div class="sm:text-right shrink-0">
				<span class="text-[10px] text-slate-400 block">Cakupan Izin:</span>
				<strong class="text-xs font-semibold text-slate-900 dark:text-white">
					{getGrantedCount(activeRole)} / {totalPermissionsCount} Izin Aktif
				</strong>
			</div>
		</div>

		<!-- Quick Batch Actions Toolbar -->
		<div class="flex flex-wrap items-center justify-between gap-2 border-y border-slate-100 dark:border-white/5 py-2.5">
			<span class="text-[11px] text-slate-400 font-medium">Pilihan Cepat:</span>
			<div class="flex items-center gap-1.5">
				<Button
					variant="ghost"
					onclick={handleSelectAllPermissions}
					disabled={activeRole.isSystem && activeRole.slug === 'superadmin'}
					class="h-7 px-2.5 text-[11px]"
				>
					<span>Pilih Semua</span>
				</Button>

				<Button
					variant="ghost"
					onclick={handleSelectViewOnly}
					disabled={activeRole.isSystem && activeRole.slug === 'superadmin'}
					class="h-7 px-2.5 text-[11px]"
				>
					<span>Hanya Lihat (View)</span>
				</Button>

				<Button
					variant="ghost"
					onclick={handleResetPermissions}
					disabled={activeRole.isSystem && activeRole.slug === 'superadmin'}
					class="h-7 px-2.5 text-[11px] text-rose-500 hover:text-rose-600"
				>
					<span>Kosongkan</span>
				</Button>
			</div>
		</div>

		<!-- Permissions Matrix Table -->
		<div class="rounded-xl border border-slate-200/70 dark:border-white/[0.06] overflow-x-auto max-h-[380px] overflow-y-auto">
			<table class="w-full text-xs text-left">
				<thead class="sticky top-0 bg-slate-100 dark:bg-[#151926] z-10">
					<tr class="border-b border-slate-200/80 dark:border-white/10 text-slate-400 font-semibold">
						<th class="p-3">Modul Sistem</th>
						{#each actionTypes as act}
							<th class="p-3 text-center whitespace-nowrap">{act.label}</th>
						{/each}
					</tr>
				</thead>
				<tbody class="divide-y divide-slate-100 dark:divide-white/5">
					{#each modulesList as mod}
						<tr class="hover:bg-slate-50/60 dark:hover:bg-white/[0.02] transition-colors">
							<!-- Module Info -->
							<td class="p-3">
								<button
									type="button"
									onclick={() => handleToggleModuleAll(mod.id)}
									class="text-left group cursor-pointer"
									title="Klik untuk memilih/membatalkan semua izin di modul ini"
								>
									<p class="font-semibold text-slate-900 dark:text-white group-hover:text-[#007AFF] transition-colors text-xs">
										{mod.name}
									</p>
									<span class="text-[10px] text-slate-400 block font-mono">{mod.desc}</span>
								</button>
							</td>

							<!-- Actions Checkbox Columns -->
							{#each actionTypes as act}
								{@const isChecked = !!activeRole.permissions[`${mod.id}.${act.id}`]}
								<td class="p-3 text-center">
									<button
										type="button"
										onclick={() => handleTogglePermission(mod.id, act.id)}
										disabled={activeRole.isSystem && activeRole.slug === 'superadmin'}
										class="w-6 h-6 rounded-lg flex items-center justify-center mx-auto transition-all cursor-pointer {isChecked
											? 'bg-[#007AFF] text-white'
											: 'bg-slate-100 dark:bg-white/5 text-transparent border border-slate-200/80 dark:border-white/10 hover:border-slate-300'} {activeRole.isSystem && activeRole.slug === 'superadmin' ? 'opacity-80 cursor-not-allowed' : ''}"
									>
										<Check class="w-3.5 h-3.5 stroke-[2.5]" />
									</button>
								</td>
							{/each}
						</tr>
					{/each}
				</tbody>
			</table>
		</div>

		<!-- Footer Buttons -->
		<div class="flex items-center justify-between pt-3 border-t border-slate-100 dark:border-white/5">
			<span class="text-[11px] text-slate-400">
				Perubahan izin akan langsung aktif pada sesi token berikutnya.
			</span>

			<div class="flex items-center gap-2">
				<Button variant="ghost" onclick={() => (isPermissionsModalOpen = false)}>
					Batal
				</Button>
				<Button variant="primary" onclick={savePermissions} class="px-4">
					<Save class="w-3.5 h-3.5 mr-1" />
					<span>Simpan Izin</span>
				</Button>
			</div>
		</div>
	</div>
</Modal>

<!-- Modal Buat Role Kustom Baru -->
<Modal
	bind:open={isNewRoleModalOpen}
	title="Buat Role Kustom Baru"
	description="Definisikan nama peran baru dan konfigurasi wewenang izinnya"
>
	<div class="space-y-4 text-xs">
		<Input
			bind:value={newRoleName}
			label="Nama Peran (Role Name)"
			placeholder="Contoh: Auditor Eksternal, Supervisor Akun"
		/>

		<Input
			bind:value={newRoleSlug}
			label="Slug Identifier (Unik)"
			placeholder="Contoh: auditor-eksternal"
		/>

		<Input
			bind:value={newRoleDescription}
			label="Deskripsi Wewenang"
			placeholder="Jelaskan batasan dan peruntukan role ini..."
		/>

		<div class="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 text-slate-700 dark:text-slate-300 text-[11px]">
			Setelah role dibuat, modal konfigurasi perizinan matriks akan otomatis terbuka untuk mengatur akses modul secara rinci.
		</div>

		<div class="flex justify-end gap-2 pt-2 border-t border-slate-100 dark:border-white/5">
			<Button variant="ghost" onclick={() => (isNewRoleModalOpen = false)}>
				Batal
			</Button>
			<Button variant="primary" onclick={createNewRole}>
				Simpan Role
			</Button>
		</div>
	</div>
</Modal>

