import requests
from django.conf import settings

def fetch_user_conversations(user_id):
    """
    Fetches the list of conversations for a specific user from Intercom.
    Returns a list of simplified ticket objects.
    """
    if not settings.INTERCOM_ACCESS_TOKEN:
        print("[WARNING] No Intercom Access Token found.")
        return []

    url = "https://api.intercom.io/conversations"
    headers = {
        "Authorization": f"Bearer {settings.INTERCOM_ACCESS_TOKEN}",
        "Accept": "application/json"
    }
    
    # Filter by user_id (the 20i ID we stored as the Intercom contact's user_id)
    params = {
        "type": "user",
        "user_id": str(user_id),
        "per_page": 20
    }

    try:
        print(f"[DEBUG] Fetching Intercom tickets for User ID: {user_id}")
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            conversations = data.get('conversations', [])
            
            # Simplify data for the template
            tickets = []
            for conv in conversations:
                # Determine status
                state = conv.get('state', 'open')
                if state == 'closed':
                    status_label = 'Resolved'
                    status_color = 'green'
                else:
                    status_label = 'Open'
                    status_color = 'blue'
                
                # Get subject or snippet
                source = conv.get('source', {})
                subject = source.get('subject') or source.get('body', 'No Subject')
                
                # Clean up subject (remove HTML if necessary, simplified here)
                from django.utils.html import strip_tags
                subject = strip_tags(subject)
                if len(subject) > 60:
                    subject = subject[:57] + "..."

                tickets.append({
                    'id': conv.get('id'),
                    'subject': subject,
                    'created_at': conv.get('created_at'),
                    'updated_at': conv.get('updated_at'),
                    'status': status_label,
                    'status_color': status_color,
                    'link_url': f"https://app.intercom.com/a/inbox/{settings.INTERCOM_APP_ID}/inbox/conversation/{conv.get('id')}" 
                    # Note: link_url is for admin, user uses JS SDK
                })
            
            print(f"[DEBUG] Found {len(tickets)} tickets.")
            return tickets
        else:
            print(f"[ERROR] Intercom API Error: {response.status_code} - {response.text}")
            return []
            
    except requests.RequestException as e:
        print(f"[ERROR] Intercom Connection Error: {e}")
        return []

def create_ticket(user_id, email, subject, body, priority):
    """
    Creates a new conversation in Intercom on behalf of the user.
    """
    if not settings.INTERCOM_ACCESS_TOKEN:
        return False, "Missing API Token"

    url = "https://api.intercom.io/conversations"
    headers = {
        "Authorization": f"Bearer {settings.INTERCOM_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Intercom API structure for user-initiated conversation
    payload = {
        "from": {
            "type": "user",
            "user_id": str(user_id)
        },
        "body": f"[{priority.upper()} PRIORITY] {subject}\n\n{body}"
    }

    try:
        print(f"[DEBUG] Creating Intercom ticket for {user_id}: {subject}")
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("[SUCCESS] Ticket created.")
            return True, response.json().get('id')
        else:
            print(f"[ERROR] API Error: {response.status_code} - {response.text}")
            return False, f"API Error: {response.status_code}"
            
    except requests.RequestException as e:
        print(f"[ERROR] Connection Error: {e}")
        return False, str(e)
