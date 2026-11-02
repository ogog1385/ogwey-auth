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

def check_account_status(sess_name):
    """بررسی سلامت و مشخصات عمومی اکانت"""
    sess_path = os.path.join(SESSIONS_DIR, sess_name)
    try:
        client = pyrubi.Client(sess_path)
        me = client.get_me()
        user_info = me.get("user", {})
        first_name = user_info.get("first_name", "کاربر")
        last_name = user_info.get("last_name", "")
        return {
            "status": "active",
            "name": f"{first_name} {last_name}".strip(),
            "session": sess_name
        }
    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc),
            "session": sess_name
        }

PENDING_LOGINS = {}

def start_login_process(chat_id, phone_number):
    """شروع درخواست کد تایید با اصلاح فرمت شماره"""
    # پاکسازی شماره و استانداردسازی (تبدیل 09... به 989...)
    clean_phone = phone_number.replace("+", "").strip()
    if clean_phone.startswith("0"):
        clean_phone = "98" + clean_phone[1:]
    elif not clean_phone.startswith("98"):
        clean_phone = "98" + clean_phone
        
    sess_name = f"acc_{clean_phone}"
    sess_path = os.path.join(SESSIONS_DIR, sess_name)
    
    try:
        # ساخت کلاینت و درخواست کد
        client = pyrubi.Client(sess_path)
        
        # بررسی وجود متد send_code
        if hasattr(client, "send_code"):
            res = client.send_code(clean_phone)
        else:
            # روش جایگزین در صورت تفاوت در نسخه pyrubi
            raise AttributeError("متد send_code در این نسخه از pyrubi یافت نشد.")
        
        PENDING_LOGINS[chat_id] = {"client": client, "session": sess_name}
        return {"status": "code_sent", "message": f"کد تایید با موفقیت به شماره {clean_phone}+ ارسال شد.\nلطفاً فقط کد دریافتی را بفرستید:"}
    except Exception as e:
        return {"status": "error", "message": f"خطا در ارسال کد به روبیکا:\n{str(e)}"}

def verify_login_code(chat_id, code):
    """تایید نهایی کد وارد شده"""
    user_data = PENDING_LOGINS.get(chat_id)
    if not user_data:
        return {"status": "error", "message": "ابتدا باید دستور /add را همراه با شماره تلفن ارسال کنید."}
    
    client = user_data["client"]
    try:
        client.sign_in(code)
        del PENDING_LOGINS[chat_id]
        return {"status": "success", "message": "حساب با موفقیت اضافه شد و سشن ذخیره گردید! ✅"}
    except Exception as e:
        return {"status": "error", "message": f"خطا در تایید کد: {str(e)}"}
