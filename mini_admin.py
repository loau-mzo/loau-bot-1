import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

from helpers import read_lines, write_text, append_line

logger = logging.getLogger(__name__)

BROADCAST_STATE = 0

def get_mini_admin_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton('عدد المشتركين 👥', callback_data='mini_admin_users'),
            InlineKeyboardButton('رسالة للكل 📩', callback_data='mini_admin_set_bc')
        ],
        [InlineKeyboardButton('حالة البوت 🔋', callback_data='mini_admin_stats')]
    ]
    return InlineKeyboardMarkup(keyboard)

def mini_admin_panel(update: Update, context: CallbackContext) -> None:
    """Shows the mini admin panel."""
    text = "أهلا مطوري...\nشبيك لبيك البوت بين يديك..."
    update.message.reply_text(text, reply_markup=get_mini_admin_keyboard())

def show_user_count(update: Update, context: CallbackContext) -> None:
    """Shows the user count from the stats file."""
    query = update.callback_query
    users_list = read_lines(context.bot_data['stats_users_file'])
    query.answer(f"المشتركين {len(users_list)}", show_alert=True)

def set_broadcast_prompt(update: Update, context: CallbackContext) -> int:
    """Asks for the broadcast message."""
    query = update.callback_query
    users_list = read_lines(context.bot_data['stats_users_file'])
    text = f"أرسل رسالتك ليتم إرسالها إلى {len(users_list)} مشترك 👥\nكتابة فقط...🌚"

    write_text(context.bot_data['stats_bc_file'], "yas")

    query.answer()
    query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("الغاء 🚫", callback_data="mini_admin_cancel_bc")]]))
    return BROADCAST_STATE

def cancel_broadcast(update: Update, context: CallbackContext) -> int:
    """Cancels the broadcast."""
    query = update.callback_query
    write_text(context.bot_data['stats_bc_file'], "no")
    query.answer("تم الالغاء")
    query.edit_message_text("تم الغاء الاذاعة.")
    return ConversationHandler.END

def handle_broadcast_message(update: Update, context: CallbackContext) -> int:
    """Handles the broadcast message and sends it to users."""
    message_text = update.message.text
    stats_bc_file = context.bot_data['stats_bc_file']

    if read_lines(stats_bc_file)[0] != "yas":
        return ConversationHandler.END

    users_list = read_lines(context.bot_data['stats_users_file'])
    update.message.reply_text(f"تم قبول رسالتك!\nويتم إرسالها إلى {len(users_list)} مشترك 👥")

    for user_id in users_list:
        try:
            context.bot.send_message(chat_id=user_id, text=message_text)
        except Exception as e:
            logger.warning(f"Mini broadcast failed for user {user_id}: {e}")

    write_text(stats_bc_file, "no")
    return ConversationHandler.END

def show_bot_status(update: Update, context: CallbackContext) -> None:
    """Shows bot status."""
    # This is a simplified version of the PHP's speed check
    query = update.callback_query
    bot_username = context.bot.username
    date = datetime.datetime.now().strftime("%y/%m/%d")
    time = datetime.datetime.now().strftime("%H:%M:%S")

    text = f"معلومات البوت:\n\nمعرف البوت [ @{bot_username} ]\nحالة البوت ممتازة\nالوقت الآن: 20{date} | {time}"
    query.answer()
    query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data="mini_admin_main")]]))

def main_menu_from_status(update: Update, context: CallbackContext) -> None:
    """Goes back to the main mini admin menu."""
    query = update.callback_query
    text = "أهلا مطوري...\nشبيك لبيك البوت بين يديك..."
    query.answer()
    query.edit_message_text(text, reply_markup=get_mini_admin_keyboard())

def add_user_to_stats(update: Update, context: CallbackContext) -> None:
    """Adds a user to the stats file if they don't exist."""
    user = update.effective_user
    if not user: return

    stats_file = context.bot_data.get('stats_users_file')
    if not stats_file: return

    users_list = read_lines(stats_file)
    if str(user.id) not in users_list:
        append_line(stats_file, user.id)
