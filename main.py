#!/usr/bin/env python3
# ================== التثبيت التلقائي للمكتبات ==================
import subprocess
import sys
import time

def install_packages():
    packages = ['pyTelegramBotAPI==4.14.0', 'requests==2.31.0']
    for package in packages:
        try:
            __import__(package.split('==')[0].lower())
        except ImportError:
            print(f'📦 Installing {package}...')
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

install_packages()

# ================== استيراد المكتبات ==================
import telebot
import requests
import os
from datetime import datetime, timedelta
from telebot import apihelper
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# ================== حل مشكلة المنفذ في Render ==================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")
    
    def log_message(self, format, *args):
        pass

def run_http_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"🌐 HTTP dummy server running on port {port}")
    server.serve_forever()

http_thread = threading.Thread(target=run_http_server, daemon=True)
http_thread.start()
print("✅ HTTP dummy server started for Render")

# ================== تكوين البوت ==================
BOT_TOKEN = os.getenv('BOT_TOKEN', '8715052656:AAGLzpeGJTOaibykJhV8bbL-fn1ge9o8uhk')
bot = telebot.TeleBot(BOT_TOKEN)

# إزالة webhook
try:
    bot.remove_webhook()
    time.sleep(1)
except Exception as e:
    print(f"⚠️ Could not remove webhook: {e}")

# تخزين مؤقت
user_data_cache = {}

# ================== دالة إرسال OTP (مطابقة للسكربت المحلي) ==================
def send_otp(msisdn):
    """إرسال رمز OTP - نفس السكربت المحلي الذي عمل"""
    url = 'https://apim.djezzy.dz/oauth2/registration'
    payload = f'msisdn={msisdn}&client_id=6E6CwTkp8H1CyQxraPmcEJPQ7xka&scope=smsotp'
    headers = {
        'User-Agent': 'Djezzy/2.6.7',
        'Connection': 'close',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache',
        'Accept': 'application/json'
    }
    try:
        print(f"📤 Sending OTP to: {msisdn}")
        response = requests.post(url, data=payload, headers=headers, timeout=15)
        print(f"📥 Status code: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        if response.status_code == 200:
            return True
        else:
            print(f"⚠️ Failed with status {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f'⚠️ Error sending OTP: {e}')
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
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException as e:
        print(f'⚠️ Error verifying OTP: {e}')
        return None

def apply_gift(chat_id, msisdn, access_token, username, name):
    user_info = user_data_cache.get(str(chat_id))
    if user_info and user_info.get('last_applied'):
        last_time = datetime.fromisoformat(user_info['last_applied'])
        if datetime.now() - last_time < timedelta(days=1):
            bot.send_message(chat_id, "⚠️ You cannot use the gift now. Please wait 24 hours.")
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
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response_data = response.json()
        expected_msg = f"the subscription to the product {gift_code} successfully done"
        
        if response_data.get('message') == expected_msg:
            hidden_phone = hide_phone_number(msisdn)
            success_msg = (
                f"🎉 Gift {gift_code} activated successfully!\n\n"
                f"📣 **User details:**\n"
                f"👤 Name: {name}\n"
                f"🧑‍💻 Username: @{username}\n"
                f"📞 Phone: {hidden_phone}\n"
            )
            bot.send_message(chat_id, success_msg, parse_mode='Markdown')
            
            if str(chat_id) in user_data_cache:
                user_data_cache[str(chat_id)]['last_applied'] = datetime.now().isoformat()
            return True
        else:
            bot.send_message(chat_id, f"⚠️ Error: {response_data.get('message', 'unknown')}")
            return False
    except requests.RequestException as e:
        print(f'⚠️ Error applying gift: {e}')
        bot.send_message(chat_id, "⚠️ Error applying gift. Try again later.")
        return False

def hide_phone_number(phone_number):
    return phone_number[:4] + '*******' + phone_number[-2:]

def show_main_menu(chat_id, text="Choose an action:"):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn_gift = telebot.types.InlineKeyboardButton("🎁 Activate Walkwin Gift", callback_data='walkwingift')
    btn_new = telebot.types.InlineKeyboardButton("🔄 New Number", callback_data='send_number')
    markup.add(btn_gift, btn_new)
    bot.send_message(chat_id, text, reply_markup=markup)

# ================== Bot Handlers ==================
@bot.message_handler(commands=['start'])
def handle_start(msg):
    chat_id = msg.chat.id
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='📱 Send Phone Number', callback_data='send_number'))
    bot.send_message(chat_id, '👋 Welcome! Please send your Djezzy phone number (starts with 07).', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'send_number')
