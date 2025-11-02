import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Faýl bukjasy
if not os.path.exists("vpn_files"):
    os.makedirs("vpn_files")

TOKEN = "8238956091:AAE0GUZKQA6hbkvBLPolg0jhhe6viCU-vTc"
adminler = {7194433458}

kanallar = []               # Goşulmaly kanallar
optional_kanallar = []      # Goşulmasa-da bolar
gizlin_kanallar = []        # Gizlin barlanmaly

menu_yazgy = "Kanallara goşulyň we VPN kody alyň:"
vpn_kody = "Täze VPN: DARKTUNNEL-123456"
vpn_faýl_ýoly = "vpn.ovpn"
banlananlar = []
ulanyjylar = set()

# ====================== /start ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ulanyjylar.add(user_id)

    if user_id in banlananlar:
        await update.message.reply_text("Siz banlandyňyz.")
        return

    kanal_buttons = []
    row = []

    # Goşulmaly kanallar
    for i, (name, url) in enumerate(kanallar, 1):
        row.append(InlineKeyboardButton(name, url=url))
        if i % 2 == 0:
            kanal_buttons.append(row)
            row = []
    if row:
        kanal_buttons.append(row)

    # Optional kanallar
    for name, url in optional_kanallar:
        kanal_buttons.append([InlineKeyboardButton(name, url=url)])

    kanal_buttons.append([InlineKeyboardButton("Agza boldum ✅", callback_data="kody_al")])
    keyboard = InlineKeyboardMarkup(kanal_buttons)

    await update.message.reply_text(menu_yazgy, reply_markup=keyboard)


# ====================== Admin panel ======================
async def show_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👑 Sponsor goş ", callback_data="kanal_gos"),
         InlineKeyboardButton("📛 Sponsor aýyr", callback_data="kanal_ayyr")],
        [InlineKeyboardButton("🕵‍♂ Gizlin kanal goş", callback_data="gizlin_kanal_gos"),
         InlineKeyboardButton("📛 Gizlin kanal aýyr", callback_data="gizlin_kanal_ayyr")],
        [InlineKeyboardButton("💠 Optional kanal goş", callback_data="optional_kanal_gos"),
         InlineKeyboardButton("💠 Optional kanal aýyr", callback_data="optional_kanal_ayyr")],
        [InlineKeyboardButton("🔄 VPN kod üýtget", callback_data="vpn_uytget"),
         InlineKeyboardButton("✏️ Menýu üýtget", callback_data="menu_uytget")],
        [InlineKeyboardButton("🔁 Kanal tertibi", callback_data="kanal_tertibi")],
        [InlineKeyboardButton("🔀 Kanallara post", callback_data="kanallara_post")],
        [InlineKeyboardButton("🔔 Rassylka", callback_data="bildiris"),
         InlineKeyboardButton("📊 Statistika", callback_data="statistika")],
        [InlineKeyboardButton("👑 Admin goş", callback_data="admin_gos"),
         InlineKeyboardButton("📛 Admin aýyr", callback_data="admin_ayyr")],
        [InlineKeyboardButton("🚫 Gadagan et", callback_data="banla"),
         InlineKeyboardButton("✅ Gadagançylygy aýyr", callback_data="ban_ac")]
    ])
    await update.message.reply_text("Admin panel:", reply_markup=admin_keyboard)


async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in adminler:
        return
    await show_panel(update, context)


