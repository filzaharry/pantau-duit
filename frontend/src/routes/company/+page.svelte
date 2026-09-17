<script lang="ts">
	import { formatRupiah, formatDate } from '$lib/utils/formatters';
	import Button from '$lib/components/ui/Button.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import {
		Building2,
		Users,
		Clock,
		Fingerprint,
		CreditCard,
		FileText,
		CalendarCheck,
		Receipt,
		ArrowUpRight,
		CheckCircle2,
		AlertTriangle,
		TrendingUp,
		Sun,
		Sunset,
		Moon,
		Activity,
		ShieldCheck,
		RefreshCw
	} from 'lucide-svelte';

	let isSyncing = $state(false);

	function quickSync() {
		isSyncing = true;
		notificationStore.info('Menghubungi socket terminal fingerprint...', 'Sinkronisasi Dimulai');
		setTimeout(() => {
			isSyncing = false;
			notificationStore.success('Semua data absensi shift telah tersinkronisasi!', 'Operasional Lancar');
		}, 1200);
	}
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full">
	<!-- Hero Command Center Header -->
	<div class="relative overflow-hidden p-6 sm:p-8 rounded-3xl bg-gradient-to-br from-[#007AFF]/15 via-purple-500/10 to-transparent border border-[#007AFF]/20 backdrop-blur-xl">
		<div class="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
			<div>
				<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#007AFF]/10 border border-[#007AFF]/20 text-[#007AFF] text-xs font-semibold mb-3">
					<Building2 class="w-3.5 h-3.5" />
					<span>Enterprise HR & Payroll Command Center</span>
				</div>
				<h1 class="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white tracking-tight">
					PT Pantau Duit Solusindo
				</h1>
				<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1 max-w-2xl">
					Pusat komando operasional pabrik, manajemen shift 24/7, integrasi perangkat biometric, dan rekonsiliasi penggajian terpadu
				</p>
			</div>

			<div class="flex items-center gap-3">
				<Button variant="outline" size="sm" onclick={quickSync} disabled={isSyncing}>
					<RefreshCw class="w-4 h-4 mr-1.5 {isSyncing ? 'animate-spin' : ''}" />
					<span>{isSyncing ? 'Menarik Log...' : 'Sync Fingerprint'}</span>
				</Button>

				<a
					href="/company/attendance"
					class="px-4 py-2 rounded-2xl bg-[#007AFF] text-white text-xs font-semibold hover:bg-[#007AFF]/90 transition-all flex items-center gap-1.5 shadow-sm"
				>
					<Clock class="w-4 h-4" />
					<span>Pantau Presensi Hari Ini</span>
				</a>
			</div>
		</div>
	</div>

	<!-- Metric Highlights Grid -->
	<div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
		<a
			href="/company/employees"
			class="p-5 rounded-3xl bg-white/80 dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/10 backdrop-blur-xl hover:border-blue-500/40 transition-all group"
		>
			<div class="flex items-center justify-between">
				<span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Karyawan</span>
				<div class="p-2.5 rounded-2xl bg-blue-500/10 text-[#007AFF] group-hover:scale-110 transition-transform">
					<Users class="w-5 h-5" />
				</div>
			</div>
			<div class="mt-3 flex items-baseline gap-2">
				<span class="text-3xl font-bold text-slate-900 dark:text-white">8</span>
				<span class="text-xs text-slate-400">orang</span>
			</div>
			<p class="text-[11px] text-emerald-600 mt-1 flex items-center gap-1 font-medium">
				<CheckCircle2 class="w-3.5 h-3.5" />
				<span>7 Karyawan Aktif, 1 Probation</span>
			</p>
		</a>

		<a
			href="/company/attendance"
			class="p-5 rounded-3xl bg-white/80 dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/10 backdrop-blur-xl hover:border-emerald-500/40 transition-all group"
		>
			<div class="flex items-center justify-between">
				<span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Presensi Hari Ini</span>
				<div class="p-2.5 rounded-2xl bg-emerald-500/10 text-emerald-600 group-hover:scale-110 transition-transform">
					<Clock class="w-5 h-5" />
				</div>
			</div>
			<div class="mt-3 flex items-baseline gap-2">
				<span class="text-3xl font-bold text-slate-900 dark:text-white">5</span>
				<span class="text-xs text-slate-400">/ 6 terjadwal</span>
			</div>
			<p class="text-[11px] text-emerald-600 mt-1 flex items-center gap-1 font-medium">
				<CheckCircle2 class="w-3.5 h-3.5" />
				<span>83.3% Hadir Tepat Waktu</span>
			</p>
		</a>

		<a
			href="/company/fingerprint"
			class="p-5 rounded-3xl bg-white/80 dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/10 backdrop-blur-xl hover:border-purple-500/40 transition-all group"
		>
			<div class="flex items-center justify-between">
				<span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Terminal Fingerprint</span>
				<div class="p-2.5 rounded-2xl bg-purple-500/10 text-purple-600 group-hover:scale-110 transition-transform">
					<Fingerprint class="w-5 h-5" />
				</div>
			</div>
			<div class="mt-3 flex items-baseline gap-2">
				<span class="text-3xl font-bold text-slate-900 dark:text-white">2</span>
				<span class="text-xs text-slate-400">unit online</span>
			</div>
			<p class="text-[11px] text-purple-600 mt-1 flex items-center gap-1 font-medium">
				<Activity class="w-3.5 h-3.5" />
				<span>Socket Port 4370 Terhubung</span>
			</p>
		</a>

		<a
			href="/company/payroll"
			class="p-5 rounded-3xl bg-white/80 dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/10 backdrop-blur-xl hover:border-amber-500/40 transition-all group"
		>
			<div class="flex items-center justify-between">
				<span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Payroll Terbayar</span>
				<div class="p-2.5 rounded-2xl bg-amber-500/10 text-amber-600 group-hover:scale-110 transition-transform">
					<CreditCard class="w-5 h-5" />
				</div>
			</div>
			<div class="mt-3">
				<span class="text-2xl font-bold font-mono text-slate-900 dark:text-white">Rp 109,1M</span>
			</div>
			<p class="text-[11px] text-slate-500 mt-1 flex items-center gap-1">
				<span>Agustus 2026 &bull; Lunas Terdebet</span>
			</p>
		</a>
	</div>

	<!-- Shift Operations Real-time Overview -->
	<div class="p-6 rounded-3xl bg-white/80 dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/10 backdrop-blur-xl space-y-4">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-2.5">
				<div class="p-2 rounded-xl bg-blue-500/10 text-[#007AFF]">
					<Activity class="w-5 h-5" />
				</div>
				<div>
					<h3 class="font-bold text-sm text-slate-900 dark:text-white">Status Shift Operasional Hari Ini</h3>
					<p class="text-xs text-slate-500">Jadwal pembagian shift pabrik, gudang logistik, dan kantor pusat</p>
				</div>
			</div>
			<span class="text-xs font-mono text-slate-400">17 September 2026</span>
		</div>

		<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
			<div class="p-4 rounded-2xl border border-blue-500/20 bg-blue-500/5 space-y-2">
				<div class="flex items-center justify-between">
					<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-500 text-white">S-OFFICE</span>
					<span class="text-[11px] text-blue-600 font-semibold">Sedang Bertugas</span>
				</div>
				<h4 class="font-bold text-xs text-slate-900 dark:text-white">Jam Kantor Reguler</h4>
				<p class="text-[11px] font-mono text-slate-500">08:30 - 17:30 WIB</p>
				<p class="text-[11px] text-slate-600 dark:text-slate-400 pt-2 border-t border-slate-200/50 dark:border-white/5">
					Staff bertugas: <strong>3 Karyawan</strong>
				</p>
			</div>

			<div class="p-4 rounded-2xl border border-emerald-500/20 bg-emerald-500/5 space-y-2">
				<div class="flex items-center justify-between">
					<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500 text-white">S-PAGI</span>
					<span class="text-[11px] text-emerald-600 font-semibold">Selesai Bertugas</span>
				</div>
				<h4 class="font-bold text-xs text-slate-900 dark:text-white">Shift 1 (Pagi)</h4>
				<p class="text-[11px] font-mono text-slate-500">07:00 - 15:00 WIB</p>
				<p class="text-[11px] text-slate-600 dark:text-slate-400 pt-2 border-t border-slate-200/50 dark:border-white/5">
					Staff bertugas: <strong>2 Karyawan</strong> (1 Lembur)
				</p>
			</div>

			<div class="p-4 rounded-2xl border border-amber-500/20 bg-amber-500/5 space-y-2">
				<div class="flex items-center justify-between">
					<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500 text-white">S-SIANG</span>
					<span class="text-[11px] text-amber-600 font-semibold">Sedang Berjalan</span>
				</div>
				<h4 class="font-bold text-xs text-slate-900 dark:text-white">Shift 2 (Siang)</h4>
				<p class="text-[11px] font-mono text-slate-500">15:00 - 23:00 WIB</p>
				<p class="text-[11px] text-slate-600 dark:text-slate-400 pt-2 border-t border-slate-200/50 dark:border-white/5">
					Staff bertugas: <strong>1 Karyawan</strong>
				</p>
			</div>

			<div class="p-4 rounded-2xl border border-purple-500/20 bg-purple-500/5 space-y-2">
				<div class="flex items-center justify-between">
					<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-500 text-white">S-MALAM</span>
					<span class="text-[11px] text-purple-600 font-semibold">Persiapan</span>
				</div>
				<h4 class="font-bold text-xs text-slate-900 dark:text-white">Shift 3 (Cross-Day)</h4>
				<p class="text-[11px] font-mono text-slate-500">23:00 - 07:00 WIB</p>
				<p class="text-[11px] text-slate-600 dark:text-slate-400 pt-2 border-t border-slate-200/50 dark:border-white/5">
					Staff standby: <strong>Regu Malam</strong>
				</p>
			</div>
		</div>
	</div>

	<!-- Module Navigation Cards Grid -->
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
		<a
			href="/company/attendance"
			class="p-5 rounded-3xl bg-white/80 dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/10 backdrop-blur-xl hover:border-[#007AFF]/40 transition-all flex items-start gap-4 group"
		>
			<div class="p-3 rounded-2xl bg-blue-500/10 text-[#007AFF] group-hover:scale-110 transition-transform">
				<Clock class="w-6 h-6" />
			</div>
			<div>
				<h4 class="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-1.5">
					<span>Presensi & Shift Kerja</span>
					<ArrowUpRight class="w-4 h-4 text-slate-400 group-hover:text-[#007AFF] group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
				</h4>
				<p class="text-xs text-slate-500 mt-1">
					Monitoring toleransi keterlambatan, lembur, dan audit trail koreksi manual HR
				</p>
			</div>
		</a>

		<a
			href="/company/fingerprint"
			class="p-5 rounded-3xl bg-white/80 dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/10 backdrop-blur-xl hover:border-purple-500/40 transition-all flex items-start gap-4 group"
		>
			<div class="p-3 rounded-2xl bg-purple-500/10 text-purple-600 group-hover:scale-110 transition-transform">
				<Fingerprint class="w-6 h-6" />
			</div>
			<div>
				<h4 class="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-1.5">
					<span>Mesin Fingerprint Hardware</span>
					<ArrowUpRight class="w-4 h-4 text-slate-400 group-hover:text-purple-600 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
				</h4>
				<p class="text-xs text-slate-500 mt-1">
					Socket port 4370, raw attendance logs, deduplikasi tap, dan pemetaan PIN
				</p>
			</div>
		</a>

		<a
			href="/company/payroll"
			class="p-5 rounded-3xl bg-white/80 dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/10 backdrop-blur-xl hover:border-emerald-500/40 transition-all flex items-start gap-4 group"
		>
			<div class="p-3 rounded-2xl bg-emerald-500/10 text-emerald-600 group-hover:scale-110 transition-transform">
				<CreditCard class="w-6 h-6" />
			</div>
			<div>
				<h4 class="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-1.5">
					<span>Payroll & Slip Gaji</span>
					<ArrowUpRight class="w-4 h-4 text-slate-400 group-hover:text-emerald-600 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
				</h4>
				<p class="text-xs text-slate-500 mt-1">
					Kalkulasi gaji otomatis terhubung ke absensi, BPJS TK, BPJS Kes & PPh 21
				</p>
			</div>
		</a>

		<a
			href="/company/documents"
			class="p-5 rounded-3xl bg-white/80 dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/10 backdrop-blur-xl hover:border-blue-500/40 transition-all flex items-start gap-4 group"
		>
			<div class="p-3 rounded-2xl bg-blue-500/10 text-blue-600 group-hover:scale-110 transition-transform">
				<FileText class="w-6 h-6" />
			</div>
			<div>
				<h4 class="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-1.5">
					<span>Dokumen & Surat HR</span>
					<ArrowUpRight class="w-4 h-4 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
				</h4>
				<p class="text-xs text-slate-500 mt-1">
					Generator PKWT, SK Karyawan Tetap, SP-1/2/3, dan Paklaring siap cetak PDF
				</p>
			</div>
		</a>

		<a
			href="/company/leaves"
			class="p-5 rounded-3xl bg-white/80 dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/10 backdrop-blur-xl hover:border-amber-500/40 transition-all flex items-start gap-4 group"
		>
			<div class="p-3 rounded-2xl bg-amber-500/10 text-amber-600 group-hover:scale-110 transition-transform">
				<CalendarCheck class="w-6 h-6" />
			</div>
			<div>
				<h4 class="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-1.5">
					<span>Cuti & Perizinan</span>
					<ArrowUpRight class="w-4 h-4 text-slate-400 group-hover:text-amber-600 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
				</h4>
				<p class="text-xs text-slate-500 mt-1">
					Form pengajuan cuti tahunan, sakit dokter, dan alur persetujuan manajer
				</p>
			</div>
		</a>

		<a
			href="/company/reimbursements"
			class="p-5 rounded-3xl bg-white/80 dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/10 backdrop-blur-xl hover:border-purple-500/40 transition-all flex items-start gap-4 group"
		>
			<div class="p-3 rounded-2xl bg-purple-500/10 text-purple-600 group-hover:scale-110 transition-transform">
				<Receipt class="w-6 h-6" />
			</div>
			<div>
				<h4 class="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-1.5">
					<span>Klaim Reimbursement</span>
					<ArrowUpRight class="w-4 h-4 text-slate-400 group-hover:text-purple-600 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
				</h4>
				<p class="text-xs text-slate-500 mt-1">
					Klaim biaya operasional karyawan dan pencairan otomatis kas perusahaan
				</p>
			</div>
		</a>
	</div>
</div>
