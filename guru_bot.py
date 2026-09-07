#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 GURU + DARK X FUSION BOT — Wingo 1M Predictor
🧠 ENGINES: GURU + DARK X (1M FIXED)
✅ MATCH = PREDICTION + RESULT
❌ NO MATCH = SHOW RESULT ONLY
"""

import asyncio
import time
import requests
import os
import random
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

try:
    from telegram import Bot
except ImportError:
    print("❌ python-telegram-bot not installed! Run: pip install python-telegram-bot")
    exit(1)

# ============================================================
# 🔥 কনফিগারেশন
# ============================================================
BOT_TOKEN = "8632082751:AAEcUqV8hFs-Id0E9uL0ltvW-e6ybZkKcJ0"
CHAT_ID = "6678981102"
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"

# ============================================================
# ওয়েব সার্ভার (পোর্ট 8080)
# ============================================================
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"GURU+DARK X FUSION BOT is running!")

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

# ============================================================
# বট ইনিশিয়ালাইজ
# ============================================================
bot = Bot(token=BOT_TOKEN)

# ============================================================
# গ্লোবাল ভেরিয়েবল
# ============================================================
match_wins = 0
match_losses = 0
match_total = 0
current_streak = 0
best_streak = 0
current_level = 1

history_data = []
last_predicted_period = None
last_predicted_signal = None
last_predicted_num = None
last_match_status = None
prediction_sent_for_period = {}
result_sent_for_period = {}

# Hourly Stats
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
hourly_report_sent = False

# ============================================================
# 🧠 GURU ALGORITHM
# ============================================================
def guru_algorithm(period_number):
    str_period = str(period_number)
    digit_sum = sum(int(c) for c in str_period if c.isdigit())
    remainder = digit_sum % 10
    pred = "BIG" if remainder >= 5 else "SMALL"
    
    if pred == "BIG":
        conf = 70 + (remainder - 5) * 3
    else:
        conf = 70 + (4 - remainder) * 3
    conf = min(95, max(55, conf))
    
    return pred, remainder, conf

# ============================================================
# 🧠 DARK X ENGINE
# ============================================================
def dark_x_engine(data, level):
    """
    DARK X ALGORITHM - Anti-Loss Pattern Detection
    """
    if len(data) < 3:
        return {"prediction": "BIG", "confidence": 50, "number": 7}
    
    types = [d['side'] for d in data[:10]]
    last1 = types[0] if len(types) > 0 else "BIG"
    last2 = types[1] if len(types) > 1 else "BIG"
    last3 = types[2] if len(types) > 2 else "BIG"
    
    # Base prediction
    if last1 == "SMALL":
        pred = "BIG"
        conf = 75
    else:
        pred = "SMALL"
        conf = 60
    
    # Strong patterns
    if last1 == "BIG" and last2 == "BIG":
        pred = "SMALL"
        conf = 90
    elif last1 == "SMALL" and last2 == "SMALL":
        pred = "BIG"
        conf = 95
    elif last1 == "SMALL" and last2 == "BIG":
        pred = "BIG"
        conf = 70
    elif last1 == "BIG" and last2 == "SMALL":
        pred = "BIG"
        conf = 85
    
    # Triple pattern detection
    if last1 == last2 == last3:
        pred = "SMALL" if last1 == "BIG" else "BIG"
        conf = 98
    
    # Level based adjustment (recovery)
    if level == 3 and len(data) > 0:
        latest_num = data[0]['number']
        pred = "SMALL" if latest_num >= 5 else "BIG"
        conf = 99
    
    # Number prediction
    if pred == "BIG":
        # BIG numbers: 5,6,7,8,9
        num = random.choice([5, 6, 7, 8, 9])
    else:
        # SMALL numbers: 0,1,2,3,4
        num = random.choice([0, 1, 2, 3, 4])
    
    return {"prediction": pred, "confidence": conf, "number": num}

# ============================================================
# 🧠 FUSION ENGINE (GURU + DARK X)
# ============================================================
def fusion_predict(period_number, data, level):
    guru_pred, guru_num, guru_conf = guru_algorithm(period_number)
    dark = dark_x_engine(data, level)
    dark_pred = dark['prediction']
    dark_conf = dark['confidence']
    
    if guru_pred == dark_pred:
        matched = True
        final_pred = guru_pred
        final_num = guru_num
        final_conf = int((guru_conf + dark_conf) / 2)
    else:
        matched = False
        final_pred = guru_pred
        final_num = guru_num
        final_conf = guru_conf
    
    return {
        'matched': matched,
        'prediction': final_pred,
        'number': final_num,
        'confidence': final_conf,
        'guru': guru_pred,
        'guru_conf': guru_conf,
        'dark': dark_pred,
        'dark_conf': dark_conf,
        'dark_num': dark['number']
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
    global hourly_stats, last_hour_report_time, hourly_report_sent
    
    current_time = time.time()
    
    if current_time - last_hour_report_time >= 3600 and not hourly_report_sent:
        total = hourly_stats['total_rounds']
        wins = hourly_stats['total_wins']
        losses = hourly_stats['total_losses']
        win_rate = (wins / total * 100) if total > 0 else 0
        
        current_hour = datetime.now().strftime('%I:%M %p')
        
        msg = (
            f"📊 *HOURLY PERFORMANCE REPORT*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🕐 *TIME:* {current_hour}\n"
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
            f"💎 GURU+DARK X FUSION BOT"
        )
        
        try:
            await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")
            print(f"✅ Hourly Report Sent at {current_hour}")
            hourly_report_sent = True
            last_hour_report_time = current_time
            
            hourly_stats = {
                'total_rounds': 0,
                'total_wins': 0,
                'total_losses': 0,
                'max_win_streak': 0,
                'max_loss_streak': 0,
                'current_streak': 0,
                'streak_type': 'WIN'
            }
        except Exception as e:
            print(f"❌ Failed to send hourly report: {e}")

# ============================================================
# 🚀 মেইন লুপ
# ============================================================
async def prediction_bot():
    global match_wins, match_losses, match_total
    global current_streak, best_streak, current_level
    global history_data, last_predicted_period
    global last_predicted_signal, last_predicted_num, last_match_status
    global prediction_sent_for_period, result_sent_for_period
    global hourly_report_sent

    print("🔥 GURU+DARK X FUSION BOT STARTED...")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🧠 ENGINES: GURU + DARK X (1M)")
    print("📡 MODE: 1 MINUTE")
    print("━━━━━━━━━━━━━━━━━━━━")

    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=(
                "🔥 *GURU+DARK X FUSION BOT* 🔥\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🧠 ENGINES: GURU + DARK X (1M)\n"
                "✅ MATCH = PREDICTION + RESULT\n"
                "❌ NO MATCH = SHOW RESULT ONLY\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "⏳ WAITING FOR FIRST SIGNAL..."
            ),
            parse_mode="Markdown"
        )
    except:
        pass

    while True:
        try:
            current_sec = int(time.time()) % 60
            await asyncio.sleep(60 - current_sec + 2)

            raw_list = fetch_api_data()
            if not raw_list:
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

            print(f"📡 Period: {latest_issue} | Result: {actual_num} ({actual_type})")

            # ============================================================
            # RESULT CHECK
            # ============================================================
            if last_predicted_period == latest_issue and not result_sent_for_period.get(latest_issue, False):
                if last_match_status == 'match' and last_predicted_signal is not None:
                    # শুধু সাইজ মিললে WIN (JACKPOT বাদ)
                    is_win = (last_predicted_signal == actual_type)

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
                        current_level = 1
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
                        current_level = (current_level % 3) + 1

                    match_total += 1
                    hourly_stats['total_rounds'] += 1

                    total_games = match_wins + match_losses
                    win_rate = (match_wins / total_games * 100) if total_games > 0 else 0.0

                    result_msg = (
                        f"🎯 *RESULT*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 #{latest_issue[-5:]}\n"
                        f"🎯 PRED: `{last_predicted_signal}` → `{last_predicted_num}`\n"
                        f"🎰 ACTUAL: `{actual_num}` (`{actual_type}`)\n"
                        f"📌 {status}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📊 WIN RATE: `{win_rate:.1f}%` ({match_wins}W/{match_losses}L)\n"
                        f"🔥 STREAK: `{current_streak:+d}`\n"
                        f"👑 LEVEL: `{current_level}x`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"💎 GURU+DARK X FUSION BOT"
                    )

                    try:
                        await bot.send_message(chat_id=CHAT_ID, text=result_msg, parse_mode="Markdown")
                        result_sent_for_period[latest_issue] = True
                        print(f"✅ Result sent for {latest_issue}")
                        await asyncio.sleep(1)
                    except Exception as e:
                        print(f"❌ Failed to send result: {e}")

                    await send_hourly_report()

                else:
                    result_msg = (
                        f"🎯 *RESULT*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 #{latest_issue[-5:]}\n"
                        f"🎰 ACTUAL: `{actual_num}` (`{actual_type}`)\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"💎 GURU+DARK X FUSION BOT"
                    )

                    try:
                        await bot.send_message(chat_id=CHAT_ID, text=result_msg, parse_mode="Markdown")
                        result_sent_for_period[latest_issue] = True
                        print(f"✅ No-Match result sent for {latest_issue}")
                        await asyncio.sleep(1)
                    except Exception as e:
                        print(f"❌ Failed to send result: {e}")

                last_predicted_period = None
                last_predicted_signal = None
                last_predicted_num = None
                last_match_status = None

            # ============================================================
            # NEW PREDICTION
            # ============================================================
            next_period = str(int(latest_issue) + 1)

            if not prediction_sent_for_period.get(next_period, False):
                pred = fusion_predict(next_period, history_data, current_level)
                last_match_status = 'match' if pred['matched'] else 'no_match'

                # ডিবাগ
                print(f"🔮 Next: {next_period}")
                print(f"   GURU: {pred['guru']} ({pred['guru_conf']}%)")
                print(f"   DARK X: {pred['dark']} ({pred['dark_conf']}%)")
                print(f"   MATCH: {pred['matched']}")

                if pred['matched']:
                    pred_msg = (
                        f"🔥 *PREDICTION* 🔥\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 #{next_period[-5:]}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"✅ MATCH FOUND!\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🎯 *{pred['prediction']}*\n"
                        f"🔢 NUMBER: `{pred['number']}`\n"
                        f"⚡ CONF: `{pred['confidence']}%`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🧠 GURU: `{pred['guru']}` ({pred['guru_conf']}%)\n"
                        f"🧠 DARK X: `{pred['dark']}` ({pred['dark_conf']}%) → {pred['dark_num']}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"👑 LEVEL: `{current_level}x`\n"
                        f"⏳ RESULT AWAITING...\n"
                        f"💎 GURU+DARK X FUSION BOT"
                    )

                    last_predicted_period = next_period
                    last_predicted_signal = pred['prediction']
                    last_predicted_num = pred['number']
                    prediction_sent_for_period[next_period] = True

                    try:
                        await bot.send_message(chat_id=CHAT_ID, text=pred_msg, parse_mode="Markdown")
                        print(f"✅ Prediction sent for {next_period}")
                    except Exception as e:
                        print(f"❌ Failed to send prediction: {e}")

                else:
                    no_match_msg = (
                        f"❌ *NO MATCH*\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 #{next_period[-5:]}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🧠 GURU: `{pred['guru']}` ({pred['guru_conf']}%)\n"
                        f"🧠 DARK X: `{pred['dark']}` ({pred['dark_conf']}%) → {pred['dark_num']}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"❌ NO MATCH FOUND\n"
                        f"⏳ RESULT WILL BE SHOWN...\n"
                        f"💎 GURU+DARK X FUSION BOT"
                    )

                    last_predicted_period = next_period
                    last_predicted_signal = None
                    last_predicted_num = None
                    prediction_sent_for_period[next_period] = True

                    try:
                        await bot.send_message(chat_id=CHAT_ID, text=no_match_msg, parse_mode="Markdown")
                        print(f"✅ No-Match prediction sent for {next_period}")
                    except Exception as e:
                        print(f"❌ Failed to send prediction: {e}")

                if len(prediction_sent_for_period) > 5:
                    oldest = min(prediction_sent_for_period.keys())
                    del prediction_sent_for_period[oldest]
                if len(result_sent_for_period) > 5:
                    oldest = min(result_sent_for_period.keys())
                    del result_sent_for_period[oldest]

        except Exception as e:
            print(f"❌ Error in main loop: {e}")
            await asyncio.sleep(5)

if __name__ == '__main__':
    print("🔥 GURU+DARK X FUSION BOT")
    print("━━━━━━━━━━━━━━━━━━━━")
    print(f"🤖 TOKEN: {BOT_TOKEN[:10]}...")
    print(f"📡 CHAT: {CHAT_ID}")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🧠 ENGINES: GURU + DARK X")
    print("📡 MODE: 1 MINUTE")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🔄 Starting bot...")
    asyncio.run(prediction_bot())
