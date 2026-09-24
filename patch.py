import re

with open('bot/handlers/tracking.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''listing_name = chat_title
    is_returning = False
    if response and response.get("status") == "ok":
        listing_name = response.get("listing_name", chat_title)
        is_returning = response.get("is_returning", False)
        
    if action == "join":
        action_text = "qaytib qo'shildi" if is_returning else "yangi obunachi qo'shildi"
    else:
        action_text = "obunachi chiqib ketdi"
        
    icon = "📥" if action == "join" else "📤"
    msg = f"{icon} {listing_name}: {action_text}\\n(Kim: {user_info})"'''

content = re.sub(r'listing_name = chat_title.*?(?=\n\s*for admin_id in)', replacement, content, flags=re.DOTALL)

with open('bot/handlers/tracking.py', 'w', encoding='utf-8') as f:
    f.write(content)