def handle_send_number(callback):
    chat_id = callback.message.chat.id
    bot.send_message(chat_id, '📱 Send your phone number now (10 digits starting with 07):')
    bot.register_next_step_handler_by_chat_id(chat_id, handle_phone_number)

def handle_phone_number(msg):
    chat_id = msg.chat.id
    text = msg.text.strip()
    
    if text.startswith('07') and len(text) == 10 and text.isdigit():
        msisdn = '213' + text[1:]
        waiting_msg = bot.send_message(chat_id, "⏳ Sending verification code... Please wait")
        if send_otp(msisdn):
            bot.delete_message(chat_id, waiting_msg.message_id)
            bot.send_message(chat_id, '🔢 OTP code sent. Please enter the code you received:')
            bot.register_next_step_handler_by_chat_id(chat_id, lambda m: handle_otp(m, msisdn))
        else:
            bot.delete_message(chat_id, waiting_msg.message_id)
            bot.send_message(chat_id, '⚠️ Failed to send OTP. Check the number and try again.')
            show_main_menu(chat_id, "Try again:")
    else:
        bot.send_message(chat_id, '⚠️ Invalid number. Must start with 07 and be 10 digits.')
        show_main_menu(chat_id, "Try again:")

def handle_otp(msg, msisdn):
    chat_id = msg.chat.id
    otp = msg.text.strip()
    waiting_msg = bot.send_message(chat_id, "⏳ Verifying code...")
    tokens = verify_otp(msisdn, otp)
    bot.delete_message(chat_id, waiting_msg.message_id)
    
    if tokens:
        user_data_cache[str(chat_id)] = {
            'username': msg.from_user.username or "none",
            'telegram_id': chat_id,
            'msisdn': msisdn,
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token'],
            'last_applied': None
        }
        bot.send_message(chat_id, '✅ Verification successful!')
        show_main_menu(chat_id)
    else:
        bot.send_message(chat_id, '⚠️ Invalid OTP code. Try again.')
        show_main_menu(chat_id, "Enter number again or try again:")

@bot.callback_query_handler(func=lambda call: call.data == 'walkwingift')
def handle_walkwingift(callback):
    chat_id = callback.message.chat.id
    user_info = user_data_cache.get(str(chat_id))
    
    if not user_info:
        bot.send_message(chat_id, "⚠️ You haven't logged in yet. Send your number first.")
        handle_send_number(callback)
        return
    
    waiting_msg = bot.send_message(chat_id, "⏳ Activating gift...")
    apply_gift(chat_id, user_info['msisdn'], user_info['access_token'], 
               user_info['username'], callback.from_user.first_name)
    bot.delete_message(chat_id, waiting_msg.message_id)
    show_main_menu(chat_id, "Operation completed. Choose another action:")

# ================== Start Bot ==================
if __name__ == '__main__':
    print('✅ Starting bot...')
    print('📦 All packages installed')
    
    while True:
        try:
            print('🚀 Bot is running...')
            bot.polling(none_stop=True, interval=0, timeout=20)
        except apihelper.ApiTelegramException as e:
            if "409" in str(e):
                print("⚠️ Another bot instance detected (409). Retrying in 10 seconds...")
                time.sleep(10)
                try:
                    bot.remove_webhook()
                except:
                    pass
                continue
            else:
                print(f"❌ Unexpected error: {e}")
                time.sleep(5)
        except Exception as e:
            print(f"❌ General error: {e}")
            time.sleep(5)
