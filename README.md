# 💰 PantauDuit — Telegram-First Personal Finance Platform

Platform command center pencatatan keuangan pribadi (_personal budgeting_) terintegrasi bot Telegram. Dibangun dengan fokus pada kecepatan, privasi data pengguna, dan antarmuka modern yang intuitif.

---

## 🚀 Panduan Cepat Menjalankan Aplikasi (Terminal)

### 1. Menjalankan Frontend (Web Dashboard)

Frontend dibangun menggunakan **SvelteKit (Svelte 5)** dan **Tailwind CSS**.

Buka terminal dan jalankan:

```bash
# 1. Masuk ke folder frontend
cd frontend

# 2. Install dependencies (hanya saat pertama kali)
npm install

# 3. Jalankan development server
npm run dev
```

Buka browser di:
👉 **[http://localhost:5173](http://localhost:5173)**

---

### 2. Menjalankan Backend (Database & Seeder)

Backend menggunakan **Python**, **SQLAlchemy**, dan **PostgreSQL**.

Buka tab/jendela terminal baru dan jalankan:

```bash
# 1. Masuk ke folder backend
cd backend

# 2. Aktifkan virtual environment
source .venv/bin/activate
# (Jika belum ada .venv, buat dulu: python3 -m venv .venv)

# 3. Install dependencies (hanya saat pertama kali)
pip install -r requirements.txt

# 4. Buat file konfigurasi .env (jika belum ada)
cp .env.example .env
# Pastikan konfigurasi DATABASE_URL di .env sudah sesuai dengan PostgreSQL lokal Anda

# 5. Jalankan migrasi schema database
alembic upgrade head

# 6. Jalankan seeder data awal (RBAC, Paket Langganan, Kategori)
python -m app.seeds.runner
```

---

## 👤 Kredensial Akun Demo

Aplikasi menyediakan beberapa akun demo bawaan untuk menguji berbagai role dan tipe workspace (*Personal*, *Family*, *Enterprise Business*, *Superadmin*):

| Pengguna | Email | Kata Sandi | Role | Tipe Workspace & Deskripsi |
| :--- | :--- | :--- | :--- | :--- |
| **User A (Budi)** | `budi@pantauduit.id` | `password123` | `SUBSCRIBER` | **Personal** — Budgeting pribadi & integrasi bot Telegram |
| **User B (Hendra)** | `hendra@rahardjo.com` | `password123` | `ADMIN` | **Family** — Kolaborasi multi-akun keluarga & RBAC |
| **User C (Superadmin)** | `admin@pantauduit.id` | `password123` | `SUPERUSER` | **Platform Governance** — Tata kelola role, permission & audit log |
| **User D (Reza)** | `reza.aditya@pantauduit.id` | `password123` | `ADMIN` | **Business (Company)** — PT Pantau Duit Solusindo (HR, Shift, Fingerprint, Dokumen & Payroll) |

> 💡 **Tip**: Anda juga dapat menekan tombol **"Masuk Instan via Telegram Bot"** pada halaman login untuk masuk langsung ke akun demo.

---

## 🛠️ Perintah Berguna Lainnya

### Frontend

| Perintah          | Deskripsi                                       |
| ----------------- | ----------------------------------------------- |
| `npm run dev`     | Menjalankan local dev server dengan hot-reload  |
| `npm run check`   | Menjalankan type-checking (TypeScript & Svelte) |
| `npm run build`   | Membuat production build aplikasi               |
| `npm run preview` | Menjalankan preview dari hasil build production |

### Backend

| Perintah | Deskripsi |
| -------- | --------- |

<!-- source .venv/bin/activate -->

| `pytest` | Menjalankan automated test suite |
| `alembic upgrade head` | Menerapkan migrasi database terbaru |
| `alembic revision --autogenerate -m "pesan"` | Membuat file migrasi baru |
| `python -m app.seeds.runner` | Menjalankan seeder idempotent ke database |

---

## 📁 Struktur Direktori Proyek

```text
pantau-duit/
├── frontend/             # Antarmuka web pengguna (SvelteKit 2, Svelte 5, Tailwind v4)
│   ├── src/
│   │   ├── lib/          # Global UI components (Table, Modal, DatePicker, dsb)
│   │   └── routes/       # Halaman modul (/dashboard, /transactions, /accounts, /roles, dsb)
│   └── package.json
│
├── backend/              # Layanan backend & database schema
│   ├── alembic/          # File migrasi database SQLAlchemy
│   ├── app/
│   │   ├── core/         # Konfigurasi DB, JWT & enkripsi keamanan
│   │   ├── models/       # Definisi model tabel PostgreSQL
│   │   └── seeds/        # Script seeder data awal
│   └── requirements.txt  # Python package dependencies
│
└── README.md             # Panduan proyek
```
