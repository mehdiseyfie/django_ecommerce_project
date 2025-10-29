# ecommerce

یک پروژه Django برای فروشگاه (ecommerce).

راهنما برای آپلود به گیت‌هاب و اجرای محلی:

1. اگر مخزن در محلی ساخته نشده است، این دستورات را اجرا کنید:

```bash
# در ریشه پروژه
git init
git branch -M main
git add .
git commit -m "Initial commit: add .gitignore and README"
```

2. در گیت‌هاب یک مخزن جدید بسازید و سپس آدرس remote را اضافه و push کنید:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

3. نکات مهم قبل از push:
- از قرار گرفتن فایل‌های حساس در repo جلوگیری کنید (مثلاً `db.sqlite3`, `.env`, `config/settings_local.py`).
- مقدار `SECRET_KEY` و تنظیمات حساس را در `config/settings.py` مستقیم قرار ندهید؛ از متغیرهای محیطی استفاده کنید.
- وابستگی‌ها را در `requirements.txt` ثبت کنید: `pip freeze > requirements.txt`

4. اجرای لوکال (نمونه):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```.
