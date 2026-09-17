/**
 * Tipe data TypeScript & Enum angka untuk modul Perusahaan (HR & Payroll)
 */

export const DepartmentStatus = {
	INACTIVE: 0,
	ACTIVE: 1
} as const;
export type DepartmentStatus = (typeof DepartmentStatus)[keyof typeof DepartmentStatus];

export const DesignationLevel = {
	STAFF: 1,
	SENIOR: 2,
	LEAD: 3,
	MANAGER: 4,
	DIRECTOR: 5,
	C_LEVEL: 6
} as const;
export type DesignationLevel = (typeof DesignationLevel)[keyof typeof DesignationLevel];

export const Gender = {
	UNSPECIFIED: 0,
	MALE: 1,
	FEMALE: 2
} as const;
export type Gender = (typeof Gender)[keyof typeof Gender];

export const EmploymentType = {
	PERMANENT: 1,
	CONTRACT: 2,
	INTERN: 3,
	FREELANCE: 4
} as const;
export type EmploymentType = (typeof EmploymentType)[keyof typeof EmploymentType];

export const EmployeeStatus = {
	INACTIVE: 0,
	ACTIVE: 1,
	PROBATION: 2,
	RESIGNED: 3,
	TERMINATED: 4
} as const;
export type EmployeeStatus = (typeof EmployeeStatus)[keyof typeof EmployeeStatus];

export const PayrollStatus = {
	DRAFT: 0,
	CALCULATED: 1,
	APPROVED: 2,
	PAID: 3,
	VOID: 4
} as const;
export type PayrollStatus = (typeof PayrollStatus)[keyof typeof PayrollStatus];

export const PayrollItemStatus = {
	UNPAID: 0,
	PAID: 1
} as const;
export type PayrollItemStatus = (typeof PayrollItemStatus)[keyof typeof PayrollItemStatus];

export const LeaveType = {
	ANNUAL: 1,
	SICK: 2,
	MATERNITY: 3,
	UNPAID: 4,
	SPECIAL: 5
} as const;
export type LeaveType = (typeof LeaveType)[keyof typeof LeaveType];

export const LeaveStatus = {
	PENDING: 0,
	APPROVED: 1,
	REJECTED: 2,
	CANCELLED: 3
} as const;
export type LeaveStatus = (typeof LeaveStatus)[keyof typeof LeaveStatus];

export const ReimbursementStatus = {
	DRAFT: 0,
	SUBMITTED: 1,
	APPROVED: 2,
	PAID: 3,
	REJECTED: 4
} as const;
export type ReimbursementStatus = (typeof ReimbursementStatus)[keyof typeof ReimbursementStatus];

export interface Department {
	id: string;
	tenant_id: string;
	code: string;
	name: string;
	description?: string | null;
	status: DepartmentStatus;
	created_at?: string;
}

export interface Designation {
	id: string;
	tenant_id: string;
	department_id: string;
	title: string;
	level: DesignationLevel;
	created_at?: string;
}

export interface Employee {
	id: string;
	tenant_id: string;
	nik: string;
	full_name: string;
	email?: string | null;
	phone?: string | null;
	gender: Gender;
	department_id?: string | null;
	department_name?: string | null;
	designation_id?: string | null;
	designation_title?: string | null;
	employment_type: EmploymentType;
	status: EmployeeStatus;
	join_date: string;
	basic_salary: number;
	bank_name?: string | null;
	bank_account_number?: string | null;
	bank_account_holder?: string | null;
	npwp?: string | null;
	bpjs_tk_number?: string | null;
	bpjs_kes_number?: string | null;
	created_at?: string;
}

export interface PayrollRun {
	id: string;
	tenant_id: string;
	period_month: number;
	period_year: number;
	title: string;
	total_gross: number;
	total_deductions: number;
	total_net: number;
	status: PayrollStatus;
	paid_at?: string | null;
	payment_account_id?: string | null;
	notes?: string | null;
	items_count?: number;
}

export interface PayrollItem {
	id: string;
	payroll_run_id: string;
	employee_id: string;
	employee_name?: string;
	employee_nik?: string;
	employee_dept?: string;
	employee_bank?: string;
	employee_account?: string;
	basic_salary: number;
	allowances: number;
	overtime: number;
	deductions: number;
	bpjs_tk_employee: number;
	bpjs_tk_company: number;
	bpjs_kes_employee: number;
	bpjs_kes_company: number;
	pph21: number;
	gross_salary: number;
	net_salary: number;
	status: PayrollItemStatus;
}

export interface LeaveRequest {
	id: string;
	tenant_id: string;
	employee_id: string;
	employee_name?: string;
	employee_nik?: string;
	leave_type: LeaveType;
	start_date: string;
	end_date: string;
	total_days: number;
	reason?: string | null;
	status: LeaveStatus;
	rejection_reason?: string | null;
}

export interface Reimbursement {
	id: string;
	tenant_id: string;
	employee_id: string;
	employee_name?: string;
	employee_nik?: string;
	title: string;
	description?: string | null;
	amount: number;
	receipt_url?: string | null;
	status: ReimbursementStatus;
	paid_at?: string | null;
}

