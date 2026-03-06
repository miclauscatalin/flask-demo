# 📋 Task Organizer — Flask & Python

Scroll Down for English Version

> **Aplicație web completă** pentru gestionarea sarcinilor personale, cu autentificare în doi pași (2FA), memento-uri prin email, upload de imagini și panou de administrare.
>
> **Full-stack web app** for personal task management with two-factor authentication (2FA), email reminders, image uploads and admin panel.

---

## ✨ Funcționalități / Features

| Funcționalitate | Detalii |
|---|---|
| 🔐 Autentificare | Înregistrare, login, logout, "Ține-mă minte" |
| 🔑 2FA prin email | Cod de 6 cifre trimis pe email, expiră în 10 min |
| 🔄 Reset parolă | Cod trimis pe email, expiră în 15 min |
| ✅ Gestionare sarcini | Creare, editare, vizualizare, ștergere, marcare ca finalizat |
| 📅 Scadențe & memento-uri | Dată de scadență + dată de memento cu email automat |
| 📸 Upload imagini | Max 5 poze/task (JPG, PNG, GIF, WEBP), max 8 MB fiecare |
| 🔩 Lightbox | Click pe imagine → vizualizare fullscreen |
| 📋 Clipboard paste | Ctrl+V direct în zona de upload |
| 🌐 Bilingv RO/EN | Interfață și emailuri în română și engleză |
| 👑 Panou admin | Gestionare utilizatori, promovare/retrogradare rol |
| 📧 Configurare SMTP | Interfață web pentru setările de email (doar admin) |
| 📆 Export calendar | Descarcă sarcina ca fișier .ICS (Google Calendar, Outlook) |
| ⏰ Scheduler | APScheduler verifică mementourile la fiecare minut |

---

## 🖼️ Structura proiectului / Project Structure

```
flask-demo/
├── app.py                  # Aplicația principală Flask, toate rutele
├── models.py               # Modele SQLAlchemy: User, Task, SMTPSettings
├── forms.py                # Formulare WTForms
├── config.py               # Configurare (citește din .env)
├── scheduler.py            # APScheduler — trimite emailuri memento
├── init_db.py              # Script inițializare bază de date
├── migrate_lang.py         # Migrare DB: coloana preferred_lang
├── requirements.txt        # Dependențe Python
├── .env.example            # Șablon fișier de configurare (copiază ca .env)
├── services/
│   ├── brevo_email.py      # Trimitere email prin SMTP (Brevo / alt provider)
│   └── brevo_sms.py        # Placeholder SMS
├── static/
│   ├── app.js              # JavaScript client (i18n, search, lightbox)
│   ├── styles.css          # Stiluri CSS globale
│   ├── logo.png            # Logo aplicație
│   └── uploads/            # Imagini încărcate de utilizatori (auto-creat)
└── templates/
    ├── base.html           # Layout de bază (navbar, footer, i18n, lightbox)
    ├── index.html          # Pagina principală
    ├── login.html          # Autentificare
    ├── register.html       # Înregistrare
    ├── verify_2fa.html     # Verificare cod 2FA
    ├── forgot_password.html
    ├── reset_password.html
    ├── tasks.html          # Lista sarcini + formular adăugare
    ├── task_view.html      # Vizualizare detaliu sarcină
    ├── task_edit.html      # Editare sarcină
    ├── profile.html        # Profil utilizator + setare email
    ├── smtp.html           # Configurare SMTP (doar admin)
    └── admin/
        └── dashboard.html  # Panou administrare utilizatori
```

---

## 🚀 Instalare și rulare locală / Installation & Local Setup

### 1. Clonează repository-ul / Clone the repository

```bash
git clone https://github.com/MiclausCatalin/flask-task-tracker.git
cd flask-task-tracker
```

### 2. Creează și activează un mediu virtual / Create and activate a virtual environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalează dependențele / Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Creează fișierul `.env` / Create the `.env` file

Copiază șablonul și completează valorile:
```bash
# Windows
copy .env.example .env

# Linux / macOS
cp .env.example .env
```

Deschide `.env` și completează:

