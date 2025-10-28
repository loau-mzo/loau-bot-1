import logging
import json
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

# Local Imports
from api_client import FiveSimAPI
import keyboards

logger = logging.getLogger(__name__)

# --- Constants ---
SALES_ADMIN_ID = 5252815668
TOKENSIM = "9ba7ea40dfca4ede9a3acaaab35398a3"
REQUIRED_CHANNELS = ["CH_X_BOT", "E_G_Y_0", "medo_mods"]
api = FiveSimAPI(TOKENSIM)

# --- Conversation States for Admin ---
ADD_PRODUCT_NAME, ADD_PRODUCT_PRICE, ADD_PRODUCT_COUNTRY, ADD_PRODUCT_APP = range(4)
DEL_PRODUCT_CODE = 5

# --- Keyboards ---
def get_sales_main_menu() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton('شراء رقم جديد📞', callback_data='sales_numbers')], [InlineKeyboardButton('جمع النقاط💰', callback_data='sales_collect'), InlineKeyboardButton('شرح البوت ⁉️', callback_data='sales_about')], [InlineKeyboardButton('شراء نقاط 💸', callback_data='sales_buy_points'), InlineKeyboardButton('أرقام بدون نقاط 🆓', callback_data='sales_free_numbers')], [InlineKeyboardButton('ملف البوت🤖', callback_data='sales_bot_info')]]
    return InlineKeyboardMarkup(keyboard)

def get_services_keyboard() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton('telegram', callback_data='sales_service_tg')], [InlineKeyboardButton('facebook', callback_data='sales_service_facebook'), InlineKeyboardButton('instagram', callback_data='sales_service_ig')], [InlineKeyboardButton('whatsapp', callback_data='sales_service_whatsapp'), InlineKeyboardButton('openai', callback_data='sales_service_openai'), InlineKeyboardButton('google', callback_data='sales_service_google')], [InlineKeyboardButton('paypal', callback_data='sales_service_paypal'), InlineKeyboardButton('amazon', callback_data='sales_service_amazon')], [InlineKeyboardButton('tiktok', callback_data='sales_service_tiktok')], [InlineKeyboardButton('الرجوع الى القائمة الرئيسية🔙', callback_data='sales_back_to_main')]]
    return InlineKeyboardMarkup(keyboard)

def get_sales_admin_menu() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton('إضافة سلعة', callback_data='sales_admin_add'), InlineKeyboardButton('- حذف سلعة', callback_data='sales_admin_del')], [InlineKeyboardButton('الخروج', callback_data='sales_admin_exit')]]
    return InlineKeyboardMarkup(keyboard)

# --- User Handlers ---
def start_sales(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    data_manager = context.bot_data['data_manager']
    sales_data = data_manager.get('sales')
    for channel in REQUIRED_CHANNELS:
        try:
            member = context.bot.get_chat_member(f"@{channel}", user.id)
            if member.status in ['left', 'kicked']:
                channels_text = "\n".join([f"@{ch}" for ch in REQUIRED_CHANNELS])
                update.message.reply_text(f"عليك الاشتراك في قنوات البوت\n{channels_text}", reply_to_message_id=update.message.message_id)
                return
        except Exception as e:
            logger.error(f"Error checking subscription for @{channel}: {e}")
            update.message.reply_text("حدث خطأ أثناء التحقق من اشتراكك في القنوات.")
            return
    user_id_str = str(user.id)
    if user_id_str not in sales_data:
        sales_data[user_id_str] = {'collect': 0, 'id': []}
    if len(context.args) > 0:
        referrer_id = context.args[0]
        if referrer_id.isdigit() and str(referrer_id) != user_id_str:
            if 'referred_by' not in sales_data[user_id_str]:
                sales_data[user_id_str]['referred_by'] = referrer_id
                if str(referrer_id) in sales_data:
                    sales_data[str(referrer_id)]['collect'] += 1
                    try:
                        context.bot.send_message(chat_id=referrer_id, text=f"- قام : {user.mention_html()} بالدخول الى الرابط الخاص وحصلت على نقطة واحده ، ✨\n~ رصيدك : {sales_data[str(referrer_id)]['collect']} ₽", parse_mode='HTML')
                    except Exception as e:
                        logger.warning(f"Could not notify referrer {referrer_id}: {e}")
    data_manager.set('sales', sales_data)
    user_points = sales_data[user_id_str].get('collect', 0)
    welcome_text = f"🎭 أهلا وسهلا بك في بوت الأرقام 《 تسليم تلقائي 》\n🌹 يتوفر لدينا أرقام لمختلف الدول العربية  🇾🇪🇾🇪 والأجنبية🚩\n♾ لتفعيل برامج التواصل الإجتماعي\n💰 مجانا وبدون دفع مال 🤑\n🤘 فقط كل ما عليك هو دعوة اصدقائك الى البوت عبر الرابط الخاص بك\n💡 وستحصل على نقطة واحدة مقابل كل دخول عضو جديد الى البوت من طرفك\n~ رصيدك الآن: {user_points} ₽"
    update.message.reply_text(welcome_text, reply_markup=get_sales_main_menu())

def collect_points(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user = update.effective_user
    bot_username = context.bot.username
    text = f"* ❍ هذا هو الرابط الخاص بك...\nhttps://t.me/{bot_username}?start={user.id}..."
    query.answer()
    query.edit_message_text(text, parse_mode='Markdown', disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("العودة إلى القائمة الرئيسية 🔙", callback_data="sales_back_to_main")]]))

