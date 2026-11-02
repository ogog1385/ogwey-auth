# -*- coding: utf-8 -*-
import os
import pyrubi

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")

if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)

def list_sessions():
    """برگرداندن لیست نام نشست‌های ذخیره‌شده"""
    if not os.path.exists(SESSIONS_DIR):
        return []
    files = os.listdir(SESSIONS_DIR)
    sessions_set = set()
    for f in files:
        base_name = os.path.splitext(f)[0]
        if base_name:
            sessions_set.add(base_name)
    return sorted(list(sessions_set))

def check_account_status(session_name):
    """بررسی سلامت و مشخصات عمومی اکانت"""
    sess_path = os.path.join(SESSIONS_DIR, session_name)
    try:
        client = pyrubi.Client(sess_path)
        me = client.get_me()
        user_info = me.get("user", {})
        first_name = user_info.get("first_name", "کاربر")
        last_name = user_info.get("last_name", "")
        return {
            "status": "active",
            "name": f"{first_name} {last_name}".strip(),
            "session": session_name
        }
    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc),
            "session": session_name
        }

# نگهداری موقت وضعیت‌های در حال انتظار برای هر ادمین
PENDING_LOGINS = {}

def start_login_process(chat_id, phone_number):
    """شروع درخواست کد تایید"""
    clean_phone = phone_number.replace("+", "").strip()
    sess_name = f"acc_{clean_phone}"
    sess_path = os.path.join(SESSIONS_DIR, sess_name)
    
    try:
        # ایجاد کلاینت با مسیر سشن
        client = pyrubi.Client(sess_path)
        # ارسال درخواست کد تایید با متد داخلی pyrubi
        client.send_code(phone_number)
        
        PENDING_LOGINS[chat_id] = {"client": client, "session": sess_name}
        return {"status": "code_sent", "message": f"کد تایید به شماره {phone_number} ارسال شد.\nلطفاً فقط کد دریافتی را بفرستید (مثلاً: 12345):"}
    except Exception as e:
        return {"status": "error", "message": f"خطا در ارسال کد: {str(e)}"}

def verify_login_code(chat_id, code):
    """تایید نهایی کد وارد شده و ثبت نام"""
    user_data = PENDING_LOGINS.get(chat_id)
    if not user_data:
        return {"status": "error", "message": "ابتدا باید دستور /add را همراه با شماره تلفن ارسال کنید."}
    
    client = user_data["client"]
    try:
        # تایید کد و ورود نهایی
        client.sign_in(code)
        del PENDING_LOGINS[chat_id]
        return {"status": "success", "message": "حساب با موفقیت اضافه شد و سشن ذخیره گردید! ✅"}
    except Exception as e:
        return {"status": "error", "message": f"خطا در تایید کد: {str(e)}"}
