from enum import IntEnum


class TenantTypeEnum(IntEnum):
    """
    Tipe organisasi / tenant pada sistem.
    0: PERSONAL (Pengguna individu)
    1: FAMILY   (Keluarga / pasangan)
    2: BUSINESS (Perusahaan / bisnis / UMKM)
    """
    PERSONAL = 0
    FAMILY = 1
    BUSINESS = 2


class DepartmentStatusEnum(IntEnum):
    """
    Status operasional departemen.
    0: INACTIVE
    1: ACTIVE
    """
    INACTIVE = 0
    ACTIVE = 1


class DesignationLevelEnum(IntEnum):
    """
    Tingkat hierarki jabatan dalam organisasi.
    1: STAFF
    2: SENIOR
    3: LEAD / SUPERVISOR
    4: MANAGER
    5: DIRECTOR
    6: C_LEVEL / EXECUTIVE
    """
    STAFF = 1
    SENIOR = 2
    LEAD = 3
    MANAGER = 4
    DIRECTOR = 5
    C_LEVEL = 6


class GenderEnum(IntEnum):
    """
    Jenis kelamin karyawan.
    0: UNSPECIFIED
    1: MALE
    2: FEMALE
    """
    UNSPECIFIED = 0
    MALE = 1
    FEMALE = 2


class EmploymentTypeEnum(IntEnum):
    """
    Tipe ikatan kerja karyawan.
    1: PERMANENT (Karyawan Tetap / PKWTT)
    2: CONTRACT  (Karyawan Kontrak / PKWT)
    3: INTERN    (Magang)
    4: FREELANCE (Lepas / Paruh Waktu)
    """
    PERMANENT = 1
    CONTRACT = 2
    INTERN = 3
    FREELANCE = 4


class EmployeeStatusEnum(IntEnum):
    """
    Status kepegawaian saat ini.
    0: INACTIVE   (Non-aktif)
    1: ACTIVE     (Aktif bekerja)
    2: PROBATION  (Masa percobaan)
    3: RESIGNED   (Mengundurkan diri)
    4: TERMINATED (Diberhentikan)
    """
    INACTIVE = 0
    ACTIVE = 1
    PROBATION = 2
    RESIGNED = 3
    TERMINATED = 4


class PayrollStatusEnum(IntEnum):
    """
    Status pemrosesan siklus penggajian bulanan.
    0: DRAFT      (Draf / belum diproses)
    1: CALCULATED (Terkalkulasi / siap di-review)
    2: APPROVED   (Disetujui manajemen)
    3: PAID       (Telah dibayarkan & terjurnal)
    4: VOID       (Dibatalkan)
    """
    DRAFT = 0
    CALCULATED = 1
    APPROVED = 2
    PAID = 3
    VOID = 4


class PayrollItemStatusEnum(IntEnum):
    """
    Status pembayaran per slip gaji karyawan.
    0: UNPAID (Belum ditransfer)
    1: PAID   (Telah ditransfer)
    """
    UNPAID = 0
    PAID = 1


class LeaveTypeEnum(IntEnum):
    """
    Jenis pengajuan cuti atau izin.
    1: ANNUAL    (Cuti tahunan)
    2: SICK      (Izin sakit)
    3: MATERNITY (Cuti melahirkan / paternity)
    4: UNPAID    (Cuti di luar tanggungan)
    5: SPECIAL   (Izin khusus / kedukaan / pernikahan)
    """
    ANNUAL = 1
    SICK = 2
    MATERNITY = 3
    UNPAID = 4
    SPECIAL = 5


class LeaveStatusEnum(IntEnum):
    """
    Status persetujuan pengajuan cuti.
    0: PENDING   (Menunggu persetujuan)
    1: APPROVED  (Disetujui)
    2: REJECTED  (Ditolak)
    3: CANCELLED (Dibatalkan pemohon)
    """
    PENDING = 0
    APPROVED = 1
    REJECTED = 2
    CANCELLED = 3


class ReimbursementStatusEnum(IntEnum):
    """
    Status klaim pengeluaran operasional (reimbursement).
    0: DRAFT     (Draf klaim)
    1: SUBMITTED (Diajukan)
    2: APPROVED  (Disetujui manajer/finance)
    3: PAID      (Telah dicairkan & terjurnal)
    4: REJECTED  (Ditolak)
    """
    DRAFT = 0
    SUBMITTED = 1
    APPROVED = 2
    PAID = 3
    REJECTED = 4


