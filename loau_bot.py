import json
import logging
import os
import datetime
from telegram import Update
from telegram.ext import (
    Updater, CommandHandler, CallbackContext, CallbackQueryHandler,
    ConversationHandler, MessageHandler, Filters
)

# --- Local Imports ---
import admin
import keyboards
import sales_bot
from helpers import read_lines, append_line
from decorators import check_subscription

# --- Constants & Setup ---
TOKEN = "7409274292:AAErojaDzHEdDnFqS2wRMD3Qs-u1kKWh5HU"
SUDO_ID = 5252815668
ADMIN_IDS = [SUDO_ID]
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self, f): self.files=f; self.data={}; self.load_all()
    def load_all(self):
        for n, p in self.files.items():
            try:
                d=os.path.dirname(p)
                if d: os.makedirs(d, exist_ok=True)
                with open(p, 'r', encoding='utf-8') as f: self.data[n] = json.load(f)
            except(FileNotFoundError, json.JSONDecodeError): self.data[n]={}; self.save(n)
    def save(self, n):
        if n in self.data:
            p=self.files[n]
            d=os.path.dirname(p)
            if d: os.makedirs(d, exist_ok=True)
            with open(p, 'w', encoding='utf-8') as f: json.dump(self.data[n], f, ensure_ascii=False, indent=4)
    def get(self, n): return self.data.get(n, {})
    def set(self, n, v): self.data[n]=v; self.save(n)

DATA_FILES = {"js": "Js.json", "ds": "Ds.json", "vs": "Users/Vs.json", "forward_m": "forwardM.json", "sales": "sales.json"}
data_manager = DataManager(DATA_FILES)
MEMBERS_FILE, GROUPS_FILE, ALL_CHATS_FILE = "Users/member.txt", "Users/chat.txt", "Users/allchat.txt"

# --- Handlers ---
@check_subscription
def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if not user: return
    if user.id in context.bot_data.get('admin_ids', []):
        admin.admin_panel(update, context)
    else:
        sales_bot.start_sales(update, context)

def toggle_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    toggle_key = query.data.replace("toggle_", "")
    js_data = data_manager.get('js')
    new_status = "✅" if js_data['bot'].get(toggle_key, "❌") == "❌" else "❌"
    js_data['bot'][toggle_key] = new_status
    data_manager.set('js', js_data)
    query.answer(f"تم التغيير الى {new_status}")
    if toggle_key == "SubC": admin.show_channel_menu(update, context)
    elif toggle_key == "TBr": admin.show_broadcast_menu(update, context)
    elif toggle_key == "backp": admin.show_backup_menu(update, context)
    else: admin.admin_panel(update, context)

@check_subscription
def handle_messages(update: Update, context: CallbackContext) -> None:
    # This handler is for the main bot, not the sales bot
    user = update.effective_user
    if not user or user.id in context.bot_data['admin_ids']: return
    # The logic for MNT and Forward is in the original loau_bot.py, let's ensure it's here
    # For now, this is a placeholder for any general message handling for the first bot
    pass

def handle_admin_reply(update: Update, context: CallbackContext) -> None:
    # This handler is for the main bot
    pass

