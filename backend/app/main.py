import os
import re
import uuid
from datetime import datetime, timezone, timedelta, date
from decimal import Decimal
from typing import List, Optional, Any
import jwt
import json
import urllib.request
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, or_, update, delete

from app.core.config import settings
from app.core.database import get_db, engine, SessionLocal
from app.core.security import verify_password, hash_password
from app.models.auth import User
from app.models.tenant import Tenant, TenantUser
from app.models.rbac import Role, TenantUserRole, Permission, RolePermission
from app.models.billing import Subscription, Plan
from app.models.financial import Account, Category, Transaction, Budget, FinancialGoal, GoalContribution
from app.models.investment import InvestmentHolding, InvestmentAsset
from app.models.company import Employee, AttendanceRecord, PayrollRun, Department
from app.models.telegram import TelegramAccount, TelegramChat, TelegramBot
from app.services.telegram_bot import handle_telegram_update, send_telegram_message

app = FastAPI(
    title="PantauDuit API",
    description="Backend REST API terhubung langsung ke PostgreSQL Database dengan JWT Authentication",
    version="2.0.0"
)

# Enable CORS for frontend SvelteKit dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)

JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 48


@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        user = db.execute(select(User).where(User.name.ilike("%filza%"))).scalar_one_or_none()
        if not user:
            user = db.execute(select(User).where(User.email.ilike("%filza%"))).scalar_one_or_none()
        if user:
            tenant_ids = get_user_tenant_ids(user, db)
            if tenant_ids:
                accounts = db.execute(select(Account).where(Account.tenant_id.in_(tenant_ids), Account.name == "tes")).scalars().all()
                for acc in accounts:
                    tx_count = db.execute(select(Transaction).where(Transaction.account_id == acc.id)).scalars().all()
                    if len(tx_count) == 0:
                        cat = db.execute(select(Category).where(Category.type.in_(["INCOME", "BOTH"]))).first()
                        cat_obj = cat[0] if cat else None
                        recovery_tx = Transaction(
                            tenant_id=acc.tenant_id,
                            account_id=acc.id,
                            category_id=cat_obj.id if cat_obj else None,
                            amount=Decimal("500000.00"),
                            transaction_type="INCOME",
                            transaction_date=datetime.now(timezone.utc),
                            source="DASHBOARD",
                            status="COMPLETED",
                            description="uang pertama tabungan",
                            notes="Pemasukan pertama via dashboard",
                            created_by=user.id
                        )
                        db.add(recovery_tx)
                        acc.current_balance = Decimal("500000.00")
                        db.commit()
                        print(f"[STARTUP] Successfully recovered 500,000 transaction for user {user.name} on account {acc.name}")
    except Exception as e:
        db.rollback()
        print(f"[STARTUP] Error checking recovery: {e}")
    finally:
        db.close()


# =========================================================================
# Token Helpers
# =========================================================================
def create_access_token(user_id: str, email: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "iat": now,
        "exp": now + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autentikasi diperlukan. Header Authorization Bearer tidak ditemukan.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token tidak valid: klaim sub tidak ditemukan",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesi telah kedaluwarsa. Silakan masuk kembali.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token autentikasi tidak valid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        u_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Format ID Pengguna tidak valid")

    user = db.execute(select(User).where(User.id == u_uuid)).scalar_one_or_none()
    if not user or user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Akun pengguna tidak aktif atau tidak ditemukan di database",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    if not credentials or not credentials.credentials:
        return None
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return None
        return db.execute(select(User).where(User.id == uuid.UUID(user_id))).scalar_one_or_none()
    except Exception:
        return None


# =========================================================================
# User & Permissions Database Builder
# =========================================================================
def get_user_tenant_ids(user: User, db: Session) -> List[uuid.UUID]:
    """Retrieve all active tenant IDs the user belongs to."""
    memberships = db.execute(
        select(TenantUser.tenant_id).where(TenantUser.user_id == user.id, TenantUser.status == "ACTIVE")
    ).scalars().all()
    tenant_ids = [m for m in memberships if m is not None]
    
    if not tenant_ids and user.is_superadmin:
        master_t = db.execute(select(Tenant).where(Tenant.slug.in_(["pantauduit-master", "pantau-tech-corp"]))).first()
        if master_t:
            return [master_t[0].id]
            
    return tenant_ids


def get_user_workspace_and_permissions(user: User, db: Session):
    """Retrieve full tenant, role, and permissions strictly from PostgreSQL tables."""
    # 1. Tenant Membership
    membership = db.execute(
        select(TenantUser).where(TenantUser.user_id == user.id, TenantUser.status == "ACTIVE")
    ).scalar_one_or_none()

    tenant_data = None
    sub_data = None
    role_name = "SUBSCRIBER"
    permissions_list: List[str] = []

    if membership:
        tenant = db.execute(select(Tenant).where(Tenant.id == membership.tenant_id)).scalar_one_or_none()
        if tenant:
            tenant_data = {
                "id": str(tenant.id),
                "name": tenant.name,
                "slug": tenant.slug,
                "type": tenant.type,
                "currency": tenant.currency,
                "timezone": tenant.timezone
            }

            # Subscription
            sub = db.execute(select(Subscription).where(Subscription.tenant_id == tenant.id)).scalar_one_or_none()
            if sub:
                plan = db.execute(select(Plan).where(Plan.id == sub.plan_id)).scalar_one_or_none() if sub.plan_id else None
                sub_data = {
                    "id": str(sub.id),
                    "tenant_id": str(sub.tenant_id),
                    "plan_id": str(sub.plan_id),
                    "status": sub.status,
                    "tier": "enterprise" if (plan and "enterprise" in plan.code.lower()) else ("pro" if (plan and "pro" in plan.code.lower()) else "starter")
                }

            # Roles from TenantUserRole
            tur_list = db.execute(
                select(TenantUserRole).where(TenantUserRole.tenant_user_id == membership.id)
            ).scalars().all()

            for tur in tur_list:
                role = db.execute(select(Role).where(Role.id == tur.role_id)).scalar_one_or_none()
                if role:
                    if role.slug in ["admin", "owner"]:
                        role_name = "ADMIN"
                    elif role.slug == "superadmin":
                        role_name = "SUPERUSER"

                    # Get granular permissions from RolePermission
                    role_perms = db.execute(
                        select(Permission).join(RolePermission, RolePermission.permission_id == Permission.id)
                        .where(RolePermission.role_id == role.id)
                    ).scalars().all()
                    for p in role_perms:
                        if p.slug not in permissions_list:
                            permissions_list.append(p.slug)

    # If user is superadmin flag
    if user.is_superadmin:
        role_name = "SUPERUSER"
        all_perms = db.execute(select(Permission)).scalars().all()
        permissions_list = [p.slug for p in all_perms]

    if not tenant_data:
        # Fallback to first available tenant in DB
        first_t = db.execute(select(Tenant)).first()
        if first_t:
            t = first_t[0]
            tenant_data = {
                "id": str(t.id),
                "name": t.name,
                "slug": t.slug,
                "type": t.type,
                "currency": t.currency,
                "timezone": t.timezone
            }

    username = user.email.split("@")[0]

    user_info = {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "username": username,
        "avatar_url": user.avatar_url or "",
        "status": user.status,
        "is_superadmin": user.is_superadmin,
        "role": role_name,
        "permissions": permissions_list,
        "email_verified_at": user.email_verified_at.isoformat() if user.email_verified_at else None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
    }

    return user_info, tenant_data, sub_data


