<script lang="ts">
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Table, { type TableColumn } from '$lib/components/ui/Table.svelte';
	import {
		Sliders,
		SlidersHorizontal,
		Shield,
		Lock,
		Bot,
		CreditCard,
		Database,
		Save,
		RotateCcw,
		CheckCircle2,
		AlertTriangle,
		Server,
		Clock,
		Coins,
		Zap,
		Search,
		Edit3,
		Check,
		Filter
	} from 'lucide-svelte';

	interface ParameterItem {
		id: string;
		key: string;
		name: string;
		description: string;
		category: 'TIER' | 'BOT' | 'FINANSIAL' | 'KEAMANAN';
		categoryLabel: string;
		value: number | string | boolean;
		defaultValue: number | string | boolean;
		unit?: string;
		type: 'number' | 'string' | 'boolean' | 'select';
		options?: { label: string; value: string }[];
		min?: number;
		max?: number;
		step?: number;
		updatedAt: string;
	}

	// 17 Global SaaS Parameters
	const parameters = $state<ParameterItem[]>([
		// Kuota & Batas Tier SaaS
		{
			id: 'param-01',
			key: 'TRIAL_DAYS',
			name: 'Masa Percobaan Pengguna Baru',
			description: 'Durasi akses uji coba gratis fitur Pro saat pengguna baru pertama kali mendaftar',
			category: 'TIER',
			categoryLabel: 'Kuota & Tier SaaS',
			value: 14,
			defaultValue: 14,
			unit: 'Hari',
			type: 'number',
			min: 1,
			max: 90,
			updatedAt: 'Hari ini, 22:45'
		},
		{
			id: 'param-02',
			key: 'FREE_MAX_ACCOUNTS',
			name: 'Batas Maksimal Rekening Dompet (Free)',
			description: 'Jumlah maksimal akun bank/e-wallet/kas yang dapat dibuat akun Free tier',
			category: 'TIER',
			categoryLabel: 'Kuota & Tier SaaS',
			value: 3,
			defaultValue: 3,
			unit: 'Rekening',
			type: 'number',
			min: 1,
			max: 20,
			updatedAt: 'Hari ini, 22:45'
		},
		{
			id: 'param-03',
			key: 'FREE_MAX_BUDGETS',
			name: 'Batas Maksimal Pos Anggaran (Free)',
			description: 'Jumlah alokasi pos budget belanja bulanan maksimal untuk tier Free',
			category: 'TIER',
			categoryLabel: 'Kuota & Tier SaaS',
			value: 5,
			defaultValue: 5,
			unit: 'Pos Budget',
			type: 'number',
			min: 1,
			max: 50,
			updatedAt: 'Hari ini, 22:45'
		},
		{
			id: 'param-04',
			key: 'FREE_MONTHLY_TX_LIMIT',
			name: 'Batas Transaksi Bulanan Free Tier',
			description: 'Kuota transaksi masuk dan keluar yang dapat dicatat per bulan pada paket Free',
			category: 'TIER',
			categoryLabel: 'Kuota & Tier SaaS',
			value: 100,
			defaultValue: 100,
			unit: 'Tx / Bulan',
			type: 'number',
			min: 10,
			max: 1000,
			updatedAt: 'Hari ini, 22:45'
		},
		{
			id: 'param-05',
			key: 'PRO_MONTHLY_PRICE',
			name: 'Biaya Langganan Pro Bulanan',
			description: 'Tarif berlangganan fitur tanpa batas PantauDuit Pro per bulan (dalam Rupiah)',
			category: 'TIER',
			categoryLabel: 'Kuota & Tier SaaS',
			value: 29000,
			defaultValue: 29000,
			unit: 'Rp / Bulan',
			type: 'number',
			min: 10000,
			step: 1000,
			updatedAt: 'Hari ini, 22:45'
		},

		// Mesin Bot Telegram & Webhook
		{
			id: 'param-06',
			key: 'TELEGRAM_RATE_LIMIT',
			name: 'Rate Limiter Webhook Telegram',
			description: 'Ambang batas maksimal request pesan per menit untuk proteksi bot anti-spam',
			category: 'BOT',
			categoryLabel: 'Bot Telegram',
			value: 60,
			defaultValue: 60,
			unit: 'Pesan / Mnt',
			type: 'number',
			min: 10,
			max: 300,
			updatedAt: 'Hari ini, 22:45'
		},
		{
			id: 'param-07',
			key: 'TELEGRAM_TIMEOUT_SECONDS',
			name: 'Timeout Konfirmasi Chatbot',
			description: 'Batas waktu kedaluwarsa balasan dialog interaktif sesi chat Telegram',
			category: 'BOT',
			categoryLabel: 'Bot Telegram',
			value: 30,
			defaultValue: 30,
			unit: 'Detik',
			type: 'number',
			min: 5,
			max: 120,
			updatedAt: 'Hari ini, 22:45'
		},
		{
			id: 'param-08',
			key: 'NLP_CONFIDENCE_THRESHOLD',
			name: 'Tingkat Kepercayaan Parser NLP AI',
			description: 'Minimal skor akurasi pemahaman parsing transaksi chat sebelum meminta konfirmasi ulang',
			category: 'BOT',
			categoryLabel: 'Bot Telegram',
			value: 85,
			defaultValue: 85,
			unit: '% Akurasi',
			type: 'number',
			min: 50,
			max: 99,
			updatedAt: 'Hari ini, 22:45'
		},
		{
			id: 'param-09',
			key: 'MAX_WEBHOOK_RETRIES',
			name: 'Maksimal Percobaan Ulang Worker Celery',
			description: 'Frekuensi retry worker saat webhook Telegram mengalami gangguan jaringan sementara',
			category: 'BOT',
			categoryLabel: 'Bot Telegram',
			value: 3,
			defaultValue: 3,
			unit: 'Percobaan',
			type: 'number',
			min: 1,
			max: 10,
			updatedAt: 'Hari ini, 22:45'
		},

		// Keuangan & Konfigurasi
		{
			id: 'param-10',
			key: 'DEFAULT_CURRENCY',
			name: 'Mata Uang Acuan Utama Sistem',
			description: 'Simbol dan kode valuta acuan standar untuk agregasi ringkasan dashboard finansial',
			category: 'FINANSIAL',
			categoryLabel: 'Keuangan & Format',
			value: 'IDR',
			defaultValue: 'IDR',
			unit: 'Valuta',
			type: 'select',
			options: [
				{ label: 'IDR - Rupiah Indonesia (Rp)', value: 'IDR' },
				{ label: 'USD - Dolar Amerika Serikat ($)', value: 'USD' },
				{ label: 'SGD - Dolar Singapura (S$)', value: 'SGD' }
			],
			updatedAt: 'Hari ini, 22:45'
		},
		{
			id: 'param-11',
			key: 'MIN_INVESTMENT_AMOUNT',
			name: 'Minimal Nominal Transaksi Investasi',
			description: 'Batas bawah validasi angka saat mencatat transaksi instrumen investasi',
			category: 'FINANSIAL',
			categoryLabel: 'Keuangan & Format',
			value: 10000,
			defaultValue: 10000,
			unit: 'Rupiah',
			type: 'number',
			min: 1000,
			step: 1000,
			updatedAt: 'Hari ini, 22:45'
		},
		{
			id: 'param-12',
			key: 'DAILY_REMINDER_TIME',
			name: 'Waktu Pengingat Rekap Malam Bot',
			description: 'Jadwal cron pesan bot Telegram mengingatkan pencatatan pengeluaran harian',
			category: 'FINANSIAL',
			categoryLabel: 'Keuangan & Format',
			value: '20:00',
			defaultValue: '20:00',
			unit: 'WIB',
			type: 'string',
			updatedAt: 'Hari ini, 22:45'
		},
		{
			id: 'param-13',
			key: 'AUTO_ROUND_DECIMAL',
			name: 'Bulatkan Format Angka (Tanpa Sen)',
			description: 'Menyembunyikan angka desimal .00 di belakang nominal uang untuk keterbacaan bersih',
			category: 'FINANSIAL',
			categoryLabel: 'Keuangan & Format',
			value: true,
			defaultValue: true,
			unit: 'Format Bulat',
			type: 'boolean',
			updatedAt: 'Hari ini, 22:45'
		},

		// Keamanan & Operasional Server
		{
			id: 'param-14',
			key: 'MAINTENANCE_MODE',
			name: 'Mode Pemeliharaan (Maintenance Mode)',
			description: 'Jika aktif, hanya Superadmin yang dapat masuk; pengguna dialihkan ke maintenance screen',
			category: 'KEAMANAN',
			categoryLabel: 'Keamanan & Server',
			value: false,
			defaultValue: false,
			unit: 'Status Sistem',
			type: 'boolean',
			updatedAt: 'Hari ini, 22:45'
		},
		{
			id: 'param-15',
			key: 'JWT_TOKEN_EXPIRY_DAYS',
			name: 'Masa Berlaku Token Sesi JWT',
			description: 'Durasi aktif token login sebelum pengguna diwajibkan masuk ulang',
			category: 'KEAMANAN',
			categoryLabel: 'Keamanan & Server',
			value: 7,
			defaultValue: 7,
			unit: 'Hari',
			type: 'number',
			min: 1,
			max: 30,
			updatedAt: 'Hari ini, 22:45'
		},
		{
			id: 'param-16',
			key: 'MAX_OTP_ATTEMPTS',
			name: 'Batas Maksimal Percobaan OTP',
			description: 'Jumlah toleransi kesalahan input kode verifikasi sebelum akun ditangguhkan sementara',
			category: 'KEAMANAN',
			categoryLabel: 'Keamanan & Server',
			value: 5,
			defaultValue: 5,
			unit: 'Kali Percobaan',
			type: 'number',
			min: 3,
			max: 10,
			updatedAt: 'Hari ini, 22:45'
		},
		{
			id: 'param-17',
			key: 'IP_BAN_DURATION_MINUTES',
			name: 'Durasi Blokir IP Terdeteksi Anomali',
			description: 'Masa penahanan IP address yang terdeteksi melakukan spam atau brute force',
			category: 'KEAMANAN',
			categoryLabel: 'Keamanan & Server',
			value: 15,
			defaultValue: 15,
			unit: 'Menit',
			type: 'number',
			min: 5,
			max: 120,
			updatedAt: 'Hari ini, 22:45'
		}
	]);

	// Filter & Search
	let searchQuery = $state('');
	let selectedCategory = $state<string>('ALL');

	const filteredParameters = $derived(
		parameters.filter((p) => {
			const query = searchQuery.toLowerCase().trim();
			const matchQuery =
				!query ||
				p.key.toLowerCase().includes(query) ||
				p.name.toLowerCase().includes(query) ||
				p.description.toLowerCase().includes(query);

			const matchCategory = selectedCategory === 'ALL' || p.category === selectedCategory;
			return matchQuery && matchCategory;
		})
	);

	// Table Columns
	const columns: TableColumn<ParameterItem>[] = [
		{ header: 'Parameter & Kode Kunci', key: 'name', width: '280px' },
		{ header: 'Kategori', key: 'categoryLabel', width: '160px' },
		{ header: 'Deskripsi Konfigurasi', key: 'description' },
		{ header: 'Nilai Saat Ini', key: 'value', width: '200px' },
		{ header: 'Status Cache', key: 'updatedAt', align: 'center', width: '120px' },
		{ header: 'Aksi', align: 'right', width: '100px', sortable: false }
	];

	// Edit Modal State
	let isEditModalOpen = $state(false);
	let editingParam = $state<ParameterItem | null>(null);
	let editValueNumber = $state<number>(0);
	let editValueString = $state<string>('');
	let editValueBoolean = $state<boolean>(false);

	function openEditModal(param: ParameterItem) {
		editingParam = param;
		if (param.type === 'number') {
			editValueNumber = Number(param.value);
		} else if (param.type === 'boolean') {
			editValueBoolean = Boolean(param.value);
		} else {
			editValueString = String(param.value);
		}
		isEditModalOpen = true;
	}

	function saveParameterEdit() {
		if (!editingParam) return;

		if (editingParam.type === 'number') {
			editingParam.value = editValueNumber;
		} else if (editingParam.type === 'boolean') {
			editingParam.value = editValueBoolean;
		} else {
			editingParam.value = editValueString;
		}

		editingParam.updatedAt = 'Baru saja';
		isEditModalOpen = false;
		notificationStore.toast(`Parameter "${editingParam.name}" berhasil diperbarui!`, 'success');
	}

	function toggleBooleanInline(param: ParameterItem) {
		if (param.type !== 'boolean') return;
		param.value = !param.value;
		param.updatedAt = 'Baru saja';
		notificationStore.toast(`Parameter "${param.name}" diubah ke ${param.value ? 'AKTIF' : 'NONAKTIF'}.`, 'info');
	}

	// Saving States
	let isSaving = $state(false);

	function saveAllParameters() {
		isSaving = true;
		setTimeout(() => {
			isSaving = false;
			notificationStore.toast('Seluruh parameter sistem global berhasil disinkronkan ke Redis Cache TTL!', 'success');
		}, 500);
	}

	function resetToDefaults() {
		for (const p of parameters) {
			p.value = p.defaultValue;
			p.updatedAt = 'Baru saja';
		}
		notificationStore.toast('Seluruh parameter telah dikembalikan ke nilai default standar.', 'info');
	}

	// Helper for format display
	function formatValueDisplay(param: ParameterItem): string {
		if (param.type === 'boolean') {
			return param.value ? 'AKTIF (TRUE)' : 'NONAKTIF (FALSE)';
		}
		if (param.key === 'PRO_MONTHLY_PRICE') {
			return `Rp ${Number(param.value).toLocaleString('id-ID')} / Bln`;
		}
		if (param.unit) {
			return `${param.value} ${param.unit}`;
		}
		return String(param.value);
	}

	const isMaintenanceActive = $derived(
		Boolean(parameters.find((p) => p.key === 'MAINTENANCE_MODE')?.value)
	);
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full pb-24 lg:pb-10">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
		<div>
			<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
				<SlidersHorizontal class="w-6 h-6 text-[#007AFF] dark:text-[#0A84FF]" />
				<span>Parameter Sistem (General Parameters)</span>
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
				Konfigurasi nilai parameter global SaaS PantauDuit, batas kuota tier pelanggan, toleransi NLP bot, dan kontrol keamanan
			</p>
		</div>

		<div class="flex items-center gap-2 self-start sm:self-auto">
			<Button variant="outline" onclick={resetToDefaults} class="h-9 px-3.5 text-xs">
				<RotateCcw class="w-3.5 h-3.5" />
				<span>Reset Default</span>
			</Button>

			<Button variant="primary" onclick={saveAllParameters} disabled={isSaving} class="h-9 px-4 text-xs">
				<Save class="w-3.5 h-3.5" />
				<span>{isSaving ? 'Menyimpan...' : 'Simpan Semua'}</span>
			</Button>
		</div>
	</div>

	<!-- Top Metric Ribbon Strip (4 Columns) -->
	<div class="p-3 sm:p-5 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
		<div class="grid grid-cols-2 lg:grid-cols-4 gap-2.5 sm:gap-4 lg:divide-x divide-slate-100 dark:divide-white/5">
			<!-- Col 1: Total Parameters -->
			<div class="flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-[#007AFF]/10 text-[#007AFF] dark:text-[#0A84FF] flex items-center justify-center shrink-0">
					<Sliders class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Parameter Global</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">{parameters.length} Parameter Aktif</span>
					<span class="text-[10px] sm:text-[11px] text-emerald-500 font-medium truncate block">Cached in Redis TTL</span>
				</div>
			</div>

			<!-- Col 2: Maintenance Status -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
					<Server class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Status Pemeliharaan</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">{isMaintenanceActive ? 'MAINTENANCE ON' : 'Operasional Normal'}</span>
					<span class="text-[10px] sm:text-[11px] {isMaintenanceActive ? 'text-amber-500' : 'text-emerald-500'} font-medium truncate block">
						{isMaintenanceActive ? 'Akses dibatasi' : 'Semua layanan live'}
					</span>
				</div>
			</div>

			<!-- Col 3: Encryption -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400 flex items-center justify-center shrink-0">
					<Lock class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Enkripsi Penyimpanan</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">AES-256 GCM</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">Secrets & Token Terisolasi</span>
				</div>
			</div>

			<!-- Col 4: Sync Time -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-blue-500/10 text-blue-500 flex items-center justify-center shrink-0">
					<Clock class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Sinkronisasi Terakhir</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">Hari ini, 22:45 WIB</span>
					<span class="text-[10px] sm:text-[11px] text-emerald-500 font-medium truncate block">Zero Latency Drift</span>
				</div>
			</div>
		</div>
	</div>

	<!-- Toolbar: Search & Category Filter -->
	<div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5">
		<div class="relative flex-1">
			<Search class="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="Cari berdasarkan kode parameter, nama, atau fungsi..."
				class="w-full h-9 pl-9 pr-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-[#007AFF] transition-colors"
			/>
		</div>

		<div class="flex items-center gap-2">
			<select
				bind:value={selectedCategory}
				class="h-9 px-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-700 dark:text-slate-300 focus:outline-none focus:border-[#007AFF]"
			>
				<option value="ALL">Semua Kategori ({parameters.length})</option>
				<option value="TIER">Kuota & Tier SaaS ({parameters.filter(p => p.category === 'TIER').length})</option>
				<option value="BOT">Mesin Bot Telegram ({parameters.filter(p => p.category === 'BOT').length})</option>
				<option value="FINANSIAL">Keuangan & Konfigurasi ({parameters.filter(p => p.category === 'FINANSIAL').length})</option>
				<option value="KEAMANAN">Keamanan & Server ({parameters.filter(p => p.category === 'KEAMANAN').length})</option>
			</select>

			{#if searchQuery || selectedCategory !== 'ALL'}
				<Button
					variant="ghost"
					onclick={() => { searchQuery = ''; selectedCategory = 'ALL'; }}
					class="h-9 px-3 text-xs text-slate-500"
				>
					<RotateCcw class="w-3.5 h-3.5 mr-1" />
					<span>Reset</span>
				</Button>
			{/if}
		</div>
	</div>

	<!-- Global Reusable Table Component for Parameters -->
	<Table
		title="Tabel Parameter Konfigurasi Platform"
		subtitle="Daftar nilai parameter runtime yang disinkronkan secara global di seluruh layanan PantauDuit"
		icon={SlidersHorizontal}
		badge="{filteredParameters.length} Parameter"
		{columns}
		items={filteredParameters}
		emptyMessage="Tidak ada parameter yang cocok"
		emptyDescription="Coba ubah kata kunci pencarian atau reset filter kategori di atas."
	>
		{#snippet row(param, index)}
			<tr class="hover:bg-slate-50/60 dark:hover:bg-white/[0.02] transition-colors">
				<!-- Parameter Key & Name -->
				<td class="p-3.5 whitespace-nowrap">
					<div class="space-y-0.5">
						<span class="font-semibold text-xs text-slate-900 dark:text-white block">
							{param.name}
						</span>
						<span class="inline-block px-1.5 py-0.2 rounded text-[10px] font-mono text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-white/5 border border-slate-200/60 dark:border-white/10">
							{param.key}
						</span>
					</div>
				</td>

				<!-- Category Badge -->
				<td class="p-3.5 whitespace-nowrap">
					{#if param.category === 'TIER'}
						<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-lg text-[10px] font-semibold bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
							<CreditCard class="w-3 h-3" />
							<span>{param.categoryLabel}</span>
						</span>
					{:else if param.category === 'BOT'}
						<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-lg text-[10px] font-semibold bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20">
							<Bot class="w-3 h-3" />
							<span>{param.categoryLabel}</span>
						</span>
					{:else if param.category === 'FINANSIAL'}
						<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-lg text-[10px] font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
							<Coins class="w-3 h-3" />
							<span>{param.categoryLabel}</span>
						</span>
					{:else}
						<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-lg text-[10px] font-semibold bg-purple-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/20">
							<Shield class="w-3 h-3" />
							<span>{param.categoryLabel}</span>
						</span>
					{/if}
				</td>

				<!-- Description -->
				<td class="p-3.5">
					<p class="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-2 leading-relaxed max-w-md">
						{param.description}
					</p>
				</td>

				<!-- Current Value -->
				<td class="p-3.5 whitespace-nowrap">
					{#if param.type === 'boolean'}
						<button
							type="button"
							onclick={() => toggleBooleanInline(param)}
							class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold cursor-pointer transition-colors {param.value
								? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/15'
								: 'bg-slate-100 dark:bg-white/5 text-slate-500 dark:text-slate-400 border border-slate-200/60 dark:border-white/10 hover:bg-slate-200/50'}"
							title="Klik untuk toggle status langsung"
						>
							<span class="w-1.5 h-1.5 rounded-full {param.value ? 'bg-emerald-500' : 'bg-slate-400'}"></span>
							<span>{param.value ? 'AKTIF' : 'NONAKTIF'}</span>
						</button>
					{:else}
						<div class="inline-flex items-center gap-2">
							<span class="px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-white/5 text-slate-900 dark:text-white font-mono text-xs font-semibold border border-slate-200/60 dark:border-white/10">
								{formatValueDisplay(param)}
							</span>
						</div>
					{/if}
				</td>

				<!-- Cache Status -->
				<td class="p-3.5 whitespace-nowrap text-center">
					<span class="inline-flex items-center gap-1.5 text-[10px] font-mono text-slate-400">
						<span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
						<span>Redis TTL</span>
					</span>
				</td>

				<!-- Actions -->
				<td class="p-3.5 whitespace-nowrap text-right">
					<Button
						variant="outline"
						onclick={() => openEditModal(param)}
						class="h-7 px-2.5 text-[11px] border-slate-200/80 dark:border-white/10 hover:border-[#007AFF]"
						title="Ubah nilai parameter"
					>
						<Edit3 class="w-3 h-3 text-[#007AFF] dark:text-[#0A84FF] mr-1" />
						<span>Ubah</span>
					</Button>
				</td>
			</tr>
		{/snippet}

		{#snippet footer()}
			<div class="flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-slate-500 dark:text-slate-400 px-2 py-1">
				<span class="text-[11px]">
					Setiap perubahan disimpan dalam memori Redis berkecepatan tinggi dengan replikasi instan ke database.
				</span>
				<div class="flex items-center gap-3 text-[11px]">
					<span class="flex items-center gap-1.5">
						<span class="w-2 h-2 rounded-full bg-amber-500"></span> Kuota & Tier
					</span>
					<span class="flex items-center gap-1.5">
						<span class="w-2 h-2 rounded-full bg-blue-500"></span> Bot Telegram
					</span>
					<span class="flex items-center gap-1.5">
						<span class="w-2 h-2 rounded-full bg-emerald-500"></span> Keuangan
					</span>
					<span class="flex items-center gap-1.5">
						<span class="w-2 h-2 rounded-full bg-purple-500"></span> Keamanan
					</span>
				</div>
			</div>
		{/snippet}
	</Table>
</div>

<!-- Modal Ubah Nilai Parameter -->
{#if editingParam}
	<Modal
		bind:open={isEditModalOpen}
		title="Ubah Parameter: {editingParam.name}"
		description="Perbarui nilai konfigurasi runtime sistem untuk kunci {editingParam.key}"
	>
		<div class="space-y-4 text-xs">
			<!-- Info Parameter Card -->
			<div class="p-3 rounded-xl bg-slate-50 dark:bg-white/[0.02] border border-slate-100 dark:border-white/5 space-y-1">
				<div class="flex items-center justify-between">
					<span class="font-mono text-[10px] text-slate-400">{editingParam.key}</span>
					<span class="px-2 py-0.5 rounded text-[9px] font-semibold bg-slate-100 dark:bg-white/5 text-slate-500">
						{editingParam.categoryLabel}
					</span>
				</div>
				<p class="text-[11px] text-slate-500 dark:text-slate-400">
					{editingParam.description}
				</p>
			</div>

			<!-- Form Control Depending on Type -->
			{#if editingParam.type === 'number'}
				<div>
					<label for="param-edit-number" class="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 block">
						Nilai Konfigurasi ({editingParam.unit || 'Angka'})
					</label>
					<div class="flex items-center gap-2">
						<input
							id="param-edit-number"
							type="number"
							bind:value={editValueNumber}
							min={editingParam.min}
							max={editingParam.max}
							step={editingParam.step || 1}
							class="w-full h-9 px-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-900 dark:text-white font-semibold focus:outline-none focus:border-[#007AFF]"
						/>
						{#if editingParam.unit}
							<span class="text-slate-400 shrink-0 font-medium text-[11px]">{editingParam.unit}</span>
						{/if}
					</div>
					{#if editingParam.min !== undefined || editingParam.max !== undefined}
						<span class="text-[10px] text-slate-400 mt-1 block">
							Batas: Min {editingParam.min ?? '-'} &bull; Max {editingParam.max ?? '-'}
						</span>
					{/if}
				</div>
			{:else if editingParam.type === 'select'}
				<div>
					<label for="param-edit-select" class="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 block">
						Pilih Nilai
					</label>
					<select
						id="param-edit-select"
						bind:value={editValueString}
						class="w-full h-9 px-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-[#007AFF]"
					>
						{#each editingParam.options || [] as opt}
							<option value={opt.value}>{opt.label}</option>
						{/each}
					</select>
				</div>
			{:else if editingParam.type === 'boolean'}
				<div>
					<span class="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 block">
						Status Parameter
					</span>
					<label for="param-edit-boolean" class="flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-white/[0.02] border border-slate-100 dark:border-white/5 cursor-pointer">
						<div>
							<p class="font-semibold text-slate-800 dark:text-slate-200">
								{editValueBoolean ? 'Aktifkan (True)' : 'Nonaktifkan (False)'}
							</p>
							<span class="text-[10px] text-slate-400">
								{editValueBoolean ? 'Fitur / pengaturan ini sedang aktif di seluruh sistem' : 'Fitur / pengaturan ini sedang dinonaktifkan'}
							</span>
						</div>
						<input
							id="param-edit-boolean"
							type="checkbox"
							bind:checked={editValueBoolean}
							class="w-4 h-4 rounded text-[#007AFF] focus:ring-0 cursor-pointer"
						/>
					</label>
				</div>
			{:else}
				<div>
					<label for="param-edit-text" class="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 block">
						Nilai Teks
					</label>
					<input
						id="param-edit-text"
						type="text"
						bind:value={editValueString}
						class="w-full h-9 px-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-[#007AFF]"
					/>
				</div>
			{/if}

			<!-- Default Value Reference -->
			<div class="text-[10px] text-slate-400 flex items-center justify-between pt-1">
				<span>Nilai Bawaan Standar:</span>
				<strong class="font-mono text-slate-600 dark:text-slate-300">{String(editingParam.defaultValue)}</strong>
			</div>

			<!-- Footer Buttons -->
			<div class="flex justify-end gap-2 pt-2 border-t border-slate-100 dark:border-white/5">
				<Button variant="ghost" onclick={() => (isEditModalOpen = false)}>
					Batal
				</Button>
				<Button variant="primary" onclick={saveParameterEdit}>
					Simpan Nilai
				</Button>
			</div>
		</div>
	</Modal>
{/if}

