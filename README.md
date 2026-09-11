# Staff Application Portal

A professional FOXMC Streamlit staff recruitment portal with:

- Public FOXMC staff application form with all five requested sections and situational questions
- Discord join button
- Supabase cloud database
- Secure admin login using a bcrypt password hash
- Admin dashboard
- Search and status filters
- Pending / Under Review / Approved / Rejected workflow
- Internal admin notes
- Responsive dark professional UI
- GitHub + Streamlit Cloud deployment ready

## 1. Create the database

Create a Supabase project and open **SQL Editor**.

Paste and run `supabase.sql`.

## 2. Create the admin password hash

On your PC, install bcrypt:

```bash
pip install bcrypt
```

Then run:

```bash
python -c "import bcrypt; print(bcrypt.hashpw(b'YOUR_PASSWORD', bcrypt.gensalt()).decode())"
```

Copy the resulting hash.

## 3. Streamlit Cloud secrets

In your Streamlit Cloud app settings, add:

```toml
SUPABASE_URL = "https://YOUR-PROJECT.supabase.co"
SUPABASE_KEY = "YOUR-SERVICE-ROLE-KEY"
DISCORD_URL = "https://discord.gg/YOURSERVER"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = "YOUR_BCRYPT_HASH"
```

Important: never commit the service-role key or password hash to GitHub.

## 4. Deploy

Push these files to GitHub:

- `app.py`
- `requirements.txt`
- `supabase.sql`
- `README.md`

Then create a Streamlit Cloud app and select:

`app.py`

The app will use the secrets from Streamlit Cloud.

## Recommended production upgrades

For a larger paid service, add:

- Supabase Auth for multiple administrators
- Email/Discord webhook notifications
- Applicant status lookup page
- Admin roles and permissions
- Application review history/audit log
- Rate limiting / CAPTCHA
- Custom domain
- Privacy policy and terms
- Automated backup
