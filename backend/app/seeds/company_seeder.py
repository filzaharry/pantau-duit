import uuid
from datetime import date, datetime, time, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select

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
    OvertimeRequest,
    FingerprintDevice,
    FingerprintRawLog,
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
    AttendanceSourceEnum,
    OvertimeStatusEnum,
    FingerprintDeviceStatusEnum,
    FingerprintSyncStatusEnum,
    DocumentTemplateTypeEnum,
    DocumentStatusEnum,
)


def seed_company(db: Session) -> dict[str, int]:
    """Idempotently seed business tenant, departments, employees, and payroll data."""
    # 1. Pastikan Tenant Perusahaan (PT Pantau Duit Solusindo)
    company_slug = "pantau-tech-corp"
    company_tenant = db.execute(select(Tenant).where(Tenant.slug == company_slug)).scalar_one_or_none()

    if not company_tenant:
        company_tenant = Tenant(
            name="PT Pantau Duit Solusindo",
            slug=company_slug,
            type="BUSINESS",
            currency="IDR",
            timezone="Asia/Jakarta",
        )
        db.add(company_tenant)
        db.flush()

    tenant_id = company_tenant.id

    # 2. Seed Departemen
    departments_data = [
        {"code": "ENG", "name": "Engineering & Technology", "description": "Software engineering, infrastructure, dan produk digital"},
        {"code": "FIN", "name": "Finance & Accounting", "description": "Pengelolaan kas operasional, perpajakan, dan pembukuan"},
        {"code": "HRD", "name": "Human Resources & GA", "description": "Manajemen talenta, penggajian, dan operasional kantor"},
        {"code": "MKT", "name": "Marketing & Growth", "description": "Akuisisi pengguna, branding, dan kemitraan bisnis"},
    ]

    dept_map: dict[str, Department] = {}
    created_depts = 0

    for d_item in departments_data:
        dept = db.execute(
            select(Department).where(Department.tenant_id == tenant_id, Department.code == d_item["code"])
        ).scalar_one_or_none()

        if not dept:
            dept = Department(
                tenant_id=tenant_id,
                code=d_item["code"],
                name=d_item["name"],
                description=d_item["description"],
                status=DepartmentStatusEnum.ACTIVE,
            )
            db.add(dept)
            db.flush()
            created_depts += 1

        dept_map[d_item["code"]] = dept

    # 3. Seed Jabatan (Designations)
    designations_data = [
        {"dept": "ENG", "title": "Lead Software Architect", "level": DesignationLevelEnum.LEAD},
        {"dept": "ENG", "title": "Senior Fullstack Engineer", "level": DesignationLevelEnum.SENIOR},
        {"dept": "ENG", "title": "Frontend Svelte Specialist", "level": DesignationLevelEnum.STAFF},
        {"dept": "FIN", "title": "Finance Operations Manager", "level": DesignationLevelEnum.MANAGER},
        {"dept": "FIN", "title": "Accounting & Tax Officer", "level": DesignationLevelEnum.STAFF},
        {"dept": "HRD", "title": "Head of People & Culture", "level": DesignationLevelEnum.MANAGER},
        {"dept": "HRD", "title": "People Operations Associate", "level": DesignationLevelEnum.STAFF},
        {"dept": "MKT", "title": "Growth Marketing Lead", "level": DesignationLevelEnum.LEAD},
    ]

    desig_map: dict[str, Designation] = {}
    created_desigs = 0

    for dg_item in designations_data:
        dept_id = dept_map[dg_item["dept"]].id
        desig = db.execute(
            select(Designation).where(
                Designation.tenant_id == tenant_id,
                Designation.department_id == dept_id,
                Designation.title == dg_item["title"],
            )
        ).scalar_one_or_none()

        if not desig:
            desig = Designation(
                tenant_id=tenant_id,
                department_id=dept_id,
                title=dg_item["title"],
                level=dg_item["level"],
            )
            db.add(desig)
            db.flush()
            created_desigs += 1

        desig_map[dg_item["title"]] = desig

    # 4. Seed Karyawan (Employees)
    employees_data = [
        {
            "nik": "EMP-001",
            "full_name": "Reza Aditya Pratama",
            "email": "reza.aditya@pantauduit.id",
            "phone": "+6281298760001",
            "gender": GenderEnum.MALE,
            "dept": "ENG",
            "desig": "Lead Software Architect",
            "emp_type": EmploymentTypeEnum.PERMANENT,
            "status": EmployeeStatusEnum.ACTIVE,
            "join_date": date(2023, 1, 15),
            "basic_salary": Decimal("24000000.00"),
            "bank_name": "BCA",
            "bank_account_number": "8830192811",
            "bank_account_holder": "Reza Aditya Pratama",
            "npwp": "81.234.567.8-012.000",
            "bpjs_tk": "19028374651",
            "bpjs_kes": "000182938475",
        },
        {
            "nik": "EMP-002",
            "full_name": "Siti Nurhaliza Putri",
            "email": "siti.putri@pantauduit.id",
            "phone": "+6281298760002",
            "gender": GenderEnum.FEMALE,
            "dept": "FIN",
            "desig": "Finance Operations Manager",
            "emp_type": EmploymentTypeEnum.PERMANENT,
            "status": EmployeeStatusEnum.ACTIVE,
            "join_date": date(2023, 3, 1),
            "basic_salary": Decimal("18500000.00"),
            "bank_name": "Bank Mandiri",
            "bank_account_number": "1370018293847",
            "bank_account_holder": "Siti Nurhaliza Putri",
            "npwp": "82.918.273.6-013.000",
            "bpjs_tk": "19028374652",
            "bpjs_kes": "000182938476",
        },
        {
            "nik": "EMP-003",
            "full_name": "Budi Santoso",
            "email": "budi.santoso@pantauduit.id",
            "phone": "+6281298760003",
            "gender": GenderEnum.MALE,
            "dept": "ENG",
            "desig": "Senior Fullstack Engineer",
            "emp_type": EmploymentTypeEnum.PERMANENT,
            "status": EmployeeStatusEnum.ACTIVE,
            "join_date": date(2023, 6, 10),
            "basic_salary": Decimal("16000000.00"),
            "bank_name": "BCA",
            "bank_account_number": "8830492812",
            "bank_account_holder": "Budi Santoso",
            "npwp": "83.123.456.7-014.000",
            "bpjs_tk": "19028374653",
            "bpjs_kes": "000182938477",
        },
        {
            "nik": "EMP-004",
            "full_name": "Anindya Kirana",
            "email": "anindya.k@pantauduit.id",
            "phone": "+6281298760004",
            "gender": GenderEnum.FEMALE,
            "dept": "HRD",
            "desig": "Head of People & Culture",
            "emp_type": EmploymentTypeEnum.PERMANENT,
            "status": EmployeeStatusEnum.ACTIVE,
            "join_date": date(2023, 4, 15),
            "basic_salary": Decimal("17000000.00"),
            "bank_name": "BSI",
            "bank_account_number": "7182938491",
            "bank_account_holder": "Anindya Kirana",
            "npwp": "84.345.678.9-015.000",
            "bpjs_tk": "19028374654",
            "bpjs_kes": "000182938478",
        },
        {
            "nik": "EMP-005",
            "full_name": "Dimas Arya Wijaya",
            "email": "dimas.arya@pantauduit.id",
            "phone": "+6281298760005",
            "gender": GenderEnum.MALE,
            "dept": "ENG",
            "desig": "Frontend Svelte Specialist",
            "emp_type": EmploymentTypeEnum.CONTRACT,
            "status": EmployeeStatusEnum.ACTIVE,
            "join_date": date(2024, 1, 10),
            "basic_salary": Decimal("11000000.00"),
            "bank_name": "Bank Jago",
            "bank_account_number": "109283746519",
            "bank_account_holder": "Dimas Arya Wijaya",
            "npwp": "85.456.789.0-016.000",
            "bpjs_tk": "19028374655",
            "bpjs_kes": "000182938479",
        },
        {
            "nik": "EMP-006",
            "full_name": "Jessica Amanda",
            "email": "jessica.m@pantauduit.id",
            "phone": "+6281298760006",
            "gender": GenderEnum.FEMALE,
            "dept": "MKT",
            "desig": "Growth Marketing Lead",
            "emp_type": EmploymentTypeEnum.PERMANENT,
            "status": EmployeeStatusEnum.ACTIVE,
            "join_date": date(2023, 8, 20),
            "basic_salary": Decimal("15000000.00"),
            "bank_name": "BCA",
            "bank_account_number": "8830918273",
            "bank_account_holder": "Jessica Amanda",
            "npwp": "86.567.890.1-017.000",
            "bpjs_tk": "19028374656",
            "bpjs_kes": "000182938480",
        },
        {
            "nik": "EMP-007",
            "full_name": "Fajar Hidayat",
            "email": "fajar.h@pantauduit.id",
            "phone": "+6281298760007",
            "gender": GenderEnum.MALE,
            "dept": "FIN",
            "desig": "Accounting & Tax Officer",
            "emp_type": EmploymentTypeEnum.CONTRACT,
            "status": EmployeeStatusEnum.PROBATION,
            "join_date": date(2026, 7, 1),
            "basic_salary": Decimal("8500000.00"),
            "bank_name": "BCA",
            "bank_account_number": "8830112233",
            "bank_account_holder": "Fajar Hidayat",
            "npwp": "87.678.901.2-018.000",
            "bpjs_tk": "19028374657",
            "bpjs_kes": "000182938481",
        },
        {
            "nik": "EMP-008",
            "full_name": "Nadia Larasati",
            "email": "nadia.larasati@pantauduit.id",
            "phone": "+6281298760008",
            "gender": GenderEnum.FEMALE,
            "dept": "HRD",
            "desig": "People Operations Associate",
            "emp_type": EmploymentTypeEnum.INTERN,
            "status": EmployeeStatusEnum.ACTIVE,
            "join_date": date(2026, 6, 1),
            "basic_salary": Decimal("4500000.00"),
            "bank_name": "BNI",
            "bank_account_number": "0891827364",
            "bank_account_holder": "Nadia Larasati",
            "npwp": "88.789.012.3-019.000",
            "bpjs_tk": "19028374658",
            "bpjs_kes": "000182938482",
        },
    ]

    emp_objs: list[Employee] = []
    created_emps = 0

    for e_item in employees_data:
        emp = db.execute(
            select(Employee).where(Employee.tenant_id == tenant_id, Employee.nik == e_item["nik"])
        ).scalar_one_or_none()

        dept_id = dept_map[e_item["dept"]].id
        desig_id = desig_map[e_item["desig"]].id

        if not emp:
            emp = Employee(
                tenant_id=tenant_id,
                nik=e_item["nik"],
                full_name=e_item["full_name"],
                email=e_item["email"],
                phone=e_item["phone"],
                gender=e_item["gender"],
                department_id=dept_id,
                designation_id=desig_id,
                employment_type=e_item["emp_type"],
                status=e_item["status"],
                join_date=e_item["join_date"],
                basic_salary=e_item["basic_salary"],
                bank_name=e_item["bank_name"],
                bank_account_number=e_item["bank_account_number"],
                bank_account_holder=e_item["bank_account_holder"],
                npwp=e_item["npwp"],
                bpjs_tk_number=e_item["bpjs_tk"],
                bpjs_kes_number=e_item["bpjs_kes"],
            )
            db.add(emp)
            db.flush()
            created_emps += 1
        else:
            emp.department_id = dept_id
            emp.designation_id = desig_id
            emp.basic_salary = e_item["basic_salary"]

        emp_objs.append(emp)

    # 5. Seed Siklus Penggajian (Payroll Run Agustus 2026)
    period_year = 2026
    period_month = 8

    payroll_run = db.execute(
        select(PayrollRun).where(
            PayrollRun.tenant_id == tenant_id,
            PayrollRun.period_year == period_year,
            PayrollRun.period_month == period_month,
        )
    ).scalar_one_or_none()

    created_payroll_items = 0
    if not payroll_run:
        payroll_run = PayrollRun(
            tenant_id=tenant_id,
            period_month=period_month,
            period_year=period_year,
            title="Gaji Bulanan Karyawan - Agustus 2026",
            status=PayrollStatusEnum.PAID,
            paid_at=datetime(2026, 8, 28, 10, 0, 0, tzinfo=timezone.utc),
            notes="Payroll rutin Agustus 2026 ditransfer via Bank Central Asia (BCA Payroll Batch).",
        )
        db.add(payroll_run)
        db.flush()

        tot_gross = Decimal("0.00")
        tot_ded = Decimal("0.00")
        tot_net = Decimal("0.00")

        for emp in emp_objs:
            base = emp.basic_salary
            allowance = Decimal("1500000.00") if base >= Decimal("15000000.00") else Decimal("750000.00")
            overtime = Decimal("500000.00") if emp.nik in ("EMP-003", "EMP-005") else Decimal("0.00")

            gross = base + allowance + overtime

            # BPJS TK Karyawan (JHT 2% + JP 1%)
            bpjs_tk_emp = (base * Decimal("0.03")).quantize(Decimal("0.01"))
            # BPJS TK Perusahaan (JKK 0.24% + JKM 0.3% + JHT 3.7% + JP 2% = 6.24%)
            bpjs_tk_comp = (base * Decimal("0.0624")).quantize(Decimal("0.01"))

            # BPJS Kesehatan Karyawan (1%)
            bpjs_kes_emp = (base * Decimal("0.01")).quantize(Decimal("0.01"))
            # BPJS Kesehatan Perusahaan (4%)
            bpjs_kes_comp = (base * Decimal("0.04")).quantize(Decimal("0.01"))

            # Estimasi PPh 21 bulanan
            pph21 = (base * Decimal("0.05")).quantize(Decimal("0.01")) if base >= Decimal("10000000.00") else Decimal("0.00")

            total_deductions = bpjs_tk_emp + bpjs_kes_emp + pph21
            net = gross - total_deductions

            item = PayrollItem(
                payroll_run_id=payroll_run.id,
                employee_id=emp.id,
                basic_salary=base,
                allowances=allowance,
                overtime=overtime,
                deductions=Decimal("0.00"),
                bpjs_tk_employee=bpjs_tk_emp,
                bpjs_tk_company=bpjs_tk_comp,
                bpjs_kes_employee=bpjs_kes_emp,
                bpjs_kes_company=bpjs_kes_comp,
                pph21=pph21,
                gross_salary=gross,
                net_salary=net,
                status=PayrollItemStatusEnum.PAID,
            )
            db.add(item)
            created_payroll_items += 1

            tot_gross += gross
            tot_ded += total_deductions
            tot_net += net

        payroll_run.total_gross = tot_gross
        payroll_run.total_deductions = tot_ded
        payroll_run.total_net = tot_net

    # 6. Seed Sample Cuti (Leaves) & Reimbursement
    sample_emp = emp_objs[0]
    existing_leave = db.execute(
        select(LeaveRequest).where(LeaveRequest.employee_id == sample_emp.id)
    ).first()

    if not existing_leave:
        leave1 = LeaveRequest(
            tenant_id=tenant_id,
            employee_id=sample_emp.id,
            leave_type=LeaveTypeEnum.ANNUAL,
            start_date=date(2026, 9, 21),
            end_date=date(2026, 9, 23),
            total_days=3,
            reason="Liburan keluarga tahunan",
            status=LeaveStatusEnum.APPROVED,
        )
        db.add(leave1)

    existing_reimburse = db.execute(
        select(Reimbursement).where(Reimbursement.employee_id == sample_emp.id)
    ).first()

    if not existing_reimburse:
        reimb1 = Reimbursement(
            tenant_id=tenant_id,
            employee_id=sample_emp.id,
            title="Langganan Lisensi Cloud Server & Domain Staging",
            description="Pembayaran cloud infrastructure development via credit card pribadi",
            amount=Decimal("1250000.00"),
            status=ReimbursementStatusEnum.APPROVED,
        )
        db.add(reimb1)

    # 7. Seed Shifts (Shift Pabrik & Operasional)
    shifts_data = [
        {"code": "S-OFFICE", "name": "Jam Kantor Reguler", "start": time(8, 30), "end": time(17, 30), "cross": False, "color": "#3B82F6", "late_tol": 15},
        {"code": "S-PAGI", "name": "Shift 1 (Pagi)", "start": time(7, 0), "end": time(15, 0), "cross": False, "color": "#10B981", "late_tol": 10},
        {"code": "S-SIANG", "name": "Shift 2 (Siang)", "start": time(15, 0), "end": time(23, 0), "cross": False, "color": "#F59E0B", "late_tol": 10},
        {"code": "S-MALAM", "name": "Shift 3 (Malam/Cross-day)", "start": time(23, 0), "end": time(7, 0), "cross": True, "color": "#6366F1", "late_tol": 10},
    ]

    shift_map: dict[str, Shift] = {}
    created_shifts = 0

    for s_item in shifts_data:
        shift_obj = db.execute(
            select(Shift).where(Shift.tenant_id == tenant_id, Shift.code == s_item["code"])
        ).scalar_one_or_none()

        if not shift_obj:
            shift_obj = Shift(
                tenant_id=tenant_id,
                code=s_item["code"],
                name=s_item["name"],
                start_time=s_item["start"],
                end_time=s_item["end"],
                is_cross_day=s_item["cross"],
                late_tolerance_minutes=s_item["late_tol"],
                color_code=s_item["color"],
                status=ShiftStatusEnum.ACTIVE,
            )
            db.add(shift_obj)
            db.flush()
            created_shifts += 1

        shift_map[s_item["code"]] = shift_obj

    # 8. Seed Fingerprint Devices
    devices_data = [
        {
            "name": "Lobby Utama & Turnstile Gerbang",
            "sn": "ZK-GATE-01",
            "brand": "ZKTeco iClock 680",
            "ip": "192.168.1.201",
            "port": 4370,
            "location": "Gerbang Depan Pabrik & Lobby Utama",
            "status": FingerprintDeviceStatusEnum.ONLINE,
        },
        {
            "name": "Pintu Masuk Gudang & Line 2",
            "sn": "ZK-WH-02",
            "brand": "ZKTeco K40",
            "ip": "192.168.1.202",
            "port": 4370,
            "location": "Gudang Logistik & Area Perakitan",
            "status": FingerprintDeviceStatusEnum.ONLINE,
        },
    ]

    device_objs: list[FingerprintDevice] = []
    created_devices = 0

    for dev_item in devices_data:
        dev = db.execute(
            select(FingerprintDevice).where(
                FingerprintDevice.tenant_id == tenant_id,
                FingerprintDevice.device_sn == dev_item["sn"],
            )
        ).scalar_one_or_none()

        if not dev:
            dev = FingerprintDevice(
                tenant_id=tenant_id,
                device_name=dev_item["name"],
                device_sn=dev_item["sn"],
                brand=dev_item["brand"],
                ip_address=dev_item["ip"],
                port=dev_item["port"],
                location=dev_item["location"],
                status=dev_item["status"],
                last_sync_at=datetime.now(timezone.utc),
            )
            db.add(dev)
            db.flush()
            created_devices += 1

        device_objs.append(dev)

    # 9. Seed Fingerprint Employee Mappings
    created_mappings = 0
    for idx, emp in enumerate(emp_objs):
        pin = f"{1001 + idx}"
        existing_map = db.execute(
            select(FingerprintEmployeeMapping).where(
                FingerprintEmployeeMapping.tenant_id == tenant_id,
                FingerprintEmployeeMapping.employee_id == emp.id,
            )
        ).scalar_one_or_none()

        if not existing_map:
            mapping = FingerprintEmployeeMapping(
                tenant_id=tenant_id,
                device_user_id=pin,
                employee_id=emp.id,
            )
            db.add(mapping)
            created_mappings += 1

    # 10. Seed Attendance Records & Raw Logs
    today = date(2026, 9, 17)
    created_attendance = 0
    created_logs = 0

    attendance_scenarios = [
        # (emp_idx, shift_code, check_in_dt, check_out_dt, status, late_min, ot_min, notes)
        (0, "S-OFFICE", datetime(2026, 9, 17, 8, 22, tzinfo=timezone.utc), datetime(2026, 9, 17, 17, 35, tzinfo=timezone.utc), AttendanceStatusEnum.PRESENT, 0, 0, None),
        (1, "S-OFFICE", datetime(2026, 9, 17, 8, 28, tzinfo=timezone.utc), datetime(2026, 9, 17, 17, 31, tzinfo=timezone.utc), AttendanceStatusEnum.PRESENT, 0, 0, None),
        (2, "S-PAGI", datetime(2026, 9, 17, 7, 24, tzinfo=timezone.utc), datetime(2026, 9, 17, 15, 5, tzinfo=timezone.utc), AttendanceStatusEnum.LATE, 14, 0, "Terlambat 14 menit karena antrian gerbang"),
        (3, "S-SIANG", datetime(2026, 9, 17, 14, 55, tzinfo=timezone.utc), None, AttendanceStatusEnum.PRESENT, 0, 0, "Sedang bertugas shift siang"),
        (4, "S-PAGI", datetime(2026, 9, 17, 6, 52, tzinfo=timezone.utc), datetime(2026, 9, 17, 17, 15, tzinfo=timezone.utc), AttendanceStatusEnum.PRESENT, 0, 120, "Lembur 2 jam maintenance mesin"),
    ]

    for item in attendance_scenarios:
        emp = emp_objs[item[0]]
        shift = shift_map[item[1]]
        att = db.execute(
            select(AttendanceRecord).where(
                AttendanceRecord.tenant_id == tenant_id,
                AttendanceRecord.employee_id == emp.id,
                AttendanceRecord.date == today,
            )
        ).scalar_one_or_none()

        if not att:
            work_duration = 0
            if item[2] and item[3]:
                work_duration = int((item[3] - item[2]).total_seconds() // 60)
            elif item[2]:
                work_duration = 240

            att = AttendanceRecord(
                tenant_id=tenant_id,
                employee_id=emp.id,
                shift_id=shift.id,
                date=today,
                check_in_time=item[2],
                check_out_time=item[3],
                status=item[4],
                work_duration_minutes=work_duration,
                late_minutes=item[5],
                early_leave_minutes=0,
                overtime_minutes=item[6],
                source=AttendanceSourceEnum.FINGERPRINT,
                correction_notes=item[7],
            )
            db.add(att)
            db.flush()
            created_attendance += 1

            # Buat Raw Log untuk check-in
            if item[2] and device_objs:
                dev = device_objs[0]
                pin = f"{1001 + item[0]}"
                raw_in = FingerprintRawLog(
                    tenant_id=tenant_id,
                    device_id=dev.id,
                    device_user_id=pin,
                    timestamp=item[2],
                    verify_mode=1,
                    sync_status=FingerprintSyncStatusEnum.PROCESSED,
                    matched_employee_id=emp.id,
                    processed_attendance_id=att.id,
                )
                db.add(raw_in)
                created_logs += 1

            # Buat Raw Log untuk check-out jika ada
            if item[3] and device_objs:
                dev = device_objs[0]
                pin = f"{1001 + item[0]}"
                raw_out = FingerprintRawLog(
                    tenant_id=tenant_id,
                    device_id=dev.id,
                    device_user_id=pin,
                    timestamp=item[3],
                    verify_mode=1,
                    sync_status=FingerprintSyncStatusEnum.PROCESSED,
                    matched_employee_id=emp.id,
                    processed_attendance_id=att.id,
                )
                db.add(raw_out)
                created_logs += 1

    # 11. Seed Document Templates
    templates_data = [
        {
            "title": "Perjanjian Kerja Waktu Tertentu (PKWT)",
            "type": DocumentTemplateTypeEnum.KONTRAK_PKWT,
            "body": """# SURAT PERJANJIAN KERJA WAKTU TERTENTU (PKWT)
**Nomor: {{letter_number}}**

Pada hari ini, tanggal {{issued_date}}, bertempat di Jakarta, telah disepakati Perjanjian Kerja antara:

1. **{{company_name}}**, beralamat di {{company_address}}, dalam hal ini diwakili oleh **{{director_name}}** selaku Direktur Utama, selanjutnya disebut **PIHAK PERTAMA**.
2. **{{employee_name}}**, NIK: {{employee_nik}}, bertempat tinggal di {{employee_address}}, selanjutnya disebut **PIHAK KEDUA**.

Kedua belah pihak sepakat mengadakan perjanjian kerja dengan ketentuan:
- **Pasal 1 (Jabatan & Penempatan)**: PIHAK KEDUA diterima bekerja sebagai **{{designation}}** pada Departemen **{{department}}**.
- **Pasal 2 (Jangka Waktu)**: Perjanjian berlaku selama {{contract_duration}} terhitung sejak {{start_date}} hingga {{end_date}}.
- **Pasal 3 (Kompensasi & Benefit)**: PIHAK KEDUA berhak atas gaji pokok sebesar **{{basic_salary}}** per bulan beserta fasilitas BPJS Ketenagakerjaan dan Kesehatan sesuai ketentuan hukum yang berlaku.

Demikian surat perjanjian ini dibuat dalam rangkap 2 (dua) bermeterai cukup dan memiliki kekuatan hukum yang sama.
""",
        },
        {
            "title": "Surat Keputusan Pengangkatan Karyawan Tetap (SK Tetap)",
            "type": DocumentTemplateTypeEnum.SK_PENGANGKATAN,
            "body": """# SURAT KEPUTUSAN PENGANGKATAN KARYAWAN TETAP
**Nomor: {{letter_number}}**

Menimbang hasil evaluasi kinerja masa percobaan (probation), Manajemen **{{company_name}}** memutuskan:

1. Mengangkat Saudara/i **{{employee_name}}** (NIK: {{employee_nik}}) sebagai **Karyawan Tetap (Permanent Employee)** terhitung sejak tanggal {{effective_date}}.
2. Jabatan yang diemban adalah **{{designation}}** pada Departemen **{{department}}**.
3. Seluruh hak, tunjangan, dan benefit reguler karyawan tetap berlaku efektif sejak tanggal keputusan ini.

Ditetapkan di: Jakarta  
Tanggal: {{issued_date}}  
**{{company_name}}**
""",
        },
        {
            "title": "Surat Peringatan Pertama (SP-1)",
            "type": DocumentTemplateTypeEnum.SURAT_PERINGATAN,
            "body": """# SURAT PERINGATAN PERTAMA (SP-1)
**Nomor: {{letter_number}}**

Diberikan kepada:
- **Nama**: {{employee_name}}
- **NIK**: {{employee_nik}}
- **Departemen**: {{department}}
- **Jabatan**: {{designation}}

Surat Peringatan ini diterbitkan sehubungan dengan pelanggaran kedisiplinan kerja berupa:
{{violation_details}}

Surat Peringatan ini berlaku selama 6 (enam) bulan sejak tanggal diterbitkan. Karyawan diharapkan memperbaiki kedisiplinan dan kepatuhan terhadap SOP perusahaan.
""",
        },
        {
            "title": "Surat Keterangan Pengalaman Kerja (Paklaring)",
            "type": DocumentTemplateTypeEnum.SURAT_PAKLARING,
            "body": """# SURAT KETERANGAN KERJA (PAKLARING)
**Nomor: {{letter_number}}**

Dengan ini Manajemen **{{company_name}}** menerangkan bahwa:
- **Nama**: {{employee_name}}
- **NIK**: {{employee_nik}}
- **Jabatan Terakhir**: {{designation}} (Departemen {{department}})
- **Masa Kerja**: {{start_date}} s/d {{end_date}}

Telah menyelesaikan masa baktinya dengan baik. Kami menyampaikan apresiasi dan terima kasih setinggi-tingginya atas dedikasi dan kontribusi yang telah diberikan kepada perusahaan selama masa bertugas.
""",
        },
    ]

    template_map: dict[int, DocumentTemplate] = {}
    created_templates = 0

    for t_data in templates_data:
        t_obj = db.execute(
            select(DocumentTemplate).where(
                DocumentTemplate.tenant_id == tenant_id,
                DocumentTemplate.type == t_data["type"],
            )
        ).scalar_one_or_none()

        if not t_obj:
            t_obj = DocumentTemplate(
                tenant_id=tenant_id,
                title=t_data["title"],
                type=t_data["type"],
                template_body=t_data["body"],
                is_active=True,
            )
            db.add(t_obj)
            db.flush()
            created_templates += 1

        template_map[t_data["type"]] = t_obj

    # 12. Seed Sample Employee Documents
    created_docs = 0
    if DocumentTemplateTypeEnum.KONTRAK_PKWT in template_map and len(emp_objs) > 2:
        pkwt_tpl = template_map[DocumentTemplateTypeEnum.KONTRAK_PKWT]
        emp_sample = emp_objs[2]
        doc_no = f"001/HRD-PKWT/09/2026"

        existing_doc = db.execute(
            select(EmployeeDocument).where(
                EmployeeDocument.tenant_id == tenant_id,
                EmployeeDocument.letter_number == doc_no,
            )
        ).scalar_one_or_none()

        if not existing_doc:
            doc = EmployeeDocument(
                tenant_id=tenant_id,
                employee_id=emp_sample.id,
                template_id=pkwt_tpl.id,
                letter_number=doc_no,
                title=f"PKWT - {emp_sample.full_name}",
                content=pkwt_tpl.template_body.replace("{{employee_name}}", emp_sample.full_name)
                .replace("{{employee_nik}}", emp_sample.nik)
                .replace("{{letter_number}}", doc_no)
                .replace("{{issued_date}}", "17 September 2026")
                .replace("{{company_name}}", "PT Pantau Duit Solusindo")
                .replace("{{company_address}}", "Jl. Sudirman Kav. 52-53, Jakarta Selatan")
                .replace("{{director_name}}", "Reza Aditya Pratama")
                .replace("{{designation}}", "Frontend Svelte Specialist")
                .replace("{{department}}", "Engineering & Technology")
                .replace("{{contract_duration}}", "12 (dua belas) bulan")
                .replace("{{start_date}}", "01 Januari 2026")
                .replace("{{end_date}}", "31 Desember 2026")
                .replace("{{basic_salary}}", "Rp 12.000.000"),
                status=DocumentStatusEnum.GENERATED,
                issued_date=date(2026, 9, 17),
            )
            db.add(doc)
            created_docs += 1

    db.commit()

    return {
        "departments": created_depts,
        "designations": created_desigs,
        "employees": created_emps,
        "payroll_items": created_payroll_items,
        "shifts": created_shifts,
        "devices": created_devices,
        "mappings": created_mappings,
        "attendance": created_attendance,
        "raw_logs": created_logs,
        "templates": created_templates,
        "documents": created_docs,
    }

