# language: Python, file: osint_bot.py, runtime: 3.10+, target: Telegram Bot API
# Hitler Leak OSINT V1.0 — ULTRA PREMIUM UI
import json, logging, asyncio
from datetime import datetime, timezone
import httpx
from telegram import Update, ForceReply
from telegram.ext import (Application, CommandHandler, MessageHandler,
                          ConversationHandler, ContextTypes, filters)
from telegram.constants import ParseMode

# ── CONFIG ────────────────────────────────────────────────
BOT_TOKEN   = "9258585656:AAG4QR1wiiSL_WJrKiEg7mQDBSU-KvTJOb4"
API_BASE    = "https://leak-api.asurpapa.workers.dev/api"
API_KEY     = "2k_COMPLETE"
TIMEOUT     = 30.0
CHUNK_LIMIT = 3800

CREDIT_OVERRIDE = {
    "developer": "@Root_Hitler",
    "contact":   "@Sudo_Moon",
    "footer":    "Powered by:- Smiling Hacker",
}
BOT_NAME = "HITLER LEAK OSINT"
BOT_VER  = "V1.0 • ULTRA"

ASK_NUMBER = 1
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("osint_bot")

# ── FANCY FONT ────────────────────────────────────────────
_U="ABCDEFGHIJKLMNOPQRSTUVWXYZ"; _L="abcdefghijklmnopqrstuvwxyz"; _D="0123456789"
_M={}
_M.update({c:chr(0x1D400+i) for i,c in enumerate(_U)})
_M.update({c:chr(0x1D41A+i) for i,c in enumerate(_L)})
_M.update({c:chr(0x1D7CE+i) for i,c in enumerate(_D)})
def fancy(s): return "".join(_M.get(c,c) for c in str(s))
def fspace(s): return " ".join(fancy(c) for c in s)

# ── API ───────────────────────────────────────────────────
async def lookup_number(number):
    params = {"key": API_KEY, "term": number}
    async with httpx.AsyncClient(timeout=TIMEOUT) as c:
        r = await c.get(API_BASE, params=params); r.raise_for_status()
        try: return r.json()
        except json.JSONDecodeError: return {"raw": r.text}

# ── CREDIT OVERRIDE ───────────────────────────────────────
def rewrite_credit(d):
    if isinstance(d, dict):
        if "credit" in d and isinstance(d["credit"], dict):
            d["credit"] = dict(CREDIT_OVERRIDE)
        for v in d.values(): rewrite_credit(v)
    elif isinstance(d, list):
        for x in d: rewrite_credit(x)
    return d

# ── EMOJI MAP ─────────────────────────────────────────────
EMOJI_MAP = {
 "name":"👤","full_name":"👤","first_name":"👤","last_name":"👤","father":"👨","mother":"👩",
 "phone":"📱","mobile":"📱","number":"📱","msisdn":"📱","alt_phone":"☎️","whatsapp":"💬",
 "email":"📧","mail":"📧","aadhaar":"🪪","aadhar":"🪪","pan":"💳","voter":"🗳","passport":"📘",
 "address":"🏠","location":"📍","city":"🏙","state":"🗺","district":"🏘","pincode":"📮","country":"🌍",
 "dob":"🎂","age":"🎂","gender":"⚧","carrier":"📡","operator":"📡","network":"📡","circle":"🗼",
 "photo":"🖼","image":"🖼","facebook":"📘","instagram":"📸","twitter":"🐦","telegram":"✈️",
 "bank":"🏦","account":"🏦","ifsc":"🏦","upi":"💸","vehicle":"🚗","rc":"🚗","ip":"🌐","device":"💻",
 "title":"📌","description":"📝","desc":"📝","details":"📝","source":"📚","leak":"🩸","breach":"🩸",
 "database":"🗄","db":"🗄","records":"📁","result":"📁","results":"📁","data":"📦","info":"ℹ️",
 "status":"🚦","error":"❌","message":"💬","query":"🔍","term":"🔍","date":"📅","count":"🔢","total":"🔢",
}
def emoji_for(k):
    kl = k.lower().strip()
    if kl in EMOJI_MAP: return EMOJI_MAP[kl]
    for t,e in EMOJI_MAP.items():
        if t in kl: return e
    return "▫️"
