async def send_and_delete_later(text, delay=300):
    try:
        sent = await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode='Markdown')
        await asyncio.sleep(delay)
        await bot.delete_message(chat_id=CHAT_ID, message_id=sent.message_id)
    except Exception as e:
        print(f"Lỗi xoá cảnh báo MÚC NGAY: {e}")
import ccxt
import pandas as pd
from ta.momentum import RSIIndicator
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

TELEGRAM_TOKEN = '7559763098:AAE1TYL5wfbKOeohmUYSVVbXFWv7N10HJRc'
CHAT_ID = '-1002654240601'
# Các lệnh:
# /rsi <timeframe>
# /rsi_15m /rsi_30m /rsi_1h /rsi_4h /rsi_12h /rsi_1d
# /chatid — xem chat ID nhóm


bot = Bot(token=TELEGRAM_TOKEN)
exchange = ccxt.bybit({
    'apiKey': 'qbj8JgIYbwlxqfrQNY',
    'secret': 'd2Glc7SIFr8U88ZbeqF0Rpfkh3apDGlRPiOL',
})
bingx = ccxt.bingx({
    'apiKey': 'RAaNwkXMtgfAhBr62161DhqVuF8joNUt89kWCwfpktDEiUrGK2dbeQV88sjxoqRtWqYlJKpFHoG5bavPiFA',
    'secret': 'y0YD2KghpGsbAAemraR46i0UmCnPbxYPN3aOaHPx30eBO6Bdj4GO33b253sEU07KxQeqN61dIHYoKX7v2Yw',
})

# Danh sách các cặp muốn theo dõi
valid_symbols = [
    'GMX/USDT', 'HYPEUSDT', 'AVAX/USDT', 'BTC/USDT', 'PEPE/USDT',
    'SEI/USDT', 'TRUMP/USDT', 'UNI/USDT', 'ADA/USDT', 'FLOKI/USDT', 'LINK/USDT',
    'RENDER/USDT', 'AI16Z/USDT', 'BOME/USDT', 'BONK/USDT', 'DOGE/USDT',
    'ETH/USDT', 'MEME/USDT', 'SHIB/USDT', 'VIRTUAL/USDT','SOLAYERUSDT','SOLVUSDT'
]
TOKEN_EMOJIS = {
    "GMX": "🦾",
    "BTC": "₿",
    "ETH": "Ξ",
    "PEPE": "🐸",
    "AVAX": "🗻",
    "TRUMP": "🇺🇸",
    "UNI": "🦄",
    "ADA": "🌊",
    "FLOKI": "🐶",
    "LINK": "🔗",
    "RENDER": "🖼️",
    "AI16Z": "🤖",
    "BOME": "💣",
    "BONK": "🐕",
    "DOGE": "🐕",
    "MEME": "🖼️",
    "SHIB": "🐕",
    "SEI": "🌊",
    "VIRTUAL": "🕹️",
    "SOLAYER": "🌞",
    "HYPE": "🔥",
    "SOL": "🌞",
}
SYMBOLS = valid_symbols

TOKEN_EMOJIS = {
    "GMX": "🟣",
    "HYPE": "🔥",
    "AVAX": "🗻",
    "BTC": "₿",
    "PEPE": "🐸",
    "SEI": "🌊",
    "TRUMP": "👑",
    "UNI": "🦄",
    "ADA": "🅰️",
    "FLOKI": "🐕",
    "LINK": "🔗",
    "RENDER": "🎨",
    "AI16Z": "🤖",
    "BOME": "💣",
    "BONK": "🐶",
    "DOGE": "🐕",
    "ETH": "Ξ",
    "MEME": "🖼️",
    "SHIB": "🐕",
    "VIRTUAL": "💻",
    "SOLAYER": "☀️",
}

print(f"✅ Danh sách token USDT Perpetual được theo dõi ({len(SYMBOLS)}):")
for sym in SYMBOLS:
    print(f" - {sym}")

# Thông báo khởi động cho telegram (có thể dùng trong hàm nếu cần)
tracked_msg = f"*📊 Danh sách token USDT Perpetual được theo dõi ({len(SYMBOLS)}):*"

TIMEFRAMES = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1m']

last_rsi_message_id = None
# Biến theo dõi ID tin nhắn cũ cho auto_rsi_match_alert
last_rsi_match_message_id = None

