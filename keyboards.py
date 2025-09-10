from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_admin_keyboard(js_data: dict) -> InlineKeyboardMarkup:
    bot_settings = js_data.get('bot', {})
    keyboard = [[InlineKeyboardButton(f"الاشعارات: {bot_settings.get('Notices', '❌')}", callback_data="toggle_Notices"), InlineKeyboardButton(f"التواصل: {bot_settings.get('Forward', '❌')}", callback_data="toggle_Forward"), InlineKeyboardButton(f"البوت: {bot_settings.get('BotS', '✅')}", callback_data="toggle_BotS")], [InlineKeyboardButton(f"التصفيه التلقائيه : {bot_settings.get('TSF', '❌')}", callback_data="toggle_TSF")], [InlineKeyboardButton(f"منع التكرار : {bot_settings.get('MNT', '❌')}", callback_data="toggle_MNT")], [InlineKeyboardButton("قسم الاشتراك الاجباري", callback_data="ChaneLL"), InlineKeyboardButton("قسم الاذاعه", callback_data="broDa")], [InlineKeyboardButton("قسم النسخه الاحتياطيه", callback_data="Bckup")], [InlineKeyboardButton("قسم الادمنيه", callback_data="Admins"), InlineKeyboardButton("قسم الحظر", callback_data="band")], [InlineKeyboardButton("قسم الأحصائيات", callback_data="count")], [InlineKeyboardButton("قسم الاعلانات", callback_data="EV1"), InlineKeyboardButton("قسم التمويل", callback_data="ET")], [InlineKeyboardButton("نقل ملكيه البوت", callback_data="sudo_transfer")]]
    return InlineKeyboardMarkup(keyboard)

def get_back_button(text="رجوع", callback_data="cancel") -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(text, callback_data=callback_data)]]
    return InlineKeyboardMarkup(keyboard)

def get_channel_menu_keyboard(js_data: dict) -> InlineKeyboardMarkup:
    sub_c_status = js_data.get('bot', {}).get('SubC', '✅')
    keyboard = [[InlineKeyboardButton(f"كليشه واحده : {sub_c_status}", callback_data="toggle_SubC"), InlineKeyboardButton("اضافه قناة ➕", callback_data="add_channel")], [InlineKeyboardButton("عرض القنوات 📋", callback_data="view_channels"), InlineKeyboardButton("حذف القنوات 🗑", callback_data="delete_all_channels")], [InlineKeyboardButton("تغيير كليشه الاشتراك 📃", callback_data="set_sub_message")], [InlineKeyboardButton("اضف اشتراك وهمي 🔢", callback_data="add_fake_sub"), InlineKeyboardButton("حذف الاشتراك الوهمي 🗑", callback_data="delete_fake_sub")], [InlineKeyboardButton("رجوع", callback_data="cancel")]]
    return InlineKeyboardMarkup(keyboard)

def get_ban_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton("حظر عضو ➕", callback_data="ban_user_prompt")], [InlineKeyboardButton("المحظورين 🚫", callback_data="view_banned")], [InlineKeyboardButton("رجوع", callback_data="cancel")]]
    return InlineKeyboardMarkup(keyboard)

def get_admin_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton("رفع ادمن ➕", callback_data="add_admin_prompt")], [InlineKeyboardButton("الادمنيه 📑", callback_data="view_admins")], [InlineKeyboardButton("رجوع", callback_data="cancel")]]
    return InlineKeyboardMarkup(keyboard)

def get_ads_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton("عرض الاعلان ⚙️", callback_data="view_ad")], [InlineKeyboardButton("ضع اعلان 🎁", callback_data="add_ad_prompt"), InlineKeyboardButton("حذف الاعلان 🗑", callback_data="delete_ad")], [InlineKeyboardButton("رجوع", callback_data="cancel")]]
    return InlineKeyboardMarkup(keyboard)

