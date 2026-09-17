<script lang="ts">
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Table, { type TableColumn } from '$lib/components/ui/Table.svelte';
	import {
		Shield,
		Terminal,
		Search,
		Filter,
		RotateCcw,
		CheckCircle2,
		AlertTriangle,
		Lock,
		Users,
		Bot,
		CreditCard,
		Database,
		Clock,
		ExternalLink,
		Eye
	} from 'lucide-svelte';

	let searchQuery = $state('');
	let selectedCategory = $state<'ALL' | 'AUTH' | 'SUBSCRIPTION' | 'TELEGRAM' | 'RBAC' | 'SYSTEM'>('ALL');
	let selectedStatus = $state<'ALL' | 'SUCCESS' | 'WARNING' | 'BLOCKED'>('ALL');
	let inspectingLog = $state<any | null>(null);

	// Mock Audit Logs Data
	const auditLogs = $state([
		{
			id: 'log-001',
			timestamp: '16:04:12 WIB',
			date: '12 Sep 2026',
			actor: 'alex@pantauduit.id',
			actorRole: 'TENANT_OWNER',
			tenant: 'Workspace Personal Alex',
			category: 'SUBSCRIPTION',
			event: 'SUBSCRIPTION_RENEWAL',
			status: 'SUCCESS',
			ip: '180.252.164.21',
			details: 'Pro plan recurring renewal via Midtrans SNAP (Invoice #INV-202609-0041). Total Rp 49.000 terverifikasi.',
			payload: {
				plan: 'PRO',
				amount: 49000,
				gateway: 'MIDTRANS',
				payment_type: 'GOPAY_QRIS',
				status: 'settlement'
			}
		},
		{
			id: 'log-002',
			timestamp: '15:58:30 WIB',
			date: '12 Sep 2026',
			actor: '@PantauDuitBot (Engine)',
			actorRole: 'SYSTEM_BOT',
			tenant: 'Kedai Kopi Bahagia UMKM',
			category: 'TELEGRAM',
			event: 'TELEGRAM_WEBHOOK_BATCH',
			status: 'SUCCESS',
			ip: '149.154.167.220',
			details: 'Webhook batch 14 pesan diparsing dengan akurasi 99.2% NLP confidence. 14 transaksi baru dicatat otomatis.',
			payload: {
				batch_size: 14,
				avg_latency_ms: 18,
				intent_confidence: 0.992,
				category_mapped: 'Pengeluaran Bahan Baku'
			}
		},
		{
			id: 'log-003',
			timestamp: '15:42:05 WIB',
			date: '12 Sep 2026',
			actor: 'hendra@rahardjo.com',
			actorRole: 'TENANT_OWNER',
			tenant: 'Keluarga Rahardjo Finansial',
			category: 'RBAC',
			event: 'RBAC_ROLE_GRANTED',
			status: 'SUCCESS',
			ip: '114.122.45.89',
			details: 'Owner menambahkan peran "Accountant" untuk anggota maya@rahardjo.com dengan izin view & create report.',
			payload: {
				target_user: 'maya@rahardjo.com',
				assigned_role: 'Accountant',
				permissions: ['read:transactions', 'create:reports']
			}
		},
		{
			id: 'log-004',
			timestamp: '15:10:19 WIB',
			date: '12 Sep 2026',
			actor: 'celery_ledger_worker',
			actorRole: 'SYSTEM_CRON',
			tenant: 'Platform Global',
			category: 'SYSTEM',
			event: 'DAILY_LEDGER_RECONCILIATION',
			status: 'SUCCESS',
			ip: '127.0.0.1',
			details: 'Rekonsiliasi otomatis 33 buku besar kas tenant selesai. 0 drifting saldo, seluruh mutasi sinkron dengan snapshot.',
			payload: {
				accounts_checked: 33,
				drifts_found: 0,
				total_reconciled_volume: 1482000000
			}
		},
		{
			id: 'log-005',
			timestamp: '14:35:50 WIB',
			date: '12 Sep 2026',
			actor: 'unknown_client (Suspicious)',
			actorRole: 'ANONYMOUS',
			tenant: 'N/A',
			category: 'AUTH',
			event: 'FAILED_AUTH_ATTEMPT',
			status: 'BLOCKED',
			ip: '114.124.90.112',
			details: 'Rate limiter otomatis aktif: 5 kali percobaan OTP salah berturut-turut pada target nomor +62812998811xx. IP diblokir 15 menit.',
			payload: {
				attempt_count: 5,
				action_taken: 'IP_TEMPORARY_BAN',
				duration_minutes: 15,
				target_endpoint: '/api/v1/auth/otp/verify'
			}
		},
		{
			id: 'log-006',
			timestamp: '13:20:04 WIB',
			date: '12 Sep 2026',
			actor: 'admin@pantauduit.id',
			actorRole: 'SUPERUSER',
			tenant: 'Kedai Kopi Bahagia UMKM',
			category: 'RBAC',
			event: 'SUPERADMIN_IMPERSONATION',
			status: 'WARNING',
			ip: '36.88.12.94',
			details: 'Superadmin melakukan impersonasi baca-saja (read-only) untuk investigasi tiket komplain webhook sinkronisasi.',
			payload: {
				admin_user: 'admin@pantauduit.id',
				ticket_id: 'TIK-9821',
				mode: 'READ_ONLY',
				session_ttl: 1800
			}
		},
		{
			id: 'log-007',
			timestamp: '11:15:22 WIB',
			date: '12 Sep 2026',
			actor: 'maya@tech.id',
			actorRole: 'TENANT_OWNER',
			tenant: 'Workspace Maya Dev',
			category: 'AUTH',
			event: 'USER_LOGIN_SUCCESS',
			status: 'SUCCESS',
			ip: '182.253.8.45',
			details: 'Login via Telegram Web Login widget berhasil. Sesi JWT token diterbitkan dengan masa berlaku 7 hari.',
			payload: {
				auth_provider: 'TELEGRAM_OAUTH',
				device: 'Safari on macOS',
				mfa_used: false
			}
		}
	]);

	const filteredLogs = $derived(
		auditLogs.filter((log) => {
			if (selectedCategory !== 'ALL' && log.category !== selectedCategory) return false;
			if (selectedStatus !== 'ALL' && log.status !== selectedStatus) return false;

			if (searchQuery.trim()) {
				const q = searchQuery.toLowerCase();
				const matchActor = log.actor.toLowerCase().includes(q);
				const matchTenant = log.tenant.toLowerCase().includes(q);
				const matchEvent = log.event.toLowerCase().includes(q);
				const matchDetails = log.details.toLowerCase().includes(q);
				const matchIp = log.ip.toLowerCase().includes(q);
				if (!matchActor && !matchTenant && !matchEvent && !matchDetails && !matchIp) return false;
			}

			return true;
		})
	);

	function resetFilters() {
		searchQuery = '';
		selectedCategory = 'ALL';
		selectedStatus = 'ALL';
	}

	const columns: TableColumn<any>[] = [
		{ key: 'timestamp', header: 'Waktu', sortable: true },
		{ key: 'actor', header: 'Aktor & Peran', sortable: true },
		{ key: 'tenant', header: 'Ruang Kerja (Tenant)', sortable: true },
		{ key: 'event', header: 'Event', sortable: true },
		{ key: 'status', header: 'Status', sortable: true },
		{ key: 'details', header: 'Detail Log', sortable: false },
		{ key: 'actions', header: 'Aksi', align: 'right', sortable: false, width: '60px' }
	];
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full pb-24 lg:pb-10">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
		<div>
			<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
				<Shield class="w-6 h-6 text-purple-600 dark:text-purple-400" />
				<span>Security & Audit Trail Logs</span>
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
				Jejak audit keamanan platform, log otentikasi, impersonasi superadmin, dan aktivitas webhook sensitif
			</p>
		</div>

		<div class="flex items-center gap-2 self-start sm:self-auto">
			<div class="px-3 h-9 rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-xs font-semibold border border-emerald-500/20 flex items-center gap-1.5">
				<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
				<span>Live Event Stream Aktif</span>
			</div>
		</div>
	</div>

	<!-- Top Metric Ribbon Strip (4 Columns) -->
	<div class="p-3 sm:p-5 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
		<div class="grid grid-cols-2 lg:grid-cols-4 gap-2.5 sm:gap-4 lg:divide-x divide-slate-100 dark:divide-white/5">
			<!-- Col 1: Total Events Logged -->
			<div class="flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400 flex items-center justify-center shrink-0">
					<Terminal class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Total Event Terdata</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">12.480 Event</span>
					<span class="text-[10px] sm:text-[11px] text-emerald-500 font-medium truncate block">+1.240 Hari Ini</span>
				</div>
			</div>

			<!-- Col 2: Security Pass Rate -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
					<CheckCircle2 class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Tingkat Keberhasilan</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">99.8% Sukses</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">Otentikasi & Mutasi Normal</span>
				</div>
			</div>

			<!-- Col 3: Blocked Threats -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-rose-500/10 text-rose-600 dark:text-rose-400 flex items-center justify-center shrink-0">
					<Lock class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Percobaan Diblokir</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">24 Ancaman</span>
					<span class="text-[10px] sm:text-[11px] text-rose-500 font-medium truncate block">Rate Limiting Auto-Ban</span>
				</div>
			</div>

			<!-- Col 4: Active Admin Sessions -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-blue-500/10 text-[#007AFF] dark:text-[#0A84FF] flex items-center justify-center shrink-0">
					<Users class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Sesi Superadmin</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">1 Sesi Aktif</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">IP Jakarta (MFA Verified)</span>
				</div>
			</div>
		</div>
	</div>

	<!-- Controls & Category Filters -->
	<div class="space-y-3">
		<!-- Category Tabs -->
		<div class="flex items-center gap-1.5 overflow-x-auto no-scrollbar pb-1">
			{#each [
				{ id: 'ALL', label: 'Semua Event' },
				{ id: 'AUTH', label: 'Otentikasi & Login' },
				{ id: 'SUBSCRIPTION', label: 'Langganan & Pembayaran' },
				{ id: 'TELEGRAM', label: 'Webhook Telegram' },
				{ id: 'RBAC', label: 'Hak Akses (RBAC)' },
				{ id: 'SYSTEM', label: 'Sistem & Rekonsiliasi' }
			] as tab}
				<button
					type="button"
					onclick={() => (selectedCategory = tab.id as any)}
					class="px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all shrink-0 {selectedCategory === tab.id
						? 'bg-[#007AFF] text-white shadow-sm'
						: 'bg-white dark:bg-white/5 border border-slate-200/70 dark:border-white/10 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
				>
					{tab.label}
				</button>
			{/each}
		</div>

		<!-- Search and Status Filter Bar -->
		<div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5">
			<div class="relative flex-1">
				<Search class="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
				<input
					type="text"
					bind:value={searchQuery}
					placeholder="Cari aktor, email, event, IP address, atau detail..."
					class="w-full h-9 pl-9 pr-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-[#007AFF] transition-colors"
				/>
			</div>

			<div class="flex items-center gap-2">
				<select
					bind:value={selectedStatus}
					class="h-9 px-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-700 dark:text-slate-300 focus:outline-none focus:border-[#007AFF]"
				>
					<option value="ALL">Semua Status</option>
					<option value="SUCCESS">Status: SUCCESS</option>
					<option value="WARNING">Status: WARNING</option>
					<option value="BLOCKED">Status: BLOCKED</option>
				</select>

				{#if searchQuery || selectedCategory !== 'ALL' || selectedStatus !== 'ALL'}
					<Button variant="ghost" onclick={resetFilters} class="h-9 px-3 text-xs text-slate-500">
						<RotateCcw class="w-3.5 h-3.5 mr-1" />
						<span>Reset</span>
					</Button>
				{/if}
			</div>
		</div>
	</div>

	<!-- Global Reusable Table Component for Audit Logs -->
	<Table
		title="Daftar Jejak Audit Keamanan"
		subtitle="Append-only log aktivitas sistem, keamanan, dan mutasi data platform"
		icon={Terminal}
		badge="{filteredLogs.length} Entri Ditemukan"
		{columns}
		items={filteredLogs}
		emptyMessage="Tidak ada log yang cocok"
		emptyDescription="Coba ubah kata kunci pencarian atau sesuaikan filter status dan event."
	>
		{#snippet row(log, index)}
			<tr class="hover:bg-slate-50/60 dark:hover:bg-white/[0.02] transition-colors">
				<td class="p-3.5 whitespace-nowrap text-slate-500 dark:text-slate-400 font-mono">
					<div>{log.timestamp}</div>
					<div class="text-[10px] text-slate-400">{log.date}</div>
				</td>
				<td class="p-3.5 whitespace-nowrap font-sans">
					<p class="font-semibold text-slate-900 dark:text-white">{log.actor}</p>
					<div class="flex items-center gap-1.5 mt-0.5">
						<span class="px-1.5 py-0.2 rounded text-[9px] font-semibold bg-slate-100 dark:bg-white/5 text-slate-500 font-mono">
							{log.actorRole}
						</span>
						<span class="text-[10px] text-slate-400 font-mono">IP: {log.ip}</span>
					</div>
				</td>
				<td class="p-3.5 whitespace-nowrap font-sans text-slate-700 dark:text-slate-300">
					{log.tenant}
				</td>
				<td class="p-3.5 whitespace-nowrap">
					<span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-purple-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/20">
						{log.event}
					</span>
				</td>
				<td class="p-3.5 whitespace-nowrap">
					<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold flex items-center gap-1 w-fit {log.status === 'SUCCESS'
						? 'bg-emerald-500/10 text-emerald-600 border border-emerald-500/20'
						: log.status === 'WARNING'
							? 'bg-amber-500/10 text-amber-600 border border-amber-500/20'
							: 'bg-rose-500/10 text-rose-600 border border-rose-500/20'}">
						{#if log.status === 'SUCCESS'}
							<CheckCircle2 class="w-3 h-3" />
						{:else if log.status === 'WARNING'}
							<AlertTriangle class="w-3 h-3" />
						{:else}
							<Lock class="w-3 h-3" />
						{/if}
						<span>{log.status}</span>
					</span>
				</td>
				<td class="p-3.5 font-sans text-slate-600 dark:text-slate-300 max-w-xs truncate" title={log.details}>
					{log.details}
				</td>
				<td class="p-3.5 text-right whitespace-nowrap font-sans">
					<button
						type="button"
						onclick={() => (inspectingLog = log)}
						class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-white/5 hover:bg-[#007AFF] hover:text-white text-slate-600 dark:text-slate-300 font-semibold transition-all text-[11px] cursor-pointer"
					>
						<Eye class="w-3.5 h-3.5" />
						<span>Payload</span>
					</button>
				</td>
			</tr>
		{/snippet}
	</Table>
</div>

<!-- Inspect Payload Modal -->
{#if inspectingLog}
	<Modal
		open={true}
		title={`Inspeksi Audit Log: ${inspectingLog.event}`}
		onclose={() => (inspectingLog = null)}
	>
		<div class="space-y-4 text-xs">
			<div class="p-3 rounded-xl bg-slate-50 dark:bg-white/[0.03] border border-slate-200/70 dark:border-white/10 space-y-1.5 font-sans">
				<div class="flex justify-between">
					<span class="text-slate-400">Aktor:</span>
					<strong class="text-slate-900 dark:text-white font-mono">{inspectingLog.actor} ({inspectingLog.actorRole})</strong>
				</div>
				<div class="flex justify-between">
					<span class="text-slate-400">Ruang Kerja:</span>
					<span class="text-slate-800 dark:text-slate-200">{inspectingLog.tenant}</span>
				</div>
				<div class="flex justify-between">
					<span class="text-slate-400">Waktu & IP:</span>
					<span class="font-mono text-slate-700 dark:text-slate-300">{inspectingLog.date} {inspectingLog.timestamp} &bull; {inspectingLog.ip}</span>
				</div>
				<div class="flex justify-between">
					<span class="text-slate-400">Status:</span>
					<span class="font-semibold text-emerald-600">{inspectingLog.status}</span>
				</div>
			</div>

			<div>
				<span class="text-[10px] uppercase font-semibold text-slate-400 tracking-wider">Ringkasan Kejadian</span>
				<p class="mt-1 p-2.5 rounded-lg bg-slate-50 dark:bg-white/5 border border-slate-100 dark:border-white/5 text-slate-800 dark:text-slate-200">
					{inspectingLog.details}
				</p>
			</div>

			<div>
				<span class="text-[10px] uppercase font-semibold text-slate-400 tracking-wider">Payload Data (JSON)</span>
				<pre class="mt-1 p-3 rounded-xl bg-[#0d1117] text-emerald-400 font-mono text-[11px] overflow-x-auto">{JSON.stringify(inspectingLog.payload, null, 2)}</pre>
			</div>

			<div class="flex justify-end pt-2">
				<Button variant="outline" onclick={() => (inspectingLog = null)}>
					Tutup
				</Button>
			</div>
		</div>
	</Modal>
{/if}
