#!/usr/bin/env python3
# ================== Auto Install Required Libraries ==================
import subprocess
import sys
import time

def install_packages():
    packages = ['pyTelegramBotAPI==4.14.0', 'requests==2.31.0', 'flask==2.3.3', 'pysocks==1.7.1']
    for package in packages:
        try:
            __import__(package.split('==')[0].lower())
        except ImportError:
            print(f'📦 Installing {package}...')
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

install_packages()

# ================== Import Libraries ==================
import telebot
import requests
import os
from datetime import datetime, timedelta
from telebot import apihelper
import threading
from flask import Flask
import random

# ================== Flask server for Render ==================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    print(f"🌐 Flask server running on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()
print("✅ Flask server started")

# ================== Bot Configuration ==================
BOT_TOKEN = '8715052656:AAHifc8Q1Ns-u0twtvXIVS8GIpViIvQ0pHE'
bot = telebot.TeleBot(BOT_TOKEN)

# ================== Proxy Configuration ==================
# قائمة بروكسيات عامة - جرب واحدة
PROXIES = [
    {'http': 'socks5://51.158.68.68:1080', 'https': 'socks5://51.158.68.68:1080'},
    {'http': 'socks5://185.183.157.92:4145', 'https': 'socks5://185.183.157.92:4145'},
    {'http': 'http://45.77.34.171:8080', 'https': 'http://45.77.34.171:8080'},
]

# اختر بروكسي عشوائي
proxy = random.choice(PROXIES)
print(f"🔒 Using proxy: {proxy}")

# ================== Session Cleanup ==================
print("=" * 50)
print("🔧 Starting session cleanup...")
print("=" * 50)
try:
    print("📡 Removing webhook...")
    bot.remove_webhook()
    time.sleep(2)
    print("✅ Webhook removed")
    
    print("🔄 Clearing pending updates...")
    updates = bot.get_updates(offset=-1, timeout=1)
    if updates:
        last_id = updates[-1].update_id
        bot.get_updates(offset=last_id + 1, timeout=1)
        print(f"✅ Cleared {len(updates)} updates")
    else:
        print("✅ No pending updates")
    print("✅ Session cleanup completed successfully")
except Exception as e:
    print(f"⚠️ Warning during cleanup: {e}")
print("=" * 50)
print("🚀 Starting bot with proxy...")
print("=" * 50)

# In-memory storage
user_data_cache = {}

# ================== Helper Functions with Proxy ==================
def send_otp(msisdn):
    url = 'https://apim.djezzy.dz/oauth2/registration'
    payload = f'msisdn={msisdn}&client_id=6E6CwTkp8H1CyQxraPmcEJPQ7xka&scope=smsotp'
    headers = {
        'User-Agent': 'Djezzy/2.6.7',
        'Connection': 'close',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache',
        'Accept': 'application/json'
    }
    
    # جرب بدون بروكسي أولاً
    try:
        print(f"📤 Sending OTP to: {msisdn} (direct)")
        response = requests.post(url, data=payload, headers=headers, timeout=15)
        print(f"📥 Status code: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ OTP sent successfully (direct)")
            return True
    except Exception as e:
        print(f"⚠️ Direct connection failed: {e}")
    
    # جرب مع بروكسي
    try:
        print(f"📤 Sending OTP to: {msisdn} (with proxy)")
        response = requests.post(url, data=payload, headers=headers, timeout=30, proxies=proxy)
        print(f"📥 Status code: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ OTP sent successfully (with proxy)")
            return True
    except Exception as e:
        print(f"⚠️ Proxy connection failed: {e}")
    
    return False

def verify_otp(msisdn, otp):
    url = 'https://apim.djezzy.dz/oauth2/token'
    payload = f'otp={otp}&mobileNumber={msisdn}&scope=openid&client_id=6E6CwTkp8H1CyQxraPmcEJPQ7xka&client_secret=MVpXHW_ImuMsxKIwrJpoVVMHjRsa&grant_type=mobile'
    headers = {
        'User-Agent': 'Djezzy/2.6.7',
        'Connection': 'close',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache'
    }
    
    # جرب بدون بروكسي أولاً
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    
    # جرب مع بروكسي
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=20, proxies=proxy)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    
    return None

def apply_gift(chat_id, msisdn, access_token, username, name):
    user_info = user_data_cache.get(str(chat_id))
    if user_info and user_info.get('last_applied'):
        last_time = datetime.fromisoformat(user_info['last_applied'])
        if datetime.now() - last_time < timedelta(days=1):
            bot.send_message(chat_id, "⚠️ لا يمكنك استخدام الهدية الآن. الرجاء الانتظار 24 ساعة.")
            return False

    gift_code = 'GIFTWALKWIN2GO'
    url = f'https://apim.djezzy.dz/djezzy-api/api/v1/subscribers/{msisdn}/subscription-product'
    payload = {
        'data': {
            'id': 'GIFTWALKWIN',
            'type': 'products',
            'meta': {
                'services': {
                    'steps': 10000,
                    'code': gift_code,
                    'id': 'WALKWIN'
                }
            }
        }
    }
    headers = {
        'User-Agent': 'Djezzy/2.6.7',
        'Connection': 'Keep-Alive',
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': f'Bearer {access_token}'
    }

    try:
        print(f"🎁 Applying gift for {msisdn}")
        response = requests.post(url, json=payload, headers=headers, timeout=15, proxies=proxy)
        print(f"📥 Gift response status: {response.status_code}")
        print(f"📥 Gift response: {response.text}")
        
        if not response.text:
            bot.send_message(chat_id, "⚠️ استجابة فارغة من الخادم. حاول مرة أخرى.")
            return False
            
        response_data = response.json()
        expected_msg = f"the subscription to the product {gift_code} successfully done"
        
        if response_data.get('message') == expected_msg:
            hidden_phone = hide_phone_number(msisdn)
            success_msg = (
                f"🎉 تم تفعيل الهدية {gift_code} بنجاح!\n\n"
                f"📣 **تفاصيل المستخدم:**\n"
                f"👤 الاسم: {name}\n"
                f"🧑‍💻 المعرف: @{username}\n"
                f"📞 الرقم: {hidden_phone}\n"
            )
            bot.send_message(chat_id, success_msg, parse_mode='Markdown')
            
            if str(chat_id) in user_data_cache:
                user_data_cache[str(chat_id)]['last_applied'] = datetime.now().isoformat()
            return True
        else:
            error_msg = response_data.get('message', 'غير معروف')
            bot.send_message(chat_id, f"⚠️ حدث خطأ: {error_msg}")
            return False
    except Exception as e:
        print(f'⚠️ Error applying gift: {e}')
        bot.send_message(chat_id, "⚠️ حدث خطأ أثناء تطبيق الهدية. حاول مرة أخرى لاحقًا.")
        return False