# =========================================================================
# Pydantic Schemas
# =========================================================================
class LoginRequest(BaseModel):
    email: str
    password: str

class TransactionCreate(BaseModel):
    account_id: str
    destination_account_id: Optional[str] = None
    category_id: Optional[str] = None
    amount: float
    transaction_type: str = "EXPENSE"
    transaction_date: Optional[str] = None
    source: str = "DASHBOARD"
    description: str
    notes: Optional[str] = None

class TransactionUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = None
    category_id: Optional[str] = None
    notes: Optional[str] = None
    transaction_date: Optional[str] = None

class AccountCreate(BaseModel):
    name: str
    type: str = "BANK"
    account_number: Optional[str] = None
    opening_balance: float = 0.0
    color: Optional[str] = "#007AFF"
    icon: Optional[str] = "bca"

class CategoryCreate(BaseModel):
    name: str
    type: str = "EXPENSE"
    icon: Optional[str] = "tag"
    color: Optional[str] = "#007AFF"

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None

class BudgetCreate(BaseModel):
    category_id: Optional[str] = None
    name: Optional[str] = None
    amount: float
    alert_threshold_percent: int = 80
    period: str = "MONTHLY"

class GoalCreate(BaseModel):
    name: str
    target_amount: float
    target_date: Optional[str] = None
    color: Optional[str] = "#007AFF"
    icon: Optional[str] = "target"
    initial_deposit: Optional[float] = 0.0
    account_id: Optional[str] = None

class GoalContribute(BaseModel):
    account_id: str
    amount: float
    notes: Optional[str] = None

class GoalWithdraw(BaseModel):
    account_id: str
    amount: float

class InvestmentCreate(BaseModel):
    account_id: str
    name: str
    symbol: str
    asset_class: str
    quantity: float
    buy_price: float
    current_price: Optional[float] = None
    notes: Optional[str] = None


# =========================================================================
# Public Health Check
# =========================================================================
@app.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# =========================================================================
# Telegram Webhook & Bot Integration Endpoints
# =========================================================================
@app.post("/api/telegram/webhook")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    """Public webhook receiver for Telegram Bot updates."""
    try:
        body = await request.json()
    except Exception:
        return {"ok": True, "status": "invalid_json"}

    bot_token = settings.TELEGRAM_BOT_TOKEN
    if not bot_token or bot_token.endswith("PLACEHOLDER"):
        return {"ok": True, "status": "bot_token_not_configured"}

    try:
        result = handle_telegram_update(body, db, bot_token)
        return {"ok": True, "result": result}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"ok": True, "error": str(e)}


