import logging
import json
import time
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, ConversationHandler

# Local Imports
import keyboards
from helpers import read_lines, get_chat_link, write_text, append_line

# Conversation states
ADD_CHANNEL, BAN_USER, ADD_ADMIN, ADD_AD, BROADCAST_MESSAGE = range(5)
UPLOAD_MEMBERS, UPLOAD_GROUPS = range(5, 7)

logger = logging.getLogger(__name__)

def admin_panel(update: Update, context: CallbackContext) -> int:
    data_manager = context.bot_data['data_manager']
    query = update.callback_query
    text = "• اهلا بك في لوحه الأدمن الخاصه بالبوت 🤖\n\n- يمكنك التحكم في البوت الخاص بك من هنا\n\n~~~~~~~~~~~~~~~~~"
    keyboard = keyboards.get_main_admin_keyboard(data_manager.get('js'))
    if query:
        query.answer()
        query.edit_message_text(text=text, reply_markup=keyboard, parse_mode='Markdown')
    else:
        update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')
    js_data = data_manager.get('js')
    if 'type' in js_data and str(update.effective_user.id) in js_data['type']:
        del js_data['type'][str(update.effective_user.id)]
        data_manager.set('js', js_data)
    return ConversationHandler.END

# ... (all other handlers are the same, just fixing restore path)

def restore_backup(update: Update, context: CallbackContext) -> None:
    """Restores Js.json from Js.txt."""
    query = update.callback_query
    data_manager = context.bot_data['data_manager']
    js_backup_path = "Js.txt" # Corrected path

    if os.path.exists(js_backup_path):
        try:
            with open(js_backup_path, 'r') as f:
                js_data = json.load(f)
            data_manager.set('js', js_data)
            query.answer("تم تجديد البيانات ✅", show_alert=True)
            admin_panel(update, context)
        except Exception as e:
            query.answer(f"فشل الاستعادة: {e}", show_alert=True)
    else:
        query.answer("لا توجد بيانات لأستعادتها", show_alert=True)

# ... (rest of the file is the same)
