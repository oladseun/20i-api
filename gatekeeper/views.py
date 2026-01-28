import random
import hmac
import hashlib
import requests
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages


def login_view(request):
    """
    Step 1: Login View - Email Input
    
    Accepts email input, verifies user exists in 20i API,
    generates OTP, and sends it via email.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, 'Please enter an email address.')
            return render(request, 'gatekeeper/login.html')
        
        # Call 20i API to fetch all stack users
        try:
            headers = {
                'Authorization': f'Bearer {settings.TWENTYI_API_TOKEN}',
                'Content-Type': 'application/json'
            }
            
            # Step 1: Get Reseller ID
            print(f"[DEBUG] Calling 20i API: {settings.TWENTYI_API_BASE_URL}/reseller")
            reseller_resp = requests.get(
                f'{settings.TWENTYI_API_BASE_URL}/reseller', 
                headers=headers, 
                timeout=10
            )
            
            if reseller_resp.status_code != 200:
                print(f"[ERROR] Failed to get reseller info: {reseller_resp.status_code}")
                messages.error(request, 'Error connecting to authentication service (Reseller lookup).')
                return render(request, 'gatekeeper/login.html')
                
            resellers = reseller_resp.json()
            if not resellers or len(resellers) == 0:
                messages.error(request, 'No reseller account found.')
                return render(request, 'gatekeeper/login.html')
                
            reseller_id = resellers[0].get('id')
            print(f"[DEBUG] Found Reseller ID: {reseller_id}")
            
            # Step 2: Get Stack Users for this reseller
            susers_url = f'{settings.TWENTYI_API_BASE_URL}/reseller/{reseller_id}/susers'
            print(f"[DEBUG] Calling Stack Users endpoint: {susers_url}")
            
            response = requests.get(susers_url, headers=headers, timeout=10)
            
            print(f"[DEBUG] Response status code: {response.status_code}")
            
            if response.status_code != 200:
                messages.error(request, f'Error connecting to authentication service. Status: {response.status_code}')
                return render(request, 'gatekeeper/login.html')
            
            # Step 3: Parse Dictionary Response
            # The API returns a 'contact' dict with full details (including email)
            # and a 'users' dict with summary details (where name might be the email)
            raw_data = response.json()
            
            users_data = {}
            
            # Prefer 'contact' key as it contains explicit email fields
            if 'contact' in raw_data and isinstance(raw_data['contact'], dict):
                print("[DEBUG] Found 'contact' key - using it for email verification.")
                users_data = raw_data['contact']
            
            # Fallback to 'users' key if contact is empty/missing
            if not users_data and 'users' in raw_data and isinstance(raw_data['users'], dict):
                print("[DEBUG] Found 'users' key - using it as fallback.")
                users_data = raw_data['users']
            
            # Fallback to raw data if neither exists (old API structure?)
            if not users_data:
                users_data = raw_data
            
            print(f"[DEBUG] Input email: '{email}'")
            print(f"[DEBUG] Found {len(users_data)} items to check")
            
            # Search for user with matching email
            user_found = None
            found_user_id = None
            
            if isinstance(users_data, dict):
                for key, data in users_data.items():
                    # Check explicit email field
                    api_email = data.get('email', '').strip()
                    
                    # Also check name field if it looks like an email (fallback for 'users' dict)
                    api_name = data.get('name', '').strip()
                    
                    if api_email.lower() == email.lower() or ('@' in api_name and api_name.lower() == email.lower()):
                        user_found = data
                        # Extract numeric ID from key "stack-user:123" if present
                        if ':' in key:
                            found_user_id = key.split(':')[1]
                        # If ID is explicitly in data, use that (safest)
                        if data.get('id'):
                            found_user_id = data.get('id')
                        # Fallback to key if no ID found
                        if not found_user_id:
                            found_user_id = key
                            
                        # If we matched on 'name' but not 'email', make sure we have an email for session
                        if not api_email and '@' in api_name:
                             api_email = api_name
                             
                        # Store found email back in data for session use
                        if not data.get('email'):
                            data['email'] = api_email
                            
                        print(f"[DEBUG] Match found! ID: {found_user_id}")
                        break
            elif isinstance(users_data, list):
                # Fallback if API changes structure
                for user in users_data:
                    api_email = user.get('email', '').strip()
                    
                    if api_email.lower() == email.lower():
                        user_found = user
                        found_user_id = user.get('id')
                        break
            
            if not user_found:
                messages.error(request, 'No account found with this email address.')
                return render(request, 'gatekeeper/login.html')
            
            # Generate 4-digit OTP
            otp = str(random.randint(1000, 9999))
            
            # Store OTP and user data in session
            # Construct name
            first_name = user_found.get('firstName', '')
            last_name = user_found.get('lastName', '')
            if first_name or last_name:
                name = f"{first_name} {last_name}".strip()
            else:
                name = user_found.get('person_name', email.split('@')[0])
                
            request.session['otp'] = otp
            request.session['user_email'] = email
            request.session['user_id'] = found_user_id
            request.session['user_name'] = name
            request.session.modified = True
            
            print(f"[DEBUG] Session updated. Sending OTP to {email}")
            
            # Send OTP via Email
            try:
                print(f"[DEBUG] Attempting to send email via {settings.EMAIL_BACKEND}...")
                send_mail(
                    subject='Your Support Gatekeeper Login Code',
                    message=f'Your verification code is: {otp}\n\nThis code will expire in 30 minutes.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                print(f"[DEBUG] Email sent successfully to {email}")
            except Exception as e:
                print(f"[ERROR] Failed to send email: {str(e)}")
                # Log usage of what credentials (masked)
                user_val = settings.EMAIL_HOST_USER or "None"
                pass_val = "Set" if settings.EMAIL_HOST_PASSWORD else "Not Set"
                print(f"[DEBUG] Credential status - User: {user_val}, Pass: {pass_val}")
                
                messages.error(request, f"System error sending email. Please contact support. (Ref: {type(e).__name__})")
                return render(request, 'gatekeeper/login.html')
            
            messages.success(request, f'A verification code has been sent to {email}')
            return redirect('verify_otp')
            
        except requests.RequestException as e:
            print(f"[ERROR] Request exception: {str(e)}")
            messages.error(request, f'Error connecting to authentication service. Please try again. ({str(e)})')
            return render(request, 'gatekeeper/login.html')
        except Exception as e:
            print(f"[ERROR] Unexpected exception: {str(e)}")
            messages.error(request, f'An unexpected error occurred. Please try again. ({str(e)})')
            return render(request, 'gatekeeper/login.html')
    
    return render(request, 'gatekeeper/login.html')


def verify_otp_view(request):
    """
    Step 2: Verify OTP View - OTP Input
    
    Validates the OTP code against session data and
    marks user as verified.
    """
    # Check if OTP exists in session
    if 'otp' not in request.session:
        messages.error(request, 'Session expired. Please login again.')
        return redirect('login')
    
    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()
        
        if not entered_otp:
            messages.error(request, 'Please enter the verification code.')
            return render(request, 'gatekeeper/verify_otp.html')
        
        # Validate OTP
        if entered_otp == request.session.get('otp'):
            # Mark user as verified
            request.session['verified'] = True
            
            # Clear OTP from session (no longer needed)
            del request.session['otp']
            
            messages.success(request, 'Verification successful! Welcome to your dashboard.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid verification code. Please try again.')
            return render(request, 'gatekeeper/verify_otp.html')
    
    return render(request, 'gatekeeper/verify_otp.html')


def dashboard_view(request):
    """
    Step 3: Dashboard View - Intercom Secure Mode
    
    Protected dashboard that displays Intercom widget with
    secure mode (HMAC-SHA256 hash).
    """
    # Check if user is verified
    if not request.session.get('verified'):
        messages.error(request, 'Please login to access the dashboard.')
        return redirect('login')
    
    # Get user data from session
    user_id = request.session.get('user_id')
    user_email = request.session.get('user_email')
    user_name = request.session.get('user_name')
    
    # Generate Intercom user_hash using HMAC-SHA256
    user_hash = hmac.new(
        settings.INTERCOM_SECRET_KEY.encode('utf-8'),
        str(user_id).encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    context = {
        'user_id': user_id,
        'user_email': user_email,
        'user_name': user_name,
        'user_hash': user_hash,
        'intercom_app_id': settings.INTERCOM_APP_ID,
    }
    
    return render(request, 'gatekeeper/dashboard.html', context)


def logout_view(request):
    """
    Logout view - clears session and redirects to login
    """
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')