def back_to_main_menu(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id_str = str(update.effective_user.id)
    sales_data = context.bot_data['data_manager'].get('sales')
    user_points = sales_data.get(user_id_str, {}).get('collect', 0)
    welcome_text = f"🎭 أهلا وسهلا بك في بوت الأرقام ...\n~ رصيدك الآن: {user_points} ₽"
    query.answer()
    query.edit_message_text(welcome_text, reply_markup=get_sales_main_menu())

def show_services(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    text = "💯 الان قم باختيار التطبيق التي تريد تشغيل الرقم عليه\n👇 من الكيبورد أدناه"
    query.answer()
    query.edit_message_text(text, reply_markup=get_services_keyboard())

def show_products_for_service(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    service_name = query.data.replace("sales_service_", "")
    data_manager = context.bot_data['data_manager']
    sales_data = data_manager.get('sales')
    all_products = sales_data.get('sales', {})
    user_points = sales_data.get(str(update.effective_user.id), {}).get('collect', 0)
    keyboard_rows = [[InlineKeyboardButton('⁉️الكمية', callback_data='noop'), InlineKeyboardButton('💲السعر', callback_data='noop'), InlineKeyboardButton('🚩دولة الرقم', callback_data='noop')]]
    found_products = False
    for code, product in all_products.items():
        if product.get("apps") == service_name:
            found_products = True
            stock_display = "متوفر✅"
            keyboard_rows.append([InlineKeyboardButton(f"{stock_display}", callback_data=f"sales_buy_{code}"), InlineKeyboardButton(str(product.get('price', 'N/A')), callback_data=f"sales_buy_{code}"), InlineKeyboardButton(product.get('name', 'N/A'), callback_data=f"sales_buy_{code}")])
    if not found_products:
        query.answer("لا توجد أرقام متاحة لهذا التطبيق حاليًا.", show_alert=True)
        return
    keyboard_rows.append([InlineKeyboardButton('العودة إلى قائمة الخدمات🔙', callback_data='sales_numbers')])
    text = f"🙋‍♂️ أهلآ عـزيـزي آلَمستخدم\n💯 إليك قائمة بالأرقام المتوفرةحاليا💯 قم بالضغط على احد الارقام لشرائه\n~ رصيدك الآن: {user_points} ₽"
    query.answer()
    query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard_rows))

def noop(update: Update, context: CallbackContext) -> None:
    update.callback_query.answer()

def confirm_purchase(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    product_code = query.data.replace("sales_buy_", "")
    data_manager = context.bot_data['data_manager']
    sales_data = data_manager.get('sales')
    product = sales_data.get('sales', {}).get(product_code)
    if not product:
        query.answer("خطأ - المنتج غير موجود.", show_alert=True)
        return
    user_points = sales_data.get(str(update.effective_user.id), {}).get('collect', 0)
    product_price = int(product.get('price', 9999))
    if user_points < product_price:
        query.answer("نقاطك غير كافية لشراء هذا الرقم", show_alert=True)
        return
    context.user_data['product_to_buy'] = product_code
    text = f"هل أنت متأكد وتريد إتمام الطلب...؟\n\nطلبك هو:\nرقم لدولة {product['name']} بسعر {product['price']} 👉"
    query.answer()
    query.edit_message_text(text, reply_markup=keyboards.keyboard_confirm_reject(yes_callback="sales_execute_purchase", no_callback="sales_numbers"))

def execute_purchase(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    product_code = context.user_data.get('product_to_buy')
    if not product_code:
        query.answer("حدث خطأ، الرجاء المحاولة مرة أخرى.", show_alert=True)
        back_to_main_menu(update, context)
        return
    data_manager = context.bot_data['data_manager']
    sales_data = data_manager.get('sales')
    product = sales_data.get('sales', {}).get(product_code)
    user_id_str = str(update.effective_user.id)
    user_points = sales_data.get(user_id_str, {}).get('collect', 0)
    product_price = int(product.get('price', 9999))
    if user_points < product_price:
        query.answer("نقاطك غير كافية.", show_alert=True)
        return
    query.edit_message_text("تم قبول طلبك للرقم...")
    purchase_result = api.purchase_number(product['country'], product['apps'])
    if not purchase_result or 'error' in purchase_result:
        error_msg = purchase_result.get('error', 'N/A') if purchase_result else "API Error"
        query.message.reply_text(f"لم يتم تنفيذ طلبك\nنظراً لمشكلة: {error_msg}")
        return
    purchased_number = purchase_result['number']
    purchase_id = purchase_result['id']
    sales_data[user_id_str]['collect'] -= product_price
    data_manager.set('sales', sales_data)
    user_text = f"رقمك هو\n`+{purchased_number}`\nاطلب الكود خلال 15 دقيقة..."
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('اجلب الكود', callback_data=f"sales_getcode_{purchase_id}")], [InlineKeyboardButton('محظور', callback_data=f"sales_ban_{purchase_id}_{purchased_number}")], [InlineKeyboardButton('تم', callback_data="sales_done")]])
    query.message.reply_text(user_text, reply_markup=keyboard, parse_mode='Markdown')
    admin_text = f"الأيدي: {update.effective_user.id}\nالمعرف: @{update.effective_user.username}\nقام بشراء {product['name']}...\nرقمه هو `+{purchased_number}`"
    try:
        context.bot.send_message(SALES_ADMIN_ID, admin_text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Failed to send purchase notification to admin: {e}")

def get_sms_code(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    purchase_id = query.data.replace("sales_getcode_", "")
    result = api.get_sms_code(purchase_id)
    raw_result = result.get('raw', 'ERROR')
    if "STATUS_WAIT_CODE" in raw_result:
        query.answer("الكود لم يصل تأكد من ارساله", show_alert=True)
    elif "STATUS_OK" in raw_result:
        code = raw_result.split(':')[1]
        query.edit_message_text(f"*الكود الخاص بك هو:*\n`{code}`", parse_mode='Markdown')
    else:
        query.answer("حدث خطأ أثناء جلب الكود.", show_alert=True)

def report_banned(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    parts = query.data.split('_')
    purchase_id, number = parts[2], parts[3]
    api.ban_number(purchase_id)
    text = "*❍ تم ارسال طلبك الى فريق الدعم بنجاح...*"
    query.edit_message_text(text, parse_mode='Markdown')
    admin_text = f"*طلب اعادة النقاط لان الرقم محظور...\nايدي المرسل:* `{update.effective_user.id}`..."
    try:
        context.bot.send_message(SALES_ADMIN_ID, admin_text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Failed to send ban report to admin: {e}")

def purchase_done(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.edit_message_text("شكرا لاستخدامك البوت")

# --- Admin Handlers ---
def sales_admin_panel(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != SALES_ADMIN_ID: return
    update.message.reply_text("- مرحباً مطوري...", reply_markup=get_sales_admin_menu())

def add_product_prompt(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    query.edit_message_text('أرسل إسم السلعة؟!', reply_markup=keyboards.get_back_button("إلغاء", "sales_admin_exit"))
    return ADD_PRODUCT_NAME

def add_product_name(update: Update, context: CallbackContext) -> int:
    context.user_data['new_product'] = {'name': update.message.text}
    update.message.reply_text('- تم حفظ إسم السلعة... أرسل الآن سعرها')
    return ADD_PRODUCT_PRICE

def add_product_price(update: Update, context: CallbackContext) -> int:
    try:
        context.user_data['new_product']['price'] = int(update.message.text)
        update.message.reply_text("ارسل اسم الدولة")
        return ADD_PRODUCT_COUNTRY
    except ValueError:
        update.message.reply_text("السعر يجب ان يكون رقما.")
        return ADD_PRODUCT_PRICE

def add_product_country(update: Update, context: CallbackContext) -> int:
    context.user_data['new_product']['country'] = update.message.text.lower()
    update.message.reply_text("الان قم بارسال اسم التطبيق")
    return ADD_PRODUCT_APP

def add_product_app(update: Update, context: CallbackContext) -> int:
    context.user_data['new_product']['apps'] = update.message.text.lower()
    code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
    data_manager = context.bot_data['data_manager']
    sales_data = data_manager.get('sales')
    if 'sales' not in sales_data: sales_data['sales'] = {}
    sales_data['sales'][code] = context.user_data['new_product']
    data_manager.set('sales', sales_data)
    product = context.user_data['new_product']
    text = f"تم حفظ الإسم والسعر...✅\nإسم السلعة: {product['name']}...\nالكود: `{code}`"
    update.message.reply_text(text, parse_mode='Markdown', reply_markup=get_sales_admin_menu())
    context.user_data.pop('new_product', None)
    return ConversationHandler.END

def exit_admin_conversation(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    query.edit_message_text("- مرحباً مطوري...", reply_markup=get_sales_admin_menu())
    return ConversationHandler.END