# Hàm tính RSI
def get_rsi(symbol, timeframe):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=100)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df.dropna(inplace=True)
        if df.empty or len(df['close']) < 14:
            return "N/A"
        rsi_series = RSIIndicator(close=df['close'], window=14).rsi()
        rsi = rsi_series.iloc[-1]
        rsi_min = rsi_series.min()
        rsi_max = rsi_series.max()
        last_price = df['close'].iloc[-1]
        return round(rsi, 2), round(last_price, 2), round(rsi_min, 2), round(rsi_max, 2), 'bybit'
    except Exception:
        try:
            ohlcv = bingx.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=100)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            df.dropna(inplace=True)
            if df.empty or len(df['close']) < 14:
                return "N/A"
            rsi_series = RSIIndicator(close=df['close'], window=14).rsi()
            rsi = rsi_series.iloc[-1]
            rsi_min = rsi_series.min()
            rsi_max = rsi_series.max()
            last_price = df['close'].iloc[-1]
            return round(rsi, 2), round(last_price, 2), round(rsi_min, 2), round(rsi_max, 2), 'bingx'
        except Exception:
            return "N/A"

# Lệnh xử lý `/rsi 1h`
async def rsi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args or args[0] not in TIMEFRAMES:
        await update.message.reply_text("⏱ Vui lòng nhập timeframe hợp lệ: /rsi 15m | 1h | 4h | 1d", parse_mode="Markdown")
        return

    tf = args[0]
    message = f"📈 RSI 14 - Timeframe {tf}:\n"
    table_lines = ["| Token | RSI | Min | Max | Giá | Trạng thái |"]
    for symbol in SYMBOLS:
        try:
            rsi, price, rsi_min, rsi_max, _ = get_rsi(symbol, tf)
            token_code = symbol.replace("/USDT", "").replace("USDT", "")
            emoji = TOKEN_EMOJIS.get(token_code.upper(), "📈")
            chart_url = f"https://www.bybit.com/trade/usdt/{token_code}USDT"
            if isinstance(rsi, (int, float)):
                if rsi > 76:
                    state = "*🟢 CẢNH BÁO: Quá mua mạnh*"
                    table_lines.append(f"| {emoji} [{symbol} 📈]({chart_url}) | **{rsi}** | {rsi_min} | {rsi_max} | {price} | {state} |")
                    alert_msg = f"⚠️ {state.strip('*')} cho {symbol} - RSI: {rsi} | Giá: {price} | TF: {tf}"
                    # Cảnh báo "MÚC NGAY" chỉ khi cả 15m và 1h đều quá mua mạnh/quá bán mạnh
                    if tf in ['15m', '1h']:
                        other_tf = '1h' if tf == '15m' else '15m'
                        rsi_other = get_rsi(symbol, other_tf)
                        if isinstance(rsi_other, tuple):
                            rsi_o = rsi_other[0]
                            if rsi >= 76 and rsi_o >= 76:
                                alert_msg = f"🚨 *MÚC NGAY (SHORT)* {symbol} | RSI {tf}: {rsi} | RSI {other_tf}: {rsi_o} | Giá: {price}"
                                if alert_msg.startswith("🚨 *MÚC NGAY"):
                                    await send_and_delete_later(alert_msg)
                                else:
                                    await bot.send_message(chat_id=CHAT_ID, text=alert_msg, parse_mode='Markdown')
                            elif rsi <= 28 and rsi_o <= 28:
                                alert_msg = f"🚨 *MÚC NGAY (LONG)* {symbol} | RSI {tf}: {rsi} | RSI {other_tf}: {rsi_o} | Giá: {price}"
                                if alert_msg.startswith("🚨 *MÚC NGAY"):
                                    await send_and_delete_later(alert_msg)
                                else:
                                    await bot.send_message(chat_id=CHAT_ID, text=alert_msg, parse_mode='Markdown')
                    else:
                        await bot.send_message(chat_id=CHAT_ID, text=alert_msg, parse_mode="Markdown")
                elif 70 >= rsi >= 30:
                    continue  # Ẩn token RSI trung lập
                elif rsi > 70:
                    state = "*🟢 Quá mua*"
                    table_lines.append(f"| {emoji} [{symbol} 📈]({chart_url}) | {rsi} | {rsi_min} | {rsi_max} | {price} | {state} |")
                elif rsi < 28:
                    state = "*🔴 CẢNH BÁO: Quá bán mạnh*"
                    table_lines.append(f"| {emoji} [{symbol} 📈]({chart_url}) | **{rsi}** | {rsi_min} | {rsi_max} | {price} | {state} |")
                    alert_msg = f"⚠️ {state.strip('*')} cho {symbol} - RSI: {rsi} | Giá: {price} | TF: {tf}"
                    if tf in ['15m', '1h']:
                        other_tf = '1h' if tf == '15m' else '15m'
                        rsi_other = get_rsi(symbol, other_tf)
                        if isinstance(rsi_other, tuple):
                            rsi_o = rsi_other[0]
                            if rsi >= 76 and rsi_o >= 76:
                                alert_msg = f"🚨 *MÚC NGAY (SHORT)* {symbol} | RSI {tf}: {rsi} | RSI {other_tf}: {rsi_o} | Giá: {price}"
                                if alert_msg.startswith("🚨 *MÚC NGAY"):
                                    await send_and_delete_later(alert_msg)
                                else:
                                    await bot.send_message(chat_id=CHAT_ID, text=alert_msg, parse_mode='Markdown')
                            elif rsi <= 28 and rsi_o <= 28:
                                alert_msg = f"🚨 *MÚC NGAY (LONG)* {symbol} | RSI {tf}: {rsi} | RSI {other_tf}: {rsi_o} | Giá: {price}"
                                if alert_msg.startswith("🚨 *MÚC NGAY"):
                                    await send_and_delete_later(alert_msg)
                                else:
                                    await bot.send_message(chat_id=CHAT_ID, text=alert_msg, parse_mode='Markdown')
                    else:
                        await bot.send_message(chat_id=CHAT_ID, text=alert_msg, parse_mode="Markdown")
                elif rsi < 30:
                    state = "*🔴 Quá bán*"
                    table_lines.append(f"| {emoji} [{symbol} 📈]({chart_url}) | {rsi} | {rsi_min} | {rsi_max} | {price} | {state} |")
            else:
                table_lines.append(f"| {symbol} | {rsi} | - | - | - | - |")
        except Exception as e:
            table_lines.append(f"| {symbol} | lỗi ({str(e)}) | - | - | - | - |")

    if len(table_lines) > 1:
        message += "\n".join(table_lines)
    else:
        message += "⚪ Không có token nào nằm ngoài vùng trung lập."
    await update.message.reply_text(message, parse_mode="Markdown")
    if update.effective_chat.id != int(CHAT_ID):
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

