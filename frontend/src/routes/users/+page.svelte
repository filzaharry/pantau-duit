<script lang="ts">
	import { onMount } from 'svelte';
	import { apiFetch } from '$lib/services/api';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Table, { type TableColumn } from '$lib/components/ui/Table.svelte';
	import {
		Users,
		UserPlus,
		Search,
		Filter,
		RotateCcw,
		Shield,
		CheckCircle2,
		AlertCircle,
		Building2,
		User as UserIcon,
		Building,
		Lock,
		Pencil,
		Trash2
	} from 'lucide-svelte';

	// Filters
	let searchQuery = $state('');
	let selectedRoleType = $state<string>('ALL');
	let selectedStatus = $state<string>('ALL');
	let isFilterOpen = $state(false);
	let isLoading = $state(true);

	const isFilterActive = $derived(selectedRoleType !== 'ALL' || selectedStatus !== 'ALL');

	// Modals
	let isAddUserModalOpen = $state(false);
	let isEditModalOpen = $state(false);
	let isDeleteModalOpen = $state(false);
	let selectedUserForAction = $state<any | null>(null);

	// Form State for Add User
	let newUserName = $state('');
	let newUserEmail = $state('');
	let newUserPassword = $state('');
	let newUserRoleType = $state<'PERSONAL' | 'COMPANY'>('PERSONAL');
	let newWorkspaceName = $state('');
	let formError = $state('');
	let isSubmitting = $state(false);

	// Form State for Edit User
	let editUserName = $state('');
	let editUserEmail = $state('');
	let editUserPassword = $state('');
	let editUserRoleType = $state<'PERSONAL' | 'COMPANY'>('PERSONAL');
	let editWorkspaceName = $state('');
	let editUserStatus = $state<'ACTIVE' | 'SUSPENDED'>('ACTIVE');

	// Database Users State
	let users = $state<any[]>([]);

	onMount(() => {
		loadUsers();
	});

	async function loadUsers() {
		isLoading = true;
		try {
			const res = await apiFetch<any[]>('/users');
			if (res.data) {
				users = res.data;
			} else {
				console.warn('Gagal memuat pengguna dari backend:', res.error);
			}
		} catch (err) {
			console.error('Error saat memuat pengguna:', err);
		} finally {
			isLoading = false;
		}
	}

	// Filtered users list
	const filteredUsers = $derived(
		users.filter((u) => {
			if (selectedRoleType !== 'ALL' && u.role_type !== selectedRoleType) return false;
			if (selectedStatus !== 'ALL' && u.status !== selectedStatus) return false;

			if (searchQuery.trim()) {
				const q = searchQuery.toLowerCase();
				const matchName = u.name.toLowerCase().includes(q);
				const matchEmail = u.email.toLowerCase().includes(q);
				const matchWs = (u.workspace_name || '').toLowerCase().includes(q);
				if (!matchName && !matchEmail && !matchWs) return false;
			}

			return true;
		})
	);

	// Clean single-value columns
	const columns: TableColumn[] = [
		{ header: 'Nama', key: 'name', width: '180px' },
		{ header: 'Email', key: 'email', width: '220px' },
		{ header: 'Role', key: 'role_type', width: '140px' },
		{ header: 'Workspace', key: 'workspace_name', width: '200px' },
		{ header: 'Terdaftar', key: 'created_at', width: '120px' },
		{ header: 'Terakhir Masuk', key: 'last_active', width: '150px' },
		{ header: 'Status', key: 'status', width: '110px' },
		{ header: 'Aksi', align: 'right', width: '100px', sortable: false }
	];

	function resetFilters() {
		selectedRoleType = 'ALL';
		selectedStatus = 'ALL';
		isFilterOpen = false;
	}

	async function handleAddUser() {
		formError = '';
		if (!newUserName.trim() || !newUserEmail.trim()) {
			formError = 'Nama lengkap dan alamat email wajib diisi.';
			return;
		}

		isSubmitting = true;
		try {
			const res = await apiFetch<any>('/users', {
				method: 'POST',
				body: JSON.stringify({
					name: newUserName.trim(),
					email: newUserEmail.trim(),
					password: newUserPassword.trim() || 'password123',
					role_type: newUserRoleType,
					workspace_name: newWorkspaceName.trim() || undefined
				})
			});

			if (res.data) {
				notificationStore.toast(`Pengguna ${newUserName} berhasil dibuat (${newUserRoleType})!`, 'success');
				isAddUserModalOpen = false;
				newUserName = '';
				newUserEmail = '';
				newUserPassword = '';
				newWorkspaceName = '';
				newUserRoleType = 'PERSONAL';
				await loadUsers();
			} else {
				formError = res.error || 'Gagal mendaftarkan pengguna di database.';
			}
		} catch (err: any) {
			formError = err.message || 'Terjadi kesalahan sistem.';
		} finally {
			isSubmitting = false;
		}
	}

	function openEditModal(user: any) {
		selectedUserForAction = user;
		editUserName = user.name;
		editUserEmail = user.email;
		editUserPassword = '';
		editUserRoleType = user.role_type || 'PERSONAL';
		editWorkspaceName = user.workspace_name || '';
		editUserStatus = user.status || 'ACTIVE';
		formError = '';
		isEditModalOpen = true;
	}

	async function handleUpdateUser() {
		if (!selectedUserForAction) return;
		formError = '';
		if (!editUserName.trim() || !editUserEmail.trim()) {
			formError = 'Nama dan email wajib diisi.';
			return;
		}

		isSubmitting = true;
		try {
			const res = await apiFetch<any>(`/users/${selectedUserForAction.id}`, {
				method: 'PUT',
				body: JSON.stringify({
					name: editUserName.trim(),
					email: editUserEmail.trim(),
					password: editUserPassword.trim() || undefined,
					role_type: editUserRoleType,
					workspace_name: editWorkspaceName.trim() || undefined,
					status: editUserStatus
				})
			});

			if (res.data) {
				notificationStore.toast(`Data pengguna ${editUserName} berhasil diperbarui!`, 'success');
				isEditModalOpen = false;
				selectedUserForAction = null;
				await loadUsers();
			} else {
				formError = res.error || 'Gagal memperbarui pengguna.';
			}
		} catch (err: any) {
			formError = err.message || 'Terjadi kesalahan sistem.';
		} finally {
			isSubmitting = false;
		}
	}

	function openDeleteModal(user: any) {
		selectedUserForAction = user;
		isDeleteModalOpen = true;
	}

	async function handleDeleteUser() {
		if (!selectedUserForAction) return;
		isSubmitting = true;
		try {
			const res = await apiFetch<any>(`/users/${selectedUserForAction.id}`, {
				method: 'DELETE'
			});

			if (res.data) {
				notificationStore.toast(`Pengguna ${selectedUserForAction.name} berhasil dihapus permanen!`, 'success');
				isDeleteModalOpen = false;
				selectedUserForAction = null;
				await loadUsers();
			} else {
				notificationStore.toast(res.error || 'Gagal menghapus pengguna.', 'error');
			}
		} catch (err: any) {
			notificationStore.toast(err.message || 'Terjadi kesalahan sistem.', 'error');
		} finally {
			isSubmitting = false;
		}
	}
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full pb-24 lg:pb-10">
	<!-- Page Header -->
	<div class="pb-2 border-b border-slate-200/80 dark:border-white/10">
		<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
			<Users class="w-6 h-6 text-[#007AFF] dark:text-[#0A84FF]" />
			<span>Manajemen Pengguna (User Management)</span>
		</h1>
		<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
			Kelola daftar pengguna terdaftar di database, buat user baru di Role Personal maupun Role Company
		</p>
	</div>

	<!-- 4-Column Metric Ribbon -->
	<div class="p-3 sm:p-5 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
		<div class="grid grid-cols-2 lg:grid-cols-4 gap-2.5 sm:gap-4 lg:divide-x divide-slate-100 dark:divide-white/5">
			<!-- Col 1: Total Users -->
			<div class="flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-[#007AFF]/10 text-[#007AFF] dark:text-[#0A84FF] flex items-center justify-center shrink-0">
					<Users class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Total Pengguna</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">{users.length} Akun</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 font-medium truncate block">Database PostgreSQL</span>
				</div>
			</div>

			<!-- Col 2: Role Personal -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-blue-500/10 text-[#007AFF] flex items-center justify-center shrink-0">
					<UserIcon class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Role Personal</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">
						{users.filter((u) => u.role_type === 'PERSONAL').length} Akun
					</span>
					<span class="text-[10px] sm:text-[11px] text-blue-500 font-medium truncate block">Keuangan Mandiri</span>
				</div>
			</div>

			<!-- Col 3: Role Company -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400 flex items-center justify-center shrink-0">
					<Building2 class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Role Company</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">
						{users.filter((u) => u.role_type === 'COMPANY').length} Akun
					</span>
					<span class="text-[10px] sm:text-[11px] text-purple-500 font-medium truncate block">Bisnis & HR Payroll</span>
				</div>
			</div>

			<!-- Col 4: Superadmin -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-amber-500/10 text-amber-600 dark:text-amber-400 flex items-center justify-center shrink-0">
					<Shield class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Administrator</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">
						{users.filter((u) => u.is_superadmin).length} Akun
					</span>
					<span class="text-[10px] sm:text-[11px] text-amber-600 dark:text-amber-400 font-medium truncate block">Full Governance</span>
				</div>
			</div>
		</div>
	</div>

	<!-- Unified Action Toolbar: Search (Max 40%), Filter Button (with Popover), & Create Button -->
	<div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
		<!-- Search Field (Max 40% Width) -->
		<div class="relative w-full sm:w-[40%] sm:max-w-[40%]">
			<Search class="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="Cari nama, email, atau workspace..."
				class="w-full h-9 pl-9 pr-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-[#007AFF] transition-colors"
			/>
		</div>

		<!-- Action Buttons: Filter & Tambah Pengguna (Aligned inline) -->
		<div class="flex items-center gap-2">
			<!-- Filter Button with Popover -->
			<div class="relative">
				<Button
					variant="ghost"
					onclick={() => (isFilterOpen = !isFilterOpen)}
					class="h-9 px-3 text-xs border border-slate-200/80 dark:border-white/10 {isFilterActive ? 'text-[#007AFF] border-[#007AFF]/40 bg-[#007AFF]/5' : ''}"
				>
					<Filter class="w-3.5 h-3.5 mr-1.5" />
					<span>Filter</span>
					{#if isFilterActive}
						<span class="w-1.5 h-1.5 rounded-full bg-[#007AFF] ml-1"></span>
					{/if}
				</Button>

				{#if isFilterOpen}
					<!-- Backdrop -->
					<button
						type="button"
						aria-label="Tutup menu filter"
						class="fixed inset-0 z-30 cursor-default bg-transparent"
						onclick={() => (isFilterOpen = false)}
					></button>

					<!-- Filter Dropdown Popover -->
					<div class="absolute right-0 top-full mt-2 w-64 p-3.5 rounded-2xl bg-white dark:bg-[#151926] border border-slate-200/80 dark:border-white/10 shadow-2xl z-40 space-y-3">
						<div>
							<span class="text-[11px] font-semibold text-slate-700 dark:text-slate-300 block mb-1.5">Tipe Role</span>
							<select
								bind:value={selectedRoleType}
								class="w-full h-8 px-2.5 rounded-lg border border-slate-200/80 dark:border-white/10 bg-slate-50 dark:bg-white/5 text-xs text-slate-700 dark:text-slate-300 focus:outline-none focus:border-[#007AFF]"
							>
								<option value="ALL">Semua Tipe Role</option>
								<option value="PERSONAL">Role Personal</option>
								<option value="COMPANY">Role Company</option>
							</select>
						</div>

						<div>
							<span class="text-[11px] font-semibold text-slate-700 dark:text-slate-300 block mb-1.5">Status Akun</span>
							<select
								bind:value={selectedStatus}
								class="w-full h-8 px-2.5 rounded-lg border border-slate-200/80 dark:border-white/10 bg-slate-50 dark:bg-white/5 text-xs text-slate-700 dark:text-slate-300 focus:outline-none focus:border-[#007AFF]"
							>
								<option value="ALL">Semua Status</option>
								<option value="ACTIVE">Aktif (Active)</option>
								<option value="SUSPENDED">Ditangguhkan</option>
							</select>
						</div>

						{#if isFilterActive}
							<div class="pt-1 border-t border-slate-100 dark:border-white/5 flex justify-end">
								<button
									type="button"
									onclick={resetFilters}
									class="text-[11px] font-semibold text-rose-500 hover:underline cursor-pointer"
								>
									Reset Filter
								</button>
							</div>
						{/if}
					</div>
				{/if}
			</div>

			<!-- Button Tambah Pengguna (Create) -->
			<Button variant="primary" onclick={() => (isAddUserModalOpen = true)} class="h-9 px-3.5 text-xs">
				<UserPlus class="w-4 h-4 mr-1.5" />
				<span>Tambah Pengguna</span>
			</Button>
		</div>
	</div>

	<!-- Users Data Table: 1 Value Per Column & Action Buttons on Every Row -->
	<Table
		title="Daftar Pengguna Database"
		subtitle="Data pengguna PostgreSQL yang dikelola langsung oleh Administrator"
		icon={Users}
		badge="{filteredUsers.length} Pengguna"
		{columns}
		items={filteredUsers}
		emptyMessage="Tidak ada pengguna yang cocok"
		emptyDescription="Coba ubah kata kunci pencarian atau filter tipe role di atas."
	>
		{#snippet row(user, index)}
			<tr class="hover:bg-slate-50/60 dark:hover:bg-white/[0.02] transition-colors">
				<!-- Kolom 1: Nama (1 Nilai) -->
				<td class="p-3.5 whitespace-nowrap font-semibold text-slate-900 dark:text-white">
					{user.name}
				</td>

				<!-- Kolom 2: Email (1 Nilai) -->
				<td class="p-3.5 whitespace-nowrap font-mono text-slate-600 dark:text-slate-400 text-xs">
					{user.email}
				</td>

				<!-- Kolom 3: Role (1 Nilai Badge) -->
				<td class="p-3.5 whitespace-nowrap">
					{#if user.is_superadmin}
						<span class="px-2.5 py-0.5 rounded-lg text-[10px] font-bold bg-purple-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/20 inline-block">
							SUPERADMIN
						</span>
					{:else if user.role_type === 'COMPANY'}
						<span class="px-2.5 py-0.5 rounded-lg text-[10px] font-semibold bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20 inline-block">
							ROLE COMPANY
						</span>
					{:else}
						<span class="px-2.5 py-0.5 rounded-lg text-[10px] font-semibold bg-[#007AFF]/10 text-[#007AFF] dark:text-[#0A84FF] border border-[#007AFF]/20 inline-block">
							ROLE PERSONAL
						</span>
					{/if}
				</td>

				<!-- Kolom 4: Workspace (1 Nilai) -->
				<td class="p-3.5 whitespace-nowrap text-slate-700 dark:text-slate-300">
					{user.workspace_name}
				</td>

				<!-- Kolom 5: Terdaftar (1 Nilai) -->
				<td class="p-3.5 whitespace-nowrap text-slate-500 dark:text-slate-400">
					{user.created_at}
				</td>

				<!-- Kolom 6: Terakhir Masuk (1 Nilai) -->
				<td class="p-3.5 whitespace-nowrap text-slate-500 dark:text-slate-400">
					{user.last_active}
				</td>

				<!-- Kolom 7: Status (1 Nilai Badge) -->
				<td class="p-3.5 whitespace-nowrap">
					<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold flex items-center gap-1 w-fit {user.status === 'ACTIVE'
						? 'bg-emerald-500/10 text-emerald-600 border border-emerald-500/20'
						: 'bg-rose-500/10 text-rose-600 border border-rose-500/20'}">
						{#if user.status === 'ACTIVE'}
							<CheckCircle2 class="w-3 h-3" />
						{:else}
							<AlertCircle class="w-3 h-3" />
						{/if}
						<span>{user.status === 'ACTIVE' ? 'Aktif' : 'Ditangguhkan'}</span>
					</span>
				</td>

				<!-- Kolom 8: Aksi (Button Update & Delete pada masing-masing row) -->
				<td class="p-3.5 text-right whitespace-nowrap">
					<div class="flex items-center justify-end gap-1.5">
						<!-- Button Update / Edit -->
						<button
							type="button"
							onclick={() => openEditModal(user)}
							title="Ubah Data Pengguna"
							class="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-white/10 text-slate-500 hover:text-[#007AFF] transition-colors cursor-pointer"
						>
							<Pencil class="w-3.5 h-3.5" />
						</button>

						<!-- Button Delete -->
						{#if !user.is_superadmin}
							<button
								type="button"
								onclick={() => openDeleteModal(user)}
								title="Hapus Pengguna"
								class="p-1.5 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-950/30 text-slate-500 hover:text-rose-600 transition-colors cursor-pointer"
							>
								<Trash2 class="w-3.5 h-3.5" />
							</button>
						{/if}
					</div>
				</td>
			</tr>
		{/snippet}
	</Table>

	<!-- Modal Tambah Pengguna Baru (Role Personal & Role Company) -->
	<Modal
		bind:open={isAddUserModalOpen}
		title="Tambah Pengguna Baru"
		description="Daftarkan pengguna baru langsung ke database dengan Role Personal atau Role Company"
	>
		<div class="space-y-4 text-xs">
			<Input
				bind:value={newUserName}
				label="Nama Lengkap Pengguna"
				placeholder="Contoh: Rudi Hermawan"
				required
			/>

			<Input
				bind:value={newUserEmail}
				type="email"
				label="Alamat Email"
				placeholder="Contoh: rudi@example.com"
				required
			/>

			<Input
				bind:value={newUserPassword}
				type="password"
				label="Kata Sandi Awal"
				placeholder="Minimal 6 karakter (Default: password123)"
			/>

			<div>
				<span class="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 block">
					Pilih Role & Tipe Workspace
				</span>
				<div class="grid grid-cols-2 gap-2.5">
					<button
						type="button"
						onclick={() => (newUserRoleType = 'PERSONAL')}
						class="p-3 rounded-xl border text-left flex flex-col gap-1 transition-all {newUserRoleType === 'PERSONAL'
							? 'border-[#007AFF] bg-[#007AFF]/5 text-[#007AFF] ring-1 ring-[#007AFF]'
							: 'border-slate-200 dark:border-white/10 hover:border-slate-300 dark:hover:border-white/20'}"
					>
						<div class="flex items-center gap-1.5 font-bold text-xs">
							<UserIcon class="w-3.5 h-3.5" />
							<span>Role Personal</span>
						</div>
						<p class="text-[10px] text-slate-500 dark:text-slate-400">
							Workspace personal untuk pengelolaan keuangan pribadi & budgeting.
						</p>
					</button>

					<button
						type="button"
						onclick={() => (newUserRoleType = 'COMPANY')}
						class="p-3 rounded-xl border text-left flex flex-col gap-1 transition-all {newUserRoleType === 'COMPANY'
							? 'border-indigo-600 bg-indigo-500/5 text-indigo-600 ring-1 ring-indigo-600'
							: 'border-slate-200 dark:border-white/10 hover:border-slate-300 dark:hover:border-white/20'}"
					>
						<div class="flex items-center gap-1.5 font-bold text-xs">
							<Building2 class="w-3.5 h-3.5" />
							<span>Role Company</span>
						</div>
						<p class="text-[10px] text-slate-500 dark:text-slate-400">
							Workspace perusahaan untuk operasional, HR, payroll, & absensi.
						</p>
					</button>
				</div>
			</div>

			<Input
				bind:value={newWorkspaceName}
				label="Nama Workspace (Opsional)"
				placeholder={newUserRoleType === 'COMPANY' ? 'Contoh: PT Sinar Makmur Sejahtera' : 'Contoh: Workspace Pribadi Rudi'}
			/>

			{#if formError}
				<p class="text-xs text-rose-500 bg-rose-50 dark:bg-rose-950/30 p-2.5 rounded-xl border border-rose-200">
					{formError}
				</p>
			{/if}
		</div>

		{#snippet footer()}
			<div class="flex items-center justify-end gap-2">
				<Button variant="ghost" onclick={() => (isAddUserModalOpen = false)} disabled={isSubmitting}>
					Batal
				</Button>
				<Button variant="primary" onclick={handleAddUser} disabled={isSubmitting}>
					<span>{isSubmitting ? 'Menyimpan...' : 'Simpan Pengguna'}</span>
				</Button>
			</div>
		{/snippet}
	</Modal>

	<!-- Modal Ubah Data Pengguna (Update) -->
	<Modal
		bind:open={isEditModalOpen}
		title="Ubah Data Pengguna"
		description="Perbarui informasi profil, role, atau workspace pengguna di database"
	>
		<div class="space-y-4 text-xs">
			<Input
				bind:value={editUserName}
				label="Nama Lengkap Pengguna"
				placeholder="Nama lengkap"
				required
			/>

			<Input
				bind:value={editUserEmail}
				type="email"
				label="Alamat Email"
				placeholder="nama@email.com"
				required
			/>

			<Input
				bind:value={editUserPassword}
				type="password"
				label="Kata Sandi Baru (Opsional)"
				placeholder="Kosongkan jika tidak ingin mengubah kata sandi"
			/>

			<div>
				<span class="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 block">
					Tipe Role & Workspace
				</span>
				<div class="grid grid-cols-2 gap-2.5">
					<button
						type="button"
						onclick={() => (editUserRoleType = 'PERSONAL')}
						class="p-2.5 rounded-xl border text-left flex items-center gap-2 transition-all {editUserRoleType === 'PERSONAL'
							? 'border-[#007AFF] bg-[#007AFF]/5 text-[#007AFF] font-bold ring-1 ring-[#007AFF]'
							: 'border-slate-200 dark:border-white/10'}"
					>
						<UserIcon class="w-3.5 h-3.5" />
						<span>Role Personal</span>
					</button>

					<button
						type="button"
						onclick={() => (editUserRoleType = 'COMPANY')}
						class="p-2.5 rounded-xl border text-left flex items-center gap-2 transition-all {editUserRoleType === 'COMPANY'
							? 'border-indigo-600 bg-indigo-500/5 text-indigo-600 font-bold ring-1 ring-indigo-600'
							: 'border-slate-200 dark:border-white/10'}"
					>
						<Building2 class="w-3.5 h-3.5" />
						<span>Role Company</span>
					</button>
				</div>
			</div>

			<Input
				bind:value={editWorkspaceName}
				label="Nama Workspace"
				placeholder="Nama workspace"
			/>

			<div>
				<span class="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 block">
					Status Akun
				</span>
				<select
					bind:value={editUserStatus}
					class="w-full h-9 px-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-[#007AFF]"
				>
					<option value="ACTIVE">Aktif (Dapat masuk ke sistem)</option>
					<option value="SUSPENDED">Ditangguhkan (Akses login diblokir)</option>
				</select>
			</div>

			{#if formError}
				<p class="text-xs text-rose-500 bg-rose-50 dark:bg-rose-950/30 p-2.5 rounded-xl border border-rose-200">
					{formError}
				</p>
			{/if}
		</div>

		{#snippet footer()}
			<div class="flex items-center justify-end gap-2">
				<Button variant="ghost" onclick={() => (isEditModalOpen = false)} disabled={isSubmitting}>
					Batal
				</Button>
				<Button variant="primary" onclick={handleUpdateUser} disabled={isSubmitting}>
					<span>{isSubmitting ? 'Memperbarui...' : 'Simpan Perubahan'}</span>
				</Button>
			</div>
		{/snippet}
	</Modal>

	<!-- Modal Konfirmasi Hapus Pengguna (Delete) -->
	<Modal
		bind:open={isDeleteModalOpen}
		title="Konfirmasi Hapus Pengguna"
		description="Apakah Anda yakin ingin menghapus akun ini secara permanen dari database?"
	>
		{#if selectedUserForAction}
			<div class="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900/50 text-xs text-rose-700 dark:text-rose-300 space-y-1">
				<p class="font-bold">Perhatian: Tindakan ini tidak dapat dibatalkan!</p>
				<p>Akun <b>{selectedUserForAction.name}</b> ({selectedUserForAction.email}) dan seluruh relasi keanggotaan workspace akan dihapus permanen dari PostgreSQL.</p>
			</div>
		{/if}

		{#snippet footer()}
			<div class="flex items-center justify-end gap-2">
				<Button variant="ghost" onclick={() => (isDeleteModalOpen = false)} disabled={isSubmitting}>
					Batal
				</Button>
				<Button variant="danger" onclick={handleDeleteUser} disabled={isSubmitting}>
					<span>{isSubmitting ? 'Menghapus...' : 'Ya, Hapus Permanen'}</span>
				</Button>
			</div>
		{/snippet}
	</Modal>
</div>
