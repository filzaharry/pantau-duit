import pytest
from decimal import Decimal
from datetime import date
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.database import SessionLocal
from app.models.tenant import Tenant
from app.models.company import (
    Department,
    Designation,
    Employee,
    PayrollRun,
    PayrollItem,
    LeaveRequest,
    Reimbursement,
    Shift,
    AttendanceRecord,
    FingerprintDevice,
    FingerprintEmployeeMapping,
    DocumentTemplate,
    EmployeeDocument,
)
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
    FingerprintDeviceStatusEnum,
    DocumentTemplateTypeEnum,
    DocumentStatusEnum,
)


def test_company_tenant_and_employees_seeded():
    """Memastikan data tenant bisnis dan karyawan berhasil di-seed dengan tipe numerik yang tepat."""
    db = SessionLocal()
    try:
        tenant = db.execute(select(Tenant).where(Tenant.slug == "pantau-tech-corp")).scalar_one_or_none()
        assert tenant is not None, "Tenant PT Pantau Duit Solusindo harus ada"
        assert tenant.type == "BUSINESS"

        employees = db.execute(select(Employee).where(Employee.tenant_id == tenant.id)).scalars().all()
        assert len(employees) >= 8, "Minimal 8 karyawan harus terdaftar"

        for emp in employees:
            assert isinstance(emp.status, int), "Status harus berupa integer"
            assert emp.status in [
                EmployeeStatusEnum.INACTIVE,
                EmployeeStatusEnum.ACTIVE,
                EmployeeStatusEnum.PROBATION,
                EmployeeStatusEnum.RESIGNED,
                EmployeeStatusEnum.TERMINATED,
            ]
            assert isinstance(emp.employment_type, int), "Employment type harus integer"
            assert emp.basic_salary > 0
    finally:
        db.close()


def test_employee_status_numeric_check_constraint():
    """Memastikan CHECK constraint menolak nilai status di luar opsi numerik yang ditentukan (0-4)."""
    db = SessionLocal()
    try:
        tenant = db.execute(select(Tenant).where(Tenant.slug == "pantau-tech-corp")).scalar_one()

        invalid_emp = Employee(
            tenant_id=tenant.id,
            nik="EMP-INVALID",
            full_name="Invalid Status Employee",
            status=99,  # Nilai tidak valid, harus 0-4
            employment_type=EmploymentTypeEnum.PERMANENT,
            gender=GenderEnum.MALE,
            join_date=date(2026, 1, 1),
            basic_salary=Decimal("5000000.00"),
        )

        with pytest.raises(IntegrityError) as excinfo:
            db.add(invalid_emp)
            db.commit()

        assert "chk_employees_status" in str(excinfo.value).lower() or "check constraint" in str(excinfo.value).lower()
        db.rollback()
    finally:
        db.close()


def test_payroll_run_calculation_and_items():
    """Memastikan kalkulasi total gross, deductions, dan net salary pada payroll run sesuai dengan rincian item."""
    db = SessionLocal()
    try:
        tenant = db.execute(select(Tenant).where(Tenant.slug == "pantau-tech-corp")).scalar_one()
        payroll_run = db.execute(
            select(PayrollRun).where(
                PayrollRun.tenant_id == tenant.id,
                PayrollRun.period_year == 2026,
                PayrollRun.period_month == 8,
            )
        ).scalar_one_or_none()

        assert payroll_run is not None, "Payroll run Agustus 2026 harus ada"
        assert payroll_run.status == PayrollStatusEnum.PAID

        items = db.execute(
            select(PayrollItem).where(PayrollItem.payroll_run_id == payroll_run.id)
        ).scalars().all()

        assert len(items) >= 8

        calculated_gross = sum(i.gross_salary for i in items)
        calculated_net = sum(i.net_salary for i in items)

        assert payroll_run.total_gross == calculated_gross
        assert payroll_run.total_net == calculated_net
        assert payroll_run.total_gross >= payroll_run.total_net
    finally:
        db.close()


def test_leave_request_dates_constraint():
    """Memastikan CHECK constraint menolak pengajuan cuti dengan end_date < start_date."""
    db = SessionLocal()
    try:
        tenant = db.execute(select(Tenant).where(Tenant.slug == "pantau-tech-corp")).scalar_one()
        employee = db.execute(select(Employee).where(Employee.tenant_id == tenant.id)).first()[0]

        invalid_leave = LeaveRequest(
            tenant_id=tenant.id,
            employee_id=employee.id,
            leave_type=LeaveTypeEnum.ANNUAL,
            start_date=date(2026, 10, 10),
            end_date=date(2026, 10, 5),  # End date sebelum start date!
            total_days=1,
            status=LeaveStatusEnum.PENDING,
        )

        with pytest.raises(IntegrityError) as excinfo:
            db.add(invalid_leave)
            db.commit()

        assert "chk_leave_requests_dates" in str(excinfo.value).lower() or "check constraint" in str(excinfo.value).lower()
        db.rollback()
    finally:
        db.close()