class ShiftStatusEnum(IntEnum):
    """
    Status operasional shift kerja.
    0: INACTIVE
    1: ACTIVE
    """
    INACTIVE = 0
    ACTIVE = 1


class AttendanceStatusEnum(IntEnum):
    """
    Status kehadiran harian karyawan.
    0: ABSENT      (Mangkir / Tanpa Keterangan / Alpha)
    1: PRESENT     (Hadir tepat waktu)
    2: LATE        (Hadir terlambat)
    3: EARLY_LEAVE (Pulang lebih awal)
    4: SICK        (Izin sakit)
    5: ON_LEAVE    (Sedang cuti resmi)
    6: HOLIDAY     (Hari libur / off day)
    """
    ABSENT = 0
    PRESENT = 1
    LATE = 2
    EARLY_LEAVE = 3
    SICK = 4
    ON_LEAVE = 5
    HOLIDAY = 6


class AttendanceSourceEnum(IntEnum):
    """
    Metode / sumber data presensi masuk.
    1: FINGERPRINT (Mesin biometrik fingerprint)
    2: MOBILE_GPS  (Presensi mobile dengan lokasi GPS)
    3: MANUAL_HR   (Koreksi manual oleh HR/Admin)
    4: TELEGRAM    (Presensi bot Telegram)
    """
    FINGERPRINT = 1
    MOBILE_GPS = 2
    MANUAL_HR = 3
    TELEGRAM = 4


class OvertimeStatusEnum(IntEnum):
    """
    Status persetujuan pengajuan lembur (overtime).
    0: PENDING   (Menunggu persetujuan supervisor)
    1: APPROVED  (Disetujui lembur)
    2: REJECTED  (Ditolak)
    """
    PENDING = 0
    APPROVED = 1
    REJECTED = 2


class FingerprintDeviceStatusEnum(IntEnum):
    """
    Status koneksi perangkat mesin fingerprint fisik.
    0: OFFLINE (Terputus / offline)
    1: ONLINE  (Terhubung & aktif)
    2: ERROR   (Mengalami kendala sinkronisasi)
    """
    OFFLINE = 0
    ONLINE = 1
    ERROR = 2


class FingerprintSyncStatusEnum(IntEnum):
    """
    Status pemrosesan log data mentah dari mesin fingerprint.
    0: PENDING            (Menunggu pemrosesan)
    1: PROCESSED          (Berhasil dicatat ke kehadiran)
    2: UNMATCHED_EMPLOYEE (PIN tidak terdaftar pada karyawan)
    3: DUPLICATE          (Duplikat / double-tap dalam interval singkat)
    4: FAILED             (Gagal diproses)
    """
    PENDING = 0
    PROCESSED = 1
    UNMATCHED_EMPLOYEE = 2
    DUPLICATE = 3
    FAILED = 4


class DocumentTemplateTypeEnum(IntEnum):
    """
    Kategori template dokumen & surat resmi kepegawaian.
    1: KONTRAK_PKWT    (Perjanjian Kerja Waktu Tertentu)
    2: SK_PENGANGKATAN (Surat Keputusan Pengangkatan Karyawan Tetap)
    3: SURAT_PERINGATAN (Surat Peringatan SP-1, SP-2, SP-3)
    4: SURAT_TUGAS     (Surat Perjalanan Dinas / Tugas)
    5: SURAT_PAKLARING (Surat Keterangan Pengalaman Kerja)
    6: SURAT_MUTASI    (Surat Mutasi / Promosi Jabatan)
    """
    KONTRAK_PKWT = 1
    SK_PENGANGKATAN = 2
    SURAT_PERINGATAN = 3
    SURAT_TUGAS = 4
    SURAT_PAKLARING = 5
    SURAT_MUTASI = 6


class DocumentStatusEnum(IntEnum):
    """
    Status penerbitan dokumen kepegawaian.
    0: DRAFT     (Draf surat)
    1: GENERATED (Dokumen telah dibuat)
    2: SIGNED    (Telah ditandatangani HR & Karyawan)
    3: ARCHIVED  (Diarsipkan)
    """
    DRAFT = 0
    GENERATED = 1
    SIGNED = 2
    ARCHIVED = 3
