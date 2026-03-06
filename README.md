# 📋 Task Organizer — Flask & Python

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

---

> *Proiect construit cu Flask & Python — 2026*
