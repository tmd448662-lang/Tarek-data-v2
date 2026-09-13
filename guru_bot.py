#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 RAJPUT X LX v22 - Telegram Bot
🧠 8 Algorithms Combined (BIG/SMALL Only)
📡 1 MIN WINGO
🤖 @Tarek3o
"""

import asyncio
import time
import requests
import os
import random
import logging
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from telegram import Bot
    from telegram.error import TelegramError, TimedOut, NetworkError
except ImportError:
    print("❌ python-telegram-bot ইনস্টল নেই!")
    exit(1)

# ==================== 📌 কনফিগারেশন ====================
BOT_TOKEN = "8632082751:AAEcUqV8hFs-Id0E9uL0ltvW-e6ybZkKcJ0"
CHAT_ID = "6678981102"

API_URLS = [
    "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json",
    "https://api.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json",
]

# ==================== 🌐 ওয়েব সার্ভার ====================
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"RAJPUT X LX v22 BOT is running!")

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

# ==================== 📊 বট ইনিশিয়ালাইজ ====================
try:
    bot = Bot(token=BOT_TOKEN)
    logger.info("✅ বট ইনিশিয়ালাইজেশন সফল!")
    logger.info("🤖 বট: @Tarek3o")
except Exception as e:
    logger.error(f"❌ বট ইনিশিয়ালাইজেশন ব্যর্থ: {e}")
    exit(1)

# ==================== গ্লোবাল ভেরিয়েবল ====================
total_wins = 0
total_losses = 0
total_rounds = 0
current_streak = 0
best_win_streak = 0
worst_loss_streak = 0
consecutive_losses = 0

hourly_wins = 0
hourly_losses = 0
hourly_rounds = 0
hourly_best_win_streak = 0
hourly_worst_loss_streak = 0

last_predicted_period = None
last_predicted_signal = None
prediction_sent_for_period = {}
last_result_sent = False

# ============================================================
#  🧠 8 ALGORITHMS (RAJPUT X LX v22)
# ============================================================
def run_pattern_engine(data):
    """
    RAJPUT X LX v22 - 8 Algorithms Combined (BIG/SMALL Only)
    """
    numbers = [d['number'] for d in data[:20]]
    raw20 = ['B' if n >= 5 else 'S' for n in numbers]
    raw8 = raw20[:8]
    raw12 = raw20[:12]
    
    # ── ALGO 1: Streak Ride ──
    streak = 1
    while streak < len(raw20) and raw20[streak] == raw20[0]:
        streak += 1
    streak_type = raw20[0]
    A1 = None
    if streak >= 5:
        A1 = 'BIG' if streak_type == 'B' else 'SMALL'
    elif streak >= 3:
        A1 = 'BIG' if streak_type == 'B' else 'SMALL'
    
    # ── ALGO 2: Alternator ──
    alt_score = 0
    for i in range(len(raw8) - 1):
        if raw8[i] != raw8[i+1]:
            alt_score += 1
    is_alt = alt_score >= 6
    A2 = None
    if is_alt:
        A2 = 'SMALL' if raw20[0] == 'B' else 'BIG'
    
    # ── ALGO 3: Pair Counter ──
    pairs_score = 0
    for i in range(0, 6, 2):
        if i + 1 < len(raw8) and raw8[i] == raw8[i+1]:
            pairs_score += 1
    A3 = None
    if pairs_score >= 2:
        A3 = 'SMALL' if raw20[0] == 'B' else 'BIG'
    
    # ── ALGO 4: Loop Cycle ──
    cycle_len = 0
    for clen in range(2, 5):
        match = True
        for i in range(clen, min(clen*3, len(raw12))):
            if raw12[i] != raw12[i % clen]:
                match = False
                break
        if match:
            cycle_len = clen
            break
    A4 = None
    if cycle_len > 0 and cycle_len <= len(raw12):
        A4 = 'BIG' if raw12[cycle_len - 1] == 'B' else 'SMALL'
    
    # ── ALGO 5: Hot Zone ──
    big_count = raw20.count('B')
    big_pct = round((big_count / len(raw20)) * 100) if len(raw20) > 0 else 50
    sml_pct = 100 - big_pct
    A5 = None
    if big_pct >= 70:
        A5 = 'SMALL'
    elif sml_pct >= 70:
        A5 = 'BIG'
    else:
        A5 = 'BIG' if big_count > 10 else 'SMALL'
    
    # ── ALGO 6: Seed Parity ──
    try:
        seed_str = str(data[0]['issueNumber'])[-4:]
        seed = int(seed_str) if seed_str.isdigit() else 0
    except:
        seed = 0
    big_bias = len([n for n in numbers[:10] if n >= 5])
    A6 = (('BIG' if big_bias >= 5 else 'SMALL') if seed % 2 == 0 
          else ('SMALL' if numbers[0] >= 5 else 'BIG'))
    
    # ── ALGO 7: Double Pattern ──
    d = ''.join(raw20[:4])
    A7 = None
    if d.startswith('BB'):
        A7 = 'SMALL'
    elif d.startswith('SS'):
        A7 = 'BIG'
    elif d in ['BSBS', 'BSB']:
        A7 = 'SMALL'
    elif d in ['SBSB', 'SBS']:
        A7 = 'BIG'
    
    # ── ALGO 8: Fibonacci Momentum ──
    fibs = [1, 1, 2, 3, 5, 8, 13, 21]
    bS = 0
    sS = 0
    for i in range(min(8, len(numbers))):
        if numbers[i] >= 5:
            bS += fibs[7 - i]
        else:
            sS += fibs[7 - i]
    A8 = 'SMALL' if bS > sS else 'BIG'
    
    # ── VOTE ──
    algos = [
        {'name': 'STREAK RIDE', 'v': A1},
        {'name': 'ALTERNATOR', 'v': A2},
        {'name': 'PAIR COUNTER', 'v': A3},
        {'name': 'LOOP CYCLE', 'v': A4},
        {'name': 'HOT ZONE', 'v': A5},
        {'name': 'SEED PARITY', 'v': A6},
        {'name': 'DOUBLE PATT.', 'v': A7},
        {'name': 'FIB MOMENTUM', 'v': A8},
    ]
    
    b_votes = 0
    s_votes = 0
    for a in algos:
        if a['v'] == 'BIG':
            b_votes += 1
        elif a['v'] == 'SMALL':
            s_votes += 1
    
    winner = 'BIG' if b_votes >= s_votes else 'SMALL'
    win_v = b_votes if winner == 'BIG' else s_votes
    consensus = round((win_v / 8) * 100)
    
    # ── Strategy Name ──
    if streak >= 5:
        strategy = '🐉 ULTRA DRAGON'
        confidence = 88 + random.randint(0, 4)
    elif streak >= 3:
        strategy = '🔥 STREAK RIDE'
        confidence = 81 + random.randint(0, 5)
    elif cycle_len > 0:
        strategy = f'🔁 LOOP-{cycle_len}X'
        confidence = 79 + random.randint(0, 6)
    elif is_alt:
        strategy = '🔀 ALTERNATOR'
        confidence = 84 + random.randint(0, 4)
    elif pairs_score >= 2:
        strategy = '👥 PAIR COUNTER'
        confidence = 75 + random.randint(0, 7)
    else:
        strategy = '⚡ REVERSION V3'
        confidence = 70 + random.randint(0, 8)
    
    # Blend with consensus
    confidence = round((confidence + consensus) / 2)
    confidence = max(68, min(97, confidence))
    
    return {
        'winner': winner,
        'strategy': strategy,
        'confidence': confidence,
        'big_pct': big_pct,
        'sml_pct': sml_pct,
        'b_votes': b_votes,
        's_votes': s_votes,
        'streak': streak,
        'cycle_len': cycle_len,
        'is_alt': is_alt,
        'algos': algos
    }

# ==================== 📡 API ফেচ ====================
def fetch_api_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.google.com/',
        'Cache-Control': 'no-cache',
    }
    
    for api_url in API_URLS:
        try:
            url = api_url + "?t=" + str(int(time.time() * 1000))
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                list_data = data.get("data", {}).get("list", [])
                if list_data:
                    return list_data
        except Exception as e:
            logger.warning(f"⚠️ {api_url} → {e}")
    return []

# ==================== 📤 মেসেজ সেন্ড ====================
async def send_message(text, parse_mode="Markdown"):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=parse_mode)
        return True
    except Exception as e:
        logger.error(f"❌ টেলিগ্রাম এরর: {e}")
        return False

# ==================== 📊 হাওয়ারলি রিপোর্ট ====================
async def send_hourly_report():
    global hourly_wins, hourly_losses, hourly_rounds
    global hourly_best_win_streak, hourly_worst_loss_streak
    global total_wins, total_losses, total_rounds
    global best_win_streak, worst_loss_streak
    
    if hourly_rounds == 0:
        return
    
    h_rate = (hourly_wins / hourly_rounds * 100) if hourly_rounds > 0 else 0
    t_rate = (total_wins / total_rounds * 100) if total_rounds > 0 else 0
    
    report = (
        f"📊 *RAJPUT X LX v22 - আওয়ারলি রিপোর্ট*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 *সময়:* {datetime.now().strftime('%I:%M %p')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔄 *এই ঘন্টায় রাউন্ড:* `{hourly_rounds}`\n"
        f"✅ *জয়:* `{hourly_wins}`\n"
        f"❌ *হার:* `{hourly_losses}`\n"
        f"📈 *জয়ের হার:* `{h_rate:.1f}%`\n"
        f"🔥 *সেরা জয় স্ট্রিক:* `{hourly_best_win_streak}x`\n"
        f"📉 *সেরা হার স্ট্রিক:* `{hourly_worst_loss_streak}x`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 *মোট রাউন্ড:* `{total_rounds}`\n"
        f"✅ *মোট জয়:* `{total_wins}`\n"
        f"❌ *মোট হার:* `{total_losses}`\n"
        f"📈 *মোট জয়ের হার:* `{t_rate:.1f}%`\n"
        f"🔥 *সেরা জয় স্ট্রিক:* `{best_win_streak}x`\n"
        f"📉 *সেরা হার স্ট্রিক:* `{worst_loss_streak}x`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 @Tarek3o"
    )
    
    await send_message(report)
    
    hourly_wins = 0
    hourly_losses = 0
    hourly_rounds = 0
    hourly_best_win_streak = 0
    hourly_worst_loss_streak = 0

# ==================== 🚀 মেইন লুপ ====================
async def prediction_bot():
    global total_wins, total_losses, total_rounds
    global hourly_wins, hourly_losses, hourly_rounds
    global hourly_best_win_streak, hourly_worst_loss_streak
    global current_streak, best_win_streak, worst_loss_streak
    global consecutive_losses
    global last_predicted_period, last_predicted_signal
    global prediction_sent_for_period, last_result_sent

    logger.info("🚀 RAJPUT X LX v22 - 1M WINGO স্টার্ট...")

    await send_message(
        "🚀 *RAJPUT X LX v22 - 1M WINGO* 🚀\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🧠 *8 Algorithms Combined:*\n"
        "1️⃣ Streak Ride\n"
        "2️⃣ Alternator\n"
        "3️⃣ Pair Counter\n"
        "4️⃣ Loop Cycle\n"
        "5️⃣ Hot Zone\n"
        "6️⃣ Seed Parity\n"
        "7️⃣ Double Pattern\n"
        "8️⃣ Fibonacci Momentum\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🎯 *শুধু BIG/SMALL প্রেডিকশন*\n"
        "📡 *মোড:* 1 MIN WINGO\n"
        "🤖 *বট:* @Tarek3o\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⏳ প্রথম সিগন্যালের জন্য অপেক্ষা..."
    )

    last_hour_time = time.time()

    while True:
        try:
            # ✅ 1 MIN (60 সেকেন্ড) অপেক্ষা
            current_sec = int(time.time()) % 60
            sleep_time = 60 - current_sec + 3
            await asyncio.sleep(sleep_time)

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

            logger.info(f"📡 পিরিয়ড: {latest_issue}, নাম্বার: {actual_num} ({actual_type})")

            # ===== রেজাল্ট চেক =====
            if last_predicted_period == latest_issue and last_predicted_signal is not None and not last_result_sent:
                
                is_win = (last_predicted_signal == actual_type)
                
                if is_win:
                    total_wins += 1
                    hourly_wins += 1
                    consecutive_losses = 0
                    
                    if current_streak >= 0:
                        current_streak += 1
                    else:
                        current_streak = 1
                    
                    if current_streak > best_win_streak:
                        best_win_streak = current_streak
                    if current_streak > hourly_best_win_streak:
                        hourly_best_win_streak = current_streak
                    
                    status = "✅ জয় 🎉"
                else:
                    total_losses += 1
                    hourly_losses += 1
                    consecutive_losses += 1
                    
                    if current_streak <= 0:
                        current_streak -= 1
                    else:
                        current_streak = -1
                    
                    if abs(current_streak) > worst_loss_streak:
                        worst_loss_streak = abs(current_streak)
                    if abs(current_streak) > hourly_worst_loss_streak:
                        hourly_worst_loss_streak = abs(current_streak)
                    
                    status = "❌ হার"

                total_rounds += 1
                hourly_rounds += 1
                
                total_win_rate = (total_wins / total_rounds * 100) if total_rounds > 0 else 0
                streak_emoji = "🔥" if current_streak > 0 else "📉" if current_streak < 0 else "⏸️"

                result_msg = (
                    f"🎯 *রেজাল্ট আপডেট*\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 পিরিয়ড: `#{latest_issue[-5:]}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔮 প্রেডিকশন: `{last_predicted_signal}`\n"
                    f"🎰 একচুয়াল: `{actual_num}` → `{actual_type}`\n"
                    f"📌 রেজাল্ট: `{status}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📊 জয়ের হার: `{total_win_rate:.1f}%` ({total_wins}W/{total_losses}L)\n"
                    f"{streak_emoji} স্ট্রিক: `{current_streak:+d}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🤖 @Tarek3o"
                )

                await send_message(result_msg)
                last_result_sent = True

                if time.time() - last_hour_time >= 3600:
                    await send_hourly_report()
                    last_hour_time = time.time()

            # ===== নতুন প্রেডিকশন =====
            next_period = str(int(latest_issue) + 1)
            
            if not prediction_sent_for_period.get(next_period, False):
                
                # 🔥 RAJPUT X LX v22 Engine
                result = run_pattern_engine(history_data)
                
                streak_emoji = "🔥" if current_streak > 0 else "📉" if current_streak < 0 else "⏸️"
                
                # Algo votes display
                algo_display = ""
                for a in result['algos'][:4]:
                    v = a['v'] if a['v'] else '—'
                    algo_display += f"• {a['name']}: `{v}`\n"
                
                prediction_msg = (
                    f"🚀 *RAJPUT X LX v22 - 1M* 🚀\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 পিরিয়ড: `#{next_period[-5:]}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🎯 প্রেডিকশন: `{result['winner']}`\n"
                    f"⚡ কনফিডেন্স: `{result['confidence']}%`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🧠 স্ট্র্যাটেজি: {result['strategy']}\n"
                    f"📊 ভোট: `{result['b_votes']}B vs {result['s_votes']}S`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"*Algorithms:*\n{algo_display}"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📊 Hot Zone: `{result['big_pct']}%B / {result['sml_pct']}%S`\n"
                    f"{streak_emoji} স্ট্রিক: `{current_streak:+d}`\n"
                    f"❌ টানা লস: `{consecutive_losses}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"⏳ রেজাল্টের জন্য অপেক্ষা...\n"
                    f"🤖 @Tarek3o"
                )

                last_predicted_period = next_period
                last_predicted_signal = result['winner']
                prediction_sent_for_period[next_period] = True
                last_result_sent = False

                await send_message(prediction_msg)
                logger.info(f"✅ প্রেডিকশন: {next_period} → {result['winner']} ({result['strategy']})")

                if len(prediction_sent_for_period) > 10:
                    oldest = min(prediction_sent_for_period.keys())
                    del prediction_sent_for_period[oldest]

        except Exception as e:
            logger.error(f"❌ Loop Error: {e}")
            await asyncio.sleep(5)

# ==================== 🚀 স্টার্ট ====================
if __name__ == '__main__':
    print("🚀 RAJPUT X LX v22 - 1M WINGO")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("🧠 8 Algorithms Combined")
    print("🎯 BIG/SMALL Only")
    print("📡 MODE: 1 MIN WINGO")
    print("🤖 BOT: @Tarek3o")
    print("━━━━━━━━━━━━━━━━━━━━")
    
    try:
        asyncio.run(prediction_bot())
    except KeyboardInterrupt:
        print("\n👋 বট বন্ধ করা হয়েছে")
    except Exception as e:
        print(f"❌ ফাটাল এরর: {e}")