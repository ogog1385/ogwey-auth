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
    session_names = set()
    for f in files:
        base_name = os.path.splitext(f)[0]
        if base_name:
            session_names.add(base_name)
    return sorted(list(session_names))

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
