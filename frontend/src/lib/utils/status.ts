import {
	DepartmentStatus,
	DesignationLevel,
	Gender,
	EmploymentType,
	EmployeeStatus,
	PayrollStatus,
	PayrollItemStatus,
	LeaveType,
	LeaveStatus,
	ReimbursementStatus,
	AttendanceStatus,
	AttendanceSource,
	OvertimeStatus,
	FingerprintDeviceStatus,
	FingerprintSyncStatus,
	DocumentTemplateType,
	DocumentStatus
} from '$lib/types/company';

export type StatusVariant = 'success' | 'warning' | 'error' | 'info' | 'neutral' | 'purple';

export interface StatusMeta {
	label: string;
	variant: StatusVariant;
	description: string;
	badgeClass: string;
	dotClass: string;
}

const VARIANT_CLASSES: Record<StatusVariant, { badge: string; dot: string }> = {
	success: {
		badge: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20',
		dot: 'bg-emerald-500'
	},
	warning: {
		badge: 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20',
		dot: 'bg-amber-500'
	},
	error: {
		badge: 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20',
		dot: 'bg-rose-500'
	},
	info: {
		badge: 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20',
		dot: 'bg-blue-500'
	},
	neutral: {
		badge: 'bg-slate-500/10 text-slate-600 dark:text-slate-400 border-slate-500/20',
		dot: 'bg-slate-400'
	},
	purple: {
		badge: 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20',
		dot: 'bg-purple-500'
	}
};

/**
 * Metadata status kepegawaian (EmployeeStatus)
 * 0->inactive, 1->active, 2->probation, 3->resigned, 4->terminated
 */
export function getEmployeeStatusInfo(status: number): StatusMeta {
	let label = 'Tidak Diketahui';
	let variant: StatusVariant = 'neutral';
	let description = 'Status tidak terdefinisi';

	switch (status) {
		case EmployeeStatus.ACTIVE:
			label = 'Aktif Bekerja';
			variant = 'success';
			description = 'Karyawan aktif dalam payroll dan operasional';
			break;
		case EmployeeStatus.PROBATION:
			label = 'Masa Percobaan';
			variant = 'warning';
			description = 'Karyawan dalam masa evaluasi kerja (probation)';
			break;
		case EmployeeStatus.INACTIVE:
			label = 'Non-Aktif';
			variant = 'neutral';
			description = 'Akun karyawan dinonaktifkan sementara';
			break;
		case EmployeeStatus.RESIGNED:
			label = 'Mengundurkan Diri';
			variant = 'info';
			description = 'Telah menyelesaikan masa kerja (resigned)';
			break;
		case EmployeeStatus.TERMINATED:
			label = 'Diberhentikan';
			variant = 'error';
			description = 'Hubungan kerja telah diakhiri (PHK/Terminasi)';
			break;
	}

	return {
		label,
		variant,
		description,
		badgeClass: VARIANT_CLASSES[variant].badge,
		dotClass: VARIANT_CLASSES[variant].dot
	};
}

/**
 * Metadata tipe ikatan kerja (EmploymentType)
 * 1->permanent, 2->contract, 3->intern, 4->freelance
 */