async def auto_rsi_alert():
    global last_rsi_message_id
    timeframes = ['15m', '30m', '1h', '4h', '12h', '1d']
    while True:
        try:
            table_lines = ["| Token | RSI | Min | Max | Giá | Trạng thái | TF |"]
            for tf in timeframes:
                for symbol in SYMBOLS:
                    try:
                        rsi, price, rsi_min, rsi_max, _ = get_rsi(symbol, tf)
                        token_code = symbol.replace("/USDT", "").replace("USDT", "")
                        emoji = TOKEN_EMOJIS.get(token_code.upper(), "📈")
                        chart_url = f"https://www.bybit.com/trade/usdt/{token_code}USDT"
                        if isinstance(rsi, (int, float)):
                            if rsi > 74:
                                state = "*🟢 CẢNH BÁO: Quá mua*"
                                table_lines.append(f"| {emoji} [{symbol} 📈]({chart_url}) | **{rsi}** | {rsi_min} | {rsi_max} | {price} | {state} | {tf} |")
                            elif 70 >= rsi >= 30:
                                continue  # Ẩn token RSI trung lập
                            elif rsi > 70:
                                state = "*🟢 Quá mua*"
                                table_lines.append(f"| {emoji} [{symbol} 📈]({chart_url}) | {rsi} | {rsi_min} | {rsi_max} | {price} | {state} | {tf} |")
                            elif rsi < 28:
                                state = "*🔴 CẢNH BÁO: Quá bán*"
                                table_lines.append(f"| {emoji} [{symbol} 📈]({chart_url}) | **{rsi}** | {rsi_min} | {rsi_max} | {price} | {state} | {tf} |")
                            elif rsi < 30:
                                state = "*🔴 Quá bán*"
                                table_lines.append(f"| {emoji} [{symbol} 📈]({chart_url}) | {rsi} | {rsi_min} | {rsi_max} | {price} | {state} | {tf} |")
                    except Exception as e:
                        table_lines.append(f"| {symbol} | lỗi | - | - | - | {str(e)} | {tf} |")
            if len(table_lines) > 1:
                top_overbought = sorted(
                    [row for row in table_lines[1:] if "**" in row and "🟢" in row],
                    key=lambda x: float(x.split("|")[2].strip("* ")),
                    reverse=True
                )[:3]

                top_oversold = sorted(
                    [row for row in table_lines[1:] if "**" in row and "🔴" in row],
                    key=lambda x: float(x.split("|")[2].strip("* ")),
                )[:3]

                summary_lines = []
                if top_overbought:
                    summary_lines.append("🏆 *Top Quá Mua*:")
                    summary_lines += top_overbought
                if top_oversold:
                    summary_lines.append("💥 *Top Quá Bán*:")
                    summary_lines += top_oversold

                message = f"📊 RSI - Cảnh báo cập nhật tự động:\n"
                if summary_lines:
                    message += "\n".join(summary_lines) + "\n\n"
                message += "\n".join(table_lines)

                # Xoá tin cũ nếu có
                try:
                    if last_rsi_message_id:
                        await bot.delete_message(chat_id=CHAT_ID, message_id=last_rsi_message_id)
                except Exception as e:
                    print(f"Lỗi xoá tin nhắn cũ: {e}")
                # Gửi tin mới
                sent = await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
                last_rsi_message_id = sent.message_id
            await asyncio.sleep(600)  # 10 phút
        except Exception as e:
            print(f"Lỗi auto_rsi_alert: {e}")
            await asyncio.sleep(600)  # 10 phút
