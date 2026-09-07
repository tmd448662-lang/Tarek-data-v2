#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 GURU + RGB FUSION BOT — Wingo 1M Predictor
🧠 ENGINE 1: GURU (Digit Sum % 10)
🧠 ENGINE 2: RGB (1-Minute Period Pattern — FIXED)
✅ MATCH = PREDICTION পাঠাবে
❌ NO MATCH = শুধু রেজাল্ট দেখাবে
📡 ORDER: RESULT → PREDICTION
📊 HOURLY REPORT
🤖 Bot: @Tarek3o
"""

import asyncio
import time
import requests
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

try:
    from telegram import Bot
except ImportError:
    print("❌ python-telegram-bot not installed! Run: pip install python-telegram-bot")
    exit(1)

# ==================== কনফিগারেশন ====================
BOT_TOKEN = "8386058038:AAEwayH-C4AUr7L_tx6Ecz__xpIXnrekJw0"
CHAT_ID = "5012028880"
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"

# ==================== ওয়েব সার্ভার ====================
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"GURU+RGB FUSION BOT is running!")

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
match_wins = 0
match_losses = 0
match_total = 0
current_streak = 0
best_streak = 0

history_data = []
last_predicted_period = None
last_predicted_signal = None
last_predicted_num = None
last_match_status = None
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
# 🧠 ENGINE 1: GURU ALGORITHM (Digit Sum % 10)
# ============================================================
def guru_algorithm(period_number):
    str_period = str(period_number)
    digit_sum = sum(int(c) for c in str_period if c.isdigit())
    remainder = digit_sum % 10
    pred = "BIG" if remainder >= 5 else "SMALL"
    
    # কনফিডেন্স: remainder যত বেশি/কম তত বেশি
    if pred == "BIG":
        conf = 70 + (remainder - 5) * 3
    else:
        conf = 70 + (4 - remainder) * 3
    conf = min(95, max(55, conf))
    
    return pred, remainder, conf

# ============================================================
# 🧠 ENGINE 2: RGB ALGORITHM (১ মিনিটের জন্য ফিক্সড)
# ============================================================
def rgb_algorithm(period_number):
    """
    RGB HACK — ১ মিনিটের পিরিয়ডের জন্য
    পিরিয়ডের শেষ ৫ ডিজিট থেকে ইনডেক্স বের করে
    """
    str_period = str(period_number)
    
    # শেষ ৫ ডিজিট নিন
    if len(str_period) >= 5:
        last5 = int(str_period[-5:])
    else:
        last5 = int(str_period)
    
    # প্যাটার্ন ইনডেক্স বের করুন (০-১১)
    # প্রতি ১২ পিরিয়ডে রিপিট
    pattern_index = (last5 + 5) % 12
    
    # RGB প্যাটার্ন (১২টি)
    RGB_PATTERN = [
        {"s": "BIG", "n": 7},    # 0
        {"s": "SMALL", "n": 2},  # 1
        {"s": "SMALL", "n": 4},  # 2
        {"s": "BIG", "n": 9},    # 3
        {"s": "BIG", "n": 6},    # 4
        {"s": "SMALL", "n": 0},  # 5
        {"s": "BIG", "n": 8},    # 6
        {"s": "SMALL", "n": 3},  # 7
        {"s": "SMALL", "n": 1},  # 8
        {"s": "BIG", "n": 5},    # 9
        {"s": "BIG", "n": 7},    # 10
        {"s": "SMALL", "n": 4}   # 11
    ]
    
    pred = RGB_PATTERN[pattern_index]
    return {
        "prediction": pred["s"], 
        "confidence": 78, 
        "number": pred["n"],
        "pattern_index": pattern_index
    }

# ============================================================
# 🧠 FUSION ENGINE — GURU + RGB (MATCH/NO MATCH)
# ============================================================
def fusion_predict(period_number):
    # ENGINE 1: GURU
    guru_pred, guru_num, guru_conf = guru_algorithm(period_number)
    
    # ENGINE 2: RGB
    rgb = rgb_algorithm(period_number)
    rgb_pred = rgb['prediction']
    rgb_conf = rgb['confidence']
    rgb_num = rgb['number']
    rgb_idx = rgb['pattern_index']
    
    # === MATCH CHECK ===
    if guru_pred == rgb_pred:
        matched = True
        final_pred = guru_pred
        final_num = guru_num
        final_conf = int((guru_conf + rgb_conf) / 2)
        status = "✅ MATCH FOUND"
        status_icon = "🟢"
        match_type = "FULL MATCH"
    else:
        matched = False
        final_pred = guru_pred  # GURU কে প্রাধান্য
        final_num = guru_num
        final_conf = guru_conf
        status = "❌ NO MATCH"
        status_icon = "🔴"
        match_type = "DISAGREE"
    
    return {
        'matched': matched,
        'prediction': final_pred,
        'number': final_num,
        'confidence': final_conf,
        'guru': guru_pred,
        'guru_conf': guru_conf,
        'guru_num': guru_num,
        'rgb': rgb_pred,
        'rgb_conf': rgb_conf,
        'rgb_num': rgb_num,
        'rgb_idx': rgb_idx,
        'status': status,
        'status_icon': status_icon,
        'match_type': match_type
    }

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

        msg = (
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
            f"🧠 ENGINES: GURU + RGB (1M)\n"
            f"⚡ GURU+RGB FUSION BOT"
        )
        try:
            await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")
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
    global match_wins, match_losses, match_total
    global current_streak, best_streak
    global history_data, last_predicted_period
    global last_predicted_signal, last_predicted_num, last_match_status
    global prediction_sent_for_period, hourly_stats

    print("🔥 GURU+RGB FUSION BOT STARTED...")
    print("🧠 ENGINES: GURU + RGB (1M FIXED)")
    print("✅ MATCH = SEND PREDICTION + RESULT")
    print("❌ NO MATCH = SHOW RESULT ONLY")
    print("📡 MODE: 1 MIN WINGO")
    print("━━━━━━━━━━━━━━━━━━━━")

    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=(
                "🔥 *GURU+RGB FUSION BOT* 🔥\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🧠 *ENGINE 1:* GURU (Digit Sum)\n"
                "🧠 *ENGINE 2:* RGB (1M Pattern — FIXED)\n"
                "✅ *MATCH* = SEND PREDICTION + RESULT\n"
                "❌ *NO MATCH* = SHOW RESULT ONLY\n"
                "📡 *MODE:* 1 MIN WINGO\n"
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
            # 🔥 RESULT CHECK
            # ============================================================
            if last_predicted_period == latest_issue:
                
                if last_match_status == 'match' and last_predicted_signal is not None:
                    # ✅ MATCH — WIN/LOSS কাউন্ট হবে
                    is_win = (last_predicted_signal == actual_type)
                    is_jackpot = (actual_num == last_predicted_num)

                    if is_win:
                        match_wins += 1
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
                        match_losses += 1
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

                    match_total += 1
                    hourly_stats['total_rounds'] += 1

                    total_games = match_wins + match_losses
                    win_rate = (match_wins / total_games * 100) if total_games > 0 else 0.0

                    result_msg = (
                        f"🎯 *RESULT UPDATE (MATCH)*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 PERIOD: `#{latest_issue[-5:]}`\n"
                        f"🎯 PREDICTED: `{last_predicted_signal}` → `{last_predicted_num}`\n"
                        f"🎰 ACTUAL: `{actual_num}` (`{actual_type}`)\n"
                        f"📌 RESULT: `{status}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📊 WIN RATE: `{win_rate:.1f}%` ({match_wins}W/{match_losses}L)\n"
                        f"🔥 STREAK: `{current_streak:+d}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"⚡ GURU+RGB FUSION BOT"
                    )

                    try:
                        await bot.send_message(chat_id=CHAT_ID, text=result_msg, parse_mode="Markdown")
                        await asyncio.sleep(1)
                    except:
                        pass

                    await send_hourly_report()

                else:
                    # ❌ NO MATCH — শুধু রেজাল্ট দেখাবে
                    result_msg = (
                        f"🎯 *RESULT (NO MATCH)*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 PERIOD: `#{latest_issue[-5:]}`\n"
                        f"🎰 ACTUAL: `{actual_num}` (`{actual_type}`)\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"⚡ GURU+RGB FUSION BOT"
                    )

                    try:
                        await bot.send_message(chat_id=CHAT_ID, text=result_msg, parse_mode="Markdown")
                        await asyncio.sleep(1)
                    except:
                        pass

                last_predicted_period = None
                last_predicted_signal = None
                last_predicted_num = None
                last_match_status = None

            # ============================================================
            # 🔥 NEW PREDICTION
            # ============================================================
            next_period = str(int(latest_issue) + 1)
            print(f"🎯 NEXT PERIOD: {next_period}")

            if not prediction_sent_for_period.get(next_period, False):
                pred = fusion_predict(next_period)
                
                last_match_status = 'match' if pred['matched'] else 'no_match'
                
                if pred['matched']:
                    # ✅ MATCH FOUND
                    prediction_msg = (
                        f"🔥 *GURU+RGB FUSION PREDICTION* 🔥\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 PERIOD: `#{next_period[-5:]}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"✅ *MATCH FOUND!*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🎯 *PREDICTION:* `{pred['prediction']}`\n"
                        f"🔢 *NUMBER:* `{pred['number']}`\n"
                        f"⚡ *CONFIDENCE:* `{pred['confidence']}%`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🧠 GURU: `{pred['guru']}` ({pred['guru_conf']}%)\n"
                        f"🧠 RGB: `{pred['rgb']}` ({pred['rgb_conf']}%) [Idx:{pred['rgb_idx']}]\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"⏳ *RESULT AWAITING...*\n"
                        f"⚡ GURU+RGB FUSION BOT"
                    )

                    last_predicted_period = next_period
                    last_predicted_signal = pred['prediction']
                    last_predicted_num = pred['number']
                    prediction_sent_for_period[next_period] = True

                    try:
                        await bot.send_message(chat_id=CHAT_ID, text=prediction_msg, parse_mode="Markdown")
                        print(f"✅ MATCH: {next_period} → {pred['prediction']}")
                    except Exception as e:
                        print(f"❌ SEND FAILED: {e}")
                        
                else:
                    # ❌ NO MATCH
                    no_match_msg = (
                        f"❌ *NO MATCH*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 PERIOD: `#{next_period[-5:]}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🧠 GURU: `{pred['guru']}` ({pred['guru_conf']}%)\n"
                        f"🧠 RGB: `{pred['rgb']}` ({pred['rgb_conf']}%) [Idx:{pred['rgb_idx']}]\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"❌ NO MATCH FOUND\n"
                        f"⏳ RESULT WILL BE SHOWN...\n"
                        f"⚡ GURU+RGB FUSION BOT"
                    )

                    last_predicted_period = next_period
                    last_predicted_signal = None
                    last_predicted_num = None
                    prediction_sent_for_period[next_period] = True

                    try:
                        await bot.send_message(chat_id=CHAT_ID, text=no_match_msg, parse_mode="Markdown")
                        print(f"❌ NO MATCH: {next_period}")
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
    print("🔥 GURU+RGB FUSION BOT")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🧠 ENGINES: GURU + RGB (1M FIXED)")
    print("✅ MATCH = SEND PREDICTION + RESULT")
    print("❌ NO MATCH = SHOW RESULT ONLY")
    print("📡 MODE: 1 MIN WINGO")
    print("━━━━━━━━━━━━━━━━━━━━")
    asyncio.run(prediction_bot())