export const ShiftStatus = {
	INACTIVE: 0,
	ACTIVE: 1
} as const;
export type ShiftStatus = (typeof ShiftStatus)[keyof typeof ShiftStatus];

export const AttendanceStatus = {
	ABSENT: 0,
	PRESENT: 1,
	LATE: 2,
	EARLY_LEAVE: 3,
	SICK: 4,
	ON_LEAVE: 5,
	HOLIDAY: 6
} as const;
export type AttendanceStatus = (typeof AttendanceStatus)[keyof typeof AttendanceStatus];

export const AttendanceSource = {
	FINGERPRINT: 1,
	MOBILE_GPS: 2,
	MANUAL_HR: 3,
	TELEGRAM: 4
} as const;
export type AttendanceSource = (typeof AttendanceSource)[keyof typeof AttendanceSource];

export const OvertimeStatus = {
	PENDING: 0,
	APPROVED: 1,
	REJECTED: 2
} as const;
export type OvertimeStatus = (typeof OvertimeStatus)[keyof typeof OvertimeStatus];

export const FingerprintDeviceStatus = {
	OFFLINE: 0,
	ONLINE: 1,
	ERROR: 2
} as const;
export type FingerprintDeviceStatus = (typeof FingerprintDeviceStatus)[keyof typeof FingerprintDeviceStatus];

export const FingerprintSyncStatus = {
	PENDING: 0,
	PROCESSED: 1,
	UNMATCHED: 2,
	DUPLICATE: 3,
	FAILED: 4
} as const;
export type FingerprintSyncStatus = (typeof FingerprintSyncStatus)[keyof typeof FingerprintSyncStatus];

export const DocumentTemplateType = {
	KONTRAK_PKWT: 1,
	SK_PENGANGKATAN: 2,
	SURAT_PERINGATAN: 3,
	SURAT_TUGAS: 4,
	SURAT_PAKLARING: 5,
	SURAT_MUTASI: 6
} as const;
export type DocumentTemplateType = (typeof DocumentTemplateType)[keyof typeof DocumentTemplateType];

export const DocumentStatus = {
	DRAFT: 0,
	GENERATED: 1,
	SIGNED: 2,
	ARCHIVED: 3
} as const;
export type DocumentStatus = (typeof DocumentStatus)[keyof typeof DocumentStatus];

export interface Shift {
	id: string;
	tenant_id: string;
	name: string;
	code: string;
	start_time: string;
	end_time: string;
	is_cross_day: boolean;
	late_tolerance_minutes: number;
	color_code: string;
	status: ShiftStatus;
	created_at?: string;
}

export interface AttendanceRecord {
	id: string;
	tenant_id: string;
	employee_id: string;
	employee_name?: string;
	employee_nik?: string;
	department_name?: string;
	shift_id?: string | null;
	shift_name?: string;
	shift_code?: string;
	date: string;
	check_in_time?: string | null;
	check_out_time?: string | null;
	status: AttendanceStatus;
	work_duration_minutes: number;
	late_minutes: number;
	early_leave_minutes: number;
	overtime_minutes: number;
	source: AttendanceSource;
	correction_notes?: string | null;
	corrected_by?: string | null;
	corrected_by_name?: string | null;
}

export interface OvertimeRequest {
	id: string;
	tenant_id: string;
	employee_id: string;
	employee_name?: string;
	employee_nik?: string;
	date: string;
	start_time: string;
	end_time: string;
	duration_minutes: number;
	reason: string;
	status: OvertimeStatus;
	approved_by?: string | null;
}

export interface FingerprintDevice {
	id: string;
	tenant_id: string;
	device_name: string;
	device_sn: string;
	brand: string;
	ip_address: string;
	port: number;
	location: string;
	status: FingerprintDeviceStatus;
	last_sync_at?: string | null;
}

export interface FingerprintRawLog {
	id: string;
	tenant_id: string;
	device_id: string;
	device_name?: string;
	device_user_id: string;
	timestamp: string;
	verify_mode: number;
	sync_status: FingerprintSyncStatus;
	matched_employee_id?: string | null;
	matched_employee_name?: string | null;
	processed_attendance_id?: string | null;
	error_message?: string | null;
	created_at: string;
}

export interface FingerprintEmployeeMapping {
	id: string;
	tenant_id: string;
	device_user_id: string;
	employee_id: string;
	employee_name?: string;
	employee_nik?: string;
}

export interface DocumentTemplate {
	id: string;
	tenant_id: string;
	title: string;
	type: DocumentTemplateType;
	template_body: string;
	is_active: boolean;
	created_at?: string;
}

export interface EmployeeDocument {
	id: string;
	tenant_id: string;
	employee_id: string;
	employee_name?: string;
	employee_nik?: string;
	template_id?: string | null;
	letter_number: string;
	title: string;
	content: string;
	status: DocumentStatus;
	issued_date: string;
	file_url?: string | null;
	created_at?: string;
}

