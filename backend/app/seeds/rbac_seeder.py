from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.rbac import Role, Permission, RolePermission

MODULES = [
    "dashboard",
    "transactions",
    "accounts",
    "budgets",
    "investments",
    "goals",
    "reports",
    "telegram",
    "notifications",
    "subscription",
    "users",
    "roles",
    "permissions",
    "billing",
    "settings",
]

ACTIONS = ["view", "create", "update", "delete", "export", "manage"]


def seed_rbac(db: Session) -> dict[str, int]:
    """Idempotently seed granular permissions and system roles."""
    created_perms = 0
    created_roles = 0
    created_links = 0

    # 1. Seed Permissions
    all_perms: list[Permission] = []
    for module in MODULES:
        for action in ACTIONS:
            slug = f"{module}.{action}"
            name = f"{action.capitalize()} {module.capitalize()}"
            existing = db.execute(select(Permission).where(Permission.slug == slug)).scalar_one_or_none()
            if not existing:
                perm = Permission(
                    module=module,
                    name=name,
                    slug=slug,
                    description=f"Allows user to {action} in {module} module",
                )
                db.add(perm)
                db.flush()
                all_perms.append(perm)
                created_perms += 1
            else:
                all_perms.append(existing)

    # 2. Seed System Roles (tenant_id IS NULL)
    system_roles = [
        ("superadmin", "Superadmin", "System superadministrator with unrestricted global access"),
        ("owner", "Workspace Owner", "Tenant workspace owner with full administrative control"),
        ("admin", "Workspace Admin", "Tenant administrator managing finance, budgets, and integrations"),
        ("member", "Workspace Member", "Standard workspace member who can manage transactions and view records"),
        ("viewer", "Workspace Viewer", "Read-only access to financial reports and transactions"),
    ]

    role_objs: dict[str, Role] = {}
    for slug, name, desc in system_roles:
        existing_role = db.execute(
            select(Role).where(Role.tenant_id.is_(None), Role.slug == slug)
        ).scalar_one_or_none()

        if not existing_role:
            role = Role(
                tenant_id=None,
                name=name,
                slug=slug,
                description=desc,
                is_system=True,
            )
            db.add(role)
            db.flush()
            role_objs[slug] = role
            created_roles += 1
        else:
            role_objs[slug] = existing_role

    # 3. Associate Permissions to Roles
    # SUPERADMIN & OWNER: gets ALL permissions
    # ADMIN: gets all except billing/roles deletion
    # MEMBER: view, create, update on transactions/accounts/budgets/goals
    # VIEWER: only view permissions

    for role_slug, role in role_objs.items():
        existing_link_ids = set(
            db.execute(
                select(RolePermission.permission_id).where(RolePermission.role_id == role.id)
            ).scalars().all()
        )

        for perm in all_perms:
            should_grant = False
            if role_slug in ("superadmin", "owner"):
                should_grant = True
            elif role_slug == "admin":
                should_grant = not (perm.module in ("billing", "roles") and "delete" in perm.slug)
            elif role_slug == "member":
                should_grant = perm.module in ("transactions", "accounts", "budgets", "goals", "reports") and (
                    perm.slug.endswith(".view") or perm.slug.endswith(".create") or perm.slug.endswith(".update")
                )
            elif role_slug == "viewer":
                should_grant = perm.slug.endswith(".view")

            if should_grant and perm.id not in existing_link_ids:
                db.add(RolePermission(role_id=role.id, permission_id=perm.id))
                created_links += 1

    db.commit()
    return {"permissions": created_perms, "roles": created_roles, "role_permissions": created_links}