@app.get("/api/telegram/status")
def get_telegram_status(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Return status of bot connection for the currently authenticated user."""
    bot_token = settings.TELEGRAM_BOT_TOKEN
    bot_username = "pd_exavolt_bot"

    linked_account = None
    if current_user:
        tg_acc = db.execute(
            select(TelegramAccount).where(TelegramAccount.user_id == current_user.id)
        ).scalar_one_or_none()
        if tg_acc:
            linked_account = {
                "telegram_user_id": tg_acc.telegram_user_id,
                "telegram_username": tg_acc.telegram_username,
                "first_name": tg_acc.first_name,
                "last_name": tg_acc.last_name,
                "auth_date": tg_acc.auth_date.isoformat() if tg_acc.auth_date else None
            }

    return {
        "bot_username": bot_username,
        "bot_url": f"https://t.me/{bot_username}",
        "is_configured": bool(bot_token and not bot_token.endswith("PLACEHOLDER")),
        "is_linked": bool(linked_account is not None),
        "linked_account": linked_account,
        "pairing_code": "PD-994812",
        "pairing_email": current_user.email if current_user else "admin@pantauduit.id"
    }


@app.post("/api/telegram/set-webhook")
def set_telegram_webhook(current_user: User = Depends(get_current_user)):
    """Register the production webhook URL directly with Telegram Bot API."""
    bot_token = settings.TELEGRAM_BOT_TOKEN
    if not bot_token or bot_token.endswith("PLACEHOLDER"):
        raise HTTPException(status_code=400, detail="TELEGRAM_BOT_TOKEN belum dikonfigurasi di file .env")

    webhook_url = "https://pantau-duit.exavolt.net/api/telegram/webhook"
    api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook?url={webhook_url}"

    try:
        req = urllib.request.Request(api_url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {"status": "success", "telegram_response": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mendaftarkan webhook ke Telegram: {str(e)}")



# =========================================================================
# Auth Endpoints (Public Login & Protected /me)
# =========================================================================
@app.post("/api/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    clean_email = req.email.strip().lower()
    user = db.execute(select(User).where(User.email == clean_email)).scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="Email atau kata sandi tidak sesuai")

    if user.status != "ACTIVE":
        raise HTTPException(status_code=403, detail="Akun Anda dinonaktifkan")

    # Verify password against hash
    is_valid = False
    try:
        is_valid = verify_password(req.password, user.password_hash)
    except Exception:
        pass

    if not is_valid:
        raise HTTPException(status_code=401, detail="Email atau kata sandi tidak sesuai")

    # Update last login timestamp in PostgreSQL
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    # Generate JWT
    token = create_access_token(str(user.id), user.email)

    user_info, tenant_data, sub_data = get_user_workspace_and_permissions(user, db)

    return {
        "user": user_info,
        "workspace": tenant_data,
        "subscription": sub_data,
        "token": token
    }


@app.get("/api/auth/me")
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_info, tenant_data, sub_data = get_user_workspace_and_permissions(current_user, db)
    return {
        "user": user_info,
        "workspace": tenant_data,
        "subscription": sub_data
    }


# =========================================================================
# Protected Accounts Endpoints
# =========================================================================
@app.get("/api/accounts")
def get_accounts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_ids = get_user_tenant_ids(current_user, db)
    if not tenant_ids:
        return []

    accs = db.execute(
        select(Account).where(
            Account.tenant_id.in_(tenant_ids),
            Account.status == "ACTIVE",
            Account.deleted_at.is_(None)
        )
    ).scalars().all()
    results = []
    for a in accs:
        results.append({
            "id": str(a.id),
            "tenant_id": str(a.tenant_id),
            "name": a.name,
            "type": a.type,
            "account_number": a.account_number or "",
            "institution_name": a.name,
            "currency": a.currency,
            "opening_balance": float(a.opening_balance),
            "current_balance": float(a.current_balance),
            "balance": float(a.current_balance),
            "status": a.status,
            "is_active": True,
            "color": a.color or "#007AFF",
            "icon": a.icon or "bca"
        })
    return results

@app.post("/api/accounts")
def create_account(payload: AccountCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_ids = get_user_tenant_ids(current_user, db)
    if not tenant_ids:
        raise HTTPException(status_code=400, detail="Pengguna tidak memiliki workspace aktif")
    tenant_id = tenant_ids[0]

    new_acc = Account(
        tenant_id=tenant_id,
        name=payload.name.strip(),
        type=payload.type,
        account_number=payload.account_number.strip() if payload.account_number else "",
        currency="IDR",
        opening_balance=Decimal(str(payload.opening_balance)),
        current_balance=Decimal(str(payload.opening_balance)),
        status="ACTIVE",
        color=payload.color or "#007AFF",
        icon=payload.icon or "bca"
    )
    db.add(new_acc)
    db.flush()

    # Automatically create the first INCOME transaction for initial balance
    if payload.opening_balance > 0:
        init_cat = db.execute(
            select(Category).where(
                Category.tenant_id == tenant_id,
                Category.type == "INCOME",
                or_(Category.name.ilike("%saldo awal%"), Category.name.ilike("%income%"), Category.name.ilike("%pendapatan%"))
            )
        ).scalars().first()
        if not init_cat:
            init_cat = db.execute(
                select(Category).where(
                    Category.tenant_id == tenant_id,
                    Category.type == "INCOME"
                )
            ).scalars().first()
        if not init_cat:
            init_cat = Category(
                tenant_id=tenant_id,
                name="Saldo Awal",
                slug="saldo-awal",
                type="INCOME",
                icon="wallet",
                color="#10B981",
                is_system=True
            )
            db.add(init_cat)
            db.flush()

        init_tx = Transaction(
            tenant_id=tenant_id,
            account_id=new_acc.id,
            category_id=init_cat.id,
            amount=Decimal(str(payload.opening_balance)),
            transaction_type="INCOME",
            transaction_date=datetime.now(timezone.utc),
            source="SYSTEM",
            status="COMPLETED",
            description=f"Saldo Awal: {new_acc.name}",
            notes="Inisiasi saldo awal saat pembuatan dompet/rekening",
            created_by=current_user.id
        )
        db.add(init_tx)

    db.commit()
    db.refresh(new_acc)

    return {
        "id": str(new_acc.id),
        "name": new_acc.name,
        "current_balance": float(new_acc.current_balance),
        "type": new_acc.type,
        "balance": float(new_acc.current_balance),
        "opening_balance": float(new_acc.opening_balance),
        "account_number": new_acc.account_number,
        "currency": new_acc.currency,
        "status": new_acc.status,
        "is_active": True,
        "color": new_acc.color,
        "icon": new_acc.icon
    }

@app.put("/api/accounts/{acc_id}")
def update_account(acc_id: str, payload: AccountCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_ids = get_user_tenant_ids(current_user, db)
    if not tenant_ids:
        raise HTTPException(status_code=400, detail="Pengguna tidak memiliki workspace aktif")
    try:
        a_uuid = uuid.UUID(acc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Account ID tidak valid")
    
    acc = db.execute(select(Account).where(Account.id == a_uuid, Account.tenant_id.in_(tenant_ids))).scalar_one_or_none()
    if not acc:
        raise HTTPException(status_code=404, detail="Rekening tidak ditemukan atau bukan milik akun Anda")
    
    if payload.name:
        acc.name = payload.name.strip()
    if payload.type:
        acc.type = payload.type
    if payload.account_number is not None:
        acc.account_number = payload.account_number.strip()
    if payload.icon:
        acc.icon = payload.icon
    if payload.color:
        acc.color = payload.color
    db.commit()
    db.refresh(acc)
    return {"message": "Rekening berhasil diperbarui", "id": str(acc.id), "icon": acc.icon}

@app.delete("/api/accounts/{acc_id}")
def delete_account(acc_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_ids = get_user_tenant_ids(current_user, db)
    if not tenant_ids:
        raise HTTPException(status_code=400, detail="Pengguna tidak memiliki workspace aktif")
    try:
        a_uuid = uuid.UUID(acc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Account ID tidak valid")
    
    acc = db.execute(select(Account).where(Account.id == a_uuid, Account.tenant_id.in_(tenant_ids))).scalar_one_or_none()
    if not acc:
        raise HTTPException(status_code=404, detail="Rekening tidak ditemukan atau bukan milik akun Anda")
    
    now_utc = datetime.now(timezone.utc)
    acc.status = "ARCHIVED"
    acc.deleted_at = now_utc
    
    # Soft delete all transactions linked to this account
    db.execute(
        update(Transaction)
        .where(
            or_(Transaction.account_id == acc.id, Transaction.destination_account_id == acc.id),
            Transaction.deleted_at.is_(None)
        )
        .values(deleted_at=now_utc, status="ARCHIVED")
    )
    
    db.commit()
    return {"message": "Rekening dan seluruh transaksi terkait berhasil dihapus (soft-delete)"}


# =========================================================================
# Protected Categories Endpoints
# =========================================================================
@app.get("/api/categories")
def get_categories(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_ids = get_user_tenant_ids(current_user, db)
    if tenant_ids:
        cats = db.execute(
            select(Category).where(
                or_(Category.is_system == True, Category.tenant_id.in_(tenant_ids))
            ).order_by(Category.name)
        ).scalars().all()
    else:
        cats = db.execute(select(Category).where(Category.is_system == True).order_by(Category.name)).scalars().all()

    results = []
    for c in cats:
        results.append({
            "id": str(c.id),
            "name": c.name,
            "slug": c.slug,
            "type": c.type,
            "icon": c.icon or "tag",
            "color": c.color or "#007AFF",
            "is_system": c.is_system
        })
    return results


@app.post("/api/categories")
def create_category(payload: CategoryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_ids = get_user_tenant_ids(current_user, db)
    if not tenant_ids:
        raise HTTPException(status_code=400, detail="Pengguna tidak memiliki workspace aktif")
    tenant_id = tenant_ids[0]

    clean_name = payload.name.strip()
    if not clean_name:
        raise HTTPException(status_code=400, detail="Nama kategori wajib diisi")

    clean_type = payload.type.strip().upper() if payload.type else "EXPENSE"
    if clean_type not in ('EXPENSE', 'INCOME', 'INVESTMENT', 'BOTH'):
        clean_type = 'EXPENSE'

    slug = re.sub(r'[^a-z0-9]+', '-', clean_name.lower()).strip('-')
    if not slug:
        slug = f"cat-{uuid.uuid4().hex[:6]}"

    cat = Category(
        tenant_id=tenant_id,
        name=clean_name,
        slug=slug,
        type=clean_type,
        icon=payload.icon or "tag",
        color=payload.color or "#007AFF",
        is_system=False
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)

    return {
        "id": str(cat.id),
        "name": cat.name,
        "slug": cat.slug,
        "type": cat.type,
        "icon": cat.icon or "tag",
        "color": cat.color or "#007AFF",
        "is_system": cat.is_system
    }


@app.put("/api/categories/{category_id}")
def update_category(category_id: str, payload: CategoryUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_ids = get_user_tenant_ids(current_user, db)
    try:
        cat_uuid = uuid.UUID(category_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID Kategori tidak valid")

    cat = db.execute(select(Category).where(Category.id == cat_uuid)).scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="Kategori tidak ditemukan")

    if not current_user.is_superuser and not cat.is_system and cat.tenant_id not in tenant_ids:
        raise HTTPException(status_code=403, detail="Tidak memiliki akses ke kategori ini")

    if payload.name is not None and payload.name.strip():
        cat.name = payload.name.strip()
        new_slug = re.sub(r'[^a-z0-9]+', '-', cat.name.lower()).strip('-')
        if new_slug:
            cat.slug = new_slug
    if payload.type is not None and payload.type.strip().upper() in ('EXPENSE', 'INCOME', 'INVESTMENT', 'BOTH'):
        cat.type = payload.type.strip().upper()
    if payload.icon is not None:
        cat.icon = payload.icon
    if payload.color is not None:
        cat.color = payload.color

    db.commit()
    db.refresh(cat)

    return {
        "id": str(cat.id),
        "name": cat.name,
        "slug": cat.slug,
        "type": cat.type,
        "icon": cat.icon or "tag",
        "color": cat.color or "#007AFF",
        "is_system": cat.is_system
    }


@app.delete("/api/categories/{category_id}")
def delete_category(category_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_ids = get_user_tenant_ids(current_user, db)
    try:
        cat_uuid = uuid.UUID(category_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID Kategori tidak valid")

    cat = db.execute(select(Category).where(Category.id == cat_uuid)).scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="Kategori tidak ditemukan")

    if cat.is_system:
        raise HTTPException(status_code=400, detail="Kategori bawaan sistem tidak dapat dihapus")

    if not current_user.is_superuser and cat.tenant_id not in tenant_ids:
        raise HTTPException(status_code=403, detail="Tidak memiliki akses untuk menghapus kategori ini")

    # Unlink category from transactions and delete associated budgets
    db.execute(update(Transaction).where(Transaction.category_id == cat.id).values(category_id=None))
    db.execute(delete(Budget).where(Budget.category_id == cat.id))

    db.delete(cat)
    db.commit()
    return {"message": "Kategori berhasil dihapus"}


# =========================================================================
# Protected Transactions Endpoints
# =========================================================================
@app.get("/api/transactions")
def get_transactions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_ids = get_user_tenant_ids(current_user, db)
    if not tenant_ids:
        return []

    txs = db.execute(
        select(Transaction).where(
            Transaction.tenant_id.in_(tenant_ids),
            Transaction.deleted_at.is_(None)
        ).order_by(desc(Transaction.transaction_date))
    ).scalars().all()
    
    results = []
    for t in txs:
        acc = db.execute(select(Account).where(Account.id == t.account_id, Account.status == "ACTIVE", Account.deleted_at.is_(None))).scalar_one_or_none()
        if not acc:
            # Hide transactions belonging to archived/deleted accounts
            continue
        dest_acc = db.execute(select(Account).where(Account.id == t.destination_account_id, Account.status == "ACTIVE", Account.deleted_at.is_(None))).scalar_one_or_none() if t.destination_account_id else None
        cat = db.execute(select(Category).where(Category.id == t.category_id)).scalar_one_or_none() if t.category_id else None

        results.append({
            "id": str(t.id),
            "tenant_id": str(t.tenant_id),
            "account_id": str(t.account_id),
            "destination_account_id": str(t.destination_account_id) if t.destination_account_id else None,
            "category_id": str(t.category_id) if t.category_id else None,
            "amount": float(t.amount),
            "currency": acc.currency if acc else "IDR",
            "transaction_type": t.transaction_type,
            "transaction_date": t.transaction_date.isoformat(),
            "source": t.source,
            "status": t.status,
            "description": t.description,
            "notes": t.notes or "",
            "account_name": acc.name if acc else "Rekening",
            "destination_account_name": dest_acc.name if dest_acc else None,
            "category_name": cat.name if cat else "Umum",
            "category_icon": cat.icon if cat else "tag",
            "category_color": cat.color if cat else "#007AFF"
        })
    return results

@app.post("/api/transactions")
def create_transaction(payload: TransactionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_ids = get_user_tenant_ids(current_user, db)
    if not tenant_ids:
        raise HTTPException(status_code=400, detail="Pengguna tidak memiliki workspace aktif")

    # Verifikasi dompet/rekening minimal ada 1 dulu baru bisa catat transaksi
    user_accs = db.execute(
        select(Account).where(Account.tenant_id.in_(tenant_ids), Account.status == "ACTIVE")
    ).scalars().all()
    if not user_accs:
        raise HTTPException(
            status_code=400,
            detail="Anda belum memiliki dompet atau rekening. Minimal harus ada 1 dompet/rekening aktif sebelum mencatat transaksi."
        )

    if payload.transaction_type == "TRANSFER" and len(user_accs) < 2:
        raise HTTPException(
            status_code=400,
            detail="Transfer antar rekening membutuhkan minimal 2 dompet/rekening terdaftar."
        )

    try:
        acc_uuid = uuid.UUID(payload.account_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Account ID tidak valid")

    acc = db.execute(select(Account).where(Account.id == acc_uuid, Account.tenant_id.in_(tenant_ids))).scalar_one_or_none()
    if not acc:
        raise HTTPException(status_code=404, detail="Rekening tidak ditemukan atau bukan milik workspace Anda")

    dest_acc = None
    if payload.destination_account_id:
        try:
            dest_acc = db.execute(select(Account).where(Account.id == uuid.UUID(payload.destination_account_id), Account.tenant_id.in_(tenant_ids))).scalar_one_or_none()
        except ValueError:
            pass

    cat = None
    if payload.category_id:
        try:
            cat = db.execute(select(Category).where(Category.id == uuid.UUID(payload.category_id))).scalar_one_or_none()
        except ValueError:
            pass

    amount_dec = Decimal(str(payload.amount))

    # Parse date
    tx_date = datetime.now(timezone.utc)
    if payload.transaction_date:
        try:
            tx_date = datetime.fromisoformat(payload.transaction_date).replace(tzinfo=timezone.utc)
        except Exception:
            pass

    # Sanitize source and transaction type against DB check constraints
    clean_source = payload.source if payload.source in ("TELEGRAM", "DASHBOARD", "SYSTEM", "API") else "DASHBOARD"
    clean_type = payload.transaction_type if payload.transaction_type in ("EXPENSE", "INCOME", "INVESTMENT", "TRANSFER", "REFUND") else "EXPENSE"

    # Create transaction
    new_tx = Transaction(
        tenant_id=acc.tenant_id,
        account_id=acc.id,
        destination_account_id=dest_acc.id if dest_acc else None,
        category_id=cat.id if cat else None,
        amount=amount_dec,
        transaction_type=clean_type,
        transaction_date=tx_date,
        source=clean_source,
        status="COMPLETED",
        description=payload.description,
        notes=payload.notes or "",
        created_by=current_user.id
    )
    db.add(new_tx)

    # Atomic Balance Ledger Update
    if clean_type == "EXPENSE":
        acc.current_balance -= amount_dec
    elif clean_type == "INCOME":
        acc.current_balance += amount_dec
    elif clean_type == "TRANSFER" and dest_acc:
        acc.current_balance -= amount_dec
        dest_acc.current_balance += amount_dec

    db.commit()
    db.refresh(new_tx)

    return {
        "id": str(new_tx.id),
        "amount": float(new_tx.amount),
        "transaction_type": new_tx.transaction_type,
        "description": new_tx.description,
        "account_name": acc.name,
        "category_name": cat.name if cat else "Umum"
    }

@app.put("/api/transactions/{tx_id}")
def update_transaction(tx_id: str, payload: TransactionUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_ids = get_user_tenant_ids(current_user, db)
    if not tenant_ids:
        raise HTTPException(status_code=400, detail="Pengguna tidak memiliki workspace aktif")

    try:
        t_uuid = uuid.UUID(tx_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID Transaksi tidak valid")

    tx = db.execute(select(Transaction).where(Transaction.id == t_uuid, Transaction.tenant_id.in_(tenant_ids))).scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan atau bukan milik akun Anda")

    acc = db.execute(select(Account).where(Account.id == tx.account_id)).scalar_one_or_none()
    dest_acc = db.execute(select(Account).where(Account.id == tx.destination_account_id)).scalar_one_or_none() if tx.destination_account_id else None

    if payload.amount is not None:
        new_amt = Decimal(str(payload.amount))
        diff = new_amt - tx.amount
        if diff != 0 and acc:
            if tx.transaction_type == "EXPENSE":
                acc.current_balance -= diff
            elif tx.transaction_type == "INCOME":
                acc.current_balance += diff
            elif tx.transaction_type == "TRANSFER" and dest_acc:
                acc.current_balance -= diff
                dest_acc.current_balance += diff
        tx.amount = new_amt

    if payload.description is not None:
        tx.description = payload.description.strip()

    if payload.notes is not None:
        tx.notes = payload.notes.strip()

    if payload.category_id is not None:
        if payload.category_id in ("", "ALL"):
            tx.category_id = None
        else:
            try:
                tx.category_id = uuid.UUID(payload.category_id)
            except ValueError:
                pass

    if payload.transaction_date:
        try:
            tx.transaction_date = datetime.fromisoformat(payload.transaction_date).replace(tzinfo=timezone.utc)
        except Exception:
            pass

    db.commit()
    db.refresh(tx)

    cat = db.execute(select(Category).where(Category.id == tx.category_id)).scalar_one_or_none() if tx.category_id else None
    return {
        "id": str(tx.id),
        "amount": float(tx.amount),
        "transaction_type": tx.transaction_type,
        "description": tx.description,
        "account_name": acc.name if acc else "Rekening",
        "category_name": cat.name if cat else "Umum"
    }

@app.delete("/api/transactions/{tx_id}")
def delete_transaction(tx_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_ids = get_user_tenant_ids(current_user, db)
    if not tenant_ids:
        raise HTTPException(status_code=400, detail="Pengguna tidak memiliki workspace aktif")

    try:
        t_uuid = uuid.UUID(tx_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID Transaksi tidak valid")

    tx = db.execute(select(Transaction).where(Transaction.id == t_uuid, Transaction.tenant_id.in_(tenant_ids))).scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan atau bukan milik akun Anda")

    acc = db.execute(select(Account).where(Account.id == tx.account_id)).scalar_one_or_none()
    dest_acc = db.execute(select(Account).where(Account.id == tx.destination_account_id)).scalar_one_or_none() if tx.destination_account_id else None

    # Revert balance
    if acc:
        if tx.transaction_type == "EXPENSE":
            acc.current_balance += tx.amount
        elif tx.transaction_type == "INCOME":
            acc.current_balance -= tx.amount
        elif tx.transaction_type == "TRANSFER" and dest_acc:
            acc.current_balance += tx.amount
            dest_acc.current_balance -= tx.amount

    tx.status = "ARCHIVED"
    tx.deleted_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": "Transaksi berhasil dihapus (soft-delete) dan saldo direvert"}


# =========================================================================
# Protected Budgets & Goals Endpoints
# =========================================================================
@app.get("/api/budgets")
def get_budgets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_ids = get_user_tenant_ids(current_user, db)
    if not tenant_ids:
        return []

    budgets = db.execute(select(Budget).where(Budget.tenant_id.in_(tenant_ids))).scalars().all()
    results = []
    for b in budgets:
        cat = db.execute(select(Category).where(Category.id == b.category_id)).scalar_one_or_none() if b.category_id else None
        spent = 0.0
        if b.category_id:
            tx_sum = db.execute(
                select(Transaction.amount).where(
                    Transaction.tenant_id.in_(tenant_ids),
                    Transaction.category_id == b.category_id,
                    Transaction.transaction_type == 'EXPENSE',
                    Transaction.status == 'COMPLETED'
                )
            ).scalars().all()
            spent = float(sum(tx_sum))

        results.append({
            "id": str(b.id),
            "tenant_id": str(b.tenant_id),
            "name": b.name,
            "category_id": str(b.category_id) if b.category_id else None,
            "amount": float(b.amount),
            "limit_amount": float(b.amount),
            "spent_amount": spent,
            "period": b.period,
            "alert_threshold_percent": b.alert_threshold_percent,
            "is_active": b.is_active,
            "category_name": cat.name if cat else None,
            "category_icon": cat.icon if cat else None
        })
    return results

@app.post("/api/budgets")
def create_budget(payload: BudgetCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_ids = get_user_tenant_ids(current_user, db)
    if not tenant_ids:
        raise HTTPException(status_code=400, detail="Pengguna tidak memiliki workspace aktif")
    tenant_id = tenant_ids[0]

    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Nominal batas pengeluaran harus lebih dari 0")

    cat = None
    if payload.category_id:
        try:
            cat_uuid = uuid.UUID(payload.category_id)
            cat = db.execute(select(Category).where(Category.id == cat_uuid)).scalar_one_or_none()
        except ValueError:
            pass

    budget_name = payload.name.strip() if payload.name and payload.name.strip() else (cat.name if cat else "Batas Pengeluaran")

    today = date.today()
    start_date = date(today.year, today.month, 1)
    if today.month == 12:
        end_date = date(today.year, 12, 31)
    else:
        end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)

    new_budget = Budget(
        tenant_id=tenant_id,
        category_id=cat.id if cat else None,
        name=budget_name,
        amount=Decimal(str(payload.amount)),
        period="MONTHLY",
        start_date=start_date,
        end_date=end_date,
        alert_threshold_percent=payload.alert_threshold_percent,
        is_active=True
    )
    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)

    return {
        "id": str(new_budget.id),
        "name": new_budget.name,
        "amount": float(new_budget.amount),
        "limit_amount": float(new_budget.amount),
        "spent_amount": 0.0,
        "category_id": str(new_budget.category_id) if new_budget.category_id else None,
        "category_name": cat.name if cat else None,
        "category_icon": cat.icon if cat else None,
        "period": new_budget.period,
        "alert_threshold_percent": new_budget.alert_threshold_percent,
        "is_active": new_budget.is_active
    }

@app.delete("/api/budgets/{budget_id}")
def delete_budget(budget_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_ids = get_user_tenant_ids(current_user, db)
    if not tenant_ids:
        raise HTTPException(status_code=400, detail="Pengguna tidak memiliki workspace aktif")
    try:
        b_uuid = uuid.UUID(budget_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID Batas Pengeluaran tidak valid")

    budget = db.execute(select(Budget).where(Budget.id == b_uuid, Budget.tenant_id.in_(tenant_ids))).scalar_one_or_none()
    if not budget:
        raise HTTPException(status_code=404, detail="Batas pengeluaran tidak ditemukan")

    db.delete(budget)
    db.commit()
    return {"message": "Batas pengeluaran berhasil dihapus"}

@app.get("/api/goals")
def get_goals(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_ids = get_user_tenant_ids(current_user, db)
    if not tenant_ids:
        return []

    goals = db.execute(select(FinancialGoal).where(FinancialGoal.tenant_id.in_(tenant_ids))).scalars().all()
    results = []
    for g in goals:
        results.append({
            "id": str(g.id),
            "tenant_id": str(g.tenant_id),
            "name": g.name,
            "target_amount": float(g.target_amount),
            "current_amount": float(g.current_amount),
            "target_date": g.target_date.isoformat() if g.target_date else None,
            "status": g.status,
            "color": g.color or "#007AFF",
            "icon": g.icon or "target"
        })
    return results

@app.post("/api/goals")
def create_goal(payload: GoalCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_ids = get_user_tenant_ids(current_user, db)
    if not tenant_ids:
        raise HTTPException(status_code=400, detail="Pengguna tidak memiliki workspace aktif")
    tenant_id = tenant_ids[0]

    if payload.target_amount <= 0:
        raise HTTPException(status_code=400, detail="Target nominal tabungan harus lebih dari 0")

    t_date = None
    if payload.target_date:
        try:
            t_date = date.fromisoformat(payload.target_date.split("T")[0])
        except Exception:
            pass

    new_goal = FinancialGoal(
        tenant_id=tenant_id,
        name=payload.name.strip(),
        target_amount=Decimal(str(payload.target_amount)),
        current_amount=Decimal("0.00"),
        target_date=t_date,
        status="IN_PROGRESS",
        color=payload.color or "#007AFF",
        icon=payload.icon or "target"
    )
    db.add(new_goal)
    db.flush()

    init_dep = float(payload.initial_deposit or 0)
    if init_dep > 0:
        if not payload.account_id:
            raise HTTPException(status_code=400, detail="Pilih dompet/rekening asal untuk setoran awal tabungan")
        try:
            acc_uuid = uuid.UUID(payload.account_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="ID Dompet/Rekening tidak valid")

        acc = db.execute(select(Account).where(Account.id == acc_uuid, Account.tenant_id.in_(tenant_ids))).scalar_one_or_none()
        if not acc:
            raise HTTPException(status_code=404, detail="Dompet/rekening tidak ditemukan")

        dep_dec = Decimal(str(init_dep))
        if acc.current_balance < dep_dec:
            raise HTTPException(status_code=400, detail=f"Saldo {acc.name} tidak mencukupi (sisa saldo: Rp {acc.current_balance:,.0f})")

        acc.current_balance -= dep_dec
        new_goal.current_amount += dep_dec

        tx = Transaction(
            tenant_id=tenant_id,
            account_id=acc.id,
            amount=dep_dec,
            transaction_type="EXPENSE",
            transaction_date=datetime.now(timezone.utc),
            source="DASHBOARD",
            status="COMPLETED",
            description=f"Setoran awal tabungan: {new_goal.name}",
            notes=f"Disisihkan dari {acc.name}",
            created_by=current_user.id
        )
        db.add(tx)
        db.flush()

        contrib = GoalContribution(
            goal_id=new_goal.id,
            transaction_id=tx.id,
            amount=dep_dec,
            contribution_date=datetime.now(timezone.utc),
            notes=f"Setor awal dari {acc.name}"
        )
        db.add(contrib)

    db.commit()
    db.refresh(new_goal)

    return {
        "id": str(new_goal.id),
        "name": new_goal.name,
        "target_amount": float(new_goal.target_amount),
        "current_amount": float(new_goal.current_amount),
        "target_date": new_goal.target_date.isoformat() if new_goal.target_date else None,
        "status": new_goal.status,
        "color": new_goal.color,
        "icon": new_goal.icon
    }

@app.post("/api/goals/{goal_id}/contribute")
def contribute_to_goal(goal_id: str, payload: GoalContribute, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_ids = get_user_tenant_ids(current_user, db)
    if not tenant_ids:
        raise HTTPException(status_code=400, detail="Pengguna tidak memiliki workspace aktif")
    try:
        g_uuid = uuid.UUID(goal_id)
        acc_uuid = uuid.UUID(payload.account_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID Target atau Dompet/Rekening tidak valid")

    goal = db.execute(select(FinancialGoal).where(FinancialGoal.id == g_uuid, FinancialGoal.tenant_id.in_(tenant_ids))).scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=404, detail="Target tabungan tidak ditemukan")

    acc = db.execute(select(Account).where(Account.id == acc_uuid, Account.tenant_id.in_(tenant_ids))).scalar_one_or_none()
    if not acc:
        raise HTTPException(status_code=404, detail="Dompet/rekening tidak ditemukan")

    amt_dec = Decimal(str(payload.amount))
    if amt_dec <= 0:
        raise HTTPException(status_code=400, detail="Jumlah setoran tabungan harus lebih dari 0")

    if acc.current_balance < amt_dec:
        raise HTTPException(status_code=400, detail=f"Saldo {acc.name} tidak mencukupi (sisa saldo: Rp {acc.current_balance:,.0f})")

    acc.current_balance -= amt_dec
    goal.current_amount += amt_dec
    if goal.current_amount >= goal.target_amount:
        goal.status = "REACHED"

    tx = Transaction(
        tenant_id=acc.tenant_id,
        account_id=acc.id,
        amount=amt_dec,
        transaction_type="EXPENSE",
        transaction_date=datetime.now(timezone.utc),
        source="DASHBOARD",
        status="COMPLETED",
        description=f"Setor tabungan: {goal.name}",
        notes=payload.notes or f"Disisihkan dari {acc.name}",
        created_by=current_user.id
    )
    db.add(tx)
    db.flush()

    contrib = GoalContribution(
        goal_id=goal.id,
        transaction_id=tx.id,
        amount=amt_dec,
        contribution_date=datetime.now(timezone.utc),
        notes=payload.notes or f"Setoran via {acc.name}"
    )
    db.add(contrib)
    db.commit()

    return {
        "id": str(goal.id),
        "name": goal.name,
        "target_amount": float(goal.target_amount),
        "current_amount": float(goal.current_amount),
        "status": goal.status,
        "account_id": str(acc.id),
        "account_balance": float(acc.current_balance)
    }

@app.post("/api/goals/{goal_id}/withdraw")
def withdraw_from_goal(goal_id: str, payload: GoalWithdraw, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_ids = get_user_tenant_ids(current_user, db)
    if not tenant_ids:
        raise HTTPException(status_code=400, detail="Pengguna tidak memiliki workspace aktif")
    try:
        g_uuid = uuid.UUID(goal_id)
        acc_uuid = uuid.UUID(payload.account_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID Target atau Dompet/Rekening tidak valid")

    goal = db.execute(select(FinancialGoal).where(FinancialGoal.id == g_uuid, FinancialGoal.tenant_id.in_(tenant_ids))).scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=404, detail="Target tabungan tidak ditemukan")

    acc = db.execute(select(Account).where(Account.id == acc_uuid, Account.tenant_id.in_(tenant_ids))).scalar_one_or_none()
    if not acc:
        raise HTTPException(status_code=404, detail="Dompet/rekening tidak ditemukan")

    amt_dec = Decimal(str(payload.amount))
    if amt_dec <= 0:
        raise HTTPException(status_code=400, detail="Jumlah penarikan harus lebih dari 0")

    if goal.current_amount < amt_dec:
        raise HTTPException(status_code=400, detail=f"Jumlah penarikan melebihi isi tabungan saat ini (tersedia: Rp {goal.current_amount:,.0f})")

    goal.current_amount -= amt_dec
    if goal.current_amount < goal.target_amount:
        goal.status = "IN_PROGRESS"

    acc.current_balance += amt_dec

    tx = Transaction(
        tenant_id=acc.tenant_id,
        account_id=acc.id,
        amount=amt_dec,
        transaction_type="INCOME",
        transaction_date=datetime.now(timezone.utc),
        source="DASHBOARD",
        status="COMPLETED",
        description=f"Tarik tabungan: {goal.name}",
        notes=f"Dikembalikan ke {acc.name}",
        created_by=current_user.id
    )
    db.add(tx)
    db.commit()

    return {
        "id": str(goal.id),
        "name": goal.name,
        "target_amount": float(goal.target_amount),
        "current_amount": float(goal.current_amount),
        "status": goal.status,
        "account_id": str(acc.id),
        "account_balance": float(acc.current_balance)
    }

@app.delete("/api/goals/{goal_id}")
def delete_goal(goal_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_ids = get_user_tenant_ids(current_user, db)
    if not tenant_ids:
        raise HTTPException(status_code=400, detail="Pengguna tidak memiliki workspace aktif")
    try:
        g_uuid = uuid.UUID(goal_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID Target tidak valid")

    goal = db.execute(select(FinancialGoal).where(FinancialGoal.id == g_uuid, FinancialGoal.tenant_id.in_(tenant_ids))).scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=404, detail="Target tabungan tidak ditemukan")

    db.delete(goal)
    db.commit()
    return {"message": "Target tabungan berhasil dihapus"}

@app.get("/api/investments")
def get_investments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_ids = get_user_tenant_ids(current_user, db)
    if not tenant_ids:
        return []

    holdings = db.execute(select(InvestmentHolding).where(InvestmentHolding.tenant_id.in_(tenant_ids))).scalars().all()
    results = []
    for h in holdings:
        asset = db.execute(select(InvestmentAsset).where(InvestmentAsset.id == h.asset_id)).scalar_one_or_none()
        acc = db.execute(select(Account).where(Account.id == h.account_id)).scalar_one_or_none()
        results.append({
            "id": str(h.id),
            "tenant_id": str(h.tenant_id),
            "account_id": str(h.account_id),
            "account_name": acc.name if acc else "Dompet",
            "name": asset.name if asset else "Aset",
            "symbol": asset.symbol if asset else "AST",
            "asset_class": asset.asset_type if asset else "OTHER",
            "quantity": float(h.quantity),
            "buy_price_avg": float(h.average_buy_price),
            "current_price": float(asset.current_price) if asset else float(h.average_buy_price)
        })
    return results

@app.post("/api/investments")
def create_investment(payload: InvestmentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_ids = get_user_tenant_ids(current_user, db)
    if not tenant_ids:
        raise HTTPException(status_code=400, detail="Pengguna tidak memiliki workspace aktif")
    tenant_id = tenant_ids[0]

    try:
        acc_uuid = uuid.UUID(payload.account_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID Dompet/Rekening tidak valid")

    acc = db.execute(select(Account).where(Account.id == acc_uuid, Account.tenant_id.in_(tenant_ids))).scalar_one_or_none()
    if not acc:
        raise HTTPException(status_code=404, detail="Dompet/rekening pembayaran tidak ditemukan")

    qty_dec = Decimal(str(payload.quantity))
    buy_price_dec = Decimal(str(payload.buy_price))
    if qty_dec <= 0 or buy_price_dec <= 0:
        raise HTTPException(status_code=400, detail="Jumlah unit dan harga beli harus lebih dari 0")

    total_cost = qty_dec * buy_price_dec
    if acc.current_balance < total_cost:
        raise HTTPException(status_code=400, detail=f"Saldo {acc.name} tidak cukup untuk beli aset ini (Butuh: Rp {total_cost:,.0f}, Saldo: Rp {acc.current_balance:,.0f})")

    acc.current_balance -= total_cost

    clean_symbol = payload.symbol.strip().upper()
    valid_classes = ('STOCK', 'CRYPTO', 'MUTUAL_FUND', 'BOND', 'COMMODITY', 'REAL_ESTATE', 'OTHER')
    clean_class = payload.asset_class.upper()
    if clean_class == 'GOLD':
        clean_class = 'COMMODITY'
    elif clean_class == 'DEPOSIT':
        clean_class = 'OTHER'
    elif clean_class not in valid_classes:
        clean_class = 'OTHER'

    curr_price_dec = Decimal(str(payload.current_price)) if payload.current_price and payload.current_price > 0 else buy_price_dec

    asset = db.execute(select(InvestmentAsset).where(InvestmentAsset.symbol == clean_symbol)).scalar_one_or_none()
    if not asset:
        asset = InvestmentAsset(
            tenant_id=tenant_id,
            symbol=clean_symbol,
            name=payload.name.strip(),
            asset_type=clean_class,
            currency="IDR",
            current_price=curr_price_dec,
            last_price_updated_at=datetime.now(timezone.utc)
        )
        db.add(asset)
        db.flush()
    else:
        asset.current_price = curr_price_dec

    holding = db.execute(
        select(InvestmentHolding).where(
            InvestmentHolding.tenant_id == tenant_id,
            InvestmentHolding.account_id == acc.id,
            InvestmentHolding.asset_id == asset.id
        )
    ).scalar_one_or_none()

    if holding:
        total_prev = holding.quantity * holding.average_buy_price
        new_total_qty = holding.quantity + qty_dec
        holding.average_buy_price = (total_prev + total_cost) / new_total_qty
        holding.quantity = new_total_qty
    else:
        holding = InvestmentHolding(
            tenant_id=tenant_id,
            account_id=acc.id,
            asset_id=asset.id,
            quantity=qty_dec,
            average_buy_price=buy_price_dec
        )
        db.add(holding)
        db.flush()

    tx = Transaction(
        tenant_id=tenant_id,
        account_id=acc.id,
        amount=total_cost,
        transaction_type="EXPENSE",
        transaction_date=datetime.now(timezone.utc),
        source="DASHBOARD",
        status="COMPLETED",
        description=f"Beli aset investasi: {payload.name.strip()} ({clean_symbol})",
        notes=payload.notes or f"Beli {payload.quantity} unit via {acc.name}",
        created_by=current_user.id
    )
    db.add(tx)
    db.commit()

    return {
        "id": str(holding.id),
        "name": asset.name,
        "symbol": asset.symbol,
        "asset_class": asset.asset_type,
        "quantity": float(holding.quantity),
        "buy_price_avg": float(holding.average_buy_price),
        "current_price": float(asset.current_price),
        "account_id": str(acc.id),
        "account_name": acc.name,
        "account_balance": float(acc.current_balance)
    }

@app.delete("/api/investments/{holding_id}")
def delete_investment(holding_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_ids = get_user_tenant_ids(current_user, db)
    if not tenant_ids:
        raise HTTPException(status_code=400, detail="Pengguna tidak memiliki workspace aktif")
    try:
        h_uuid = uuid.UUID(holding_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID Aset tidak valid")

    holding = db.execute(select(InvestmentHolding).where(InvestmentHolding.id == h_uuid, InvestmentHolding.tenant_id.in_(tenant_ids))).scalar_one_or_none()
    if not holding:
        raise HTTPException(status_code=404, detail="Aset investasi tidak ditemukan")

    db.delete(holding)
    db.commit()
    return {"message": "Aset investasi berhasil dihapus"}


# =========================================================================
# Protected Company Endpoints (HR, Attendance, Payroll)
# =========================================================================
@app.get("/api/company/employees")
def get_employees(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_ids = get_user_tenant_ids(current_user, db)
    if not tenant_ids:
        return []

    emps = db.execute(select(Employee).where(Employee.tenant_id.in_(tenant_ids))).scalars().all()
    results = []
    for e in emps:
        results.append({
            "id": str(e.id),
            "nik": e.nik,
            "full_name": e.full_name,
            "email": e.email,
            "phone": e.phone or "",
            "status": e.status,
            "employment_type": e.employment_type,
            "basic_salary": float(e.basic_salary)
        })
    return results


# =========================================================================
# User Management Endpoints (Superadmin / Administrator)
# =========================================================================
class UserCreateRequest(BaseModel):
    name: str
    email: str
    password: Optional[str] = "password123"
    role_type: str = "PERSONAL"  # "PERSONAL" or "COMPANY"
    workspace_name: Optional[str] = None


@app.get("/api/users")
def list_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    users = db.execute(select(User).order_by(desc(User.created_at))).scalars().all()
    results = []
    for u in users:
        tu = db.execute(select(TenantUser).where(TenantUser.user_id == u.id)).scalar_one_or_none()
        tenant = None
        role_label = "MEMBER"
        if tu:
            tenant = db.execute(select(Tenant).where(Tenant.id == tu.tenant_id)).scalar_one_or_none()
            tur_obj = db.execute(select(TenantUserRole).where(TenantUserRole.tenant_user_id == tu.id)).scalar_one_or_none()
            if tur_obj:
                r_obj = db.execute(select(Role).where(Role.id == tur_obj.role_id)).scalar_one_or_none()
                if r_obj:
                    role_label = r_obj.name

        if u.is_superadmin:
            role_label = "Superadmin"

        results.append({
            "id": str(u.id),
            "name": u.name,
            "email": u.email,
            "status": u.status,
            "is_superadmin": u.is_superadmin,
            "role": "SUPERUSER" if u.is_superadmin else (tenant.type if tenant else "PERSONAL"),
            "role_label": role_label,
            "role_type": "COMPANY" if (tenant and tenant.type == "BUSINESS") else "PERSONAL",
            "workspace_name": tenant.name if tenant else "Personal Workspace",
            "workspace_type": tenant.type if tenant else "PERSONAL",
            "created_at": u.created_at.strftime("%d %b %Y") if u.created_at else "-",
            "last_active": u.last_login_at.strftime("%d %b %Y %H:%M") if u.last_login_at else "Belum pernah login"
        })
    return results


@app.post("/api/users")
def create_user_by_admin(req: UserCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    clean_email = req.email.strip().lower()
    existing = db.execute(select(User).where(User.email == clean_email)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Alamat email sudah terdaftar di sistem")

    user_id = uuid.uuid4()
    new_user = User(
        id=user_id,
        name=req.name.strip(),
        email=clean_email,
        password_hash=hash_password(req.password or "password123"),
        status="ACTIVE",
        is_superadmin=False,
        email_verified_at=datetime.now(timezone.utc)
    )
    db.add(new_user)
    db.flush()

    role_type_upper = (req.role_type or "PERSONAL").upper()
    if role_type_upper in ["COMPANY", "BUSINESS"]:
        ws_name = req.workspace_name.strip() if req.workspace_name else f"PT {req.name.strip()} Solusindo"
        ws_slug = f"corp-{uuid.uuid4().hex[:8]}"
        tenant = Tenant(
            id=uuid.uuid4(),
            name=ws_name,
            slug=ws_slug,
            type="BUSINESS",
            currency="IDR",
            timezone="Asia/Jakarta"
        )
        db.add(tenant)
        db.flush()

        role_to_assign = db.execute(select(Role).where(Role.slug == "admin")).scalar_one_or_none()
    else:
        ws_name = req.workspace_name.strip() if req.workspace_name else f"Workspace Pribadi {req.name.strip()}"
        ws_slug = f"user-{uuid.uuid4().hex[:8]}"
        tenant = Tenant(
            id=uuid.uuid4(),
            name=ws_name,
            slug=ws_slug,
            type="PERSONAL",
            currency="IDR",
            timezone="Asia/Jakarta"
        )
        db.add(tenant)
        db.flush()

        role_to_assign = db.execute(select(Role).where(Role.slug == "admin")).scalar_one_or_none() or db.execute(select(Role).where(Role.slug == "member")).scalar_one_or_none()

    tu = TenantUser(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        user_id=new_user.id,
        status="ACTIVE"
    )
    db.add(tu)
    db.flush()

    if role_to_assign:
        tur = TenantUserRole(
            tenant_user_id=tu.id,
            role_id=role_to_assign.id
        )
        db.add(tur)

    db.commit()

    return {
        "id": str(new_user.id),
        "name": new_user.name,
        "email": new_user.email,
        "role_type": role_type_upper,
        "workspace_name": tenant.name,
        "workspace_type": tenant.type,
        "status": new_user.status,
        "message": f"Pengguna {new_user.name} berhasil dibuat dengan role {role_type_upper} di workspace {tenant.name}."
    }


class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    status: Optional[str] = None  # 'ACTIVE' or 'SUSPENDED'
    role_type: Optional[str] = None  # 'PERSONAL' or 'COMPANY'
    workspace_name: Optional[str] = None


@app.put("/api/users/{user_id}")
def update_user_by_admin(user_id: str, req: UserUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        u_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="User ID tidak valid")

    target_user = db.execute(select(User).where(User.id == u_uuid)).scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan")

    if req.name and req.name.strip():
        target_user.name = req.name.strip()
    if req.email and req.email.strip():
        clean_email = req.email.strip().lower()
        if clean_email != target_user.email:
            exist = db.execute(select(User).where(User.email == clean_email, User.id != target_user.id)).scalar_one_or_none()
            if exist:
                raise HTTPException(status_code=400, detail="Alamat email sudah digunakan oleh pengguna lain")
            target_user.email = clean_email
    if req.password and req.password.strip():
        target_user.password_hash = hash_password(req.password.strip())
    if req.status and req.status in ["ACTIVE", "SUSPENDED"]:
        if target_user.is_superadmin and req.status != "ACTIVE":
            raise HTTPException(status_code=400, detail="Akun Superadmin tidak dapat disuspend")
        target_user.status = req.status

    tu = db.execute(select(TenantUser).where(TenantUser.user_id == target_user.id)).scalar_one_or_none()
    if tu:
        tenant = db.execute(select(Tenant).where(Tenant.id == tu.tenant_id)).scalar_one_or_none()
        if tenant:
            if req.workspace_name and req.workspace_name.strip():
                tenant.name = req.workspace_name.strip()
            if req.role_type:
                new_type = req.role_type.upper()
                if new_type in ["COMPANY", "BUSINESS"]:
                    tenant.type = "BUSINESS"
                else:
                    tenant.type = "PERSONAL"

    db.commit()
    db.refresh(target_user)
    return {"message": f"Pengguna {target_user.name} berhasil diperbarui", "id": str(target_user.id)}


@app.delete("/api/users/{user_id}")
def delete_user_by_admin(user_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        u_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="User ID tidak valid")

    if current_user.id == u_uuid:
        raise HTTPException(status_code=400, detail="Anda tidak dapat menghapus akun Anda sendiri yang sedang aktif")

    target_user = db.execute(select(User).where(User.id == u_uuid)).scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan")

    if target_user.is_superadmin:
        raise HTTPException(status_code=400, detail="Akun Superadmin utama tidak dapat dihapus")

    # Delete memberships & tenant if single-user tenant
    tu_list = db.execute(select(TenantUser).where(TenantUser.user_id == target_user.id)).scalars().all()
    for tu in tu_list:
        t_id = tu.tenant_id
        db.delete(tu)
        remaining = db.execute(select(TenantUser).where(TenantUser.tenant_id == t_id, TenantUser.user_id != target_user.id)).scalars().all()
        if not remaining:
            t_obj = db.execute(select(Tenant).where(Tenant.id == t_id)).scalar_one_or_none()
            if t_obj and t_obj.slug != "pantauduit-master":
                db.delete(t_obj)

    db.delete(target_user)
    db.commit()
    return {"message": f"Pengguna {target_user.name} ({target_user.email}) berhasil dihapus permanen dari sistem"}
