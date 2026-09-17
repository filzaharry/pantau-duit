<script lang="ts">
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Table, { type TableColumn } from '$lib/components/ui/Table.svelte';
	import {
		Menu,
		FolderTree,
		Search,
		Plus,
		Check,
		X,
		Edit3,
		Eye,
		EyeOff,
		Layers,
		ArrowUpDown,
		Shield,
		Users,
		Settings,
		RotateCcw,
		CheckCircle2
	} from 'lucide-svelte';

	let searchQuery = $state('');
	let selectedCategory = $state<string>('ALL');

	// Modal State
	let isAddMenuModalOpen = $state(false);
	let newMenuName = $state('');
	let newMenuHref = $state('');
	let newMenuCategory = $state('FINANSIAL');
	let newMenuOrder = $state(1);

	// Mock Menus List (Personal Finance & Platform Administration)
	const menuItems = $state([
		{
			id: 'menu-01',
			name: 'Ringkasan Finansial',
			href: '/dashboard',
			category: 'FINANSIAL PRIBADI',
			order: 1,
			roles: ['pro', 'free'],
			isActive: true,
			description: 'Overview saldo, pemasukan, pengeluaran, dan tren kas pribadi'
		},
		{
			id: 'menu-02',
			name: 'Riwayat Transaksi',
			href: '/transactions',
			category: 'FINANSIAL PRIBADI',
			order: 2,
			roles: ['superadmin', 'pro', 'free'],
			isActive: true,
			description: 'Catatan seluruh transaksi, mutasi, dan pencatatan belanja'
		},
		{
			id: 'menu-03',
			name: 'Dompet & Rekening',
			href: '/accounts',
			category: 'FINANSIAL PRIBADI',
			order: 3,
			roles: ['superadmin', 'pro', 'free'],
			isActive: true,
			description: 'Pengelolaan saldo rekening bank, dompet digital, dan kas fisik'
		},
		{
			id: 'menu-04',
			name: 'Batas Belanja (Budgets)',
			href: '/budgets',
			category: 'FINANSIAL PRIBADI',
			order: 4,
			roles: ['superadmin', 'pro', 'free'],
			isActive: true,
			description: 'Anggaran belanja bulanan per kategori dan kontrol boros'
		},
		{
			id: 'menu-05',
			name: 'Target Tabungan (Goals)',
			href: '/goals',
			category: 'FINANSIAL PRIBADI',
			order: 5,
			roles: ['superadmin', 'pro', 'free'],
			isActive: true,
			description: 'Target pencapaian dana impian dan tabungan masa depan'
		},
		{
			id: 'menu-06',
			name: 'Portofolio Investasi',
			href: '/investments',
			category: 'FINANSIAL PRIBADI',
			order: 6,
			roles: ['superadmin', 'pro'],
			isActive: true,
			description: 'Pencatatan aset saham, crypto, emas, dan reksa dana'
		},
		{
			id: 'menu-07',
			name: 'Ringkasan Platform',
			href: '/dashboard',
			category: 'TATA KELOLA PLATFORM',
			order: 1,
			roles: ['superadmin'],
			isActive: true,
			description: 'Pusat kontrol operasional platform PantauDuit'
		},
		{
			id: 'menu-08',
			name: 'Manajemen Pengguna (Users)',
			href: '/users',
			category: 'TATA KELOLA PLATFORM',
			order: 2,
			roles: ['superadmin'],
			isActive: true,
			description: 'Direktori akun, paket langganan, dan status pengguna'
		},
		{
			id: 'menu-09',
			name: 'Hak Akses & Role (RBAC)',
			href: '/roles',
			category: 'TATA KELOLA PLATFORM',
			order: 3,
			roles: ['superadmin'],
			isActive: true,
			description: 'Matriks izin otorisasi fitur Superadmin, Pro, dan Free'
		},
		{
			id: 'menu-10',
			name: 'Navigasi Menu',
			href: '/menus',
			category: 'TATA KELOLA PLATFORM',
			order: 4,
			roles: ['superadmin'],
			isActive: true,
			description: 'Pengaturan struktur navigasi dan visibilitas peran'
		},
		{
			id: 'menu-11',
			name: 'Parameter Sistem',
			href: '/parameters',
			category: 'TATA KELOLA PLATFORM',
			order: 5,
			roles: ['superadmin'],
			isActive: true,
			description: 'Batas kuota gratis, webhook bot, dan maintenance mode'
		},
		{
			id: 'menu-12',
			name: 'Bot Telegram & Webhook',
			href: '/telegram',
			category: 'BOT & SISTEM',
			order: 1,
			roles: ['superadmin', 'pro', 'free'],
			isActive: true,
			description: 'Status koneksi @PantauDuitBot dan asisten pencatat chat'
		},
		{
			id: 'menu-13',
			name: 'Audit Keamanan',
			href: '/audit-logs',
			category: 'BOT & SISTEM',
			order: 2,
			roles: ['superadmin'],
			isActive: true,
			description: 'Jejak log aktivitas keamanan dan event login'
		},
		{
			id: 'menu-14',
			name: 'Pengaturan Akun',
			href: '/settings',
			category: 'BOT & SISTEM',
			order: 3,
			roles: ['superadmin', 'pro', 'free'],
			isActive: true,
			description: 'Profil akun, preferensi mata uang, dan tema'
		}
	]);

	const availableRoles = [
		{ id: 'superadmin', label: 'Superadmin' },
		{ id: 'pro', label: 'Pro Subscriber' },
		{ id: 'free', label: 'Free User' }
	];

	const columns: TableColumn[] = [
		{ header: 'Urutan', key: 'order', width: '80px' },
		{ header: 'Nama Menu & Rute Path', key: 'name', width: '220px' },
		{ header: 'Kategori Navigasi', key: 'category', width: '170px' },
		{ header: 'Superadmin', align: 'center', width: '120px', sortable: false },
		{ header: 'Pro Subscriber', align: 'center', width: '120px', sortable: false },
		{ header: 'Free User', align: 'center', width: '120px', sortable: false },
		{ header: 'Status', key: 'isActive', align: 'center', width: '110px' },
		{ header: 'Aksi', align: 'right', width: '80px', sortable: false }
	];

	const filteredMenus = $derived(
		menuItems.filter((m) => {
			if (selectedCategory !== 'ALL' && m.category !== selectedCategory) return false;
			if (searchQuery.trim()) {
				const q = searchQuery.toLowerCase();
				const matchName = m.name.toLowerCase().includes(q);
				const matchHref = m.href.toLowerCase().includes(q);
				const matchCat = m.category.toLowerCase().includes(q);
				if (!matchName && !matchHref && !matchCat) return false;
			}
			return true;
		})
	);

	function toggleRoleVisibility(menu: any, roleId: string) {
		const index = menu.roles.indexOf(roleId);
		if (index > -1) {
			menu.roles.splice(index, 1);
			notificationStore.toast(`Visibilitas ${roleId} untuk menu "${menu.name}" dinonaktifkan.`, 'info');
		} else {
			menu.roles.push(roleId);
			notificationStore.toast(`Visibilitas ${roleId} untuk menu "${menu.name}" diaktifkan.`, 'success');
		}
	}

	function toggleActive(menu: any) {
		menu.isActive = !menu.isActive;
		notificationStore.toast(`Menu "${menu.name}" sekarang ${menu.isActive ? 'Aktif' : 'Disembunyikan'}.`, 'info');
	}

	function handleAddMenu() {
		if (!newMenuName.trim() || !newMenuHref.trim()) {
			notificationStore.toast('Nama menu dan path href wajib diisi.', 'error');
			return;
		}

		menuItems.push({
			id: `menu-${Date.now()}`,
			name: newMenuName.trim(),
			href: newMenuHref.trim(),
			category: newMenuCategory,
			order: newMenuOrder,
			roles: ['superadmin'],
			isActive: true,
			description: 'Menu kustom baru'
		});

		notificationStore.toast(`Menu "${newMenuName}" berhasil ditambahkan!`, 'success');
		isAddMenuModalOpen = false;
		newMenuName = '';
		newMenuHref = '';
	}
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full pb-24 lg:pb-10">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
		<div>
			<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
				<FolderTree class="w-6 h-6 text-[#007AFF] dark:text-[#0A84FF]" />
				<span>Manajemen Menu Navigasi</span>
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
				Konfigurasi struktur navigasi sidebar, pengelompokan menu, dan penentuan visibilitas peran (Role Visibility Matrix)
			</p>
		</div>

		<div class="flex items-center gap-2 self-start sm:self-auto">
			<Button variant="primary" onclick={() => (isAddMenuModalOpen = true)} class="h-9 px-4">
				<Plus class="w-4 h-4" />
				<span>Tambah Menu Baru</span>
			</Button>
		</div>
	</div>

	<!-- Top Metric Ribbon Strip (4 Columns) -->
	<div class="p-3 sm:p-5 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
		<div class="grid grid-cols-2 lg:grid-cols-4 gap-2.5 sm:gap-4 lg:divide-x divide-slate-100 dark:divide-white/5">
			<!-- Col 1: Total Menus -->
			<div class="flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-[#007AFF]/10 text-[#007AFF] dark:text-[#0A84FF] flex items-center justify-center shrink-0">
					<Menu class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Total Menu Terdaftar</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">{menuItems.length} Navigasi</span>
					<span class="text-[10px] sm:text-[11px] text-emerald-500 font-medium truncate block">100% Terindeks Rute</span>
				</div>
			</div>

			<!-- Col 2: Categories -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400 flex items-center justify-center shrink-0">
					<Layers class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Grup Kategori</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">4 Kelompok Utama</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">Finansial &bull; SaaS &bull; RBAC</span>
				</div>
			</div>

			<!-- Col 3: Superadmin Specific -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-blue-500/10 text-blue-500 flex items-center justify-center shrink-0">
					<Shield class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Menu Superadmin</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">10 Modul Khusus</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">Isolasi Hak Akses</span>
				</div>
			</div>

			<!-- Col 4: Subscriber Menus -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
					<Users class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Menu Pengguna</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">6 Modul Finansial</span>
					<span class="text-[10px] sm:text-[11px] text-emerald-500 font-medium truncate block">Mudah Digunakan</span>
				</div>
			</div>
		</div>
	</div>

	<!-- Toolbar & Category Tabs -->
	<div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5">
		<div class="relative flex-1">
			<Search class="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="Cari menu berdasarkan nama, path, atau kategori..."
				class="w-full h-9 pl-9 pr-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-[#007AFF] transition-colors"
			/>
		</div>

		<div class="flex items-center gap-2">
			<select
				bind:value={selectedCategory}
				class="h-9 px-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-700 dark:text-slate-300 focus:outline-none focus:border-[#007AFF]"
			>
				<option value="ALL">Semua Kategori</option>
				<option value="FINANSIAL PRIBADI">FINANSIAL PRIBADI</option>
				<option value="TATA KELOLA PLATFORM">TATA KELOLA PLATFORM</option>
				<option value="BOT & SISTEM">BOT & SISTEM</option>
			</select>

			{#if searchQuery || selectedCategory !== 'ALL'}
				<Button variant="ghost" onclick={() => { searchQuery = ''; selectedCategory = 'ALL'; }} class="h-9 px-3 text-xs text-slate-500">
					<RotateCcw class="w-3.5 h-3.5 mr-1" />
					<span>Reset</span>
				</Button>
			{/if}
		</div>
	</div>

	<!-- Menu & Role Visibility Table using global reusable Table component -->
	<Table
		title="Matriks Visibilitas Menu per Peran"
		subtitle="Pengaturan struktur navigasi sidebar dan otorisasi visibilitas peran pengguna"
		icon={FolderTree}
		badge="{filteredMenus.length} Menu"
		{columns}
		items={filteredMenus}
		emptyMessage="Tidak ada menu yang cocok"
		emptyDescription="Coba ubah kata kunci pencarian atau ganti filter kategori navigasi."
	>
		{#snippet row(menu, index)}
			<tr class="hover:bg-slate-50/60 dark:hover:bg-white/[0.02] transition-colors {menu.isActive ? '' : 'opacity-50'}">
				<!-- Order -->
				<td class="p-3.5 text-slate-400 font-mono">
					#{menu.order}
				</td>

				<!-- Menu Name & Path -->
				<td class="p-3.5 whitespace-nowrap">
					<p class="font-semibold text-slate-900 dark:text-white">{menu.name}</p>
					<span class="text-[10px] text-[#007AFF] dark:text-[#0A84FF] font-mono">{menu.href}</span>
				</td>

				<!-- Category -->
				<td class="p-3.5 whitespace-nowrap">
					<span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-100 dark:bg-white/5 text-slate-600 dark:text-slate-300">
						{menu.category}
					</span>
				</td>

				<!-- Role Visibility Checkboxes -->
				{#each availableRoles as role}
					{@const isVisible = menu.roles.includes(role.id)}
					<td class="p-3.5 text-center">
						<button
							type="button"
							onclick={() => toggleRoleVisibility(menu, role.id)}
							class="w-6 h-6 rounded-lg flex items-center justify-center mx-auto transition-all cursor-pointer {isVisible
								? 'bg-[#007AFF] text-white'
								: 'bg-slate-100 dark:bg-white/5 text-transparent border border-slate-200/80 dark:border-white/10 hover:border-slate-300'}"
						>
							<Check class="w-3.5 h-3.5 stroke-[2.5]" />
						</button>
					</td>
				{/each}

				<!-- Status Active -->
				<td class="p-3.5 text-center whitespace-nowrap">
					<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold {menu.isActive
						? 'bg-emerald-500/10 text-emerald-600 border border-emerald-500/20'
						: 'bg-slate-500/10 text-slate-400 border border-slate-500/20'}">
						{menu.isActive ? 'Tampil' : 'Disembunyikan'}
					</span>
				</td>

				<!-- Actions -->
				<td class="p-3.5 text-right whitespace-nowrap">
					<button
						type="button"
						onclick={() => toggleActive(menu)}
						class="p-1.5 rounded-lg bg-slate-100 dark:bg-white/5 hover:bg-[#007AFF] hover:text-white text-slate-600 dark:text-slate-300 transition-all cursor-pointer"
						title={menu.isActive ? 'Sembunyikan Menu' : 'Tampilkan Menu'}
					>
						{#if menu.isActive}
							<Eye class="w-3.5 h-3.5" />
						{:else}
							<EyeOff class="w-3.5 h-3.5" />
						{/if}
					</button>
				</td>
			</tr>
		{/snippet}
	</Table>
</div>

<!-- Modal Tambah Menu Baru -->
<Modal
	bind:open={isAddMenuModalOpen}
	title="Tambah Menu Navigasi Baru"
	description="Daftarkan menu baru ke sistem navigasi aplikasi"
>
	<div class="space-y-4 text-xs">
		<Input
			bind:value={newMenuName}
			label="Nama Label Menu"
			placeholder="Contoh: Pusat Bantuan, Integrasi API"
		/>

		<Input
			bind:value={newMenuHref}
			label="Path Rute (Href)"
			placeholder="Contoh: /help atau /integrations"
		/>

		<div class="grid grid-cols-2 gap-3">
			<div>
				<label for="new-menu-category" class="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 block">
					Kelompok Kategori
				</label>
				<select
					id="new-menu-category"
					bind:value={newMenuCategory}
					class="w-full h-9 px-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-[#151926] text-xs font-medium text-slate-700 dark:text-slate-200 focus:outline-none focus:border-[#007AFF]"
				>
					<option value="FINANSIAL">FINANSIAL</option>
					<option value="PLATFORM & SAAS">PLATFORM & SAAS</option>
					<option value="USER MANAGEMENT & RBAC">USER MANAGEMENT & RBAC</option>
					<option value="INFRASTRUKTUR & KEAMANAN">INFRASTRUKTUR & KEAMANAN</option>
				</select>
			</div>

			<div>
				<label for="new-menu-order" class="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 block">
					Urutan Tampil (Index)
				</label>
				<input
					id="new-menu-order"
					type="number"
					bind:value={newMenuOrder}
					min="1"
					class="w-full h-9 px-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-[#151926] text-xs font-medium text-slate-700 dark:text-slate-200 focus:outline-none focus:border-[#007AFF]"
				/>
			</div>
		</div>

		<div class="flex justify-end gap-2 pt-2 border-t border-slate-100 dark:border-white/5">
			<Button variant="ghost" onclick={() => (isAddMenuModalOpen = false)}>
				Batal
			</Button>
			<Button variant="primary" onclick={handleAddMenu}>
				Simpan Menu
			</Button>
		</div>
	</div>
</Modal>
