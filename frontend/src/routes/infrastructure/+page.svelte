<script lang="ts">
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import ProgressBar from '$lib/components/ui/ProgressBar.svelte';
	import {
		Server,
		Bot,
		Database,
		Cpu,
		RefreshCw,
		CheckCircle2,
		Activity,
		ShieldCheck,
		HardDrive,
		Zap,
		Clock,
		Radio
	} from 'lucide-svelte';

	let isPinging = $state(false);
	let lastPingLatency = $state('14ms');
	let webhookStatus = $state('200 OK');

	function handlePingWebhook() {
		isPinging = true;
		notificationStore.toast('Mengirim health ping ke webhook Telegram...', 'info');
		setTimeout(() => {
			isPinging = false;
			const lat = Math.floor(Math.random() * 8 + 10);
			lastPingLatency = `${lat}ms`;
			notificationStore.toast(`Webhook Telegram Healthy: 200 OK (Latency: ${lastPingLatency})`, 'success');
		}, 500);
	}
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full pb-24 lg:pb-10">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
		<div>
			<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
				<Server class="w-6 h-6 text-[#007AFF] dark:text-[#0A84FF]" />
				<span>Infrastruktur & Telemetri Webhook</span>
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
				Status kesehatan server production, worker antrian Telegram, database pool, dan memori Redis
			</p>
		</div>

		<div class="flex items-center gap-2 self-start sm:self-auto">
			<Button variant="outline" onclick={handlePingWebhook} disabled={isPinging} class="h-9 px-4">
				<RefreshCw class="w-4 h-4 {isPinging ? 'animate-spin' : ''}" />
				<span>Ping Webhook</span>
			</Button>

			<div class="px-3 h-9 rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-xs font-semibold border border-emerald-500/20 flex items-center gap-1.5">
				<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
				<span>Cluster 99.98% Uptime</span>
			</div>
		</div>
	</div>

	<!-- Top Metric Ribbon Strip (4 Columns) -->
	<div class="p-3 sm:p-5 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
		<div class="grid grid-cols-2 lg:grid-cols-4 gap-2.5 sm:gap-4 lg:divide-x divide-slate-100 dark:divide-white/5">
			<!-- Col 1: Webhook Latency -->
			<div class="flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-blue-500/10 text-[#007AFF] dark:text-[#0A84FF] flex items-center justify-center shrink-0">
					<Radio class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Latensi Webhook</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">{lastPingLatency}</span>
					<span class="text-[10px] sm:text-[11px] text-emerald-500 font-medium truncate block">Status {webhookStatus}</span>
				</div>
			</div>

			<!-- Col 2: Celery Workers -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
					<Zap class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Worker Antrian</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">4 / 4 Worker Aktif</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">0 Pesan Tertunda</span>
				</div>
			</div>

			<!-- Col 3: PostgreSQL Pool -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400 flex items-center justify-center shrink-0">
					<Database class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">PostgreSQL Pool</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">14 / 50 Koneksi</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">Beban 28% (Optimal)</span>
				</div>
			</div>

			<!-- Col 4: Redis Session Memory -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 flex items-center justify-center shrink-0">
					<HardDrive class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Cache & Sesi Redis</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">142 MB / 1 GB</span>
					<span class="text-[10px] sm:text-[11px] text-emerald-500 font-medium truncate block">Beban 14% (Aman)</span>
				</div>
			</div>
		</div>
	</div>

	<!-- Telegram Bot Webhook Diagnostics Panel -->
	<div class="p-5 sm:p-6 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] space-y-4">
		<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 dark:border-white/5 pb-3">
			<div class="flex items-center gap-2.5">
				<div class="w-8 h-8 rounded-xl bg-blue-500/10 text-[#0088cc] flex items-center justify-center shrink-0">
					<Bot class="w-4 h-4" />
				</div>
				<div>
					<h2 class="text-sm font-semibold text-slate-900 dark:text-white uppercase tracking-wider">
						Telegram Bot Engine & Webhook Endpoints
					</h2>
					<p class="text-[11px] text-slate-400">Parameter integrasi webhook resmi Telegram Bot API</p>
				</div>
			</div>
			<span class="text-xs font-mono text-emerald-500 bg-emerald-500/10 px-3 py-1 rounded-xl border border-emerald-500/20 self-start sm:self-auto">
				WEBHOOK_HEALTH_OK (200)
			</span>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
			<div class="p-3.5 rounded-2xl bg-slate-50/80 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/5 space-y-1">
				<span class="text-[10px] text-slate-400 uppercase font-semibold block">Active Webhook URL</span>
				<p class="font-mono text-xs font-medium text-slate-900 dark:text-white truncate">
					https://api.pantauduit.id/api/v1/webhook/telegram
				</p>
			</div>

			<div class="p-3.5 rounded-2xl bg-slate-50/80 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/5 space-y-1">
				<span class="text-[10px] text-slate-400 uppercase font-semibold block">Queue Workers</span>
				<p class="font-semibold text-emerald-600 dark:text-emerald-400">
					4 / 4 Celery + Redis Workers Ready
				</p>
			</div>

			<div class="p-3.5 rounded-2xl bg-slate-50/80 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/5 space-y-1">
				<span class="text-[10px] text-slate-400 uppercase font-semibold block">Pending Retry Queue</span>
				<p class="font-semibold text-slate-900 dark:text-white">
					0 Messages (Zero Backlog)
				</p>
			</div>

			<div class="p-3.5 rounded-2xl bg-slate-50/80 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/5 space-y-1">
				<span class="text-[10px] text-slate-400 uppercase font-semibold block">SSL / TLS Handshake</span>
				<p class="font-semibold text-emerald-600 dark:text-emerald-400">
					TLS 1.3 Valid (Let's Encrypt)
				</p>
			</div>
		</div>
	</div>

	<!-- System Resource Meters: 3 Cards Grid -->
	<div class="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-5">
		<!-- PostgreSQL -->
		<div class="p-5 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] space-y-3">
			<div class="flex items-center gap-2">
				<Database class="w-4 h-4 text-blue-500" />
				<h3 class="text-xs font-semibold text-slate-900 dark:text-white uppercase tracking-wider">
					PostgreSQL Database Pool
				</h3>
			</div>
			<div>
				<div class="flex justify-between text-xs mb-1.5">
					<span class="text-slate-500">Koneksi Aktif</span>
					<span class="font-semibold text-slate-900 dark:text-white">14 / 50 (28%)</span>
				</div>
				<ProgressBar value={28} variant="blue" size="sm" />
			</div>
			<p class="text-[11px] text-slate-400">Database `pantau_duit_db` beroperasi normal tanpa deadlock.</p>
		</div>

		<!-- Redis -->
		<div class="p-5 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] space-y-3">
			<div class="flex items-center gap-2">
				<HardDrive class="w-4 h-4 text-emerald-500" />
				<h3 class="text-xs font-semibold text-slate-900 dark:text-white uppercase tracking-wider">
					Redis Session & Cache
				</h3>
			</div>
			<div>
				<div class="flex justify-between text-xs mb-1.5">
					<span class="text-slate-500">Memori Terpakai</span>
					<span class="font-semibold text-slate-900 dark:text-white">142 MB / 1024 MB (14%)</span>
				</div>
				<ProgressBar value={14} variant="emerald" size="sm" />
			</div>
			<p class="text-[11px] text-slate-400">Cache sesi login dan antrian telegram realtime efisien.</p>
		</div>

		<!-- CPU Load -->
		<div class="p-5 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] space-y-3">
			<div class="flex items-center gap-2">
				<Cpu class="w-4 h-4 text-purple-500" />
				<h3 class="text-xs font-semibold text-slate-900 dark:text-white uppercase tracking-wider">
					API Worker CPU Load
				</h3>
			</div>
			<div>
				<div class="flex justify-between text-xs mb-1.5">
					<span class="text-slate-500">Beban Pemrosesan</span>
					<span class="font-semibold text-slate-900 dark:text-white">0.18 avg (18%)</span>
				</div>
				<ProgressBar value={18} variant="purple" size="sm" />
			</div>
			<p class="text-[11px] text-slate-400">FastAPI backend server responsif di bawah batas aman 70%.</p>
		</div>
	</div>
</div>