def test_reimbursement_positive_amount_constraint():
    """Memastikan pengajuan klaim reimbursement menolak nominal <= 0."""
    db = SessionLocal()
    try:
        tenant = db.execute(select(Tenant).where(Tenant.slug == "pantau-tech-corp")).scalar_one()
        employee = db.execute(select(Employee).where(Employee.tenant_id == tenant.id)).first()[0]

        zero_reimb = Reimbursement(
            tenant_id=tenant.id,
            employee_id=employee.id,
            title="Klaim Ilegal Nol Rupiah",
            amount=Decimal("0.00"),
            status=ReimbursementStatusEnum.SUBMITTED,
        )

        with pytest.raises(IntegrityError) as excinfo:
            db.add(zero_reimb)
            db.commit()

        assert "chk_reimbursements_amount" in str(excinfo.value).lower() or "check constraint" in str(excinfo.value).lower()
        db.rollback()
    finally:
        db.close()


def test_shifts_and_attendance_records():
    """Memastikan shift operasional dan record presensi karyawan terdata dengan kalkulasi durasi kerja."""
    db = SessionLocal()
    try:
        tenant = db.execute(select(Tenant).where(Tenant.slug == "pantau-tech-corp")).scalar_one()

        shifts = db.execute(select(Shift).where(Shift.tenant_id == tenant.id)).scalars().all()
        assert len(shifts) >= 4, "Harus ada minimal 4 shift kerja (Office, Pagi, Siang, Malam)"

        malam_shift = next((s for s in shifts if s.code == "S-MALAM"), None)
        assert malam_shift is not None
        assert malam_shift.is_cross_day is True, "Shift malam harus ditandai is_cross_day"
        assert malam_shift.status == ShiftStatusEnum.ACTIVE

        attendances = db.execute(
            select(AttendanceRecord).where(AttendanceRecord.tenant_id == tenant.id)
        ).scalars().all()
        assert len(attendances) >= 5, "Harus ada data presensi yang di-seed"

        for att in attendances:
            assert att.status in [
                AttendanceStatusEnum.ABSENT,
                AttendanceStatusEnum.PRESENT,
                AttendanceStatusEnum.LATE,
                AttendanceStatusEnum.EARLY_LEAVE,
                AttendanceStatusEnum.SICK,
                AttendanceStatusEnum.ON_LEAVE,
                AttendanceStatusEnum.HOLIDAY,
            ]
            assert att.work_duration_minutes >= 0
            assert att.late_minutes >= 0
    finally:
        db.close()


def test_fingerprint_devices_and_mappings():
    """Memastikan perangkat fingerprint online dan mapping PIN mesin ke karyawan terdaftar."""
    db = SessionLocal()
    try:
        tenant = db.execute(select(Tenant).where(Tenant.slug == "pantau-tech-corp")).scalar_one()

        devices = db.execute(
            select(FingerprintDevice).where(FingerprintDevice.tenant_id == tenant.id)
        ).scalars().all()
        assert len(devices) >= 2, "Harus ada minimal 2 perangkat mesin fingerprint"
        for dev in devices:
            assert dev.status == FingerprintDeviceStatusEnum.ONLINE
            assert dev.port == 4370

        mappings = db.execute(
            select(FingerprintEmployeeMapping).where(FingerprintEmployeeMapping.tenant_id == tenant.id)
        ).scalars().all()
        assert len(mappings) >= 8, "Minimal 8 karyawan terpetakan ke PIN mesin"
    finally:
        db.close()


def test_document_templates_and_generated_documents():
    """Memastikan template dokumen dinas HR dan arsip surat terbit terdata lengkap."""
    db = SessionLocal()
    try:
        tenant = db.execute(select(Tenant).where(Tenant.slug == "pantau-tech-corp")).scalar_one()

        templates = db.execute(
            select(DocumentTemplate).where(DocumentTemplate.tenant_id == tenant.id)
        ).scalars().all()
        assert len(templates) >= 4, "Harus ada template PKWT, SK Pengangkatan, SP, dan Paklaring"

        documents = db.execute(
            select(EmployeeDocument).where(EmployeeDocument.tenant_id == tenant.id)
        ).scalars().all()
        assert len(documents) >= 1, "Harus ada minimal 1 dokumen karyawan terbit"
        doc = documents[0]
        assert doc.letter_number != ""
        assert doc.status in [DocumentStatusEnum.DRAFT, DocumentStatusEnum.GENERATED, DocumentStatusEnum.SIGNED, DocumentStatusEnum.ARCHIVED]
    finally:
        db.close()


def test_attendance_status_check_constraint():
    """Memastikan CHECK constraint menolak nilai status attendance di luar 0-6."""
    db = SessionLocal()
    try:
        tenant = db.execute(select(Tenant).where(Tenant.slug == "pantau-tech-corp")).scalar_one()
        employee = db.execute(select(Employee).where(Employee.tenant_id == tenant.id)).first()[0]

        invalid_att = AttendanceRecord(
            tenant_id=tenant.id,
            employee_id=employee.id,
            date=date(2026, 9, 30),
            status=99,  # Invalid status
            source=1,
        )

        with pytest.raises(IntegrityError) as excinfo:
            db.add(invalid_att)
            db.commit()

        assert "chk_attendance_status" in str(excinfo.value).lower() or "check constraint" in str(excinfo.value).lower()
        db.rollback()
    finally:
        db.close()

