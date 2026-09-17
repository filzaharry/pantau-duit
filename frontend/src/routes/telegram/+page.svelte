<script lang="ts">
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import TelegramSimulator from '$lib/components/telegram/TelegramSimulator.svelte';
	import GlassSurface from '$lib/components/ui/GlassSurface.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import {
		Bot,
		Send,
		CheckCircle2,
		Copy,
		Sparkles,
		ShieldCheck,
		ExternalLink,
		Smartphone,
		RefreshCw
	} from 'lucide-svelte';

	let isCopied = $state(false);
	const pairingCode = 'PD-994812';

	function copyCode() {
		navigator.clipboard.writeText(pairingCode);
		isCopied = true;
		notificationStore.toast('Kode pairing disalin ke clipboard!', 'success');
		setTimeout(() => (isCopied = false), 2000);
	}
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
		<div>
			<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
				<Bot class="w-6 h-6 text-[#007AFF] dark:text-[#0A84FF]" />
				<span>Integrasi Asisten Telegram</span>
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
				Catat pengeluaran secepat kilat langsung dari chat room Telegram tanpa perlu buka aplikasi
			</p>
		</div>

		<!-- Status Badge -->
		<div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 text-xs font-semibold self-start sm:self-auto">
			<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
			<span>Status: Terhubung & Aktif</span>
		</div>
	</div>

	<!-- Connection Card -->
	<div class="p-6 sm:p-7 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] space-y-5">
		<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
			<div class="flex items-center gap-4">
				<div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-[#0088cc] to-[#006699] text-white flex items-center justify-center shrink-0">
					<Send class="w-7 h-7" />
				</div>
				<div>
					<div class="flex items-center gap-2">
						<h2 class="text-base font-semibold text-slate-900 dark:text-white">
							@PantauDuitBot
						</h2>
						<span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-[#007AFF]/10 text-[#007AFF]">
							Official Bot
						</span>
					</div>
					<p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
						Akun Telegram: <strong>@alex_finance</strong> &bull; ID: <code>198273641</code>
					</p>
				</div>
			</div>

			<a
				href="https://t.me/PantauDuitBot"
				target="_blank"
				rel="noreferrer"
				class="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-[#0088cc] hover:bg-[#0077b5] text-white text-xs font-semibold transition-all self-start sm:self-auto"
			>
				<span>Buka di Telegram</span>
				<ExternalLink class="w-3.5 h-3.5" />
			</a>
		</div>

		<!-- Pairing Code Banner -->
		<div class="p-4 rounded-2xl bg-slate-50 dark:bg-white/[0.03] border border-slate-200/70 dark:border-white/[0.06] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
			<div>
				<span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Token Pairing Akun Baru</span>
				<div class="flex items-center gap-3 mt-1">
					<span class="text-lg font-mono font-semibold text-slate-900 dark:text-white tracking-widest">
						{pairingCode}
					</span>
				</div>
			</div>

			<Button variant="outline" onclick={copyCode}>
				<Copy class="w-3.5 h-3.5" />
				<span>{isCopied ? 'Tersalin!' : 'Salin Kode'}</span>
			</Button>
		</div>
	</div>

	<!-- Syntax Cheatsheet -->
	<div class="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
		<!-- Format Cepat Delimiter -->
		<div class="p-6 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] space-y-4">
			<div class="flex items-center justify-between">
				<span class="px-2.5 py-1 rounded-lg bg-blue-500/10 text-blue-600 dark:text-blue-400 text-xs font-semibold">
					Format 1: Semicolon (;)
				</span>
			</div>
			<div>
				<h3 class="text-sm font-semibold text-slate-900 dark:text-white">
					Format Cepat (Semicolon)
				</h3>
				<p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
					Format paling cepat dan akurat: <code class="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-white/[0.06] text-blue-600 dark:text-blue-400 font-mono">nama;kategori;nominal</code>
				</p>
			</div>
			<div class="space-y-2 text-xs font-mono">
				<div class="p-2.5 rounded-xl bg-slate-50 dark:bg-white/[0.03] border border-slate-200/60 dark:border-white/[0.06] text-slate-800 dark:text-slate-200">
					bakso;makanan;15000
				</div>
				<div class="p-2.5 rounded-xl bg-slate-50 dark:bg-white/[0.03] border border-slate-200/60 dark:border-white/[0.06] text-slate-800 dark:text-slate-200">
					bensin shell;transport;45000
				</div>
				<div class="p-2.5 rounded-xl bg-slate-50 dark:bg-white/[0.03] border border-slate-200/60 dark:border-white/[0.06] text-slate-800 dark:text-slate-200">
					gaji kantor;gaji;8500000
				</div>
			</div>
		</div>

		<!-- Natural Language AI -->
		<div class="p-6 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] space-y-4">
			<div class="flex items-center justify-between">
				<span class="px-2.5 py-1 rounded-lg bg-purple-500/10 text-purple-600 dark:text-purple-400 text-xs font-semibold flex items-center gap-1.5">
					<Sparkles class="w-3.5 h-3.5" />
					<span>Format 2: AI Parser Bebas</span>
				</span>
			</div>
			<div>
				<h3 class="text-sm font-semibold text-slate-900 dark:text-white">
					Input Bebas (Natural Language)
				</h3>
				<p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
					AI PantauDuit otomatis mendeteksi kategori dan nominal dari kalimat obrolan:
				</p>
			</div>
			<div class="space-y-2 text-xs font-mono">
				<div class="p-2.5 rounded-xl bg-slate-50 dark:bg-white/[0.03] border border-slate-200/60 dark:border-white/[0.06] text-slate-800 dark:text-slate-200">
					"tadi makan bakso urat 15 ribu"
				</div>
				<div class="p-2.5 rounded-xl bg-slate-50 dark:bg-white/[0.03] border border-slate-200/60 dark:border-white/[0.06] text-slate-800 dark:text-slate-200">
					"isi bensin pertamax 50rb di spbu"
				</div>
				<div class="p-2.5 rounded-xl bg-slate-50 dark:bg-white/[0.03] border border-slate-200/60 dark:border-white/[0.06] text-slate-800 dark:text-slate-200">
					"beli kopi susu gula aren 22k"
				</div>
			</div>
		</div>
	</div>

	<!-- Interactive Live Simulator Section -->
	<div class="space-y-3">
		<div class="flex items-center gap-2">
			<Sparkles class="w-4 h-4 text-[#007AFF] dark:text-[#0A84FF]" />
			<h3 class="text-sm font-semibold text-slate-900 dark:text-white uppercase tracking-wider">
				Simulator Live Parsing Telegram
			</h3>
		</div>
		<p class="text-xs text-slate-500 dark:text-slate-400">
			Uji coba parsing pesan langsung di sini. Data yang tercatat akan otomatis memperbarui saldo dashboard secara realtime!
		</p>

		<TelegramSimulator />
	</div>
</div>