def pretty_key(k): return fancy(k.replace("_"," ").upper())
def scalar_str(v):
    if v is None: return "—"
    if isinstance(v, bool): return "✅ Yes" if v else "❌ No"
    s = str(v).strip(); return s or "—"

# ── RENDERER ──────────────────────────────────────────────
def render_value(v, indent=0, depth=0):
    pad = "  "*indent; lines=[]
    if depth > 8:
        lines.append(f"{pad}{json.dumps(v, ensure_ascii=False)}"); return lines
    if isinstance(v, dict):
        for k,val in v.items():
            if str(k).lower()=="credit": continue
            em=emoji_for(k); kl=pretty_key(k)
            if isinstance(val,(dict,list)):
                lines.append(f"{pad}┃ {em} {kl} :")
                lines.extend(render_value(val, indent+1, depth+1))
            else:
                lines.append(f"{pad}┃ {em} {kl} : {scalar_str(val)}")
    elif isinstance(v, list):
        if not v: lines.append(f"{pad}┃ ▫️ _Empty_")
        for i,it in enumerate(v,1):
            if isinstance(it,(dict,list)):
                lines.append(f"{pad}┣━ 🔹 #{fancy(str(i))}")
                lines.extend(render_value(it, indent+1, depth+1))
            else:
                lines.append(f"{pad}┃ {fancy(str(i))}. {scalar_str(it)}")
    else:
        lines.append(f"{pad}{scalar_str(v)}")
    return lines

# ── BUILDERS ──────────────────────────────────────────────
def build_header():
    return (
        "╔══════════════════════════════╗\n"
        f"  🔥 {fspace(BOT_NAME)} 🔥\n"
        f"      ⚡ {fancy(BOT_VER)} ⚡\n"
        "╠══════════════════════════════╣\n"
        "  🩸  L E A K   I N T E L L I G E N C E  🩸\n"
        "╚══════════════════════════════╝"
    )

def build_meta(cleaned):
    ts = datetime.now(timezone.utc).strftime("%d %b %Y • %H:%M UTC")
    return (
        "┌────────────────────────────┐\n"
        f"│ 🎯 {fancy('TARGET')}     : `{cleaned}`\n"
        f"│ 🕒 {fancy('TIMESTAMP')}  : {ts}\n"
        f"│ 🟢 {fancy('STATUS')}     : ONLINE\n"
        "└────────────────────────────┘"
    )

def build_credit():
    return (
        "╔══════════════════════════╗\n"
        "║   👑  " + fspace("CREDIT") + "  👑\n"
        "╠══════════════════════════╣\n"
        f"║ 🤖  {fancy('Dev')}     : {CREDIT_OVERRIDE['developer']}\n"
        f"║ 📞 {fancy('Contact')}  : [ {CREDIT_OVERRIDE['contact']} ]\n"
        f"║ ☠️  {CREDIT_OVERRIDE['footer']}\n"
        "╚══════════════════════════╝"
    )

def build_sections(cleaned, data):
    parts = [build_header()+"\n\n"+build_meta(cleaned)+"\n"]

    if isinstance(data, dict) and "raw" in data and len(data)==1:
        raw = str(data["raw"])
        parts.append("╭──────── 📦 "+fancy("RAW DATA")+" ────────╮")
        for i in range(0, len(raw), 3500):
            parts.append("```\n"+raw[i:i+3500]+"\n```")
        parts.append("╰────────────────────────────╯")
    elif isinstance(data, dict):
        for key,val in data.items():
            if str(key).lower()=="credit": continue
            em=emoji_for(key); title=pretty_key(key)
            body = "\n".join(render_value(val)) or "▫️ _Empty_"
            parts.append(
                f"╭──────── {em} {title} ────────╮\n"
                f"{body}\n"
                "╰────────────────────────────╯"
            )
    elif isinstance(data, list):
        body = "\n".join(render_value(data))
        parts.append(
            f"╭──────── 📁 {fancy('RESULTS')} ({len(data)}) ────────╮\n"
            f"{body}\n"
            "╰────────────────────────────╯"
        )
    else:
        parts.append("╭──────── 📦 "+fancy("DATA")+" ────────╮\n"+scalar_str(data)+"\n╰────────────────────────────╯")

    parts.append(build_credit())
    parts.append("⚡ _Powered by RootHitler Team_ ⚡")
    return parts