# ====================== Callback handler ======================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # ---- Kody alyň ----
    if query.data == "kody_al":
        if user_id in banlananlar:
            await query.message.reply_text("Siz banlandyňyz.")
            return

        not_joined = []
        for name, url in kanallar + gizlin_kanallar:
            kanal_username = url.split("/")[-1]
            try:
                member = await context.bot.get_chat_member(chat_id=f"@{kanal_username}", user_id=user_id)
                if member.status in ["left", "kicked"]:
                    not_joined.append(name)
            except:
                not_joined.append(name)

        if not_joined:
            await query.message.reply_text(
                "Siz aşakdaky kanallara goşulmadyk:\n" +
                "\n".join(f"• {n}" for n in not_joined)
            )
            return

        await query.message.reply_text(vpn_kody)
        try:
            with open(vpn_faýl_ýoly, "rb") as file:
                await context.bot.send_document(chat_id=user_id, document=file,
                                              filename=os.path.basename(vpn_faýl_ýoly))
        except FileNotFoundError:
            await query.message.reply_text("Siziň Koduňyz")

    # ---- Admin panel ----
    elif query.data == "panel":
        if user_id not in adminler:
            await query.message.reply_text("Bu diňe admin üçin.")
            return
        await show_panel(update, context)

    # ---- Ban / Unban ----
    elif query.data == "banla":
        context.user_data["banla"] = True
        await query.message.reply_text("Ulanyjy ID giriziň (gadagan etmek üçin):")
    elif query.data == "ban_ac":
        context.user_data["ban_ac"] = True
        await query.message.reply_text("ID giriziň (gadagançylygy aýyrmak üçin):")

    # ---- VPN / Menýu ----
    elif query.data == "vpn_uytget":
        context.user_data["vpn_text_only"] = True
        await query.message.reply_text("Täze VPN koduny giriziň ✅(diňe tekst):")
    elif query.data == "menu_uytget":
        context.user_data["menu_uytget"] = True
        await query.message.reply_text("Täze menýu ýazgysyny giriziň✅")

    # ---- Kanal goş/aýyr (oddiy) ----
    elif query.data == "kanal_gos":
        context.user_data["kanal_gos"] = True
        await query.message.reply_text("Kanal ady we URL giriziň. Mysal: Kanal Ady | https://t.me/kanal")
    elif query.data == "kanal_ayyr":
        if not kanallar:
            await query.message.reply_text("Kanal ýok.")
        else:
            txt = "\n".join(f"{i+1}. {ad}" for i, (ad, _) in enumerate(kanallar))
            await query.message.reply_text(f"Aýyrmak isleýän kanalyň belgisi:\n{txt}")
            context.user_data["kanal_ayyr"] = True

    # ---- Gizlin kanal ----
    elif query.data == "gizlin_kanal_gos":
        context.user_data["gizlin_kanal_gos"] = True
        await query.message.reply_text("Gizlin kanal ady we URL giriziň. Mysal: Ady | https://t.me/kanal")
    elif query.data == "gizlin_kanal_ayyr":
        if not gizlin_kanallar:
            await query.message.reply_text("Gizlin kanal ýok.")
        else:
            txt = "\n".join(f"{i+1}. {ad}" for i, (ad, _) in enumerate(gizlin_kanallar))
            await query.message.reply_text(f"Aýyrmak isleýän gizlin kanalyň belgisi:\n{txt}")
            context.user_data["gizlin_kanal_ayyr"] = True

    # ---- Optional kanal ----
    elif query.data == "optional_kanal_gos":
        context.user_data["optional_kanal_gos"] = True
        await query.message.reply_text("Optional kanal ady we URL giriziň. Mysal: Ady | https://t.me/kanal")
    elif query.data == "optional_kanal_ayyr":
        if not optional_kanallar:
            await query.message.reply_text("Optional kanal ýok.")
        else:
            txt = "\n".join(f"{i+1}. {ad}" for i, (ad, _) in enumerate(optional_kanallar))
            await query.message.reply_text(f"Aýyrmak isleýän optional kanalyň belgisi:\n{txt}")
            context.user_data["optional_kanal_ayyr"] = True

    # ---- Admin goş/aýyr ----
    elif query.data == "admin_gos":
        context.user_data["admin_gos"] = True
        await query.message.reply_text("Täze admin ID giriziň:")
    elif query.data == "admin_ayyr":
        if len(adminler) <= 1:
            await query.message.reply_text("Diňe bir admin bar.")
            return
        txt = ""
        for aid in adminler:
            try:
                u = await context.bot.get_chat(aid)
                name = u.username or u.first_name or "no name"
                txt += f"{aid} @{name}\n"
            except:
                txt += f"{aid} (tapylmady)\n"
        await query.message.reply_text(f"Aýyrmak isleýän adminiň ID-si:\n{txt}")
        context.user_data["admin_ayyr"] = True

    # ---- Bildiriş / Statistika ----
    elif query.data == "bildiris":
        context.user_data["bildiris"] = True
        await query.message.reply_text("Bildirişi giriziň:")
    elif query.data == "statistika":
        if user_id not in adminler:
            await query.message.reply_text("Bu diňe admin üçin.")
            return
        stats = (
            f"*Bot Statistikalary*\n\n"
            f"Ulanyjylar: *{len(ulanyjylar)}*\n"
            f"Banlananlar: *{len(banlananlar)}*\n"
            f"Adminler: *{len(adminler)}*\n"
            f"Kanallar: *{len(kanallar)}*\n"
            f"Gizlin: *{len(gizlin_kanallar)}*\n"
            f"Optional: *{len(optional_kanallar)}*\n"
            f"Sponsor: *{len(sponsor_kanallar)}*"
        )
        await query.message.reply_text(stats, parse_mode="Markdown")

    # ---- Kanallara post ----
    elif query.data == "kanallara_post":
        if user_id not in adminler:
            await query.message.reply_text("Bu diňe admin üçin.")
            return
        context.user_data["kanallara_post"] = True
        context.user_data["post_data"] = {"text": "", "photo": None, "buttons": []}
        await query.message.reply_text("Text ugradyň:")

    # ---- Kanal tertibi (täze) ----
    elif query.data == "kanal_tertibi":
        if not kanallar:
            await query.message.reply_text("Kanal ýok.")
            return
        txt = "\n".join(f"{i+1}. {ad}" for i, (ad, _) in enumerate(kanallar))
        await query.message.reply_text(
            f"*Kanallaryň tertibi*\n{txt}\n\n"
            "`1 - 4` ýaly ýazyp iki kanalyň ýerini çalyşyň",
            parse_mode="Markdown"
        )
        context.user_data["kanal_tertibi"] = True


