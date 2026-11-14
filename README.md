# NUDL — Nangarhar University Digital Library (Flat Layout)

ټول د پروژې فایلونه په همدې یوه فولډر کې دي؛ هېڅ فرعي فولډر په ZIP کې نشته.

## نصب په Windows
```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```
PostgreSQL کې `nudl` database جوړ کړئ او `.env` کې `DATABASE_URL` او `SECRET_KEY` تنظیم کړئ.

## لومړی Admin جوړول
```powershell
python create_admin.py --name "NUDL Admin" --email "admin@nudl.edu.af" --password "Use-A-Long-Unique-Password"
```
## سرور چلول
```powershell
uvicorn main:app --reload
```
Docs: http://127.0.0.1:8000/docs

یادونه: د PDF فایلونو لپاره `private_uploads` فولډر به د سرور د لومړي ځل چلېدو پر مهال په اتومات ډول جوړ شي. `.env` او اصلي پاسورډونه GitHub ته مه پورته کوئ.