def get_broadcast_menu_keyboard(js_data: dict) -> InlineKeyboardMarkup:
    tbr_status = js_data.get('bot', {}).get('TBr', '❌')
    start_b = js_data.get('bot', {}).get('startB', 0)
    keyboard = [[InlineKeyboardButton(f"تثبيت الاذاعه : {tbr_status}", callback_data="toggle_TBr")], [InlineKeyboardButton("اذاعه خاص 📢", callback_data="br:copymessage:p"), InlineKeyboardButton("توجيه خاص 🔄", callback_data="br:forwardmessage:p")], [InlineKeyboardButton("اذاعه كروبات 📢", callback_data="br:copymessage:g"), InlineKeyboardButton("توجيه كروبات 🔄", callback_data="br:forwardmessage:g")], [InlineKeyboardButton("اذاعه للكل 📢", callback_data="br:copymessage:all"), InlineKeyboardButton("توجيه للكل 🔄", callback_data="br:forwardmessage:all")], [InlineKeyboardButton("الاحصائيات 📊", callback_data="count")], [InlineKeyboardButton(f"عدد البدأ : {start_b}", callback_data="set_startB")], [InlineKeyboardButton("رجوع", callback_data="cancel")]]
    return InlineKeyboardMarkup(keyboard)

def get_backup_menu_keyboard(js_data: dict) -> InlineKeyboardMarkup:
    backup_status = js_data.get('bot', {}).get('backp', '❌')
    keyboard = [[InlineKeyboardButton(f"نسخه يوميه: {backup_status}", callback_data="toggle_backp"), InlineKeyboardButton("جلب نسخه احتياطيه", callback_data="get_backup")], [InlineKeyboardButton("استعاده الخزن", callback_data="restore_backup")], [InlineKeyboardButton("رفع نسخه اعضاء", callback_data="upload_members_prompt"), InlineKeyboardButton("رفع نسخه كروبات", callback_data="upload_groups_prompt")], [InlineKeyboardButton("رجوع", callback_data="cancel")]]
    return InlineKeyboardMarkup(keyboard)

def keyboard_confirm_reject(yes_callback="yes", no_callback="no") -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton("نعم - أنا متأكد", callback_data=yes_callback), InlineKeyboardButton("لا - إلغاء", callback_data=no_callback)]]
    return InlineKeyboardMarkup(keyboard)

# Sales Bot Keyboards
def get_sales_main_menu() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton('شراء رقم جديد📞', callback_data='sales_numbers')], [InlineKeyboardButton('جمع النقاط💰', callback_data='sales_collect'), InlineKeyboardButton('شرح البوت ⁉️', callback_data='sales_about')], [InlineKeyboardButton('شراء نقاط 💸', callback_data='sales_buy_points'), InlineKeyboardButton('أرقام بدون نقاط 🆓', callback_data='sales_free_numbers')], [InlineKeyboardButton('ملف البوت🤖', callback_data='sales_bot_info')]]
    return InlineKeyboardMarkup(keyboard)

def get_services_keyboard() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton('telegram', callback_data='sales_service_tg')], [InlineKeyboardButton('facebook', callback_data='sales_service_facebook'), InlineKeyboardButton('instagram', callback_data='sales_service_ig')], [InlineKeyboardButton('whatsapp', callback_data='sales_service_whatsapp'), InlineKeyboardButton('openai', callback_data='sales_service_openai'), InlineKeyboardButton('google', callback_data='sales_service_google')], [InlineKeyboardButton('paypal', callback_data='sales_service_paypal'), InlineKeyboardButton('amazon', callback_data='sales_service_amazon')], [InlineKeyboardButton('tiktok', callback_data='sales_service_tiktok')], [InlineKeyboardButton('الرجوع الى القائمة الرئيسية🔙', callback_data='sales_back_to_main')]]
    return InlineKeyboardMarkup(keyboard)

def get_sales_admin_menu() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton('إضافة سلعة', callback_data='sales_admin_add'), InlineKeyboardButton('- حذف سلعة', callback_data='sales_admin_del')], [InlineKeyboardButton('الخروج', callback_data='sales_admin_exit')]]
    return InlineKeyboardMarkup(keyboard)
