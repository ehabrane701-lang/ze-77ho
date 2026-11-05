#!/usr/bin/env python3
"""
𝙴𝙻𝙼𝙾𝙳𝙼𝙴𝙽 𝙷𝙾𝚂𝚃 - بوت التحكم الكامل v4 & مشغل بوتات التلجرام المدمج
"""

import os
import io
import sys
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatJoinRequest
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler,
    ChatJoinRequestHandler
)

# ========== إعداد السجل (Logging) ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== إعدادات البوت الأساسية ==========
BOT_TOKEN = os.getenv("BOT_TOKEN", "9057598891:AAGU-aOtkAydGZqLjd2xRwepsvlQW6xcggE")
API_BASE_URL = os.getenv("API_BASE_URL", "")

# ========== قائمة المسؤولين ==========
ADMIN_IDS = [
    5603553783,
]

# ========== دوال مساعدة لطلب API والتخزين ==========
def api_request(endpoint, method="GET", data=None, params=None, files=None):
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            resp = requests.get(url, params=params, timeout=30)
        elif method == "POST":
            if files:
                resp = requests.post(url, data=data, files=files, timeout=30)
            else:
                resp = requests.post(url, json=data, timeout=30)
        else:
            return None
        return resp.json() if resp else None
    except Exception as e:
        logger.error(f"API Request Error ({endpoint}): {e}")
        return {"success": False, "message": str(e)}

def api_download_file(endpoint, params=None):
    url = f"{API_BASE_URL}{endpoint}"
    try:
        resp = requests.get(url, params=params, timeout=60)
        if resp.status_code == 200:
            return resp.content, resp.headers.get('Content-Disposition', '')
        return None, None
    except Exception as e:
        logger.error(f"File Download Error ({endpoint}): {e}")
        return None, None

def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    chat_id = update.effective_chat.id
    if chat_id in ADMIN_IDS:
        return True
    return context.user_data.get("is_admin", False)

def format_user_info(user) -> str:
    """تنسيق معلومات المستخدم للإشعارات"""
    name = user.full_name or "بدون اسم"
    username = f"@{user.username}" if user.username else "بدون يوزر"
    uid = user.id
    return f"👤 الاسم: {name}\n🔗 اليوزر: {username}\n🆔 الآيدي: `{uid}`"

# ========== حالات المحادثة (Conversation States) ==========
(WAITING_FOR_API_KEY, WAITING_FOR_NEW_SERVER_NAME, WAITING_FOR_DELETE_USERNAME,
 WAITING_FOR_DOWNLOAD_USER, WAITING_FOR_DOWNLOAD_SERVER, WAITING_FOR_DOWNLOAD_FILE,
 WAITING_FOR_BROADCAST_MSG, WAITING_FOR_BAN_USER, WAITING_FOR_UNBAN_USER,
 WAITING_FOR_ADD_ADMIN, WAITING_FOR_SET_SERVERS) = range(11)

# ==========================================================
# قسم مشغل بوتات التلجرام (Runner Section - SERVERHUP / MERO HOST)
# ==========================================================
async def runner_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /start للبوتات المشغلة"""
    await update.message.reply_text(
        "👋 مرحباً! أنا بوت تلجرام يعمل من خلال SERVERHUP BRO HOST\n\n"
        "الأوامر المتاحة:\n"
        "/start - عرض هذه الرسالة\n"
        "/help - الحصول على المساعدة\n"
        "/info - معلومات البوت"
    )

async def runner_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /help للبوتات المشغلة"""
    await update.message.reply_text(
        "📚 المساعدة:\n\n"
        "هذا البوت يعمل بشكل مستمر على خادم SERVERHUP BRO HOST\n"
        "يمكنك إرسال أي رسالة والبوت سيرد عليك"
    )

async def runner_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /info للبوتات المشغلة"""
    await update.message.reply_text(
        "ℹ️ معلومات البوت:\n\n"
        "🤖 البوت: SERVERHUP BRO HOST Bot\n"
        "🏠 الخادم: SERVERHUP BRO HOST\n"
        "✅ الحالة: نشط ومستمر"
    )

async def runner_handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج الرسائل العادية للبوتات المشغلة"""
    if not update.message or not update.message.text:
        return
    user_message = update.message.text
    await update.message.reply_text(
        f"📨 تم استقبال رسالتك:\n\n{user_message}\n\n"
        "شكراً لاستخدامك mero_host!"
    )