async def top_rsi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    timeframes = ['15m', '1h', '4h']
    table_lines = []
    for tf in timeframes:
        for symbol in SYMBOLS:
            try:
                rsi_data = get_rsi(symbol, tf)
                if rsi_data == "N/A":
                    continue
                rsi, price, rsi_min, rsi_max, src = rsi_data
                token_code = symbol.replace("/USDT", "").replace("USDT", "")
                emoji = TOKEN_EMOJIS.get(token_code.upper(), "📈")
                chart_url = f"https://www.bybit.com/trade/usdt/{token_code}USDT"
                source_tag = f"[{src.upper()}]"
                if isinstance(rsi, (int, float)):
                    if rsi > 74 or rsi < 28:
                        state = "*🟢 Quá mua*" if rsi > 70 else "*🔴 Quá bán*"
                        table_lines.append((rsi, f"| {emoji} {source_tag} [{symbol} 📈]({chart_url}) | {rsi} | {price} | {state} | {tf} |"))
            except Exception as e:
                continue

    top_overbought = sorted([line for line in table_lines if "🟢" in line[1]], key=lambda x: x[0], reverse=True)[:5]
    top_oversold = sorted([line for line in table_lines if "🔴" in line[1]], key=lambda x: x[0])[:5]

    message = "*🏆 Top RSI*\n"
    if top_overbought:
        message += "\n📈 *Top Quá Mua:*\n" + "\n".join([line[1] for line in top_overbought])
    if top_oversold:
        message += "\n\n📉 *Top Quá Bán:*\n" + "\n".join([line[1] for line in top_oversold])

    await update.message.reply_text(message, parse_mode="Markdown")
# Hàm tự động báo match RSI 15m/1h (Thêm mới)
async def auto_rsi_match_alert():
    global last_rsi_match_message_id
    while True:
        try:
            matched_tokens = []
            for symbol in SYMBOLS:
                rsi_15m = get_rsi(symbol, '15m')
                rsi_1h = get_rsi(symbol, '1h')
                if rsi_15m == "N/A" or rsi_1h == "N/A":
                    continue
                rsi15, price15, _, _, src15 = rsi_15m
                rsi1h, price1h, _, _, src1h = rsi_1h
                # Điều kiện match ví dụ: 15m RSI < 30 và 1h RSI < 35
                if isinstance(rsi15, (int, float)) and isinstance(rsi1h, (int, float)):
                    if (rsi15 < 30 and rsi1h < 35) or (rsi15 > 70 and rsi1h > 65):
                        token_code = symbol.replace("/USDT", "").replace("USDT", "")
                        emoji = TOKEN_EMOJIS.get(token_code.upper(), "📈")
                        chart_url = f"https://www.bybit.com/trade/usdt/{token_code}USDT"
                        if rsi15 < 30 and rsi1h < 35:
                            state = "🔴 Quá bán đồng thời"
                        else:
                            state = "🟢 Quá mua đồng thời"
                        source_tag = f"[{src15.upper()}]"
                        matched_tokens.append(
                            f"{emoji} {source_tag} [{symbol}]({chart_url}) | RSI 15m: *{rsi15}* | RSI 1h: *{rsi1h}* | Giá: {price15} | {state}"
                        )
            if matched_tokens:
                msg = "⚡ *RSI Match 15m/1h*:\n" + "\n".join(matched_tokens)
                try:
                    if last_rsi_match_message_id:
                        await bot.delete_message(chat_id=CHAT_ID, message_id=last_rsi_match_message_id)
                except Exception as e:
                    print(f"Lỗi xoá tin nhắn RSI match: {e}")
                sent = await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")
                last_rsi_match_message_id = sent.message_id
            await asyncio.sleep(300)  # 5 phút
        except Exception as e:
            print(f"Lỗi auto_rsi_match_alert: {e}")




