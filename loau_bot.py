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
import mini_admin
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
                d=os.path.dirname(p);
                if d: os.makedirs(d, exist_ok=True)
                with open(p, 'r', encoding='utf-8') as f: self.data[n] = json.load(f)
            except(FileNotFoundError, json.JSONDecodeError): self.data[n]={}; self.save(n)
    def save(self, n):
        if n in self.data:
            p=self.files[n]; d=os.path.dirname(p)
            if d: os.makedirs(d, exist_ok=True)
            with open(p, 'w', encoding='utf-8') as f: json.dump(self.data[n], f, ensure_ascii=False, indent=4)
    def get(self, n): return self.data.get(n, {})
    def set(self, n, v): self.data[n]=v; self.save(n)

DATA_FILES = {"js": "Js.json", "ds": "Ds.json", "vs": "Vs.json", "forward_m": "forwardM.json", "sales": "sales.json"}
data_manager = DataManager(DATA_FILES)
MEMBERS_FILE, GROUPS_FILE, ALL_CHATS_FILE = "member.txt", "chat.txt", "allchat.txt"
STATS_USERS_FILE, STATS_BC_FILE = "stats_users.txt", "stats_bc.txt"

# --- Handlers ---
@check_subscription
def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if not user: return
    if user.id in context.bot_data.get('admin_ids', []): admin.admin_panel(update, context)
    else: sales_bot.start_sales(update, context)

def toggle_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query; toggle_key = query.data.replace("toggle_", "")
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
def handle_messages(update: Update, context: CallbackContext) -> None: pass
def handle_admin_reply(update: Update, context: CallbackContext) -> None: pass
def error_handler(update: object, context: CallbackContext) -> None: logger.warning('Update "%s" caused error "%s"', update, context.error)

def main() -> None:
    js_data = data_manager.get('js')
    if 'bot' not in js_data: js_data['bot'] = {}
    if js_data.get('bot', {}).get('sudo') is None: js_data['bot']['sudo'] = SUDO_ID
    if 'admin' in js_data.get('bot', {}):
        for admin_id in js_data['bot']['admin']:
            if int(admin_id) not in ADMIN_IDS: ADMIN_IDS.append(int(admin_id))

    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.bot_data.update({'data_manager': data_manager, 'admin_ids': ADMIN_IDS, 'members_file': MEMBERS_FILE, 'groups_file': GROUPS_FILE, 'all_chats_file': ALL_CHATS_FILE, 'stats_users_file': STATS_USERS_FILE, 'stats_bc_file': STATS_BC_FILE})

    job_queue = updater.job_queue
    job_queue.run_daily(admin.run_daily_backup_job, time=datetime.time(hour=2, minute=0, second=0))

    # --- Conversation Handlers ---
    mini_bc_conv = ConversationHandler(entry_points=[CallbackQueryHandler(mini_admin.set_broadcast_prompt, pattern="^mini_admin_set_bc$")], states={mini_admin.BROADCAST_STATE: [MessageHandler(Filters.text & ~Filters.command, mini_admin.handle_broadcast_message)]}, fallbacks=[CallbackQueryHandler(mini_admin.cancel_broadcast, pattern="^mini_admin_cancel_bc$")])
    # (Add all other conversation handlers)
    dispatcher.add_handler(mini_bc_conv)


    # --- Command Handlers ---
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("admin", mini_admin.mini_admin_panel))
    dispatcher.add_handler(CommandHandler("sales_admin", sales_bot.sales_admin_panel))

    # --- Callback Handlers ---
    callback_handlers = {
        # ... (all previous handlers)
        "^mini_admin_users$": mini_admin.show_user_count,
        "^mini_admin_stats$": mini_admin.show_bot_status,
        "^mini_admin_main$": mini_admin.main_menu_from_status,
    }
    for p, h in callback_handlers.items(): dispatcher.add_handler(CallbackQueryHandler(h, pattern=p))

    # --- Message Handlers ---
    dispatcher.add_handler(MessageHandler(Filters.all, mini_admin.add_user_to_stats), group=1)
    # (Add other message handlers)

    dispatcher.add_error_handler(error_handler)
    updater.start_polling()
    logger.info("Bot has started successfully.")
    updater.idle()

if __name__ == '__main__':
    main()
