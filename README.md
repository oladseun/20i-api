# 20i Support Gatekeeper

This application provides a secure way for your clients to authenticate using their 20i hosting email and access support services (like Intercom chat) without needing a separate login.

## Features

- **Secure Login**: Verifies email against your 20i Reseller account.
- **OTP Verification**: Sends a one-time code to the user's email for secure access.
- **Intercom Integration**: Securely loads Intercom Messenger with user details (HMAC signature support).
- **No Database**: Uses 20i API as the source of truth for user data.

## 🚀 How to Let Others Test It (Easy Deployment)

To let a non-technical person test this, you can deploy it to **Render.com** (free tier).

### Quick Deployment Steps

1. **Push to GitHub** (Make sure your code is on GitHub first).
2. Go to [Render.com](https://render.com) and sign up/login.
3. Click **New +** -> **Web Service**.
4. Connect your GitHub repository.
5. Scroll down to **Environment Variables** and add:
   - `TWENTYI_API_TOKEN`: Your base64 encoded API key.
   - `INTERCOM_APP_ID`: Your Intercom App ID.
   - `INTERCOM_SECRET_KEY`: Your Intercom Secret Key.
   - `SECRET_KEY`: Generate a random string (e.g., `django-insecure-test-key`).
   - `DEBUG`: `False`
6. Click **Create Web Service**.

Once deployed, Render will give you a URL (e.g., `https://gatekeeper-xyz.onrender.com`). Send that link to anyone, and they can test it!

## Local Development

If you are a developer:

1. Clone the repo.
2. `pip install -r requirements.txt`
3. Create `.env` file with your keys.
4. `python manage.py runserver`

## Tech Stack

- **Framework**: Django 4.2
- **API Integration**: requests library for 20i API
- **Security**: hmac and hashlib for Intercom Secure Mode
- **Email**: Django email backend (console for development)

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and add your API keys:

```bash
copy .env.example .env
```

Edit `.env` and add your credentials:

```env
# 20i API Configuration
TWENTYI_API_TOKEN=your_20i_bearer_token_here

# Intercom Configuration
INTERCOM_SECRET_KEY=your_intercom_secret_key_here
INTERCOM_APP_ID=your_intercom_app_id_here

# Django Configuration
SECRET_KEY=your_django_secret_key_here
DEBUG=True
```

**Where to get your API keys:**

- **20i API Token**: Log into your 20i Reseller account → API Settings → Generate Bearer Token
- **Intercom Secret Key**: Intercom Dashboard → Settings → Installation → Identity Verification → Secret Key
- **Intercom App ID**: Intercom Dashboard → Settings → Installation → App ID
- **Django Secret Key**: Generate one using: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

### 3. Run Database Migrations

```bash
python manage.py migrate
```

### 4. Start the Development Server

```bash
python manage.py runserver
```

The application will be available at: `http://localhost:8000/`

## Usage

### 1. Login Flow

1. Navigate to `http://localhost:8000/`
2. Enter your email address (must exist in your 20i Reseller account)
3. Check your console/terminal for the 4-digit OTP code
4. Enter the OTP code on the verification page
5. Access your secure dashboard

### 2. Dashboard

Once logged in, you'll see:
- Your user information (name, email, user ID)
- Session status
- Intercom chat widget (bottom-right corner)

The Intercom widget will be authenticated with Secure Mode using your user ID and HMAC-SHA256 hash.

### 3. Logout

Click the "Logout" button in the header to clear your session and return to the login page.

## File Structure

```
20i-api/
├── manage.py                          # Django management script
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
├── .gitignore                         # Git ignore file
├── support_gatekeeper/               # Django project settings
│   ├── __init__.py
│   ├── settings.py                   # Main settings (API keys, email, etc.)
│   ├── urls.py                       # Main URL routing
│   ├── asgi.py
│   └── wsgi.py
└── gatekeeper/                       # Main application
    ├── __init__.py
    ├── apps.py
    ├── admin.py
    ├── models.py
    ├── tests.py
    ├── views.py                      # Login, OTP, Dashboard views
    ├── urls.py                       # App URL routing
    └── templates/
        └── gatekeeper/
            ├── login.html            # Email input form
            ├── verify_otp.html       # OTP verification form
            └── dashboard.html        # Dashboard with Intercom
```

## How It Works

### Step 1: Login View (Email Input)

1. User enters their email address
2. System calls 20i API: `GET https://api.20i.com/reseller/stack-users`
3. Searches for matching email in the response
4. If found: generates 4-digit OTP, stores in session, sends via email
5. If not found: shows error message

### Step 2: OTP Verification

1. User enters the 4-digit code from email
2. System validates against session-stored OTP
3. If correct: marks user as verified, stores user data in session
4. Redirects to dashboard

### Step 3: Dashboard (Intercom Secure Mode)

1. Checks if user is verified (session check)
2. Retrieves user data from session
3. Generates HMAC-SHA256 hash: `hmac(secret_key, user_id)`
4. Renders dashboard with Intercom widget
5. Passes `user_hash` to Intercom for identity verification

## Email Configuration

### Development (Console Backend)

By default, emails are printed to the console. Check your terminal to see the OTP code.

### Production (SMTP)

To use a real email service, update `support_gatekeeper/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## Security Notes

- ✅ OTP codes expire after 30 minutes (session timeout)
- ✅ CSRF protection enabled on all forms
- ✅ Intercom Secure Mode prevents user impersonation
- ✅ Session-based authentication (no passwords stored)
- ✅ HTTPS recommended for production

## Troubleshooting

### "No module named django"
Run: `pip install -r requirements.txt`

### "Error connecting to authentication service"
- Check your `TWENTYI_API_TOKEN` in `.env`
- Verify the token has permission to access stack-users endpoint
- Check your internet connection

### Intercom widget not appearing
- Verify `INTERCOM_APP_ID` is correct in `.env`
- Check browser console for JavaScript errors
- Ensure Intercom account is active

### OTP not received
- Check the console/terminal output (development mode)
- For production: verify email settings in `settings.py`

## License

MIT License - feel free to use this for your projects!