```dotenv
# ─── OBLIGATORIU / REQUIRED ───────────────────────────────────────────
# Generează o cheie secretă puternică cu comanda de mai jos:
# Generate a strong secret key with:
#   python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=pune_cheia_ta_secreta_aici

# ─── ADMIN AUTO-CREAT / AUTO-CREATED ADMIN ────────────────────────────
# La primul start, aplicația creează automat acest utilizator admin.
# On first start, the app automatically creates this admin user.
ADMIN_USERNAME=admin
ADMIN_PASSWORD=ParolaFoartePuternica123!@#
ADMIN_EMAIL=admin@yourdomain.com

# ─── BAZA DE DATE / DATABASE ──────────────────────────────────────────
# SQLite implicit (recomandat pentru local). Schimbă pentru PostgreSQL în producție.
# Default SQLite (recommended for local). Change to PostgreSQL for production.
# DATABASE_URL=sqlite:///app.db
# DATABASE_URL=postgresql://user:password@localhost/dbname

# ─── URL APLICAȚIE / APP URL ──────────────────────────────────────────
# Folosit în emailuri pentru link-uri către task-uri.
# Used in emails for links to tasks.
APP_BASE_URL=http://localhost:5000

# ─── EMAIL SMTP ────────────────────────────────────────────────────────
# Poți configura SMTP direct din interfața web (Profil → SMTP), după login ca admin.
# You can configure SMTP directly from the web UI (Profile → SMTP) after logging in as admin.
# Câmpurile de mai jos sunt opționale dacă folosești interfața web.
# Fields below are optional if you use the web UI.
BREVO_API_KEY=optional

# ─── PRODUCȚIE / PRODUCTION ───────────────────────────────────────────
# Decomentează în producție pentru a activa cookie-uri HTTPS-only.
# Uncomment in production to enable HTTPS-only cookies.
# FLASK_ENV=production
```

### 5. Inițializează baza de date / Initialize the database

```bash
python init_db.py
```

> Dacă baza de date există deja și ai rulat o versiune anterioară, rulează și migrarea:
> If the database already exists from a previous version, also run the migration:
> ```bash
> python migrate_lang.py
> ```

### 6. Pornește aplicația / Start the application

```bash
flask run
```

Sau direct:
```bash
python app.py
```

Deschide browserul la: **http://localhost:5000**

---

## 📧 Configurare email SMTP / SMTP Email Setup

Aplicația trimite emailuri pentru:
- Coduri 2FA la login
- Coduri de resetare parolă
- Memento-uri automate pentru sarcini