export function getEmploymentTypeInfo(type: number): { label: string; badgeClass: string } {
	switch (type) {
		case EmploymentType.PERMANENT:
			return { label: 'Tetap (PKWTT)', badgeClass: 'bg-blue-500/10 text-blue-600 border-blue-500/20' };
		case EmploymentType.CONTRACT:
			return { label: 'Kontrak (PKWT)', badgeClass: 'bg-amber-500/10 text-amber-600 border-amber-500/20' };
		case EmploymentType.INTERN:
			return { label: 'Magang', badgeClass: 'bg-purple-500/10 text-purple-600 border-purple-500/20' };
		case EmploymentType.FREELANCE:
			return { label: 'Lepas / Freelance', badgeClass: 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20' };
		default:
			return { label: 'Lainnya', badgeClass: 'bg-slate-500/10 text-slate-600 border-slate-500/20' };
	}
}

/**
 * Metadata status siklus payroll (PayrollStatus)
 * 0->draft, 1->calculated, 2->approved, 3->paid, 4->void
 */
export function getPayrollStatusInfo(status: number): StatusMeta {
	let label = 'Draf';
	let variant: StatusVariant = 'neutral';
	let description = 'Draf belum dihitung';

	switch (status) {
		case PayrollStatus.DRAFT:
			label = 'Draf';
			variant = 'neutral';
			description = 'Draf payroll baru dibuka';
			break;
		case PayrollStatus.CALCULATED:
			label = 'Terkalkulasi';
			variant = 'info';
			description = 'Gaji, tunjangan & BPJS telah selesai dihitung';
			break;
		case PayrollStatus.APPROVED:
			label = 'Disetujui';
			variant = 'warning';
			description = 'Disetujui oleh Direksi / Finance, siap ditransfer';
			break;
		case PayrollStatus.PAID:
			label = 'Sudah Dibayar';
			variant = 'success';
			description = 'Dana telah ditransfer dan terjurnal otomatis ke kas';
			break;
		case PayrollStatus.VOID:
			label = 'Dibatalkan';
			variant = 'error';
			description = 'Siklus payroll dibatalkan';
			break;
	}

	return {
		label,
		variant,
		description,
		badgeClass: VARIANT_CLASSES[variant].badge,
		dotClass: VARIANT_CLASSES[variant].dot
	};
}

/**
 * Metadata status cuti (LeaveStatus)
 * 0->pending, 1->approved, 2->rejected, 3->cancelled
 */
export function getLeaveStatusInfo(status: number): StatusMeta {
	let label = 'Menunggu';
	let variant: StatusVariant = 'warning';
	let description = 'Menunggu persetujuan atasan';

	switch (status) {
		case LeaveStatus.PENDING:
			label = 'Menunggu Review';
			variant = 'warning';
			description = 'Menunggu persetujuan manajer / HR';
			break;
		case LeaveStatus.APPROVED:
			label = 'Disetujui';
			variant = 'success';
			description = 'Pengajuan cuti telah disetujui';
			break;
		case LeaveStatus.REJECTED:
			label = 'Ditolak';
			variant = 'error';
			description = 'Pengajuan cuti ditolak';
			break;
		case LeaveStatus.CANCELLED:
			label = 'Dibatalkan';
			variant = 'neutral';
			description = 'Dibatalkan oleh pemohon';
			break;
	}

	return {
		label,
		variant,
		description,
		badgeClass: VARIANT_CLASSES[variant].badge,
		dotClass: VARIANT_CLASSES[variant].dot
	};
}

/**
 * Metadata jenis cuti (LeaveType)
 * 1->annual, 2->sick, 3->maternity, 4->unpaid, 5->special
 */
export function getLeaveTypeLabel(type: number): string {
	switch (type) {
		case LeaveType.ANNUAL:
			return 'Cuti Tahunan';
		case LeaveType.SICK:
			return 'Izin Sakit (Surat Dokter)';
		case LeaveType.MATERNITY:
			return 'Cuti Melahirkan / Ayah';
		case LeaveType.UNPAID:
			return 'Cuti di Luar Tanggungan';
		case LeaveType.SPECIAL:
			return 'Izin Khusus / Kedukaan / Pernikahan';
		default:
			return 'Izin Lainnya';
	}
}

/**
 * Metadata status reimbursement (ReimbursementStatus)
 * 0->draft, 1->submitted, 2->approved, 3->paid, 4->rejected
 */
export function getReimbursementStatusInfo(status: number): StatusMeta {
	let label = 'Draf';
	let variant: StatusVariant = 'neutral';
	let description = 'Draf klaim';

	switch (status) {
		case ReimbursementStatus.DRAFT:
			label = 'Draf';
			variant = 'neutral';
			description = 'Klaim belum diajukan';
			break;
		case ReimbursementStatus.SUBMITTED:
			label = 'Diajukan';
			variant = 'info';
			description = 'Menunggu verifikasi bukti transaksi';
			break;
		case ReimbursementStatus.APPROVED:
			label = 'Disetujui';
			variant = 'warning';
			description = 'Disetujui, menunggu pencairan dana kas';
			break;
		case ReimbursementStatus.PAID:
			label = 'Dicairkan';
			variant = 'success';
			description = 'Dana telah dicairkan & masuk ke pengeluaran';
			break;
		case ReimbursementStatus.REJECTED:
			label = 'Ditolak';
			variant = 'error';
			description = 'Klaim tidak memenuhi syarat';
			break;
	}

	return {
		label,
		variant,
		description,
		badgeClass: VARIANT_CLASSES[variant].badge,
		dotClass: VARIANT_CLASSES[variant].dot
	};
}

/**
 * Format nama level jabatan (DesignationLevel)
 * 1->staff, 2->senior, 3->lead, 4->manager, 5->director, 6->c_level
 */
export function getDesignationLevelLabel(level: number): string {
	switch (level) {
		case DesignationLevel.STAFF:
			return 'Staff';
		case DesignationLevel.SENIOR:
			return 'Senior Specialist';
		case DesignationLevel.LEAD:
			return 'Team Lead / Supervisor';
		case DesignationLevel.MANAGER:
			return 'Manager';
		case DesignationLevel.DIRECTOR:
			return 'Director';
		case DesignationLevel.C_LEVEL:
			return 'Executive / C-Level';
		default:
			return 'Staff';
	}
}

/**
 * Metadata status presensi kehadiran (AttendanceStatus)
 * 0->absent, 1->present, 2->late, 3->early_leave, 4->sick, 5->on_leave, 6->holiday
 */
export function getAttendanceStatusInfo(status: number): StatusMeta {
	let label = 'Hadir';
	let variant: StatusVariant = 'success';
	let description = 'Hadir tepat waktu';

	switch (status) {
		case AttendanceStatus.ABSENT:
			label = 'Alpa / Mangkir';
			variant = 'error';
			description = 'Tidak hadir tanpa keterangan sah';
			break;
		case AttendanceStatus.PRESENT:
			label = 'Hadir Tepat Waktu';
			variant = 'success';
			description = 'Check-in sesuai jadwal shift';
			break;
		case AttendanceStatus.LATE:
			label = 'Terlambat';
			variant = 'warning';
			description = 'Check-in melewati batas toleransi shift';
			break;
		case AttendanceStatus.EARLY_LEAVE:
			label = 'Pulang Cepat';
			variant = 'warning';
			description = 'Check-out sebelum jam kerja berakhir';
			break;
		case AttendanceStatus.SICK:
			label = 'Sakit';
			variant = 'info';
			description = 'Izin sakit dengan surat dokter';
			break;
		case AttendanceStatus.ON_LEAVE:
			label = 'Cuti';
			variant = 'purple';
			description = 'Sedang menjalankan cuti yang disetujui';
			break;
		case AttendanceStatus.HOLIDAY:
			label = 'Hari Libur';
			variant = 'neutral';
			description = 'Hari libur nasional / operasional pabrik tutup';
			break;
	}

	return {
		label,
		variant,
		description,
		badgeClass: VARIANT_CLASSES[variant].badge,
		dotClass: VARIANT_CLASSES[variant].dot
	};
}

/**
 * Label sumber absensi (AttendanceSource)
 * 1->fingerprint, 2->mobile_gps, 3->manual_hr, 4->telegram
 */
export function getAttendanceSourceLabel(source: number): string {
	switch (source) {
		case AttendanceSource.FINGERPRINT:
			return 'Mesin Fingerprint';
		case AttendanceSource.MOBILE_GPS:
			return 'Mobile GPS';
		case AttendanceSource.MANUAL_HR:
			return 'Koreksi Manual HR';
		case AttendanceSource.TELEGRAM:
			return 'Bot Telegram';
		default:
			return 'Sistem';
	}
}

/**
 * Metadata status perangkat fingerprint (FingerprintDeviceStatus)
 * 0->offline, 1->online, 2->error
 */
export function getFingerprintDeviceStatusInfo(status: number): StatusMeta {
	let label = 'Online';
	let variant: StatusVariant = 'success';
	let description = 'Terhubung ke jaringan internal';

	switch (status) {
		case FingerprintDeviceStatus.ONLINE:
			label = 'Online';
			variant = 'success';
			description = 'Mesin online & siap menerima tap';
			break;
		case FingerprintDeviceStatus.OFFLINE:
			label = 'Offline';
			variant = 'neutral';
			description = 'Mesin tidak terhubung ke jaringan';
			break;
		case FingerprintDeviceStatus.ERROR:
			label = 'Gangguan / Error';
			variant = 'error';
			description = 'Koneksi socket gagal atau memori mesin penuh';
			break;
	}

	return {
		label,
		variant,
		description,
		badgeClass: VARIANT_CLASSES[variant].badge,
		dotClass: VARIANT_CLASSES[variant].dot
	};
}

/**
 * Metadata status sinkronisasi log fingerprint (FingerprintSyncStatus)
 * 0->pending, 1->processed, 2->unmatched, 3->duplicate, 4->failed
 */
export function getFingerprintSyncStatusInfo(status: number): StatusMeta {
	let label = 'Diproses';
	let variant: StatusVariant = 'success';
	let description = 'Log berhasil diproses ke presensi';

	switch (status) {
		case FingerprintSyncStatus.PENDING:
			label = 'Menunggu';
			variant = 'info';
			description = 'Menunggu antrian kalkulasi attendance';
			break;
		case FingerprintSyncStatus.PROCESSED:
			label = 'Tersinkron';
			variant = 'success';
			description = 'Terekonsiliasi ke data kehadiran';
			break;
		case FingerprintSyncStatus.UNMATCHED:
			label = 'PIN Tidak Dikenal';
			variant = 'warning';
			description = 'Nomor PIN belum dipetakan ke data karyawan';
			break;
		case FingerprintSyncStatus.DUPLICATE:
			label = 'Double Tap';
			variant = 'neutral';
			description = 'Tap berulang dalam rentang waktu singkat diabaikan';
			break;
		case FingerprintSyncStatus.FAILED:
			label = 'Gagal';
			variant = 'error';
			description = 'Terjadi galat pemrosesan log';
			break;
	}

	return {
		label,
		variant,
		description,
		badgeClass: VARIANT_CLASSES[variant].badge,
		dotClass: VARIANT_CLASSES[variant].dot
	};
}

/**
 * Label tipe template dokumen HR (DocumentTemplateType)
 * 1->kontrak_pkwt, 2->sk_pengangkatan, 3->surat_peringatan, 4->surat_tugas, 5->surat_paklaring, 6->surat_mutasi
 */
export function getDocumentTemplateTypeLabel(type: number): string {
	switch (type) {
		case DocumentTemplateType.KONTRAK_PKWT:
			return 'Kontrak Kerja (PKWT)';
		case DocumentTemplateType.SK_PENGANGKATAN:
			return 'SK Pengangkatan Karyawan';
		case DocumentTemplateType.SURAT_PERINGATAN:
			return 'Surat Peringatan (SP)';
		case DocumentTemplateType.SURAT_TUGAS:
			return 'Surat Tugas / Dinas';
		case DocumentTemplateType.SURAT_PAKLARING:
			return 'Surat Pengalaman Kerja (Paklaring)';
		case DocumentTemplateType.SURAT_MUTASI:
			return 'Surat Mutasi / Promosi';
		default:
			return 'Dokumen Resmi';
	}
}

/**
 * Metadata status dokumen karyawan (DocumentStatus)
 * 0->draft, 1->generated, 2->signed, 3->archived
 */
export function getDocumentStatusInfo(status: number): StatusMeta {
	let label = 'Diterbitkan';
	let variant: StatusVariant = 'info';
	let description = 'Dokumen siap ditandatangani';

	switch (status) {
		case DocumentStatus.DRAFT:
			label = 'Draf';
			variant = 'neutral';
			description = 'Draf surat dalam penyusunan';
			break;
		case DocumentStatus.GENERATED:
			label = 'Diterbitkan';
			variant = 'info';
			description = 'Dokumen resmi terbit & terarsip';
			break;
		case DocumentStatus.SIGNED:
			label = 'Ditandatangani';
			variant = 'success';
			description = 'Ditandatangani kedua belah pihak';
			break;
		case DocumentStatus.ARCHIVED:
			label = 'Diarsipkan';
			variant = 'neutral';
			description = 'Masa berlaku selesai / arsip statis';
			break;
	}

	return {
		label,
		variant,
		description,
		badgeClass: VARIANT_CLASSES[variant].badge,
		dotClass: VARIANT_CLASSES[variant].dot
	};
}

/**
 * Metadata status pengajuan lembur (OvertimeStatus)
 * 0->pending, 1->approved, 2->rejected
 */
export function getOvertimeStatusInfo(status: number): StatusMeta {
	let label = 'Menunggu';
	let variant: StatusVariant = 'warning';
	let description = 'Menunggu persetujuan atasan';

	switch (status) {
		case OvertimeStatus.PENDING:
			label = 'Menunggu';
			variant = 'warning';
			description = 'Menunggu verifikasi supervisor';
			break;
		case OvertimeStatus.APPROVED:
			label = 'Disetujui';
			variant = 'success';
			description = 'Lembur disetujui & masuk kalkulasi payroll';
			break;
		case OvertimeStatus.REJECTED:
			label = 'Ditolak';
			variant = 'error';
			description = 'Pengajuan lembur tidak disetujui';
			break;
	}

	return {
		label,
		variant,
		description,
		badgeClass: VARIANT_CLASSES[variant].badge,
		dotClass: VARIANT_CLASSES[variant].dot
	};
}

