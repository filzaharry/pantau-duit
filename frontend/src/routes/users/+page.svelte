<script lang="ts">
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
		ShieldCheck,
		Bot,
		Mail,
		CheckCircle2,
		AlertCircle,
		Lock,
		Edit3,
		KeyRound,
		UserX,
		UserCheck,
		Crown,
		Receipt
	} from 'lucide-svelte';

	// Filters
	let searchQuery = $state('');
	let selectedPlan = $state<string>('ALL');
	let selectedStatus = $state<string>('ALL');

	// Modals
	let isAddUserModalOpen = $state(false);
	let isEditRoleModalOpen = $state(false);
	let selectedUserForEdit = $state<any | null>(null);

	// Form State for Add User
	let newUserName = $state('');
	let newUserEmail = $state('');
	let newUserPlan = $state('free');
	let newUserTelegram = $state('');
	let formError = $state('');

	// Mock User Data (All Personal Finance Individuals)
	const users = $state([
		{
			id: 'usr-001',
			name: 'Alex Chandra',
			email: 'alex@pantauduit.id',
			avatarBg: 'from-purple-600 to-indigo-600',
			role: 'superadmin',
			roleLabel: 'Superadmin',
			plan: 'PRO',
			telegramUsername: '@alex_pd',
			isTelegramLinked: true,
			txCount: 320,
			status: 'ACTIVE',
			createdAt: '15 Jan 2026',
			lastActive: '2 mnt yang lalu'
		},
		{
			id: 'usr-002',
			name: 'Budi Pratama',
			email: 'budi.pratama@gmail.com',
			avatarBg: 'from-blue-600 to-cyan-600',
			role: 'subscriber',
			roleLabel: 'Pro Subscriber',
			plan: 'PRO',
			telegramUsername: '@budipratama',
			isTelegramLinked: true,
			txCount: 148,
			status: 'ACTIVE',
			createdAt: '12 Sep 2026',
			lastActive: '15 mnt yang lalu'
		},
		{
			id: 'usr-003',
			name: 'Siti Rahmawati',
			email: 'siti.rahma@yahoo.com',
			avatarBg: 'from-amber-600 to-orange-600',
			role: 'user',
			roleLabel: 'Free User',
			plan: 'FREE',
			telegramUsername: '@siti_rahma',
			isTelegramLinked: true,
			txCount: 84,
			status: 'ACTIVE',
			createdAt: '12 Sep 2026',
			lastActive: '1 jam yang lalu'
		},
		{
			id: 'usr-004',
			name: 'Dimas Nugroho',
			email: 'dimas.nugroho@gmail.com',
			avatarBg: 'from-emerald-600 to-teal-600',
			role: 'user',
			roleLabel: 'Free User',
			plan: 'FREE',
			telegramUsername: '-',
			isTelegramLinked: false,
			txCount: 19,
			status: 'ACTIVE',
			createdAt: '12 Sep 2026',
			lastActive: '3 jam yang lalu'
		},
		{
			id: 'usr-005',
			name: 'Anisa Maharani',
			email: 'anisa.mhrn@outlook.com',
			avatarBg: 'from-rose-600 to-pink-600',
			role: 'subscriber',
			roleLabel: 'Pro Subscriber',
			plan: 'PRO',
			telegramUsername: '@anisa_m',
			isTelegramLinked: true,
			txCount: 215,
			status: 'ACTIVE',
			createdAt: '11 Sep 2026',
			lastActive: '5 jam yang lalu'
		},
		{
			id: 'usr-006',
			name: 'Reza Fahrezi',
			email: 'reza.fahrezi@gmail.com',
			avatarBg: 'from-indigo-600 to-purple-600',
			role: 'user',
			roleLabel: 'Free User',
			plan: 'FREE',
			telegramUsername: '@reza_f',
			isTelegramLinked: true,
			txCount: 62,
			status: 'ACTIVE',
			createdAt: '11 Sep 2026',
			lastActive: '1 hari yang lalu'
		},
		{
			id: 'usr-007',
			name: 'Dewi Lestari',
			email: 'dewi.lestari@gmail.com',
			avatarBg: 'from-teal-600 to-cyan-600',
			role: 'subscriber',
			roleLabel: 'Pro Subscriber',
			plan: 'PRO',
			telegramUsername: '@dewilestari',
			isTelegramLinked: true,
			txCount: 190,
			status: 'ACTIVE',
			createdAt: '08 Sep 2026',
			lastActive: '2 hari yang lalu'
		},
		{
			id: 'usr-008',
			name: 'Kevin Pratama',
			email: 'kevin.spam@trashmail.com',
			avatarBg: 'from-slate-700 to-slate-800',
			role: 'user',
			roleLabel: 'Free User',
			plan: 'FREE',
			telegramUsername: '@kevin_fake',
			isTelegramLinked: false,
			txCount: 0,
			status: 'SUSPENDED',
			createdAt: '01 Agu 2026',
			lastActive: '12 hari yang lalu'
		}
	]);

	// Filtered users list
	const filteredUsers = $derived(
		users.filter((u) => {
			if (selectedPlan !== 'ALL' && u.plan !== selectedPlan) return false;
			if (selectedStatus !== 'ALL' && u.status !== selectedStatus) return false;

			if (searchQuery.trim()) {
				const q = searchQuery.toLowerCase();
				const matchName = u.name.toLowerCase().includes(q);
				const matchEmail = u.email.toLowerCase().includes(q);
				const matchTg = u.telegramUsername.toLowerCase().includes(q);
				if (!matchName && !matchEmail && !matchTg) return false;
			}

			return true;
		})
	);

	const columns: TableColumn[] = [
		{ header: 'Pengguna', key: 'name', width: '240px' },
		{ header: 'Paket Akun', key: 'plan', width: '140px' },
		{ header: 'Bot Telegram', key: 'telegramUsername', width: '160px' },
		{ header: 'Catatan Dibuat', key: 'createdAt', width: '130px' },
		{ header: 'Terakhir Aktif', key: 'lastActive', width: '150px' },
		{ header: 'Status', key: 'status', width: '120px' },
		{ header: 'Aksi', align: 'right', width: '90px', sortable: false }
	];

	function resetFilters() {
		searchQuery = '';
		selectedPlan = 'ALL';
		selectedStatus = 'ALL';
	}

	function handleAddUser() {
		formError = '';
		if (!newUserName.trim() || !newUserEmail.trim()) {
			formError = 'Nama dan email wajib diisi.';
			return;
		}

		const isPro = newUserPlan === 'pro';
		users.unshift({
			id: `usr-${Date.now()}`,
			name: newUserName.trim(),
			email: newUserEmail.trim(),
			avatarBg: 'from-blue-600 to-indigo-600',
			role: isPro ? 'subscriber' : 'user',
			roleLabel: isPro ? 'Pro Subscriber' : 'Free User',
			plan: isPro ? 'PRO' : 'FREE',
			telegramUsername: newUserTelegram.trim() ? (newUserTelegram.startsWith('@') ? newUserTelegram.trim() : `@${newUserTelegram.trim()}`) : '-',
			isTelegramLinked: Boolean(newUserTelegram.trim()),
			txCount: 0,
			status: 'ACTIVE',
			createdAt: 'Baru saja',
			lastActive: 'Baru saja'
		});

		notificationStore.toast(`Pengguna ${newUserName} berhasil didaftarkan!`, 'success');
		isAddUserModalOpen = false;
		newUserName = '';
		newUserEmail = '';
		newUserTelegram = '';
		newUserPlan = 'free';
	}

	function toggleSuspendUser(user: any) {
		if (user.role === 'superadmin') {
			notificationStore.toast('Akun Superadmin utama tidak dapat disuspend!', 'warning');
			return;
		}

		user.status = user.status === 'ACTIVE' ? 'SUSPENDED' : 'ACTIVE';
		notificationStore.toast(
			user.status === 'ACTIVE'
				? `Akun ${user.name} berhasil diaktifkan kembali.`
				: `Akun ${user.name} telah ditangguhkan.`,
			user.status === 'ACTIVE' ? 'success' : 'info'
		);
	}

	function openEditRole(user: any) {
		selectedUserForEdit = { ...user };
		isEditRoleModalOpen = true;
	}

	function handleSaveUserRole() {
		if (!selectedUserForEdit) return;

		const target = users.find((u) => u.id === selectedUserForEdit.id);
		if (target) {
			target.role = selectedUserForEdit.role;
			target.plan = selectedUserForEdit.plan;
			target.roleLabel = selectedUserForEdit.plan === 'PRO' ? 'Pro Subscriber' : selectedUserForEdit.role === 'superadmin' ? 'Superadmin' : 'Free User';
			target.status = selectedUserForEdit.status;
		}

		notificationStore.toast(`Pengaturan akun ${selectedUserForEdit.name} berhasil diperbarui!`, 'success');
		isEditRoleModalOpen = false;
		selectedUserForEdit = null;
	}
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full pb-24 lg:pb-10">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-200/80 dark:border-white/10">
		<div>
			<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
				<Users class="w-6 h-6 text-[#007AFF] dark:text-[#0A84FF]" />
				<span>Manajemen Pengguna (User Management)</span>
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
				Kelola daftar pengguna aplikasi PantauDuit, paket langganan personal, dan status akses akun
			</p>
		</div>

		<div class="flex items-center gap-2 self-start sm:self-auto">
			<Button variant="primary" onclick={() => (isAddUserModalOpen = true)} class="h-9 px-3.5 text-xs">
				<UserPlus class="w-4 h-4" />
				<span>Tambah Pengguna</span>
			</Button>
		</div>
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
					<span class="text-[10px] sm:text-[11px] text-emerald-500 font-medium truncate block">Personal Budgeting</span>
				</div>
			</div>

			<!-- Col 2: Active Users -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
					<CheckCircle2 class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Pengguna Aktif</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">
						{users.filter((u) => u.status === 'ACTIVE').length} Akun
					</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">Status Terverifikasi</span>
				</div>
			</div>

			<!-- Col 3: Telegram Linked -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-blue-500/10 text-[#0088cc] flex items-center justify-center shrink-0">
					<Bot class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Terhubung Telegram</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">
						{users.filter((u) => u.isTelegramLinked).length} Pengguna
					</span>
					<span class="text-[10px] sm:text-[11px] text-blue-500 font-medium truncate block">Chatbot Aktif</span>
				</div>
			</div>

			<!-- Col 4: Pro Plan Users -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-amber-500/10 text-amber-600 dark:text-amber-400 flex items-center justify-center shrink-0">
					<Crown class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Pelanggan Pro</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">
						{users.filter((u) => u.plan === 'PRO').length} Pengguna
					</span>
					<span class="text-[10px] sm:text-[11px] text-amber-600 dark:text-amber-400 font-medium truncate block">Fitur Penuh</span>
				</div>
			</div>
		</div>
	</div>

	<!-- Search & Filters Toolbar -->
	<div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5">
		<div class="relative flex-1">
			<Search class="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="Cari pengguna berdasarkan nama, email, atau @telegram..."
				class="w-full h-9 pl-9 pr-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-[#007AFF] transition-colors"
			/>
		</div>

		<div class="flex items-center gap-2">
			<select
				bind:value={selectedPlan}
				class="h-9 px-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-700 dark:text-slate-300 focus:outline-none focus:border-[#007AFF]"
			>
				<option value="ALL">Semua Paket Akun</option>
				<option value="PRO">Pro Subscriber</option>
				<option value="FREE">Free User</option>
			</select>

			<select
				bind:value={selectedStatus}
				class="h-9 px-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-700 dark:text-slate-300 focus:outline-none focus:border-[#007AFF]"
			>
				<option value="ALL">Semua Status</option>
				<option value="ACTIVE">Aktif (Active)</option>
				<option value="SUSPENDED">Ditangguhkan</option>
			</select>

			{#if searchQuery || selectedPlan !== 'ALL' || selectedStatus !== 'ALL'}
				<Button variant="ghost" onclick={resetFilters} class="h-9 px-3 text-xs text-slate-500">
					<RotateCcw class="w-3.5 h-3.5 mr-1" />
					<span>Reset</span>
				</Button>
			{/if}
		</div>
	</div>

	<!-- Users Data Table using global reusable Table component -->
	<Table
		title="Daftar Pengguna Platform"
		subtitle="Direktori seluruh akun personal finance individu yang terdaftar di PantauDuit"
		icon={Users}
		badge="{filteredUsers.length} Pengguna"
		{columns}
		items={filteredUsers}
		emptyMessage="Tidak ada pengguna yang cocok"
		emptyDescription="Coba ubah kata kunci pencarian atau filter status dan paket di atas."
	>
		{#snippet row(user, index)}
			<tr class="hover:bg-slate-50/60 dark:hover:bg-white/[0.02] transition-colors">
				<!-- User Avatar & Email -->
				<td class="p-3.5 whitespace-nowrap">
					<div class="flex items-center gap-3">
						<div class="w-8 h-8 rounded-full bg-gradient-to-br {user.avatarBg} text-white flex items-center justify-center font-semibold text-xs shrink-0">
							{user.name.slice(0, 2).toUpperCase()}
						</div>
						<div>
							<p class="font-semibold text-slate-900 dark:text-white">{user.name}</p>
							<span class="text-[11px] text-slate-400 font-mono">{user.email}</span>
						</div>
					</div>
				</td>

				<!-- Plan Badge -->
				<td class="p-3.5 whitespace-nowrap">
					<span class="px-2 py-0.5 rounded-lg text-[10px] font-semibold {user.plan === 'PRO'
						? 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20'
						: user.role === 'superadmin'
							? 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/20'
							: 'bg-slate-100 dark:bg-white/5 text-slate-600 dark:text-slate-300'}">
						{user.roleLabel}
					</span>
				</td>

				<!-- Telegram -->
				<td class="p-3.5 whitespace-nowrap">
					{#if user.isTelegramLinked}
						<span class="inline-flex items-center gap-1 text-[11px] font-mono text-[#0088cc]">
							<Bot class="w-3.5 h-3.5" />
							<span>{user.telegramUsername}</span>
						</span>
					{:else}
						<span class="text-[10px] text-slate-400 italic">Belum terhubung</span>
					{/if}
				</td>

				<!-- Tx Count -->
				<td class="p-3.5 whitespace-nowrap">
					<span class="inline-flex items-center gap-1 text-slate-700 dark:text-slate-300 font-medium">
						<Receipt class="w-3.5 h-3.5 text-slate-400" />
						<span>{user.txCount} entri</span>
					</span>
				</td>

				<!-- Last Active -->
				<td class="p-3.5 text-slate-500 dark:text-slate-400 whitespace-nowrap">
					<div>{user.lastActive}</div>
					<div class="text-[10px] text-slate-400">Gabung: {user.createdAt}</div>
				</td>

				<!-- Status -->
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

				<!-- Actions -->
				<td class="p-3.5 text-right whitespace-nowrap">
					<div class="flex items-center justify-end gap-1">
						<button
							type="button"
							onclick={() => openEditRole(user)}
							title="Ubah Paket / Role"
							class="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-white/10 text-slate-500 hover:text-[#007AFF] transition-colors cursor-pointer"
						>
							<Edit3 class="w-3.5 h-3.5" />
						</button>

						{#if user.role !== 'superadmin'}
							<button
								type="button"
								onclick={() => toggleSuspendUser(user)}
								title={user.status === 'ACTIVE' ? 'Tangguhkan Akun' : 'Aktifkan Akun'}
								class="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-white/10 text-slate-500 hover:text-rose-500 transition-colors cursor-pointer"
							>
								{#if user.status === 'ACTIVE'}
									<UserX class="w-3.5 h-3.5" />
								{:else}
									<UserCheck class="w-3.5 h-3.5 text-emerald-500" />
								{/if}
							</button>
						{/if}
					</div>
				</td>
			</tr>
		{/snippet}
	</Table>

	<!-- Modal Tambah Pengguna Baru -->
	<Modal
		bind:open={isAddUserModalOpen}
		title="Daftarkan Pengguna Baru"
		description="Tambahkan pengguna baru ke platform PantauDuit"
	>
		<div class="space-y-3.5 text-xs">
			<Input
				bind:value={newUserName}
				label="Nama Lengkap Pengguna"
				placeholder="Contoh: Budi Santoso"
			/>

			<Input
				bind:value={newUserEmail}
				type="email"
				label="Alamat Email Pengguna"
				placeholder="Contoh: budi@gmail.com"
			/>

			<Input
				bind:value={newUserTelegram}
				label="Username Telegram (Opsional)"
				placeholder="Contoh: @budi_pd"
			/>

			<div>
				<span class="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 block">
					Paket Langganan
				</span>
				<select
					bind:value={newUserPlan}
					class="w-full h-9 px-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-[#007AFF]"
				>
					<option value="free">Free Tier (Gratis - Standar)</option>
					<option value="pro">Pro Tier (Langganan Berbayar)</option>
				</select>
			</div>

			{#if formError}
				<p class="text-xs text-rose-500 bg-rose-50 dark:bg-rose-950/30 p-2.5 rounded-xl border border-rose-200">
					{formError}
				</p>
			{/if}
		</div>

		{#snippet footer()}
			<Button variant="ghost" onclick={() => (isAddUserModalOpen = false)}>Batal</Button>
			<Button variant="primary" onclick={handleAddUser}>Daftarkan Pengguna</Button>
		{/snippet}
	</Modal>

	<!-- Modal Ubah Paket & Status Pengguna -->
	{#if selectedUserForEdit}
		<Modal
			open={isEditRoleModalOpen}
			title="Ubah Paket & Status Pengguna"
			description="Atur paket layanan dan izin akses untuk {selectedUserForEdit.name}"
			onclose={() => {
				isEditRoleModalOpen = false;
				selectedUserForEdit = null;
			}}
		>
			<div class="space-y-4 text-xs">
				<div class="p-3 rounded-xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200/70 dark:border-white/10 space-y-1">
					<p class="font-semibold text-slate-900 dark:text-white">{selectedUserForEdit.name}</p>
					<p class="text-slate-400 font-mono text-[11px]">{selectedUserForEdit.email}</p>
				</div>

				<div>
					<span class="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 block">
						Paket Layanan
					</span>
					<select
						bind:value={selectedUserForEdit.plan}
						class="w-full h-9 px-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-[#007AFF]"
					>
						<option value="FREE">Free User (Batas Standar)</option>
						<option value="PRO">Pro Subscriber (Akses Penuh)</option>
					</select>
				</div>

				<div>
					<span class="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 block">
						Status Akun
					</span>
					<select
						bind:value={selectedUserForEdit.status}
						class="w-full h-9 px-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-[#007AFF]"
					>
						<option value="ACTIVE">Aktif (Bisa Login & Catat)</option>
						<option value="SUSPENDED">Ditangguhkan (Diblokir Sementara)</option>
					</select>
				</div>
			</div>

			{#snippet footer()}
				<Button
					variant="ghost"
					onclick={() => {
						isEditRoleModalOpen = false;
						selectedUserForEdit = null;
					}}
				>
					Batal
				</Button>
				<Button variant="primary" onclick={handleSaveUserRole}>Simpan Perubahan</Button>
			{/snippet}
		</Modal>
	{/if}
</div>
