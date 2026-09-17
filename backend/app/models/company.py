import uuid
from datetime import datetime, date, time
from decimal import Decimal
from typing import List, Optional, Any
from sqlalchemy import (
    String, Integer, SmallInteger, DateTime, Date, Time, Boolean, Text, Numeric,
    ForeignKey, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin
from app.models.enums import (
    DepartmentStatusEnum,
    DesignationLevelEnum,
    GenderEnum,
    EmploymentTypeEnum,
    EmployeeStatusEnum,
    PayrollStatusEnum,
    PayrollItemStatusEnum,
    LeaveTypeEnum,
    LeaveStatusEnum,
    ReimbursementStatusEnum,
    ShiftStatusEnum,
    AttendanceStatusEnum,
    AttendanceSourceEnum,
    OvertimeStatusEnum,
    FingerprintDeviceStatusEnum,
    FingerprintSyncStatusEnum,
    DocumentTemplateTypeEnum,
    DocumentStatusEnum,
)


class Department(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Departemen / Divisi dalam perusahaan."""
    __tablename__ = "departments"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[int] = mapped_column(
        SmallInteger,
        default=DepartmentStatusEnum.ACTIVE,
        nullable=False,
        comment="0->inactive, 1->active"
    )

    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_departments_tenant_code"),
        CheckConstraint("status IN (0, 1)", name="chk_departments_status"),
        Index("idx_departments_tenant_status", "tenant_id", "status"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="departments")
    designations: Mapped[List["Designation"]] = relationship("Designation", back_populates="department", cascade="all, delete-orphan")
    employees: Mapped[List["Employee"]] = relationship("Employee", back_populates="department")


class Designation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Jabatan / Posisi dalam departemen."""
    __tablename__ = "designations"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    level: Mapped[int] = mapped_column(
        SmallInteger,
        default=DesignationLevelEnum.STAFF,
        nullable=False,
        comment="1->staff, 2->senior, 3->lead, 4->manager, 5->director, 6->c_level"
    )

    __table_args__ = (
        CheckConstraint("level BETWEEN 1 AND 6", name="chk_designations_level"),
        Index("idx_designations_tenant_dept", "tenant_id", "department_id"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant")
    department: Mapped["Department"] = relationship("Department", back_populates="designations")
    employees: Mapped[List["Employee"]] = relationship("Employee", back_populates="designation")


class Employee(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Data induk karyawan perusahaan."""
    __tablename__ = "employees"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    designation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("designations.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    nik: Mapped[str] = mapped_column(String(50), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    gender: Mapped[int] = mapped_column(
        SmallInteger,
        default=GenderEnum.UNSPECIFIED,
        nullable=False,
        comment="0->unspecified, 1->male, 2->female"
    )
    employment_type: Mapped[int] = mapped_column(
        SmallInteger,
        default=EmploymentTypeEnum.PERMANENT,
        nullable=False,
        comment="1->permanent, 2->contract, 3->intern, 4->freelance"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger,
        default=EmployeeStatusEnum.ACTIVE,
        nullable=False,
        comment="0->inactive, 1->active, 2->probation, 3->resigned, 4->terminated"
    )

    join_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Informasi Finansial & Pajak
    basic_salary: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    bank_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    bank_account_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    bank_account_holder: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    npwp: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    bpjs_tk_number: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    bpjs_kes_number: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, default=dict, nullable=True)

    __table_args__ = (
        UniqueConstraint("tenant_id", "nik", name="uq_employees_tenant_nik"),
        CheckConstraint("gender IN (0, 1, 2)", name="chk_employees_gender"),
        CheckConstraint("employment_type IN (1, 2, 3, 4)", name="chk_employees_employment_type"),
        CheckConstraint("status IN (0, 1, 2, 3, 4)", name="chk_employees_status"),
        CheckConstraint("basic_salary >= 0", name="chk_employees_basic_salary"),
        Index("idx_employees_tenant_status", "tenant_id", "status"),
        Index("idx_employees_tenant_dept", "tenant_id", "department_id"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="employees")
    user: Mapped[Optional["User"]] = relationship("User")
    department: Mapped[Optional["Department"]] = relationship("Department", back_populates="employees")
    designation: Mapped[Optional["Designation"]] = relationship("Designation", back_populates="employees")
    payroll_items: Mapped[List["PayrollItem"]] = relationship("PayrollItem", back_populates="employee")
    leave_requests: Mapped[List["LeaveRequest"]] = relationship("LeaveRequest", back_populates="employee")
    reimbursements: Mapped[List["Reimbursement"]] = relationship("Reimbursement", back_populates="employee")
    attendance_records: Mapped[List["AttendanceRecord"]] = relationship("AttendanceRecord", back_populates="employee")
    overtime_requests: Mapped[List["OvertimeRequest"]] = relationship("OvertimeRequest", back_populates="employee")
    documents: Mapped[List["EmployeeDocument"]] = relationship("EmployeeDocument", back_populates="employee")


class PayrollRun(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Batch siklus penggajian bulanan perusahaan."""
    __tablename__ = "payroll_runs"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    period_month: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="Bulan periode (1-12)")
    period_year: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="Tahun periode (misal 2026)")
    title: Mapped[str] = mapped_column(String(100), nullable=False)

    total_gross: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    total_deductions: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    total_net: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)

    status: Mapped[int] = mapped_column(
        SmallInteger,
        default=PayrollStatusEnum.DRAFT,
        nullable=False,
        comment="0->draft, 1->calculated, 2->approved, 3->paid, 4->void"
    )

    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relasi opsional ke akun kas/bank dan transaksi pembukuan otomatis
    payment_account_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="SET NULL"),
        nullable=True
    )
    transaction_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transactions.id", ondelete="SET NULL"),
        nullable=True
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("tenant_id", "period_year", "period_month", name="uq_payroll_runs_period"),
        CheckConstraint("period_month BETWEEN 1 AND 12", name="chk_payroll_runs_month"),
        CheckConstraint("period_year >= 2000", name="chk_payroll_runs_year"),
        CheckConstraint("status IN (0, 1, 2, 3, 4)", name="chk_payroll_runs_status"),
        CheckConstraint("total_gross >= 0 AND total_deductions >= 0 AND total_net >= 0", name="chk_payroll_runs_amounts"),
        Index("idx_payroll_runs_tenant_period", "tenant_id", "period_year", "period_month"),
        Index("idx_payroll_runs_status", "status"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="payroll_runs")
    payment_account: Mapped[Optional["Account"]] = relationship("Account")
    transaction: Mapped[Optional["Transaction"]] = relationship("Transaction")
    items: Mapped[List["PayrollItem"]] = relationship("PayrollItem", back_populates="payroll_run", cascade="all, delete-orphan")


class PayrollItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Rincian slip gaji individual karyawan untuk suatu periode payroll."""
    __tablename__ = "payroll_items"

    payroll_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payroll_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    basic_salary: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    allowances: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    overtime: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    deductions: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)

    # Regulasi Ketenagakerjaan Indonesia (BPJS & Pajak)
    bpjs_tk_employee: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    bpjs_tk_company: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    bpjs_kes_employee: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    bpjs_kes_company: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    pph21: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)

    gross_salary: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    net_salary: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)

    status: Mapped[int] = mapped_column(
        SmallInteger,
        default=PayrollItemStatusEnum.UNPAID,
        nullable=False,
        comment="0->unpaid, 1->paid"
    )

    details_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, default=dict, nullable=True)

    __table_args__ = (
        UniqueConstraint("payroll_run_id", "employee_id", name="uq_payroll_items_run_employee"),
        CheckConstraint("status IN (0, 1)", name="chk_payroll_items_status"),
        CheckConstraint("net_salary >= 0", name="chk_payroll_items_net"),
        Index("idx_payroll_items_employee", "employee_id"),
    )

    payroll_run: Mapped["PayrollRun"] = relationship("PayrollRun", back_populates="items")
    employee: Mapped["Employee"] = relationship("Employee", back_populates="payroll_items")


class LeaveRequest(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Pengajuan izin dan cuti karyawan."""
    __tablename__ = "leave_requests"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    leave_type: Mapped[int] = mapped_column(
        SmallInteger,
        default=LeaveTypeEnum.ANNUAL,
        nullable=False,
        comment="1->annual, 2->sick, 3->maternity, 4->unpaid, 5->special"
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_days: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    status: Mapped[int] = mapped_column(
        SmallInteger,
        default=LeaveStatusEnum.PENDING,
        nullable=False,
        comment="0->pending, 1->approved, 2->rejected, 3->cancelled"
    )
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint("leave_type BETWEEN 1 AND 5", name="chk_leave_requests_type"),
        CheckConstraint("status IN (0, 1, 2, 3)", name="chk_leave_requests_status"),
        CheckConstraint("end_date >= start_date", name="chk_leave_requests_dates"),
        CheckConstraint("total_days > 0", name="chk_leave_requests_days"),
        Index("idx_leave_requests_tenant_status", "tenant_id", "status"),
        Index("idx_leave_requests_employee", "employee_id"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="leave_requests")
    employee: Mapped["Employee"] = relationship("Employee", back_populates="leave_requests")
    approver: Mapped[Optional["User"]] = relationship("User")


class Reimbursement(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Pengajuan klaim pengeluaran operasional karyawan."""
    __tablename__ = "reimbursements"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True
    )

    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    receipt_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    status: Mapped[int] = mapped_column(
        SmallInteger,
        default=ReimbursementStatusEnum.SUBMITTED,
        nullable=False,
        comment="0->draft, 1->submitted, 2->approved, 3->paid, 4->rejected"
    )

    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    transaction_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transactions.id", ondelete="SET NULL"),
        nullable=True
    )

    __table_args__ = (
        CheckConstraint("status IN (0, 1, 2, 3, 4)", name="chk_reimbursements_status"),
        CheckConstraint("amount > 0", name="chk_reimbursements_amount"),
        Index("idx_reimbursements_tenant_status", "tenant_id", "status"),
        Index("idx_reimbursements_employee", "employee_id"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="reimbursements")
    employee: Mapped["Employee"] = relationship("Employee", back_populates="reimbursements")
    category: Mapped[Optional["Category"]] = relationship("Category")
    approver: Mapped[Optional["User"]] = relationship("User")
    transaction: Mapped[Optional["Transaction"]] = relationship("Transaction")


class Shift(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Jadwal shift kerja operasional pabrik / gudang."""
    __tablename__ = "shifts"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_cross_day: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    late_tolerance_minutes: Mapped[int] = mapped_column(SmallInteger, default=15, nullable=False)
    color_code: Mapped[str] = mapped_column(String(20), default="#007AFF", nullable=False)
    status: Mapped[int] = mapped_column(
        SmallInteger,
        default=ShiftStatusEnum.ACTIVE,
        nullable=False,
        comment="0->inactive, 1->active"
    )

    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_shifts_tenant_code"),
        CheckConstraint("status IN (0, 1)", name="chk_shifts_status"),
        Index("idx_shifts_tenant_status", "tenant_id", "status"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="shifts")
    attendance_records: Mapped[List["AttendanceRecord"]] = relationship("AttendanceRecord", back_populates="shift")


class AttendanceRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Presensi harian karyawan (terintegrasi fingerprint, mobile, atau manual)."""
    __tablename__ = "attendance_records"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    shift_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shifts.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    check_in_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    check_out_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    status: Mapped[int] = mapped_column(
        SmallInteger,
        default=AttendanceStatusEnum.PRESENT,
        nullable=False,
        comment="0->absent, 1->present, 2->late, 3->early_leave, 4->sick, 5->on_leave, 6->holiday"
    )

    work_duration_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    late_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    early_leave_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    overtime_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    source: Mapped[int] = mapped_column(
        SmallInteger,
        default=AttendanceSourceEnum.FINGERPRINT,
        nullable=False,
        comment="1->fingerprint, 2->mobile_gps, 3->manual_hr, 4->telegram"
    )

    correction_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    corrected_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    __table_args__ = (
        UniqueConstraint("tenant_id", "employee_id", "date", name="uq_attendance_tenant_emp_date"),
        CheckConstraint("status BETWEEN 0 AND 6", name="chk_attendance_status"),
        CheckConstraint("source BETWEEN 1 AND 4", name="chk_attendance_source"),
        CheckConstraint("work_duration_minutes >= 0 AND late_minutes >= 0 AND overtime_minutes >= 0", name="chk_attendance_durations"),
        Index("idx_attendance_tenant_date_status", "tenant_id", "date", "status"),
        Index("idx_attendance_emp_date", "employee_id", "date"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="attendance_records")
    employee: Mapped["Employee"] = relationship("Employee", back_populates="attendance_records")
    shift: Mapped[Optional["Shift"]] = relationship("Shift", back_populates="attendance_records")
    corrector: Mapped[Optional["User"]] = relationship("User")


class OvertimeRequest(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Pengajuan dan rekonsiliasi lembur kerja karyawan."""
    __tablename__ = "overtime_requests"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[int] = mapped_column(
        SmallInteger,
        default=OvertimeStatusEnum.PENDING,
        nullable=False,
        comment="0->pending, 1->approved, 2->rejected"
    )
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    __table_args__ = (
        CheckConstraint("status IN (0, 1, 2)", name="chk_overtime_status"),
        CheckConstraint("duration_minutes > 0", name="chk_overtime_duration"),
        Index("idx_overtime_tenant_status", "tenant_id", "status"),
        Index("idx_overtime_employee_date", "employee_id", "date"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="overtime_requests")
    employee: Mapped["Employee"] = relationship("Employee", back_populates="overtime_requests")
    approver: Mapped[Optional["User"]] = relationship("User")


class FingerprintDevice(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Data registrasi perangkat mesin fingerprint fisik pada pabrik / kantor."""
    __tablename__ = "fingerprint_devices"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    device_name: Mapped[str] = mapped_column(String(100), nullable=False)
    device_sn: Mapped[str] = mapped_column(String(100), nullable=False)
    brand: Mapped[str] = mapped_column(String(50), default="ZKTeco", nullable=False)
    ip_address: Mapped[str] = mapped_column(String(50), nullable=False)
    port: Mapped[int] = mapped_column(Integer, default=4370, nullable=False)
    location: Mapped[str] = mapped_column(String(150), nullable=False)

    status: Mapped[int] = mapped_column(
        SmallInteger,
        default=FingerprintDeviceStatusEnum.ONLINE,
        nullable=False,
        comment="0->offline, 1->online, 2->error"
    )
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("tenant_id", "device_sn", name="uq_fingerprint_devices_sn"),
        CheckConstraint("status IN (0, 1, 2)", name="chk_fingerprint_devices_status"),
        Index("idx_fingerprint_devices_tenant_status", "tenant_id", "status"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="fingerprint_devices")
    raw_logs: Mapped[List["FingerprintRawLog"]] = relationship("FingerprintRawLog", back_populates="device", cascade="all, delete-orphan")


class FingerprintRawLog(Base, UUIDPrimaryKeyMixin):
    """Log mentah hasil tap / check-in dari mesin fingerprint sebelum diproses ke kehadiran."""
    __tablename__ = "fingerprint_raw_logs"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fingerprint_devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    device_user_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True, comment="PIN / ID user pada mesin")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    verify_mode: Mapped[int] = mapped_column(
        SmallInteger,
        default=1,
        nullable=False,
        comment="1->fingerprint, 2->face, 3->rfid, 4->pin"
    )

    sync_status: Mapped[int] = mapped_column(
        SmallInteger,
        default=FingerprintSyncStatusEnum.PENDING,
        nullable=False,
        comment="0->pending, 1->processed, 2->unmatched, 3->duplicate, 4->failed"
    )

    matched_employee_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    processed_attendance_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("attendance_records.id", ondelete="SET NULL"),
        nullable=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now, nullable=False)

    __table_args__ = (
        CheckConstraint("sync_status IN (0, 1, 2, 3, 4)", name="chk_fingerprint_raw_logs_sync"),
        Index("idx_fingerprint_raw_sync", "tenant_id", "sync_status"),
        Index("idx_fingerprint_raw_device_time", "device_id", "timestamp"),
    )

    device: Mapped["FingerprintDevice"] = relationship("FingerprintDevice", back_populates="raw_logs")
    matched_employee: Mapped[Optional["Employee"]] = relationship("Employee")
    processed_attendance: Mapped[Optional["AttendanceRecord"]] = relationship("AttendanceRecord")


class FingerprintEmployeeMapping(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Pemetaan antara nomor PIN mesin fingerprint ke data Karyawan."""
    __tablename__ = "fingerprint_employee_mappings"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    device_user_id: Mapped[str] = mapped_column(String(50), nullable=False, comment="PIN pada mesin")
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    __table_args__ = (
        UniqueConstraint("tenant_id", "device_user_id", name="uq_fp_mappings_tenant_device_uid"),
        UniqueConstraint("tenant_id", "employee_id", name="uq_fp_mappings_tenant_employee"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant")
    employee: Mapped["Employee"] = relationship("Employee")


class DocumentTemplate(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Template surat dinas dan dokumen kepegawaian HR."""
    __tablename__ = "document_templates"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    type: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        comment="1->kontrak_pkwt, 2->sk_pengangkatan, 3->surat_peringatan, 4->surat_tugas, 5->surat_paklaring, 6->surat_mutasi"
    )
    template_body: Mapped[str] = mapped_column(Text, nullable=False, comment="Template markdown/HTML dengan placeholder variabel")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        CheckConstraint("type BETWEEN 1 AND 6", name="chk_document_templates_type"),
        Index("idx_doc_templates_tenant_type", "tenant_id", "type"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="document_templates")
    documents: Mapped[List["EmployeeDocument"]] = relationship("EmployeeDocument", back_populates="template")


class EmployeeDocument(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Arsip dokumen dan surat resmi yang telah diterbitkan untuk karyawan."""
    __tablename__ = "employee_documents"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    template_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("document_templates.id", ondelete="SET NULL"),
        nullable=True
    )
    letter_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[int] = mapped_column(
        SmallInteger,
        default=DocumentStatusEnum.GENERATED,
        nullable=False,
        comment="0->draft, 1->generated, 2->signed, 3->archived"
    )
    issued_date: Mapped[date] = mapped_column(Date, nullable=False)
    file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    __table_args__ = (
        CheckConstraint("status IN (0, 1, 2, 3)", name="chk_employee_documents_status"),
        Index("idx_emp_documents_tenant_status", "tenant_id", "status"),
        Index("idx_emp_documents_employee", "employee_id"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="employee_documents")
    employee: Mapped["Employee"] = relationship("Employee", back_populates="documents")
    template: Mapped[Optional["DocumentTemplate"]] = relationship("DocumentTemplate", back_populates="documents")
