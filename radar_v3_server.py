import requests
import time
import asyncio
import os
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
bot = Bot(token=TOKEN)

MIN_LIQUIDITY = 50000
MIN_VOLUME_1H = 100000
MAX_AGE_HOURS = 6
CHECK_INTERVAL = 300

sent_tokens = set()

def get_smart_money_signal(pair):
    try:
        token_address = pair['baseToken']['address']
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{token_address}"
        txns = requests.get(url, timeout=5).json()['pair']['txns']['h1']
        buys = txns.get('buys', 0)
        if buys > 20:
            return True, f"{buys} smart buys in 1h"
    except: pass
    return False, ""

async def send_signal_v3(token, smart_note):
    symbol = token['baseToken']['symbol']
    price = float(token['priceUsd'])
    liquidity = float(token['liquidity']['usd'])
    volume_h1 = float(token['volume']['h1'])
    price_change_h1 = float(token['priceChange']['h1'])
    age = (time.time() - token['pairCreatedAt']/1000) / 3600
    url = token['url']
    ca = token['baseToken']['address']
    
    msg = f"""
🚨 **Signal V3**: ${symbol}

**Price**: `{price:.10f}$`
**1h**: `+{price_change_h1:.1f}%` | **Vol**: `{volume_h1:,.0f}$`
**LP**: `{liquidity:,.0f}$` | **Age**: `{age:.1f}h`
**Smart Money**: {smart_note}

`{ca}`
"""
    keyboard = [
        [InlineKeyboardButton("🟢 Buy 0.5 SOL", url=f"https://jup.ag/swap/SOL-{ca}")],
        [InlineKeyboardButton("🟢 Buy 1 SOL", url=f"https://jup.ag/swap/SOL-{ca}")],
        [InlineKeyboardButton("📊 Chart", url=url), InlineKeyboardButton("🔒 RugCheck", url=f"https://rugcheck.xyz/tokens/{ca}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown', reply_markup=reply_markup, disable_web_page_preview=True)

async def scan_market_v3():
    print("Sovereign Radar V3 Server Online...")
    await bot.send_message(chat_id=CHAT_ID, text="✅ **Sovereign Radar V3 Server Online**\n24/7 Hunting Active\nSmart Money + Auto Buy Buttons")
    
    while True:
        try:
            url = "https://api.dexscreener.com/latest/dex/search?q=SOL"
            data = requests.get(url, timeout=10).json()
            
            for pair in data.get('pairs', []):
                try:
                    address = pair['baseToken']['address']
                    if address in sent_tokens: continue
                        
                    liquidity = float(pair['liquidity']['usd'])
                    volume_h1 = float(pair['volume']['h1'])
                    age_hours = (time.time() - pair['pairCreatedAt']/1000) / 3600
                    
                    if liquidity > MIN_LIQUIDITY and volume_h1 > MIN_VOLUME_1H and age_hours < MAX_AGE_HOURS:
                        is_smart, note = get_smart_money_signal(pair)
                        if is_smart:
                            await send_signal_v3(pair, note)
                            sent_tokens.add(address)
                            print(f"V3 Signal: ${pair['baseToken']['symbol']} | {note}")
                            await asyncio.sleep(3)
                except: continue
        except Exception as e:
            print(f"Error: {e}")
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(scan_market_v3())
