#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 GURU SERVER BOT — Wingo 1M Predictor
🧠 Algorithm: Sum of digits % 10 → BIG >= 5 else SMALL
📡 ORDER: RESULT → PREDICTION
📊 HOURLY REPORT + RECOMMENDATION
🤖 Bot: @Tarek3o
"""

import asyncio
import time
import requests
import os
import random
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# ==================== TELEGRAM ====================
try:
    from telegram import Bot
except ImportError:
    print("❌ python-telegram-bot not installed! Run: pip install python-telegram-bot")
    exit(1)

# ==================== 🆕 কনফিগারেশন (নতুন টোকেন + চ্যাট আইডি) ====================
BOT_TOKEN = "8632082751:AAEcUqV8hFs-Id0E9uL0ltvW-e6ybZkKcJ0"
CHAT_ID = "6678981102"  # @Tarek3o এর আইডি
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"

# ==================== ওয়েব সার্ভার (Render/Railway এর জন্য) ====================
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"GURU SERVER BOT is running!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyServer)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

def keep_alive():
    while True:
        try:
            time.sleep(600)
            port = int(os.environ.get("PORT", 8080))
            requests.get(f"http://localhost:{port}/", timeout=5)
        except:
            pass

threading.Thread(target=keep_alive, daemon=True).start()

# ==================== বট ইনিশিয়ালাইজ ====================
bot = Bot(token=BOT_TOKEN)

# ==================== গ্লোবাল ভেরিয়েবল ====================
total_wins = 0
total_losses = 0
total_rounds = 0
current_streak = 0
best_streak = 0

history_data = []
last_predicted_period = None
last_predicted_signal = None
last_predicted_num = None
last_predicted_color = None
last_predicted_conf = 0
prediction_sent_for_period = {}

# ==================== হাওয়ারলি স্ট্যাটস ====================
hourly_stats = {
    'total_rounds': 0,
    'total_wins': 0,
    'total_losses': 0,
    'max_win_streak': 0,
    'max_loss_streak': 0,
    'current_streak': 0,
    'streak_type': 'WIN'
}
last_hour_report_time = time.time()

# ============================================================
# 🧠 GURU ALGORITHM — HTML এর মতো
# ============================================================
def guru_algorithm(period_number):
    """
    Period Number এর সব ডিজিটের যোগফল বের করে
    যোগফলকে ১০ দিয়ে ভাগ করলে যে remainder আসে
    ৫ বা তার বেশি হলে BIG, নাহলে SMALL
    """
    str_period = str(period_number)
    digit_sum = 0
    for ch in str_period:
        if ch.isdigit():
            digit_sum += int(ch)
    
    remainder = digit_sum % 10
    is_big = remainder >= 5
    
    # রঙ নির্ধারণ (HTML এর COLOR_MAP অনুযায়ী)
    color_map = {
        0: 'VIOLET',
        1: 'GREEN',
        2: 'RED',
        3: 'GREEN',
        4: 'RED',
        5: 'VIOLET',
        6: 'RED',
        7: 'GREEN',
        8: 'RED',
        9: 'GREEN'
    }
    
    color_emoji = {
        'VIOLET': '🟣',
        'GREEN': '🟢',
        'RED': '🔴'
    }
    
    color = color_map.get(remainder, 'UNKNOWN')
    emoji = color_emoji.get(color, '❓')
    
    # কনফিডেন্স (HTML এর মতো)
    if is_big:
        confidence = min(95, 70 + remainder * 5)
    else:
        confidence = min(95, 70 + (9 - remainder) * 5)
    
    return {
        'prediction': 'BIG' if is_big else 'SMALL',
        'number': remainder,
        'digit_sum': digit_sum,
        'remainder': remainder,
        'color': color,
        'emoji': emoji,
        'confidence': confidence
    }

# ============================================================
# 🎯 রেকমেন্ডেশন জেনারেটর
# ============================================================
def generate_recommendation(pred, stats):
    """প্রেডিকশনের ভিত্তিতে রেকমেন্ডেশন তৈরি করে"""
    recs = []
    
    # কনফিডেন্স ভিত্তিক
    if pred['confidence'] >= 85:
        recs.append("🔥 HIGH CONFIDENCE — Strong signal! Consider higher stake.")
    elif pred['confidence'] >= 70:
        recs.append("⚡ MODERATE CONFIDENCE — Safe bet with normal stake.")
    elif pred['confidence'] >= 55:
        recs.append("⚠️ LOW CONFIDENCE — Bet small or wait for better signal.")
    else:
        recs.append("🔴 VERY LOW — Avoid betting this round.")
    
    # স্ট্রিক ভিত্তিক
    if stats.get('current_streak', 0) >= 3:
        if stats.get('streak_type') == 'WIN':
            recs.append(f"🔥 {stats['current_streak']}x WIN STREAK — Ride the momentum!")
        else:
            recs.append(f"📉 {stats['current_streak']}x LOSS STREAK — Recovery mode, bet carefully.")
    
    # প্যাটার্ন ভিত্তিক
    if len(history_data) >= 5:
        recent = [h['side'] for h in history_data[:5]]
        big_count = recent.count('BIG')
        if big_count >= 4:
            recs.append("📊 Recent 5: 4+ BIGs — SMALL reversal possible soon.")
        elif big_count <= 1:
            recs.append("📊 Recent 5: 4+ SMALLs — BIG reversal possible soon.")
    
    # লস স্ট্রিক ভিত্তিক
    if stats.get('loss_streak', 0) >= 2:
        recs.append("🛡️ 2+ LOSSES — Use Martingale or wait for stronger signal.")
    
    if not recs:
        recs.append("📊 No clear pattern — bet at your own risk.")
    
    return recs

# ============================================================
# 📡 API ফেচ
# ============================================================
def fetch_api_data():
    try:
        res = requests.get(API_URL + "?t=" + str(int(time.time() * 1000)), timeout=5)
        if res.status_code == 200:
            data = res.json()
            return data.get("data", {}).get("list", [])
    except:
        pass
    return []

# ============================================================
# 📊 হাওয়ারলি রিপোর্ট
# ============================================================
async def send_hourly_report():
    global hourly_stats, last_hour_report_time

    if time.time() - last_hour_report_time >= 3600:
        total = hourly_stats['total_rounds']
        wins = hourly_stats['total_wins']
        losses = hourly_stats['total_losses']
        win_rate = (wins / total * 100) if total > 0 else 0

        report_msg = (
            f"📊 *HOURLY PERFORMANCE REPORT*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🕐 *TIME:* {datetime.now().strftime('%I:%M %p')}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔄 *TOTAL ROUNDS:* `{total}`\n"
            f"✅ *TOTAL WINS:* `{wins}`\n"
            f"❌ *TOTAL LOSSES:* `{losses}`\n"
            f"📈 *WIN RATE:* `{win_rate:.1f}%`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔥 *BEST WIN STREAK:* `{hourly_stats['max_win_streak']}x`\n"
            f"📉 *WORST LOSS STREAK:* `{hourly_stats['max_loss_streak']}x`\n"
            f"🔥 *CURRENT STREAK:* `{hourly_stats['current_streak']}x {hourly_stats['streak_type']}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ GURU SERVER BOT"
        )
        try:
            await bot.send_message(chat_id=CHAT_ID, text=report_msg, parse_mode="Markdown")
        except:
            pass

        hourly_stats = {
            'total_rounds': 0,
            'total_wins': 0,
            'total_losses': 0,
            'max_win_streak': 0,
            'max_loss_streak': 0,
            'current_streak': 0,
            'streak_type': 'WIN'
        }
        last_hour_report_time = time.time()

# ============================================================
# 🚀 মেইন লুপ
# ============================================================
async def prediction_bot():
    global total_wins, total_losses, total_rounds
    global current_streak, best_streak
    global history_data, last_predicted_period
    global last_predicted_signal, last_predicted_num
    global last_predicted_color, last_predicted_conf
    global prediction_sent_for_period, hourly_stats

    print("🔥 GURU SERVER BOT STARTED...")
    print(f"🤖 BOT: @Tarek3o")
    print(f"📡 MODE: 1 MIN WINGO")
    print("🧠 ALGORITHM: Sum of digits % 10")
    print("📊 ORDER: RESULT → PREDICTION")
    print("━━━━━━━━━━━━━━━━━━━━")

    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=(
                "🔥 *GURU SERVER BOT* 🔥\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🤖 *BOT:* @Tarek3o\n"
                "🧠 *ALGORITHM:* Digit Sum % 10\n"
                "📡 *MODE:* 1 MIN WINGO\n"
                "📊 *ORDER:* RESULT → PREDICTION\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "⏳ WAITING FOR FIRST SIGNAL..."
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Startup error: {e}")

    while True:
        try:
            current_sec = int(time.time()) % 60
            sleep_time = 60 - current_sec + 2
            await asyncio.sleep(sleep_time)

            raw_list = fetch_api_data()
            if not raw_list:
                print("⚠️ API থেকে ডেটা পাওয়া যায়নি")
                continue

            history_data = []
            for h in raw_list[:20]:
                num = int(h['number'])
                history_data.append({
                    'issueNumber': str(h['issueNumber']),
                    'number': num,
                    'side': "BIG" if num >= 5 else "SMALL"
                })

            latest = history_data[0]
            latest_issue = latest['issueNumber']
            actual_num = latest['number']
            actual_type = "BIG" if actual_num >= 5 else "SMALL"

            print(f"📡 LATEST PERIOD: {latest_issue}, NUMBER: {actual_num}")

            # ============================================================
            # 🔥 RESULT CHECK (প্রথমে রেজাল্ট)
            # ============================================================
            if last_predicted_period == latest_issue and last_predicted_signal is not None:
                is_win = (last_predicted_signal == actual_type)
                is_jackpot = (actual_num == 0 or actual_num == 5)

                if is_win:
                    total_wins += 1
                    hourly_stats['total_wins'] += 1
                    current_streak += 1
                    if current_streak > best_streak:
                        best_streak = current_streak
                    status = "✅ WIN"

                    if hourly_stats['streak_type'] == 'WIN':
                        hourly_stats['current_streak'] += 1
                    else:
                        hourly_stats['current_streak'] = 1
                        hourly_stats['streak_type'] = 'WIN'
                    if hourly_stats['current_streak'] > hourly_stats['max_win_streak']:
                        hourly_stats['max_win_streak'] = hourly_stats['current_streak']

                    if is_jackpot:
                        status = "✅ WIN ⭐ JACKPOT!"

                else:
                    total_losses += 1
                    hourly_stats['total_losses'] += 1
                    current_streak = 0
                    status = "❌ LOSS"

                    if hourly_stats['streak_type'] == 'LOSS':
                        hourly_stats['current_streak'] += 1
                    else:
                        hourly_stats['current_streak'] = 1
                        hourly_stats['streak_type'] = 'LOSS'
                    if hourly_stats['current_streak'] > hourly_stats['max_loss_streak']:
                        hourly_stats['max_loss_streak'] = hourly_stats['current_streak']

                total_rounds += 1
                hourly_stats['total_rounds'] += 1

                total_games = total_wins + total_losses
                win_rate = (total_wins / total_games * 100) if total_games > 0 else 0.0

                result_msg = (
                    f"🎯 *RESULT UPDATE*\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 PERIOD: `#{latest_issue[-5:]}`\n"
                    f"🎯 PREDICTED: `{last_predicted_signal}` → `{last_predicted_num}` ({last_predicted_color})\n"
                    f"🎰 ACTUAL: `{actual_num}` (`{actual_type}`)\n"
                    f"📌 RESULT: `{status}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📊 WIN RATE: `{win_rate:.1f}%` ({total_wins}W/{total_losses}L)\n"
                    f"🔥 STREAK: `{current_streak:+d}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"⚡ GURU SERVER BOT"
                )

                try:
                    await bot.send_message(chat_id=CHAT_ID, text=result_msg, parse_mode="Markdown")
                    await asyncio.sleep(1)
                except:
                    pass

                await send_hourly_report()

                last_predicted_period = None
                last_predicted_signal = None
                last_predicted_num = None
                last_predicted_color = None
                last_predicted_conf = 0

            # ============================================================
            # 🔥 NEW PREDICTION (রেজাল্টের পর)
            # ============================================================
            next_period = str(int(latest_issue) + 1)
            print(f"🎯 NEXT PERIOD: {next_period}")

            if not prediction_sent_for_period.get(next_period, False):
                pred = guru_algorithm(next_period)
                
                # রেকমেন্ডেশন জেনারেট
                stats_context = {
                    'current_streak': current_streak,
                    'streak_type': 'WIN' if current_streak >= 0 else 'LOSS',
                    'loss_streak': abs(current_streak) if current_streak < 0 else 0,
                    'win_streak': current_streak if current_streak > 0 else 0
                }
                recommendations = generate_recommendation(pred, stats_context)
                rec_text = "\n".join([f"• {r}" for r in recommendations[:3]])

                prediction_msg = (
                    f"🔥 *GURU SERVER PREDICTION* 🔥\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 PERIOD: `#{next_period[-5:]}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🎯 *PREDICTION:* `{pred['prediction']}`\n"
                    f"🔢 *NUMBER:* `{pred['number']}`\n"
                    f"🎨 *COLOR:* `{pred['emoji']} {pred['color']}`\n"
                    f"⚡ *CONFIDENCE:* `{pred['confidence']}%`\n"
                    f"📊 *DIGIT SUM:* `{pred['digit_sum']}` → `{pred['remainder']}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"💡 *RECOMMENDATION:*\n"
                    f"{rec_text}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"⏳ *RESULT AWAITING...*\n"
                    f"⚡ GURU SERVER BOT"
                )

                last_predicted_period = next_period
                last_predicted_signal = pred['prediction']
                last_predicted_num = pred['number']
                last_predicted_color = pred['color']
                last_predicted_conf = pred['confidence']
                prediction_sent_for_period[next_period] = True

                try:
                    await bot.send_message(chat_id=CHAT_ID, text=prediction_msg, parse_mode="Markdown")
                    print(f"✅ PREDICTION: {next_period} → {pred['prediction']} ({pred['number']})")
                except Exception as e:
                    print(f"❌ SEND FAILED: {e}")

                if len(prediction_sent_for_period) > 5:
                    oldest = min(prediction_sent_for_period.keys())
                    del prediction_sent_for_period[oldest]

        except Exception as e:
            print(f"❌ Loop Error: {e}")
            await asyncio.sleep(5)

# ==================== স্টার্ট ====================
if __name__ == '__main__':
    print("🔥 GURU SERVER BOT")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🤖 BOT: @Tarek3o")
    print(f"📡 CHAT ID: {CHAT_ID}")
    print("🧠 ALGORITHM: Digit Sum % 10")
    print("📡 MODE: 1 MIN WINGO")
    print("📊 ORDER: RESULT → PREDICTION")
    print("━━━━━━━━━━━━━━━━━━━━")
    asyncio.run(prediction_bot())
