# -*- coding: utf-8 -*-
import time
import requests
import config
import account_manager

BASE_URL = f"https://tapi.bale.ai/bot{config.BALE_BOT_TOKEN}"

def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[!] خطای ارسال پیام: {e}")

def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    params = {"offset": offset, "timeout": 20}
    try:
        response = requests.get(url, params=params, timeout=25)
        return response.json()
    except Exception:
        return None

def handle_command(chat_id, text):
    text = text.strip()

    if text == "/start":
        msg = (
            "سلام! به ربات مدیریت حساب‌ها خوش آمدید.\n\n"
            "دستورات موجود:\n"
            "🔹 /list - مشاهده لیست نشست‌های ذخیره‌شده\n"
            "🔹 /status <name> - بررسی وضعیت یک حساب\n"
            "🔹 /status_all - بررسی وضعیت تمامی حساب‌ها\n"
            "🔹 /add <name> <phone> - افزودن اکانت جدید (ارسال کد)\n"
            "🔹 /verify <name> <code> - تایید کد و ورود نهایی"
        )
        send_message(chat_id, msg)

    elif text == "/list":
        sessions = account_manager.list_sessions()
        if not sessions:
            send_message(chat_id, "❌ هیچ نشستی در سرور یافت نشد.")
            return

        reply = "📋 **نشست‌های موجود روی سرور:**\n\n"
        for idx, s in enumerate(sessions, 1):
            reply += f"{idx}. `{s}`\n"
        send_message(chat_id, reply)

    elif text == "/status_all":
        sessions = account_manager.list_sessions()
        if not sessions:
            send_message(chat_id, "❌ هیچ نشستی یافت نشد.")
            return

        send_message(chat_id, "⏳ در حال بررسی حساب‌ها، لطفاً صبور باشید...")
        report = "📊 **گزارش وضعیت حساب‌ها:**\n\n"
        for s in sessions:
            res = account_manager.check_account_status(s)
            if res["status"] == "active":
                report += f"✅ `{s}`: آنلاین ({res['name']})\n"
            else:
                report += f"⚠️ `{s}`: خطا یا منقضی‌شده\n"
        send_message(chat_id, report)

    elif text.startswith("/status "):
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            send_message(chat_id, "فرمت دستور: `/status <نام_نشست>`")
            return
        
        sess_name = parts[1].strip()
        send_message(chat_id, f"در حال بررسی `{sess_name}`...")
        res = account_manager.check_account_status(sess_name)
        if res["status"] == "active":
            send_message(chat_id, f"✅ حساب فعال است:\n👤 نام: {res['name']}")
        else:
            send_message(chat_id, f"❌ حساب در دسترس نیست:\nخطا: {res['error']}")

    elif text.startswith("/add "):
        parts = text.split()
        if len(parts) < 3:
            send_message(chat_id, "❌ فرمت اشتباه!\nمثال: `/add acc2 989123456789`")
            return
        
        sess_name = parts[1]
        phone = parts[2]
        send_message(chat_id, f"⏳ در حال درخواست کد برای `{phone}`...")
        res = account_manager.start_login_process(sess_name, phone)
        send_message(chat_id, res["message"])

    elif text.startswith("/verify "):
        parts = text.split()
        if len(parts) < 3:
            send_message(chat_id, "❌ فرمت اشتباه!\nمثال: `/verify acc2 12345`")
            return
        
        sess_name = parts[1]
        code = parts[2]
        send_message(chat_id, f"⏳ در حال تایید کد برای `{sess_name}`...")
        res = account_manager.verify_login_code(sess_name, code)
        send_message(chat_id, res["message"])

def main():
    print("[*] ربات بله با قابلیت افزودن اکانت در حال اجرا است...")
    offset = None
    while True:
        try:
            data = get_updates(offset)
            if data and data.get("ok"):
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    message = update.get("message")
                    if not message:
                        continue

                    chat_id = message["chat"]["id"]
                    text = message.get("text", "")

                    if config.ADMIN_CHAT_ID and chat_id != config.ADMIN_CHAT_ID:
                        send_message(chat_id, "⛔ شما اجازه دسترسی به این ربات را ندارید.")
                        continue

                    if text.startswith("/"):
                        handle_command(chat_id, text)

        except Exception as e:
            print(f"[!] خطای لوپ اصلی: {e}")
            time.sleep(3)

if __name__ == "__main__":
    main()