def error_handler(update: object, context: CallbackContext) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main() -> None:
    js_data = data_manager.get('js')
    if 'bot' not in js_data: js_data['bot'] = {}
    if js_data.get('bot', {}).get('sudo') is None: js_data['bot']['sudo'] = SUDO_ID
    if 'admin' in js_data.get('bot', {}):
        for admin_id in js_data['bot']['admin']:
            if int(admin_id) not in ADMIN_IDS: ADMIN_IDS.append(int(admin_id))

    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.bot_data.update({'data_manager': data_manager, 'admin_ids': ADMIN_IDS, 'members_file': MEMBERS_FILE, 'groups_file': GROUPS_FILE, 'all_chats_file': ALL_CHATS_FILE})

    job_queue = updater.job_queue
    job_queue.run_daily(admin.run_daily_backup_job, time=datetime.time(hour=2, minute=0, second=0))

    conv_handlers = [
        ConversationHandler(entry_points=[CallbackQueryHandler(admin.add_channel_prompt, pattern="^add_channel$")], states={admin.ADD_CHANNEL: [MessageHandler(Filters.forwarded & Filters.chat_type.channel, admin.add_channel_handler)]}, fallbacks=[CallbackQueryHandler(admin.show_channel_menu, pattern="^ChaneLL$")]),
        ConversationHandler(entry_points=[CallbackQueryHandler(admin.ban_user_prompt, pattern="^ban_user_prompt$")], states={admin.BAN_USER: [MessageHandler(Filters.text & ~Filters.command, admin.ban_user_handler)]}, fallbacks=[CallbackQueryHandler(admin.show_ban_menu, pattern="^band$")]),
        ConversationHandler(entry_points=[CallbackQueryHandler(admin.add_admin_prompt, pattern="^add_admin_prompt$")], states={admin.ADD_ADMIN: [MessageHandler(Filters.text & ~Filters.command, admin.add_admin_handler)]}, fallbacks=[CallbackQueryHandler(admin.show_admin_menu, pattern="^Admins$")]),
        ConversationHandler(entry_points=[CallbackQueryHandler(admin.add_ad_prompt, pattern="^add_ad_prompt$")], states={admin.ADD_AD: [MessageHandler(Filters.all & ~Filters.command, admin.add_ad_handler)]}, fallbacks=[CallbackQueryHandler(admin.show_ads_menu, pattern="^EV1$")]),
        ConversationHandler(entry_points=[CallbackQueryHandler(admin.broadcast_prompt, pattern="^br:")], states={admin.BROADCAST_MESSAGE: [MessageHandler(Filters.all & ~Filters.command, admin.broadcast_message_handler)]}, fallbacks=[CallbackQueryHandler(admin.show_broadcast_menu, pattern="^broDa$")]),
        ConversationHandler(entry_points=[CallbackQueryHandler(sales_bot.add_product_prompt, pattern="^sales_admin_add$")], states={sales_bot.ADD_PRODUCT_NAME: [MessageHandler(Filters.text & ~Filters.command, sales_bot.add_product_name)], sales_bot.ADD_PRODUCT_PRICE: [MessageHandler(Filters.text & ~Filters.command, sales_bot.add_product_price)], sales_bot.ADD_PRODUCT_COUNTRY: [MessageHandler(Filters.text & ~Filters.command, sales_bot.add_product_country)], sales_bot.ADD_PRODUCT_APP: [MessageHandler(Filters.text & ~Filters.command, sales_bot.add_product_app)],}, fallbacks=[CallbackQueryHandler(sales_bot.exit_admin_conversation, pattern="^sales_admin_exit$")]),
        ConversationHandler(entry_points=[CallbackQueryHandler(admin.upload_file_prompt, pattern="^upload_members_prompt$")], states={admin.UPLOAD_MEMBERS: [MessageHandler(Filters.document, admin.upload_file_handler)]}, fallbacks=[CallbackQueryHandler(admin.show_backup_menu, pattern="^Bckup$")]),
        ConversationHandler(entry_points=[CallbackQueryHandler(admin.upload_file_prompt, pattern="^upload_groups_prompt$")], states={admin.UPLOAD_GROUPS: [MessageHandler(Filters.document, admin.upload_file_handler)]}, fallbacks=[CallbackQueryHandler(admin.show_backup_menu, pattern="^Bckup$")])
    ]
    for conv in conv_handlers: dispatcher.add_handler(conv)

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("sales_admin", sales_bot.sales_admin_panel))

    callback_handlers = {
        "^cancel$": admin.admin_panel, "^count$": admin.show_stats, "^ChaneLL$": admin.show_channel_menu, "^view_channels$": admin.view_channels,
        "^delete_all_channels$": admin.delete_all_channels, "^del_channel_": admin.delete_channel, "^band$": admin.show_ban_menu,
        "^view_banned$": admin.view_banned_users, "^unban_": admin.unban_user, "^Admins$": admin.show_admin_menu, "^view_admins$": admin.view_admins,
        "^del_admin_": admin.remove_admin, "^EV1$": admin.show_ads_menu, "^view_ad$": admin.view_ad, "^delete_ad$": admin.delete_ad,
        "^broDa$": admin.show_broadcast_menu, "^toggle_": toggle_handler, "^Bckup$": admin.show_backup_menu, "^get_backup$": admin.get_backup,
        "^restore_backup$": admin.restore_backup,
        "^sales_collect$": sales_bot.collect_points, "^sales_back_to_main$": sales_bot.back_to_main_menu, "^sales_numbers$": sales_bot.show_services,
        "^sales_service_": sales_bot.show_products_for_service, "^sales_buy_": sales_bot.confirm_purchase, "^sales_execute_purchase$": sales_bot.execute_purchase,
        "^sales_getcode_": sales_bot.get_sms_code, "^sales_ban_": sales_bot.report_banned, "^sales_done$": sales_bot.purchase_done,
        "^noop$": sales_bot.noop, "^sales_admin_exit$": sales_bot.exit_admin_conversation
    }
    for p, h in callback_handlers.items(): dispatcher.add_handler(CallbackQueryHandler(h, pattern=p))

    dispatcher.add_handler(MessageHandler(Filters.reply & Filters.chat(SUDO_ID), handle_admin_reply))
    dispatcher.add_handler(MessageHandler(Filters.all & ~Filters.command & Filters.chat_type.private, handle_messages))

    dispatcher.add_error_handler(error_handler)
    updater.start_polling()
    logger.info("Bot has started successfully.")
    updater.idle()

if __name__ == '__main__':
    main()