**Pași configurare SMTP (recomandat: [Brevo](https://brevo.com) — plan gratuit 300 emailuri/zi):**

1. Creează cont pe [brevo.com](https://brevo.com)
2. Mergi la **SMTP & API → SMTP** și copiază:
   - Server: `smtp-relay.brevo.com`
   - Port: `587`
   - Login (username): adresa ta de email Brevo
   - Password: cheia SMTP din dashboard
3. Intră în aplicație ca **admin**
4. Click pe **SMTP** în navbar
5. Completează câmpurile și salvează
6. Testează cu butonul **Trimite email de test**

> ⚠️ Dacă SMTP nu este configurat, 2FA **nu funcționează** pentru utilizatorii non-admin.

---

## 👑 Cont Admin / Admin Account

La primul start al aplicației, contul admin este **creat automat** din valorile din `.env`:

```
username:  valoarea ADMIN_USERNAME
password:  valoarea ADMIN_PASSWORD
```

Adminul are acces la:
- Panoul de administrare utilizatori (`/admin/dashboard`)
- Configurare SMTP (poate salva setările)
- Bypass 2FA (adminul nu trece prin verificarea în doi pași)

---

## 🔐 Flux autentificare / Authentication Flow

```
Login
  │
  ├─ Admin?  ──────────────────────────→ Redirect tasks ✓
  │
  ├─ Fără email setat? ────────────────→ Redirect profil (setează emailul)
  │
  └─ User normal cu email
       │
       └─ Trimite cod 2FA pe email
            │
            └─ Verificare cod (10 min)
                 │
                 ├─ Corect ───────────→ Login ✓
                 └─ Expirat/greșit ───→ Redirecționare login
```

---

## 🌐 Bilingv RO / EN

Interfața este complet bilingvă. Comutarea se face din navbar (🇷🇴 / 🇬🇧). Preferința este salvată în `localStorage`.

**Emailurile** (2FA, memento, reset parolă) sunt trimise în limba **activă în momentul în care utilizatorul a creat ultima sarcină**. Preferința este stocată în câmpul `preferred_lang` din baza de date.

---

## 🏭 Deploy în producție / Production Deploy

### Cu Gunicorn (Linux/macOS)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Cu systemd (exemplu)

```ini
[Unit]
Description=Flask Task Organizer
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/flask-task-tracker
ExecStart=/var/www/flask-task-tracker/.venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app
Restart=always
EnvironmentFile=/var/www/flask-task-tracker/.env

[Install]
WantedBy=multi-user.target
```

### Variabile de mediu pentru producție

Asigură-te că ai setat în `.env`:
```dotenv
FLASK_ENV=production
SECRET_KEY=cheie_secreta_lunga_si_aleatoare_minimum_32_caractere
APP_BASE_URL=https://domeniultau.com
```

### Nginx reverse proxy (exemplu)

```nginx
server {
    listen 80;
    server_name domeniultau.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static/ {
        alias /var/www/flask-task-tracker/static/;
    }

    client_max_body_size 40M;
}
```

---

## 🗄️ Migrări bază de date / Database Migrations

Proiectul nu folosește Flask-Migrate. Migrările sunt scripturi Python simple:

| Script | Ce face |
|---|---|
| `init_db.py` | Creează toate tabelele de la zero |
| `migrate_lang.py` | Adaugă coloana `preferred_lang` la tabela `user` |

Dacă clonezi un repo existent cu o bază de date veche, rulează **toate** scripturile de migrare în ordine.

---

## 📦 Dependențe principale / Main Dependencies

| Pachet | Versiune | Rol |
|---|---|---|
| Flask | 3.1.3 | Framework web |
| Flask-Login | 0.6.3 | Gestionare sesiuni autentificare |
| Flask-SQLAlchemy | 3.1.1 | ORM bază de date |
| Flask-WTF | 1.2.2 | Formulare + protecție CSRF |
| APScheduler | 3.10.4 | Scheduler background pentru emailuri |
| python-dotenv | 1.2.2 | Citire variabile din `.env` |
| gunicorn | 25.1.0 | Server WSGI pentru producție |
| Werkzeug | 3.1.6 | Utilități web (hashing parole, upload) |

---

## 🔒 Securitate / Security

- Parolele sunt hash-uite cu **Werkzeug PBKDF2-SHA256**
- Protecție **CSRF** pe toate formularele (Flask-WTF)
- Cookie-uri `HttpOnly` și `SameSite=Lax` implicit
- Cookie-uri `Secure` activate automat în `FLASK_ENV=production`
- Upload-uri validate după extensie și limitate la 8 MB
- Coduri 2FA și reset cu expirare temporală
- Admin auto-creat din `.env`, nu din interfație web

---

## 📝 Licență / License

MIT License cu clauză de atribuire obligatorie.
Vezi fișierul [LICENSE](LICENSE) pentru detalii complete.

**Pe scurt:** Poți folosi, modifica și distribui codul, dar trebuie să păstrezi creditul autorului original vizibil în aplicație și documentație.

---

## 👤 Autor / Author

**MiclausCatalin**
- 📧 miclaus.catalin@gmail.com
- 🐙 [github.com/miclauscatalin](https://github.com/miclauscatalin)

- # 📋 Task Organizer — Flask & Python

> A complete full-stack web application for personal task management, featuring two-factor authentication (2FA), automated email reminders, image uploads, and an admin panel.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🔐 Authentication | Register, login, logout, "Remember me" |
| 🔑 Email 2FA | 6-digit code sent by email, expires in 10 min |
| 🔄 Password reset | Code sent by email, expires in 15 min |
| ✅ Task management | Create, edit, view, delete, mark as done |
| 📅 Due dates & reminders | Due date + reminder date with automatic email |
| 📸 Image upload | Up to 5 images/task (JPG, PNG, GIF, WEBP), max 8 MB each |
| 🔍 Lightbox | Click image → fullscreen preview |
| 📋 Clipboard paste | Ctrl+V directly into the upload zone |
| 🌐 Bilingual RO/EN | Full UI and emails in Romanian and English |
| 👑 Admin panel | User management, role promotion/demotion |
| 📧 SMTP configuration | Web UI for email settings (admin only) |
| 📆 Calendar export | Download task as .ICS file (Google Calendar, Outlook) |
| ⏰ Background scheduler | APScheduler checks reminders every minute |

---

## 🖼️ Project Structure

```
flask-demo/
├── app.py                  # Main Flask application, all routes
├── models.py               # SQLAlchemy models: User, Task, SMTPSettings
├── forms.py                # WTForms form definitions
├── config.py               # Configuration (reads from .env)
├── scheduler.py            # APScheduler — sends reminder emails
├── init_db.py              # Database initialization script
├── migrate_lang.py         # DB migration: preferred_lang column
├── requirements.txt        # Python dependencies
├── .env.example            # Configuration template (copy as .env)
├── LICENSE                 # MIT License with attribution clause
├── services/
│   ├── brevo_email.py      # Email sending via SMTP (Brevo / any provider)
│   └── brevo_sms.py        # SMS placeholder
├── static/
│   ├── app.js              # Client-side JavaScript (i18n, search, lightbox)
│   ├── styles.css          # Global CSS styles
│   ├── logo.png            # Application logo
│   └── uploads/            # User-uploaded images (auto-created)
└── templates/
    ├── base.html           # Base layout (navbar, footer, i18n, lightbox)
    ├── index.html          # Landing page
    ├── login.html          # Login page
    ├── register.html       # Registration page
    ├── verify_2fa.html     # 2FA code verification
    ├── forgot_password.html
    ├── reset_password.html
    ├── tasks.html          # Task list + add form
    ├── task_view.html      # Task detail view (read-only)
    ├── task_edit.html      # Task edit page
    ├── profile.html        # User profile + notification email
    ├── smtp.html           # SMTP configuration (admin only)
    └── admin/
        └── dashboard.html  # Admin user management panel
```

---

## 🚀 Installation & Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/miclauscatalin/flask-task-tracker.git
cd flask-task-tracker
```

### 2. Create and activate a virtual environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the `.env` file

Copy the template:
```bash
# Windows
copy .env.example .env

# Linux / macOS
cp .env.example .env
```

Open `.env` and fill in the values:

```dotenv
# ─── REQUIRED ─────────────────────────────────────────────────────────
# Generate a strong secret key with:
#   python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=paste_your_generated_key_here

# ─── AUTO-CREATED ADMIN ───────────────────────────────────────────────
# On first startup, the app automatically creates this admin user.
# You can log in immediately with these credentials.
ADMIN_USERNAME=admin
ADMIN_PASSWORD=VeryStrongPassword123!@#
ADMIN_EMAIL=admin@yourdomain.com

# ─── DATABASE ─────────────────────────────────────────────────────────
# Default: SQLite (recommended for local development).
# Change to PostgreSQL for production.
# DATABASE_URL=sqlite:///app.db
# DATABASE_URL=postgresql://user:password@localhost/dbname

# ─── APP URL ──────────────────────────────────────────────────────────
# Used in emails to generate links back to tasks.
# Change to your real domain when deploying.
APP_BASE_URL=http://localhost:5000

# ─── EMAIL SMTP (optional here) ───────────────────────────────────────
# You can configure SMTP from the web UI after logging in as admin.
# (Navbar → SMTP)
BREVO_API_KEY=optional

# ─── PRODUCTION ───────────────────────────────────────────────────────
# Uncomment to enable HTTPS-only cookies in production.
# FLASK_ENV=production
```

### 5. Initialize the database

```bash
python init_db.py
```

> If you are upgrading from a previous version with an existing database, also run all migration scripts:
> ```bash
> python migrate_lang.py
> ```

### 6. Start the application

```bash
flask run
```

Or directly:
```bash
python app.py
```

Open your browser at: **http://localhost:5000**

---

## 📧 SMTP Email Setup

The app sends emails for:
- 2FA codes at login
- Password reset codes
- Automatic task reminders

**Recommended provider: [Brevo](https://brevo.com) — free plan includes 300 emails/day.**

**Steps:**

1. Create a free account at [brevo.com](https://brevo.com)
2. Go to **SMTP & API → SMTP** and copy:
   - Server: `smtp-relay.brevo.com`
   - Port: `587`
   - Login: your Brevo email address
   - Password: your SMTP key from the dashboard
3. Log into the app as **admin**
4. Click **SMTP** in the navbar
5. Fill in the fields and save
6. Test with the **Send test email** button

> ⚠️ If SMTP is not configured, 2FA **will not work** for non-admin users.

---

## 👑 Admin Account

On first startup the admin account is **created automatically** from the `.env` values:

```
username:  value of ADMIN_USERNAME
password:  value of ADMIN_PASSWORD
```

The admin account:
- Has access to the user management panel at `/admin/dashboard`
- Can save SMTP settings
- **Bypasses 2FA** — logs in directly without an email code

---

## 🔐 Authentication Flow

```
Login
  │
  ├─ Is admin?  ────────────────────────→ Redirect to tasks ✓
  │
  ├─ No email set?  ────────────────────→ Redirect to profile (set email first)
  │
  └─ Regular user with email
       │
       └─ Send 2FA code by email
            │
            └─ Enter code (valid 10 min)
                 │
                 ├─ Correct ──────────→ Logged in ✓
                 └─ Expired / wrong ──→ Redirect to login
```

---

## 🌐 Bilingual RO / EN

The entire UI is bilingual. Switch language using the 🇷🇴 / 🇬🇧 buttons in the navbar. The preference is saved in `localStorage`.

**Emails** (2FA, reminders, password reset) are sent in the language **active when the user last created a task**. The preference is stored in the `preferred_lang` column in the database (default: `ro`).

---

## 🏭 Production Deployment

### With Gunicorn (Linux / macOS)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### systemd service example

```ini
[Unit]
Description=Flask Task Organizer
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/flask-task-tracker
ExecStart=/var/www/flask-task-tracker/.venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app
Restart=always
EnvironmentFile=/var/www/flask-task-tracker/.env

[Install]
WantedBy=multi-user.target
```

### Nginx reverse proxy example

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static/ {
        alias /var/www/flask-task-tracker/static/;
    }

    client_max_body_size 40M;
}
```

### Required `.env` values for production

```dotenv
FLASK_ENV=production
SECRET_KEY=a_very_long_random_string_at_least_32_chars
APP_BASE_URL=https://yourdomain.com
```

---

## 🗄️ Database Migrations

This project does not use Flask-Migrate. Migrations are simple Python scripts:

| Script | What it does |
|---|---|
| `init_db.py` | Creates all tables from scratch |
| `migrate_lang.py` | Adds `preferred_lang` column to the `user` table |

If you clone a repository with an existing database from an older version, run **all** migration scripts in order after `init_db.py`.

---

## 📦 Main Dependencies

| Package | Version | Role |
|---|---|---|
| Flask | 3.1.3 | Web framework |
| Flask-Login | 0.6.3 | Session / authentication management |
| Flask-SQLAlchemy | 3.1.1 | Database ORM |
| Flask-WTF | 1.2.2 | Forms + CSRF protection |
| APScheduler | 3.10.4 | Background scheduler for email reminders |
| python-dotenv | 1.2.2 | Load variables from `.env` |
| gunicorn | 25.1.0 | WSGI server for production |
| Werkzeug | 3.1.6 | Password hashing, file upload utilities |

---

## 🔒 Security

- Passwords hashed with **Werkzeug PBKDF2-SHA256**
- **CSRF protection** on all forms (Flask-WTF)
- `HttpOnly` and `SameSite=Lax` cookies by default
- `Secure` cookies automatically enabled when `FLASK_ENV=production`
- Uploads validated by extension, limited to 8 MB per file
- 2FA and reset codes expire after a set time window
- Admin account created from `.env`, never through the web UI

---

## 📝 License

MIT License with mandatory attribution clause.
See [LICENSE](LICENSE) for full details.

**In short:** You may use, modify and distribute this code freely, but you **must** keep the original author credit visible in the application UI and documentation.

---

## 👤 Author

**MiclausCatalin**
- 📧 miclaus.catalin@gmail.com
- 🐙 [github.com/miclauscatalin](https://github.com/miclauscatalin)

---

> *Built with Flask & Python — 2026*


---

> *Proiect construit cu Flask & Python — 2026*