# Lệnh /chatid: trả về ID của nhóm hoặc người gửi lệnh
async def debug_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"📎 Chat ID: `{chat_id}`", parse_mode="Markdown")

async def rsi_fixed_command(update: Update, context: ContextTypes.DEFAULT_TYPE, tf: str):
    message = f"📈 RSI - Timeframe {tf}:\n"
    table_lines = ["| Token | RSI | Min | Max | Giá | Trạng thái |"]
    for symbol in SYMBOLS:
        try:
            rsi, price, rsi_min, rsi_max, _ = get_rsi(symbol, tf)
            token_code = symbol.replace("/USDT", "").replace("USDT", "")
            emoji = TOKEN_EMOJIS.get(token_code.upper(), "📈")
            chart_url = f"https://www.bybit.com/trade/usdt/{token_code}USDT"
            if isinstance(rsi, (int, float)):
                if rsi > 76:
                    state = "*🟢 CẢNH BÁO: Quá mua mạnh*"
                    table_lines.append(f"| {emoji} [{symbol} 📈]({chart_url}) | **{rsi}** | {rsi_min} | {rsi_max} | {price} | {state} |")
                    alert_msg = f"⚠️ {state.strip('*')} cho {symbol} - RSI: {rsi} | Giá: {price} | TF: {tf}"
                    if tf in ['15m', '1h']:
                        other_tf = '1h' if tf == '15m' else '15m'
                        rsi_other = get_rsi(symbol, other_tf)
                        if isinstance(rsi_other, tuple):
                            rsi_o = rsi_other[0]
                            if rsi >= 76 and rsi_o >= 76:
                                alert_msg = f"🚨 *MÚC NGAY (SHORT)* {symbol} | RSI {tf}: {rsi} | RSI {other_tf}: {rsi_o} | Giá: {price}"
                                if alert_msg.startswith("🚨 *MÚC NGAY"):
                                    await send_and_delete_later(alert_msg)
                                else:
                                    await bot.send_message(chat_id=CHAT_ID, text=alert_msg, parse_mode='Markdown')
                            elif rsi <= 28 and rsi_o <= 28:
                                alert_msg = f"🚨 *MÚC NGAY (LONG)* {symbol} | RSI {tf}: {rsi} | RSI {other_tf}: {rsi_o} | Giá: {price}"
                                if alert_msg.startswith("🚨 *MÚC NGAY"):
                                    await send_and_delete_later(alert_msg)
                                else:
                                    await bot.send_message(chat_id=CHAT_ID, text=alert_msg, parse_mode='Markdown')
                    else:
                        await bot.send_message(chat_id=CHAT_ID, text=alert_msg, parse_mode="Markdown")
                elif 70 >= rsi >= 30:
                    continue  # Ẩn token RSI trung lập
                elif rsi > 70:
                    state = "*🟢 Quá mua*"
                    table_lines.append(f"| {emoji} [{symbol} 📈]({chart_url}) | {rsi} | {rsi_min} | {rsi_max} | {price} | {state} |")
                elif rsi < 28:
                    state = "*🔴 CẢNH BÁO: Quá bán mạnh*"
                    table_lines.append(f"| {emoji} [{symbol} 📈]({chart_url}) | **{rsi}** | {rsi_min} | {rsi_max} | {price} | {state} |")
                    alert_msg = f"⚠️ {state.strip('*')} cho {symbol} - RSI: {rsi} | Giá: {price} | TF: {tf}"
                    if tf in ['15m', '1h']:
                        other_tf = '1h' if tf == '15m' else '15m'
                        rsi_other = get_rsi(symbol, other_tf)
                        if isinstance(rsi_other, tuple):
                            rsi_o = rsi_other[0]
                            if rsi >= 76 and rsi_o >= 76:
                                alert_msg = f"🚨 *MÚC NGAY (SHORT)* {symbol} | RSI {tf}: {rsi} | RSI {other_tf}: {rsi_o} | Giá: {price}"
                                if alert_msg.startswith("🚨 *MÚC NGAY"):
                                    await send_and_delete_later(alert_msg)
                                else:
                                    await bot.send_message(chat_id=CHAT_ID, text=alert_msg, parse_mode='Markdown')
                            elif rsi <= 28 and rsi_o <= 28:
                                alert_msg = f"🚨 *MÚC NGAY (LONG)* {symbol} | RSI {tf}: {rsi} | RSI {other_tf}: {rsi_o} | Giá: {price}"
                                if alert_msg.startswith("🚨 *MÚC NGAY"):
                                    await send_and_delete_later(alert_msg)
                                else:
                                    await bot.send_message(chat_id=CHAT_ID, text=alert_msg, parse_mode='Markdown')
                    else:
                        await bot.send_message(chat_id=CHAT_ID, text=alert_msg, parse_mode="Markdown")
                elif rsi < 30:
                    state = "*🔴 Quá bán*"
                    table_lines.append(f"| {emoji} [{symbol} 📈]({chart_url}) | {rsi} | {rsi_min} | {rsi_max} | {price} | {state} |")
        except Exception as e:
            table_lines.append(f"| {symbol} | lỗi | - | - | - | {str(e)} |")
    if len(table_lines) > 1:
        message += "\n".join(table_lines)
    else:
        message += "⚪ Không có TOKEN nằm trong vùng RSI."
    await update.message.reply_text(message, parse_mode="Markdown")