# ====================== Mesaj handler ======================
async def mesaj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text or ""

    # ------------------ Kanallara post ------------------
    if context.user_data.get("kanallara_post"):
        post = context.user_data.get("post_data", {"text": "", "photo": None, "buttons": []})

        # 1. Tekst
        if not post["text"]:
            post["text"] = text
            context.user_data["post_data"] = post
            await update.message.reply_text("Surat goşmak isleýärsiňmi? (hökman däl, 'Gec' diý)")
            return

        # 2. Surat
        if not post["photo"] and update.message.photo:
            post["photo"] = update.message.photo[-1].file_id
            context.user_data["post_data"] = post
            await update.message.reply_text("Knopka goşmak isleýärsiňmi?\nMysal:\n`Knopka - https://t.me/bot`\n(Yok diý)")
            return
        if not post["photo"] and text.lower() == "gec":
            await update.message.reply_text("Knopka goşmak isleýärsiňmi?\n(Yok diý)")
            return

        # 3. Knopka
        if text.lower() == "yok":
            await send_post_to_channels(update, context)
            return

        btns = re.findall(r"(.+?)\s*-\s*(https?://\S+)", text)
        if btns:
            post["buttons"] = btns
            context.user_data["post_data"] = post
            await send_post_to_channels(update, context)
            return
        else:
            await update.message.reply_text("Nädogry format. Mysal:\n`Knopka - https://t.me/bot`\n(Yok diý)")
            return

    # ------------------ Kanal tertibi ------------------
    if context.user_data.get("kanal_tertibi"):
        m = re.match(r"(\d+)\s*-\s*(\d+)", text.strip())
        if m and len(kanallar) > 1:
            i1, i2 = int(m.group(1)) - 1, int(m.group(2)) - 1
            if 0 <= i1 < len(kanallar) and 0 <= i2 < len(kanallar):
                kanallar[i1], kanallar[i2] = kanallar[i2], kanallar[i1]
                txt = "\n".join(f"{i+1}. {ad}" for i, (ad, _) in enumerate(kanallar))
                await update.message.reply_text(f"*Tertip üýtgedildi*\n{txt}", parse_mode="Markdown")
            else:
                await update.message.reply_text("Belgiler nädogry.")
        else:
            await update.message.reply_text("Nädogry format. Mysal: `1 - 3`")
        del context.user_data["kanal_tertibi"]
        return

    # ------------------ Ban / Unban ------------------
    if context.user_data.get("banla"):
        try:
            banlananlar.append(int(text))
            await update.message.reply_text("Banlandy.")
        except:
            await update.message.reply_text("Nädogry ID")
        del context.user_data["banla"]
        return

    if context.user_data.get("ban_ac"):
        try:
            banlananlar.remove(int(text))
            await update.message.reply_text("Ban açyldy.")
        except:
            await update.message.reply_text("ID tapylmady")
        del context.user_data["ban_ac"]
        return

    # ------------------ VPN / Menýu ------------------
    if context.user_data.get("vpn_text_only"):
        global vpn_kody
        vpn_kody = text
        await update.message.reply_text(f"Täze VPN kody:\n```\n{vpn_kody}\n```", parse_mode="Markdown")
        del context.user_data["vpn_text_only"]
        return

    if context.user_data.get("menu_uytget"):
        global menu_yazgy
        menu_yazgy = text
        await update.message.reply_text(f"Täze menýu:\n```\n{menu_yazgy}\n```", parse_mode="Markdown")
        del context.user_data["menu_uytget"]
        return

    # ------------------ Bildiriş ------------------
    if context.user_data.get("bildiris"):
        for uid in ulanyjylar:
            try:
                await context.bot.send_message(uid, f"Bildiriş:\n\n{text}")
            except:
                pass
        await update.message.reply_text(f"Bildiriş ugradyldy:\n```\n{text}\n```", parse_mode="Markdown")
        del context.user_data["bildiris"]
        return

    # ------------------ Kanal goş/aýyr ------------------
    if context.user_data.get("kanal_gos"):
        try:
            ad, url = map(str.strip, text.split("|"))
            if not url.startswith("https://t.me/"):
                raise ValueError
            kanallar.append((ad, url))
            await update.message.reply_text("Kanal goşuldy")
        except:
            await update.message.reply_text("Format: `Ady | https://t.me/kanal`")
        del context.user_data["kanal_gos"]
        return

    if context.user_data.get("kanal_ayyr"):
        try:
            idx = int(text) - 1
            rem = kanallar.pop(idx)
            await update.message.reply_text(f"Kanal aýryldy: {rem[0]}")
        except:
            await update.message.reply_text("Nädogry belgi")
        del context.user_data["kanal_ayyr"]
        return

    # ------------------ Gizlin kanal ------------------
    if context.user_data.get("gizlin_kanal_gos"):
        try:
            ad, url = map(str.strip, text.split("|"))
            if not url.startswith("https://t.me/"):
                raise ValueError
            gizlin_kanallar.append((ad, url))
            await update.message.reply_text("Gizlin kanal goşuldy")
        except:
            await update.message.reply_text("Format: `Ady | https://t.me/kanal`")
        del context.user_data["gizlin_kanal_gos"]
        return

    if context.user_data.get("gizlin_kanal_ayyr"):
        try:
            idx = int(text) - 1
            rem = gizlin_kanallar.pop(idx)
            await update.message.reply_text(f"Gizlin kanal aýryldy: {rem[0]}")
        except:
            await update.message.reply_text("Nädogry belgi")
        del context.user_data["gizlin_kanal_ayyr"]
        return

    # ------------------ Optional kanal ------------------
    if context.user_data.get("optional_kanal_gos"):
        try:
            ad, url = map(str.strip, text.split("|"))
            if not url.startswith("https://t.me/"):
                raise ValueError
            optional_kanallar.append((ad, url))
            await update.message.reply_text("Optional kanal goşuldy")
        except:
            await update.message.reply_text("Format: `Ady | https://t.me/kanal`")
        del context.user_data["optional_kanal_gos"]
        return

    if context.user_data.get("optional_kanal_ayyr"):
        try:
            idx = int(text) - 1
            rem = optional_kanallar.pop(idx)
            await update.message.reply_text(f"Optional kanal aýryldy: {rem[0]}")
        except:
            await update.message.reply_text("Nädogry belgi")
        del context.user_data["optional_kanal_ayyr"]
        return

    # ------------------ Sponsor kanal ------------------
    if context.user_data.get("sponsor_gos"):
        try:
            ad, url = map(str.strip, text.split("|"))
            if not url.startswith("https://t.me/"):
                raise ValueError
            sponsor_kanallar.append((ad, url))
            await update.message.reply_text("Sponsor kanal goşuldy")
        except:
            await update.message.reply_text("Format: `Ady | https://t.me/kanal`")
        del context.user_data["sponsor_gos"]
        return

    if context.user_data.get("sponsor_ayyr"):
        try:
            idx = int(text) - 1
            rem = sponsor_kanallar.pop(idx)
            await update.message.reply_text(f"Sponsor kanal aýryldy: {rem[0]}")
        except:
            await update.message.reply_text("Nädogry belgi")
        del context.user_data["sponsor_ayyr"]
        return

    # ------------------ Admin goş/aýyr ------------------
    if context.user_data.get("admin_gos"):
        try:
            nid = int(text)
            adminler.add(nid)
            await update.message.reply_text(f"Täze admin: {nid}")
        except:
            await update.message.reply_text("Nädogry ID")
        del context.user_data["admin_gos"]
        return

    if context.user_data.get("admin_ayyr"):
        try:
            rid = int(text)
            if rid not in adminler:
                await update.message.reply_text("Admin däl")
            elif len(adminler) <= 1:
                await update.message.reply_text("Diňe bir admin galýar")
            else:
                adminler.remove(rid)
                await update.message.reply_text(f"Admin aýryldy: {rid}")
        except:
            await update.message.reply_text("Nädogry ID")
        del context.user_data["admin_ayyr"]
        return


