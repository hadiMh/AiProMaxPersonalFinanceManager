# Personal Finance Manager | مدیریت مالی شخصی

> **Bootcamp project | پروژه بوت‌کمپ**
>
> This repository is part of a specialized AI training bootcamp for programmers. You receive a working Django application with a deliberately simple interface. **Your goal is to use AI coding tools to design and redesign its appearance and user experience.**
>
> این پروژه بخشی از **بوت‌کمپ تخصصی آموزش هوش مصنوعی به برنامه‌نویسان** است. شما این برنامه Django آماده را دریافت می‌کنید و **هدف این است که با استفاده از هوش مصنوعی، ظاهر و تجربه کاربری آن را طراحی کنید.**

## Choose a language | انتخاب زبان

- [🇬🇧 English](#english)
- [🇮🇷 فارسی](#فارسی)

---

<a id="english"></a>

## 🇬🇧 English

### About the project

Personal Finance Manager is a Persian, right-to-left Django web application for recording and reviewing personal financial activity. It provides a simple interface for managing bank cards, income, expenses, transfers, and financial reports. Dates are displayed and entered using the Jalali calendar.

As a bootcamp exercise, the backend and core features are ready to run locally; the intentionally plain interface is your canvas for AI-assisted UI and UX design.

### Features

- User authentication
- Separate financial data for each user
- Bank card and cash-wallet management
- Income and expense registration
- Custom income and expense categories
- Transfers between cards and cash
- Automatic card-balance calculation
- Weekly and monthly financial dashboards
- Income and expense summaries by category
- Recent transaction lists and financial charts
- Jalali date input and display
- Responsive right-to-left interface
- Demo-data generation for quick evaluation

### Requirements

- Python 3.10 or newer
- Git
- Internet access during dependency installation

### Local setup

Clone the repository and enter its directory:

```bash
git clone https://github.com/hadiMh/AiProMaxPersonalFinanceManager.git
cd AiProMaxPersonalFinanceManager
```

Create and activate a virtual environment.

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

On macOS or Linux, if the `python` command is unavailable, use `python3` instead.

Create the local database tables:

```bash
python manage.py migrate
```

Create a demo user and sample financial data:

```bash
python manage.py seed_demo
```

Run the development server:

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser and sign in with:

```text
Username: demo
Password: demo1234
```

Press `Ctrl+C` in the terminal to stop the server. Run `python manage.py runserver` again whenever you want to start the application later. Remember to activate the virtual environment first.

### Run the tests

```bash
python manage.py test
```

### Notes

- The project uses SQLite locally, so no separate database server is required.
- The local `db.sqlite3` file is generated on your computer and is not committed to Git.
- The Jalali date picker and dashboard charts load browser assets from public CDNs, so those interface elements require an internet connection.
- This configuration is intended for learning and local development, not direct production deployment.

---

<a id="فارسی"></a>

<div dir="rtl" align="right">

<h2>🇮🇷 فارسی</h2>

<h3>معرفی پروژه</h3>

<p>مدیریت مالی شخصی یک برنامه وب فارسی و راست‌چین است که با Django ساخته شده است. با استفاده از این برنامه می‌توانید فعالیت‌های مالی شخصی خود را ثبت و بررسی کنید؛ از مدیریت کارت‌های بانکی و موجودی نقدی گرفته تا ثبت درآمد، هزینه، انتقال وجه و مشاهده گزارش‌های مالی. ورود و نمایش تاریخ‌ها نیز بر اساس تقویم شمسی انجام می‌شود.</p>

<p>در این بوت‌کمپ، بخش backend و امکانات اصلی آماده اجرا هستند؛ رابط کاربری عمداً ساده نگه داشته شده تا بتوانید با کمک هوش مصنوعی، ظاهر و تجربه کاربری آن را طراحی و بازطراحی کنید.</p>

<h3>امکانات پروژه</h3>

<ul>
  <li>ورود و خروج کاربر</li>
  <li>جداسازی کامل اطلاعات مالی هر کاربر</li>
  <li>مدیریت کارت‌های بانکی و موجودی نقدی</li>
  <li>ثبت درآمد و هزینه</li>
  <li>ساخت و مدیریت دسته‌بندی‌های درآمد و هزینه</li>
  <li>انتقال وجه بین کارت‌ها و موجودی نقدی</li>
  <li>محاسبه خودکار موجودی هر کارت</li>
  <li>داشبورد مالی هفتگی و ماهانه</li>
  <li>نمایش خلاصه درآمد و هزینه بر اساس دسته‌بندی</li>
  <li>نمایش تراکنش‌های اخیر و نمودارهای مالی</li>
  <li>ورود و نمایش تاریخ شمسی</li>
  <li>رابط راست‌چین و واکنش‌گرا</li>
  <li>ساخت خودکار کاربر و اطلاعات نمایشی برای آزمایش سریع پروژه</li>
</ul>

<h3>پیش‌نیازها</h3>

<ul>
  <li>Python نسخه 3.10 یا جدیدتر</li>
  <li>Git</li>
  <li>دسترسی به اینترنت هنگام نصب وابستگی‌ها</li>
</ul>

<h3>راه‌اندازی روی سیستم شخصی</h3>

<p>ابتدا مخزن پروژه را کلون کنید و وارد پوشه آن شوید:</p>

</div>

```bash
git clone https://github.com/hadiMh/AiProMaxPersonalFinanceManager.git
cd AiProMaxPersonalFinanceManager
```

<div dir="rtl" align="right">

<p>یک محیط مجازی بسازید و آن را فعال کنید.</p>

<p>در macOS یا Linux:</p>

</div>

```bash
python3 -m venv .venv
source .venv/bin/activate
```

<div dir="rtl" align="right">

<p>در Windows PowerShell:</p>

</div>

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

<div dir="rtl" align="right">

<p>وابستگی‌های پروژه را نصب کنید:</p>

</div>

```bash
python -m pip install -r requirements.txt
```

<div dir="rtl" align="right">

<p>اگر در macOS یا Linux دستور <code dir="ltr">python</code> شناخته نشد، در دستورهای بعدی نیز به‌جای آن از <code dir="ltr">python3</code> استفاده کنید.</p>

<p>جدول‌های دیتابیس محلی را بسازید:</p>

</div>

```bash
python manage.py migrate
```

<div dir="rtl" align="right">

<p>کاربر دمو و اطلاعات مالی نمونه را ایجاد کنید:</p>

</div>

```bash
python manage.py seed_demo
```

<div dir="rtl" align="right">

<p>سرور توسعه را اجرا کنید:</p>

</div>

```bash
python manage.py runserver
```

<div dir="rtl" align="right">

<p>حالا آدرس <a href="http://127.0.0.1:8000/" dir="ltr">http://127.0.0.1:8000/</a> را در مرورگر باز کنید و با اطلاعات زیر وارد شوید:</p>

</div>

```text
Username: demo
Password: demo1234
```

<div dir="rtl" align="right">

<p>برای متوقف‌کردن سرور، در ترمینال کلیدهای <code dir="ltr">Ctrl+C</code> را فشار دهید. برای اجرای مجدد برنامه کافی است ابتدا محیط مجازی را فعال کنید و سپس دوباره دستور <code dir="ltr">python manage.py runserver</code> را اجرا کنید.</p>

<h3>اجرای تست‌ها</h3>

</div>

```bash
python manage.py test
```

<div dir="rtl" align="right">

<h3>نکات</h3>

<ul>
  <li>پروژه در حالت محلی از SQLite استفاده می‌کند و به نصب دیتابیس جداگانه نیاز ندارد.</li>
  <li>فایل محلی <code dir="ltr">db.sqlite3</code> روی سیستم شما ساخته می‌شود و داخل Git قرار نمی‌گیرد.</li>
  <li>انتخابگر تاریخ شمسی و نمودارهای داشبورد، فایل‌های موردنیاز مرورگر را از CDN دریافت می‌کنند؛ بنابراین این بخش‌ها به اتصال اینترنت نیاز دارند.</li>
  <li>تنظیمات فعلی برای آموزش و توسعه محلی مناسب است و نباید بدون آماده‌سازی‌های امنیتی مستقیماً در محیط واقعی منتشر شود.</li>
</ul>

</div>