async def runner_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج الأخطاء للبوتات المشغلة"""
    logger.error(msg="Exception while handling an update in runner:", exc_info=context.error)

def run_bot(token: str, bot_name: str) -> None:
    """تشغيل البوت باستخدام التوكن المعطى بشكل منفصل"""
    try:
        print("\n" + "═"*60)
        print(f" 🤖 [mero HOST] - جاري تشغيل البوت: {bot_name}")
        print(" 🚀 يتم الآن الاتصال بخوادم تلجرام...")
        print("═"*60 + "\n")
        
        logger.info(f"🤖 بدء تشغيل البوت: {bot_name}")
        
        application = Application.builder().token(token).build()

        application.add_handler(CommandHandler("start", runner_start))
        application.add_handler(CommandHandler("help", runner_help_command))
        application.add_handler(CommandHandler("info", runner_info_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, runner_handle_message))
        application.add_error_handler(runner_error_handler)

        print("\n" + "✨"*20)
        print(f" ✅ البوت {bot_name} جاهز الآن!")
        print(" 📡 الحالة: نشط وينتظر الرسائل...")
        print(" ✨ استمتع بخدمة ZAEM BRO HOST ✨")
        print("✨"*20 + "\n")
        
        logger.info(f"✅ البوت {bot_name} جاهز وينتظر الرسائل...")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل البوت {bot_name}: {str(e)}")


# ==========================================================
# قسم لوحة التحكم الرئيسية (ELMODMEN HOST v4)
# ==========================================================
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = None
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        message = query.message
    else:
        message = None

    keyboard = [
        [InlineKeyboardButton("📁 سيرفراتي", callback_data="my_servers")],
        [InlineKeyboardButton("➕ إنشاء سيرفر جديد", callback_data="create_server")],
        [InlineKeyboardButton("🚪 تسجيل الخروج", callback_data="logout")]
    ]

    if is_admin(update, context):
        keyboard.append([InlineKeyboardButton("👑 لوحة الإدارة", callback_data="admin_panel")])

    username = context.user_data.get('username', '')
    text = f"🔹 *القائمة الرئيسية* 🔹\nمرحباً {username}!"

    if message:
        try:
            await message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            await message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== طلبات الانضمام للبوت ==========
async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة طلبات الانضمام وإرسالها للأدمن"""
    join_request = update.chat_join_request
    if not join_request:
        return
    user = join_request.from_user
    chat = join_request.chat

    if "pending_join_requests" not in context.bot_data:
        context.bot_data["pending_join_requests"] = {}

    req_key = f"{chat.id}:{user.id}"
    context.bot_data["pending_join_requests"][req_key] = {
        "user_id": user.id,
        "chat_id": chat.id,
        "full_name": user.full_name,
        "username": user.username,
    }

    for admin_id in ADMIN_IDS:
        try:
            keyboard = [
                [
                    InlineKeyboardButton("✅ قبول", callback_data=f"jr_accept:{req_key}"),
                    InlineKeyboardButton("❌ رفض", callback_data=f"jr_decline:{req_key}")
                ]
            ]
            text = (
                f"📨 *طلب انضمام جديد!*\n\n"
                f"{format_user_info(user)}\n\n"
                f"📌 الجروب/القناة: `{chat.title}`\n"
                f"🆔 ID الجروب: `{chat.id}`"
            )
            await context.bot.send_message(
                chat_id=admin_id,
                text=text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            logger.error(f"خطأ إرسال طلب للأدمن {admin_id}: {e}")

async def handle_join_request_action(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str, req_key: str):
    query = update.callback_query
    parts = req_key.split(":")
    if len(parts) != 2:
        await query.answer("❌ طلب غير صالح", show_alert=True)
        return

    chat_id = int(parts[0])
    user_id = int(parts[1])

    try:
        if action == "accept":
            await context.bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)
            await query.edit_message_text(
                query.message.text + "\n\n✅ *تم القبول بنجاح!*",
                parse_mode="Markdown"
            )
        else:
            await context.bot.decline_chat_join_request(chat_id=chat_id, user_id=user_id)
            await query.edit_message_text(
                query.message.text + "\n\n❌ *تم الرفض.*",
                parse_mode="Markdown"
            )
        if "pending_join_requests" in context.bot_data:
            context.bot_data["pending_join_requests"].pop(req_key, None)
    except Exception as e:
        await query.answer(f"❌ خطأ: {e}", show_alert=True)