# ====================== Post ugratmak ======================
async def send_post_to_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post = context.user_data.get("post_data", {"text": "", "photo": None, "buttons": []})
    keyboard = []
    row = []
    for name, url in post["buttons"]:
        row.append(InlineKeyboardButton(name.strip(), url=url.strip()))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None

    all_ch = kanallar + optional_kanallar + sponsor_kanallar
    if not all_ch:
        await update.message.reply_text("Ugradyljak kanal ýok.")
        del context.user_data["kanallara_post"]
        del context.user_data["post_data"]
        return

    ok = 0
    for _, url in all_ch:
        ch = url.split("/")[-1]
        try:
            if post["photo"]:
                await context.bot.send_photo(f"@{ch}", photo=post["photo"], caption=post["text"], reply_markup=reply_markup)
            else:
                await context.bot.send_message(f"@{ch}", text=post["text"], reply_markup=reply_markup)
            ok += 1
        except Exception as e:
            await update.message.reply_text(f"@{ch} ugradyp bolmady: {e}")
    await update.message.reply_text(f"Post {ok} kanala ugradyldy.")
    del context.user_data["kanallara_post"]
    del context.user_data["post_data"]


# ====================== Bot başlat ======================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("panel", panel))
app.add_handler(CallbackQueryHandler(callback_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_handler))
app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, mesaj_handler))

print("Bot başlady!")
app.run_polling()