async def rsi_15m(update, context): await rsi_fixed_command(update, context, '15m')
async def rsi_30m(update, context): await rsi_fixed_command(update, context, '30m')
async def rsi_1h(update, context): await rsi_fixed_command(update, context, '1h')
async def rsi_4h(update, context): await rsi_fixed_command(update, context, '4h')
async def rsi_12h(update, context): await rsi_fixed_command(update, context, '12h')
async def rsi_1d(update, context): await rsi_fixed_command(update, context, '1d')

# Các lệnh:
# /rsi <timeframe>
# /rsi_15m /rsi_30m /rsi_1h /rsi_4h /rsi_12h /rsi_1d
# /chatid — xem chat ID nhóm

async def main():
    global last_rsi_match_message_id
    last_rsi_match_message_id = None
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("rsi", rsi_command))
    app.add_handler(CommandHandler("chatid", debug_chat_id))
    app.add_handler(CommandHandler("rsi_15m", rsi_15m))
    app.add_handler(CommandHandler("rsi_30m", rsi_30m))
    app.add_handler(CommandHandler("rsi_1h", rsi_1h))
    app.add_handler(CommandHandler("rsi_4h", rsi_4h))
    app.add_handler(CommandHandler("rsi_12h", rsi_12h))
    app.add_handler(CommandHandler("rsi_1d", rsi_1d))
    app.add_handler(CommandHandler("top_rsi", top_rsi))
    print("✅ Bot đang chạy...")

    # Gửi thông báo danh sách token và xoá tin cũ nếu có
    try:
        global last_rsi_message_id
        if last_rsi_message_id:
            await bot.delete_message(chat_id=CHAT_ID, message_id=last_rsi_message_id)
    except Exception as e:
        print(f"Lỗi xoá tin nhắn cũ khi khởi động: {e}")

    tracked_msg = f"*📊 Danh sách token USDT Perpetual được theo dõi ({len(SYMBOLS)}):*"
    for sym in SYMBOLS:
        emoji = TOKEN_EMOJIS.get(sym.replace("/USDT", "").replace("USDT", "").upper(), "📈")
        tracked_msg += f"\n- {emoji} `{sym}`"

    sent = await bot.send_message(chat_id=CHAT_ID, text=tracked_msg, parse_mode="Markdown")
    last_rsi_message_id = sent.message_id

    asyncio.create_task(auto_rsi_alert())
    asyncio.create_task(auto_rsi_match_alert())
    await app.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())