def hide_phone_number(phone_number):
    return phone_number[:4] + '*******' + phone_number[-2:]

def show_main_menu(chat_id, text="اختر الإجراء الذي تود القيام به:"):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn_gift = telebot.types.InlineKeyboardButton("🎁 تفعيل هدية Walkwin", callback_data='walkwingift')
    btn_new = telebot.types.InlineKeyboardButton("🔄 رقم جديد", callback_data='send_number')
    markup.add(btn_gift, btn_new)
    bot.send_message(chat_id, text, reply_markup=markup)

# ================== Bot Handlers ==================
@bot.message_handler(commands=['start'])
def handle_start(msg):
    chat_id = msg.chat.id
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='📱 إرسال رقم الهاتف', callback_data='send_number'))
    bot.send_message(chat_id, '👋 مرحبًا! الرجاء إرسال رقم هاتف Djezzy الخاص بك (يبدأ بــ 07).', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'send_number')
def handle_send_number(callback):
    chat_id = callback.message.chat.id
    bot.send_message(chat_id, '📱 أرسل رقم هاتفك الآن (10 أرقام تبدأ بـ 07):')
    bot.register_next_step_handler_by_chat_id(chat_id, handle_phone_number)

def handle_phone_number(msg):
    chat_id = msg.chat.id
    text = msg.text.strip()
    
    if text.startswith('07') and len(text) == 10 and text.isdigit():
        msisdn = '213' + text[1:]
        waiting_msg = bot.send_message(chat_id, "⏳ جاري إرسال رمز التحقق... الرجاء الانتظار")
        if send_otp(msisdn):
            bot.delete_message(chat_id, waiting_msg.message_id)
            bot.send_message(chat_id, '🔢 تم إرسال رمز OTP. أرسل الرمز الذي تلقيته:')
            bot.register_next_step_handler_by_chat_id(chat_id, lambda m: handle_otp(m, msisdn))
        else:
            bot.delete_message(chat_id, waiting_msg.message_id)
            bot.send_message(chat_id, '⚠️ فشل إرسال رمز OTP. تحقق من الرقم وحاول مرة أخرى.')
            show_main_menu(chat_id, "يمكنك المحاولة مرة أخرى:")
    else:
        bot.send_message(chat_id, '⚠️ رقم غير صالح. يجب أن يبدأ بـ 07 ويتكون من 10 أرقام.')
        show_main_menu(chat_id, "أعد المحاولة:")

def handle_otp(msg, msisdn):
    chat_id = msg.chat.id
    otp = msg.text.strip()
    waiting_msg = bot.send_message(chat_id, "⏳ جاري التحقق من الرمز...")
    tokens = verify_otp(msisdn, otp)
    bot.delete_message(chat_id, waiting_msg.message_id)
    
    if tokens:
        user_data_cache[str(chat_id)] = {
            'username': msg.from_user.username or "لا يوجد",
            'telegram_id': chat_id,
            'msisdn': msisdn,
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token'],
            'last_applied': None
        }
        bot.send_message(chat_id, '✅ تم التحقق بنجاح!')
        show_main_menu(chat_id)
    else:
        bot.send_message(chat_id, '⚠️ رمز OTP غير صحيح. حاول مرة أخرى.')
        show_main_menu(chat_id, "أعد إدخال الرقم أو حاول مرة أخرى:")

@bot.callback_query_handler(func=lambda call: call.data == 'walkwingift')
def handle_walkwingift(callback):
    chat_id = callback.message.chat.id
    user_info = user_data_cache.get(str(chat_id))
    
    if not user_info:
        bot.send_message(chat_id, "⚠️ لم تقم بتسجيل الدخول بعد. أرسل رقمك أولاً.")
        handle_send_number(callback)
        return
    
    waiting_msg = bot.send_message(chat_id, "⏳ جاري تفعيل الهدية...")
    apply_gift(chat_id, user_info['msisdn'], user_info['access_token'], 
               user_info['username'], callback.from_user.first_name)
    bot.delete_message(chat_id, waiting_msg.message_id)
    show_main_menu(chat_id, "تم تنفيذ العملية. اختر خيارًا آخر:")

# ================== Start Bot ==================
if __name__ == '__main__':
    print('✅ Bot is ready with proxy support')
    
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)