def chunk_message(parts, limit=CHUNK_LIMIT):
    chunks, cur = [], ""
    for p in parts:
        cand = (cur+"\n"+p) if cur else p
        if len(cand) <= limit: cur = cand
        else:
            if cur: chunks.append(cur)
            if len(p) > limit:
                for i in range(0,len(p),limit):
                    sub=p[i:i+limit]
                    if i+limit<len(p): chunks.append(sub)
                    else: cur=sub
            else: cur=p
    if cur: chunks.append(cur)
    return chunks

def strip_md(s): return s.replace("*","").replace("`","").replace("_","")

# ── HANDLERS ──────────────────────────────────────────────
async def cmd_start(update, ctx):
    txt = (
        build_header()+"\n\n"
        "╭─────── 🚀 "+fancy("GET STARTED")+" ───────╮\n"
        "│ 📱 Send a phone number\n"
        "│ 🧪 Example: `919918753969`\n"
        "│ 🛑 Cancel: /cancel\n"
        "╰────────────────────────────╯\n\n"
        f"☠️ _{CREDIT_OVERRIDE['footer']}_"
    )
    await update.message.reply_text(txt, parse_mode=ParseMode.MARKDOWN,
        reply_markup=ForceReply(selective=True, input_field_placeholder="Enter phone number..."))
    return ASK_NUMBER

async def handle_number(update, ctx):
    raw = update.message.text.strip()
    cleaned = "".join(ch for ch in raw if ch.isdigit())
    if len(cleaned) < 6:
        await update.message.reply_text("❌ Invalid number. Send 6+ digits. /cancel to exit.")
        return ASK_NUMBER

    loading = await update.message.reply_text(
        "╔══════════════════════════════╗\n"
        f"  🔎 {fspace('SCANNING')} 🔎\n"
        "╚══════════════════════════════╝\n"
        f"📡 Target : `{cleaned}`\n"
        "⏳ Deep search in progress...",
        parse_mode=ParseMode.MARKDOWN)

    try:
        data = await lookup_number(cleaned)
    except httpx.HTTPStatusError as e:
        await loading.edit_text(f"❌ API HTTP {e.response.status_code}\n`{e.response.text[:300]}`", parse_mode=ParseMode.MARKDOWN); return ASK_NUMBER
    except httpx.RequestError as e:
        await loading.edit_text(f"❌ Network: `{e}`", parse_mode=ParseMode.MARKDOWN); return ASK_NUMBER
    except Exception as e:
        log.exception("lookup failed")
        await loading.edit_text(f"❌ Error: `{e}`", parse_mode=ParseMode.MARKDOWN); return ASK_NUMBER

    data = rewrite_credit(data)
    chunks = chunk_message(build_sections(cleaned, data))
    for i,ch in enumerate(chunks):
        try:
            if i==0: await loading.edit_text(ch, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
            else: await update.message.reply_text(ch, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        except Exception:
            p = strip_md(ch)
            if i==0: await loading.edit_text(p, disable_web_page_preview=True)
            else: await update.message.reply_text(p, disable_web_page_preview=True)
        await asyncio.sleep(0.4)

    await update.message.reply_text(
        "➡️ Send another number, or /cancel to exit.",
        reply_markup=ForceReply(selective=True, input_field_placeholder="Enter phone number..."))
    return ASK_NUMBER

async def cmd_cancel(update, ctx):
    await update.message.reply_text("🛑 Cancelled. Use /start to begin again.")
    return ConversationHandler.END

# ── MAIN ──────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", cmd_start)],
        states={ASK_NUMBER:[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_number)]},
        fallbacks=[CommandHandler("cancel", cmd_cancel)],
        allow_reentry=True)
    app.add_handler(conv)
    log.info("Bot online. Polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()