async def notify_admins_new_user(context: ContextTypes.DEFAULT_TYPE, user):
    """إرسال إشعار لكل الأدمنية بمستخدم جديد مع زر فتح المحادثة"""
    for admin_id in ADMIN_IDS:
        try:
            keyboard = [[InlineKeyboardButton("💬 فتح المحادثة", url=f"tg://user?id={user.id}")]]
            text = (
                f"🆕 *مستخدم جديد فتح البوت!*\n\n"
                f"{format_user_info(user)}"
            )
            await context.bot.send_message(
                chat_id=admin_id,
                text=text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            logger.error(f"خطأ إشعار أدمن {admin_id}: {e}")

# ========== سيرفرات المستخدم ==========
async def show_servers_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    result = api_request("/api/bot/servers", params={"api_key": context.user_data.get("api_key", "")})
    if not result or not result.get("success"):
        await query.edit_message_text("❌ فشل جلب السيرفرات.")
        return
    servers = result.get("servers", [])
    if not servers:
        await query.edit_message_text(
            "🚀 لا توجد سيرفرات حالياً.\nاستخدم 'إنشاء سيرفر جديد'.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]]))
        return
    for srv in servers:
        status_emoji = "🟢" if srv.get('status') == "Running" else "⚫"
        text = f"{status_emoji} *{srv.get('title')}*\n"
        text += f"📊 الحالة: {srv.get('status')}\n🔌 المنفذ: {srv.get('port')}\n💾 الخطة: {srv.get('plan')}\n⏱️ وقت التشغيل: {srv.get('uptime')}"
        keyboard = [
            [InlineKeyboardButton("▶️ تشغيل", callback_data=f"action_{srv.get('folder')}_start"),
             InlineKeyboardButton("⏹️ إيقاف", callback_data=f"action_{srv.get('folder')}_stop"),
             InlineKeyboardButton("🔄 إعادة", callback_data=f"action_{srv.get('folder')}_restart")],
            [InlineKeyboardButton("🗑️ حذف", callback_data=f"action_{srv.get('folder')}_delete"),
             InlineKeyboardButton("🖥️ كونسول", callback_data=f"console_{srv.get('folder')}"),
             InlineKeyboardButton("📁 ملفات", callback_data=f"files_{srv.get('folder')}")],
        ]
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    await show_main_menu(update, context)

# ========== لوحة الإدارة الكاملة ==========
async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(update, context):
        await query.edit_message_text("❌ غير مصرح.")
        return

    result = api_request("/api/admin/users", params={"api_key": context.user_data.get("api_key", "")})
    users = result.get("users", []) if result and result.get("success") else []
    metrics = api_request("/api/system/metrics") or {}

    cpu = metrics.get("cpu", "0")
    ram = metrics.get("memory", "0")
    pending_count = len(context.bot_data.get("pending_join_requests", {}))

    text = "👑 *لوحة إدارة 𝙴𝙻𝙼𝙾𝙳𝙼𝙴𝙽 𝙷𝙾𝚂𝚃*\n\n"
    text += f"👥 المستخدمين: `{len(users)}`\n"
    text += f"🖥️ CPU: `{cpu}%` | 💾 RAM: `{ram}%`\n"
    if pending_count > 0:
        text += f"📨 طلبات انضمام معلقة: `{pending_count}`\n"
    text += "━━━━━━━━━━━━━━━━━━━━\n"
    for u in users[:8]:
        status = "🔴" if u.get("banned") else "🟢"
        text += f"{status} `{u.get('username')}` | سيرفرات: {u.get('max_servers', 1)}\n"
    if len(users) > 8:
        text += f"\n... و {len(users) - 8} مستخدم آخر"

    keyboard = [
        [InlineKeyboardButton("📊 إحصائيات النظام", callback_data="admin_stats"),
         InlineKeyboardButton("👥 عرض المستخدمين", callback_data="admin_list_users")],
        [InlineKeyboardButton("🗑️ حذف مستخدم", callback_data="admin_delete_user"),
         InlineKeyboardButton("📥 تحميل ملفات", callback_data="admin_download_files")],
        [InlineKeyboardButton("🚫 حظر مستخدم", callback_data="admin_ban_user"),
         InlineKeyboardButton("✅ رفع حظر", callback_data="admin_unban_user")],
        [InlineKeyboardButton("📣 رسالة جماعية", callback_data="admin_broadcast"),
         InlineKeyboardButton("⚙️ رفع حد السيرفرات", callback_data="admin_set_servers")],
        [InlineKeyboardButton("👮 إضافة أدمن", callback_data="admin_add_admin")],
        [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")]
    ]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(update, context):
        await query.edit_message_text("❌ غير مصرح.")
        return
    result = api_request("/api/admin/users", params={"api_key": context.user_data.get("api_key", "")})
    users = result.get("users", []) if result and result.get("success") else []
    if not users:
        await query.edit_message_text("لا يوجد مستخدمين.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]]))
        return
    text = "👥 *قائمة المستخدمين*\n\n"
    for u in users:
        status = "🔴" if u.get("banned") else "🟢"
        vip = "⭐" if u.get("is_vip") else ""
        adm = "👑" if u.get("is_admin") else ""
        text += f"{status}{vip}{adm} `{u.get('username')}` | سيرفرات: {u.get('max_servers', 1)}\n"
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]]
    if len(text) > 4000:
        text = text[:4000] + "\n..."
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== إدارة الحظر والحسابات والأدمنية ==========
async def admin_ban_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(update, context):
        return ConversationHandler.END
    await query.edit_message_text("🚫 أرسل اسم المستخدم المراد حظره:")
    context.user_data["admin_action"] = "ban"
    return WAITING_FOR_BAN_USER

async def admin_unban_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(update, context):
        return ConversationHandler.END
    await query.edit_message_text("✅ أرسل اسم المستخدم المراد رفع حظره:")
    context.user_data["admin_action"] = "unban"
    return WAITING_FOR_UNBAN_USER

async def admin_ban_execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return ConversationHandler.END
    username = update.message.text.strip()
    result = api_request("/api/admin/ban-user", method="POST", data={"username": username})
    if result and result.get("success"):
        await update.message.reply_text(f"🚫 تم حظر المستخدم `{username}` بنجاح.", parse_mode="Markdown")
    else:
        msg = result.get('message', 'خطأ') if result else 'خطأ'
        await update.message.reply_text(f"❌ فشل: {msg}")
    await show_main_menu(update, context)
    return ConversationHandler.END

async def admin_unban_execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return ConversationHandler.END
    username = update.message.text.strip()
    result = api_request("/api/admin/unban-user", method="POST", data={"username": username})
    if result and result.get("success"):
        await update.message.reply_text(f"✅ تم رفع حظر `{username}` بنجاح.", parse_mode="Markdown")
    else:
        msg = result.get('message', 'خطأ') if result else 'خطأ'
        await update.message.reply_text(f"❌ فشل: {msg}")
    await show_main_menu(update, context)
    return ConversationHandler.END

async def admin_broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(update, context):
        return ConversationHandler.END
    await query.edit_message_text("📣 أرسل الرسالة التي تريد إذاعتها لكل المستخدمين:")
    return WAITING_FOR_BROADCAST_MSG

async def admin_broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return ConversationHandler.END
    msg_text = update.message.text.strip()
    broadcast_result = api_request("/api/admin/broadcast", method="POST", data={
        "api_key": context.user_data.get("api_key", ""),
        "message": msg_text
    })
    if broadcast_result and broadcast_result.get("success"):
        await update.message.reply_text(f"✅ تم إرسال الإذاعة بنجاح!\n📊 {broadcast_result.get('message', '')}")
    else:
        msg = broadcast_result.get('message', 'تم الإرسال') if broadcast_result else 'تم الإرسال'
        await update.message.reply_text(f"⚠️ نتيجة الإذاعة: {msg}")
    await show_main_menu(update, context)
    return ConversationHandler.END

async def admin_set_servers_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(update, context):
        return ConversationHandler.END
    await query.edit_message_text("⚙️ أرسل: `اسم_المستخدم عدد_السيرفرات`\nمثال: `ahmed 5`", parse_mode="Markdown")
    return WAITING_FOR_SET_SERVERS

async def admin_set_servers_execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return ConversationHandler.END
    parts = update.message.text.strip().split()
    if len(parts) != 2 or not parts[1].isdigit():
        await update.message.reply_text("❌ صيغة خاطئة. استخدم: `اسم_المستخدم عدد_السيرفرات`", parse_mode="Markdown")
        return WAITING_FOR_SET_SERVERS
    username, count = parts[0], int(parts[1])
    result = api_request("/api/admin/set-servers", method="POST", data={"username": username, "max_servers": count})
    if result and result.get("success"):
        await update.message.reply_text(f"✅ تم ضبط حد السيرفرات لـ `{username}` على `{count}`", parse_mode="Markdown")
    else:
        msg = result.get('message', 'خطأ') if result else 'خطأ'
        await update.message.reply_text(f"❌ فشل: {msg}")
    await show_main_menu(update, context)
    return ConversationHandler.END

async def admin_add_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(update, context):
        return ConversationHandler.END
    await query.edit_message_text("👮 أرسل آيدي تيليجرام الشخص لإضافته كأدمن:\n(رقم الآيدي فقط)")
    return WAITING_FOR_ADD_ADMIN

async def admin_add_admin_execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return ConversationHandler.END
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("❌ أرسل رقم الآيدي فقط.")
        return WAITING_FOR_ADD_ADMIN
    new_admin_id = int(text)
    if new_admin_id not in ADMIN_IDS:
        ADMIN_IDS.append(new_admin_id)
        await update.message.reply_text(f"✅ تم إضافة `{new_admin_id}` كأدمن بنجاح!", parse_mode="Markdown")
        try:
            await context.bot.send_message(
                chat_id=new_admin_id,
                text="🎉 *مبروك!* تم تعيينك كأدمن في بوت 𝙴𝙻𝙼𝙾𝙳𝙼𝙴𝙽 𝙷𝙾𝚂𝚃",
                parse_mode="Markdown"
            )
        except Exception:
            pass
    else:
        await update.message.reply_text("ℹ️ هذا الشخص أدمن بالفعل.")
    await show_main_menu(update, context)
    return ConversationHandler.END

# ========== تحميل ملفات مستخدم (لأدمن التحكم) ==========
async def admin_download_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(update, context):
        await query.edit_message_text("❌ غير مصرح.")
        return ConversationHandler.END
    await query.edit_message_text("👤 أرسل اسم المستخدم الذي تريد تحميل ملفاته:")
    return WAITING_FOR_DOWNLOAD_USER

async def admin_download_got_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return ConversationHandler.END
    username = update.message.text.strip()
    context.user_data["dl_username"] = username
    result = api_request(f"/api/admin/list_user_servers/{username}",
                         params={"api_key": context.user_data.get("api_key", "")})
    if not result or not result.get("success"):
        await update.message.reply_text("❌ فشل جلب سيرفرات المستخدم أو المستخدم غير موجود.")
        return ConversationHandler.END
    servers = result.get("servers", [])
    if not servers:
        await update.message.reply_text("❌ لا توجد سيرفرات لهذا المستخدم.")
        return ConversationHandler.END
    keyboard = []
    for s in servers:
        emoji = "🟢" if s.get('status') == "Running" else "⚫"
        keyboard.append([InlineKeyboardButton(f"{emoji} {s.get('name')} ({s.get('language')})",
                                               callback_data=f"dlsrv_{s.get('folder')}")])
    keyboard.append([InlineKeyboardButton("❌ إلغاء", callback_data="main_menu")])
    await update.message.reply_text("🖥️ اختر السيرفر:", reply_markup=InlineKeyboardMarkup(keyboard))
    return WAITING_FOR_DOWNLOAD_SERVER

async def admin_download_got_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    folder = query.data.replace("dlsrv_", "")
    context.user_data["dl_folder"] = folder
    username = context.user_data.get("dl_username", "")
    result = api_request(f"/api/admin/list_user_files/{username}/{folder}",
                         params={"api_key": context.user_data.get("api_key", "")})
    if not result or not result.get("success"):
        await query.edit_message_text("❌ فشل جلب ملفات السيرفر.")
        return ConversationHandler.END
    files = [f for f in result.get("files", []) if not f.get('is_dir')]
    if not files:
        await query.edit_message_text("📂 لا توجد ملفات في هذا السيرفر.")
        return ConversationHandler.END
    keyboard = []
    for f in files[:20]:
        keyboard.append([InlineKeyboardButton(f"📄 {f.get('name')} ({f.get('size')})",
                                               callback_data=f"dlfile_{f.get('name')}")])
    keyboard.append([InlineKeyboardButton("❌ إلغاء", callback_data="main_menu")])
    await query.edit_message_text("📁 اختر الملف للتحميل:", reply_markup=InlineKeyboardMarkup(keyboard))
    return WAITING_FOR_DOWNLOAD_FILE

async def admin_download_got_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("⏳ جاري التحميل...")
    file_name = query.data.replace("dlfile_", "")
    username = context.user_data.get("dl_username", "")
    folder = context.user_data.get("dl_folder", "")
    await query.edit_message_text(f"⏳ جاري تحميل `{file_name}`...", parse_mode="Markdown")
    url = f"{API_BASE_URL}/api/admin/download_user_file"
    try:
        resp = requests.post(url, json={"username": username, "folder": folder, "file_path": file_name}, timeout=60)
        if resp.status_code == 200:
            file_bytes = io.BytesIO(resp.content)
            file_bytes.name = file_name
            await query.message.reply_document(
                document=file_bytes, filename=file_name,
                caption=f"📥 ملف `{file_name}`\n👤 المستخدم: `{username}`",
                parse_mode="Markdown"
            )
            await query.message.reply_text("✅ تم إرسال الملف!")
        else:
            await query.message.reply_text(f"❌ فشل التحميل: {resp.status_code}")
    except Exception as e:
        await query.message.reply_text(f"❌ خطأ: {str(e)}")
    return ConversationHandler.END

async def admin_delete_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(update, context):
        await query.edit_message_text("❌ غير مصرح.")
        return ConversationHandler.END
    await query.edit_message_text("📝 أرسل اسم المستخدم الذي تريد حذفه:")
    return WAITING_FOR_DELETE_USERNAME

async def admin_delete_user_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return ConversationHandler.END
    username = update.message.text.strip()
    result = api_request("/api/admin/delete-user", method="POST", data={"username": username})
    if result and result.get("success"):
        await update.message.reply_text(f"✅ تم حذف المستخدم `{username}`", parse_mode="Markdown")
    else:
        msg = result.get('message', 'خطأ') if result else 'خطأ'
        await update.message.reply_text(f"❌ فشل الحذف: {msg}")
    await show_main_menu(update, context)
    return ConversationHandler.END

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(update, context):
        await query.edit_message_text("❌ غير مصرح.")
        return
    metrics = api_request("/api/system/metrics") or {}
    users_result = api_request("/api/admin/users", params={"api_key": context.user_data.get("api_key", "")})
    total_users = len(users_result.get("users", [])) if users_result and users_result.get("success") else 0
    cpu = metrics.get("cpu", "0")
    ram = metrics.get("memory", "0")
    disk = metrics.get("disk", "0")
    text = "📊 *إحصائيات النظام*\n\n"
    text += f"🖥️ CPU: `{cpu}%`\n💾 RAM: `{ram}%`\n💿 الديسك: `{disk}%`\n👥 المستخدمين: `{total_users}`\n"
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== بدء بوت التحكم الرئيسي ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        return
    if not context.user_data.get("seen_before"):
        context.user_data["seen_before"] = True
        await notify_admins_new_user(context, user)

    if context.user_data.get("api_key"):
        result = api_request("/api/bot/verify", method="POST", data={"api_key": context.user_data["api_key"]})
        if result and result.get("success"):
            context.user_data["is_admin"] = result.get("is_admin", False)
            await update.message.reply_text(f"✅ مرحباً بعودتك {result.get('username')}!")
            await show_main_menu(update, context)
            return ConversationHandler.END
        else:
            context.user_data.clear()
            context.user_data["seen_before"] = True

    await update.message.reply_text(
        "🤖 *مرحباً بك في بوت 𝙴𝙻𝙼𝙾𝙳𝙼𝙴𝙽 𝙷𝙾𝚂𝚃!*\n\nأرسل مفتاح API الخاص بك.",
        parse_mode="Markdown"
    )
    return WAITING_FOR_API_KEY

async def handle_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return WAITING_FOR_API_KEY
    api_key = update.message.text.strip()
    result = api_request("/api/bot/verify", method="POST", data={"api_key": api_key})
    if not result or not result.get("success"):
        await update.message.reply_text("❌ مفتاح API غير صالح. حاول مرة أخرى.")
        return WAITING_FOR_API_KEY
    context.user_data["api_key"] = api_key
    context.user_data["username"] = result.get("username")
    context.user_data["is_admin"] = result.get("is_admin", False)
    await update.message.reply_text(f"✅ تم التحقق! مرحباً {result.get('username')}.")
    await show_main_menu(update, context)
    return ConversationHandler.END

async def handle_logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await query.edit_message_text("🚪 تم تسجيل الخروج. استخدم /start للدخول مجدداً.")

async def receive_server_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return ConversationHandler.END
    name = update.message.text.strip()
    result = api_request("/api/bot/create_server", method="POST", data={
        "api_key": context.user_data.get("api_key", ""),
        "name": name, "plan": "free", "storage": 100, "ram": 256, "cpu": 0.5
    })
    if result and result.get("success"):
        await update.message.reply_text(f"✅ تم إنشاء السيرفر `{name}` بنجاح!", parse_mode="Markdown")
    else:
        msg = result.get('message', 'خطأ') if result else 'خطأ'
        await update.message.reply_text(f"❌ فشل الإنشاء: {msg}")
    await show_main_menu(update, context)
    return ConversationHandler.END

# ========== معالج الأزرار الرئيسي للوحة التحكم ==========
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data.startswith("jr_accept:"):
        req_key = data[len("jr_accept:"):]
        await handle_join_request_action(update, context, "accept", req_key)
        return ConversationHandler.END
    elif data.startswith("jr_decline:"):
        req_key = data[len("jr_decline:"):]
        await handle_join_request_action(update, context, "decline", req_key)
        return ConversationHandler.END

    if data == "main_menu":
        await show_main_menu(update, context)
    elif data == "my_servers":
        await show_servers_list(update, context)
    elif data == "create_server":
        await query.edit_message_text("أرسل اسم السيرفر الجديد:")
        return WAITING_FOR_NEW_SERVER_NAME
    elif data == "logout":
        await handle_logout(update, context)
    elif data == "admin_panel":
        await show_admin_panel(update, context)
    elif data == "admin_list_users":
        await admin_list_users(update, context)
    elif data == "admin_delete_user":
        return await admin_delete_user_start(update, context)
    elif data == "admin_download_files":
        return await admin_download_start(update, context)
    elif data == "admin_ban_user":
        return await admin_ban_start(update, context)
    elif data == "admin_unban_user":
        return await admin_unban_start(update, context)
    elif data == "admin_broadcast":
        return await admin_broadcast_start(update, context)
    elif data == "admin_set_servers":
        return await admin_set_servers_start(update, context)
    elif data == "admin_add_admin":
        return await admin_add_admin_start(update, context)
    elif data.startswith("dlsrv_"):
        return await admin_download_got_server(update, context)
    elif data.startswith("dlfile_"):
        return await admin_download_got_file(update, context)
    elif data == "admin_stats":
        await admin_stats(update, context)
    elif data.startswith("action_"):
        parts = data.split('_')
        folder = '_'.join(parts[1:-1])
        action = parts[-1]
        result = api_request("/api/bot/server/action", method="POST", data={
            "api_key": context.user_data.get("api_key", ""),
            "folder": folder, "action": action
        })
        msg = result.get("message", "تم التنفيذ") if result and result.get("success") else "❌ فشل"
        try:
            await query.edit_message_text(msg)
        except Exception:
            pass
        await show_servers_list(update, context)
    elif data.startswith("console_"):
        folder = data[len("console_"):]
        result = api_request("/api/bot/console", params={
            "api_key": context.user_data.get("api_key", ""),
            "folder": folder
        })
        if result and result.get("success"):
            logs = result.get("logs", "لا توجد مخرجات")
            if len(logs) > 4000:
                logs = logs[-4000:] + "\n... (مقتطع)"
            keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="my_servers")]]
            await query.edit_message_text(f"📟 *كونسول السيرفر*\n```\n{logs}\n```",
                                          parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text("❌ فشل جلب الكونسول")
    elif data.startswith("files_"):
        folder = data[len("files_"):]
        result = api_request("/api/bot/files/list", params={
            "api_key": context.user_data.get("api_key", ""),
            "folder": folder, "path": ""
        })
        if result and result.get("success"):
            files = result.get("files", [])
            text = "📂 *ملفات السيرفر:*\n\n"
            for f in files[:20]:
                icon = "📁" if f.get('is_dir') else "📄"
                text += f"{icon} `{f.get('name')}` - {f.get('size')}\n"
            keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="my_servers")]]
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text("❌ فشل جلب الملفات")
    return ConversationHandler.END

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id not in ADMIN_IDS:
        await update.message.reply_text("❌ غير مصرح.")
        return
    keyboard = [
        [InlineKeyboardButton("👑 لوحة الإدارة", callback_data="admin_panel")]
    ]
    await update.message.reply_text(
        "👑 *لوحة الإدارة*\nاضغط للدخول:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("admin", admin_command),
            CallbackQueryHandler(button_callback)
        ],
        states={
            WAITING_FOR_API_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_api_key)],
            WAITING_FOR_NEW_SERVER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_server_name)],
            WAITING_FOR_DELETE_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_delete_user_confirm)],
            WAITING_FOR_DOWNLOAD_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_download_got_user)],
            WAITING_FOR_DOWNLOAD_SERVER: [CallbackQueryHandler(admin_download_got_server, pattern="^dlsrv_")],
            WAITING_FOR_DOWNLOAD_FILE: [CallbackQueryHandler(admin_download_got_file, pattern="^dlfile_")],
            WAITING_FOR_BROADCAST_MSG: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_broadcast_send)],
            WAITING_FOR_BAN_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_ban_execute)],
            WAITO_FOR_UNBAN_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_unban_execute)], # Handled below correctly
            WAITING_FOR_UNBAN_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_unban_execute)],
            WAITING_FOR_ADD_ADMIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_admin_execute)],
            WAITING_FOR_SET_SERVERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_set_servers_execute)],
        },
        fallbacks=[CommandHandler("start", start)],
        per_message=False,
    )

    app.add_handler(conv_handler)
    app.add_handler(ChatJoinRequestHandler(handle_join_request))

    print("🚀 بوت 𝙴𝙻𝙼𝙾𝙳𝙼𝙴𝙽 𝙷𝙾𝚂𝚃 v4 يعمل...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    # دعم تشغيل مشغل البوتات (Runner) من سطر الأوامر أو تشغيل لوحة التحكم الرئيسية تلقائياً
    if len(sys.argv) > 1:
        token = sys.argv[1]
        bot_name = sys.argv[2] if len(sys.argv) > 2 else "telegram_bot"
        run_bot(token, bot_name)
    else:
        main()
