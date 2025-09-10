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

def get_main_admin_keyboard(data_manager) -> InlineKeyboardMarkup:
    js_data = data_manager.get('js')
    bot_settings = js_data.get('bot', {})
    keyboard = [[InlineKeyboardButton(f"الاشعارات: {bot_settings.get('Notices', '❌')}", callback_data="toggle_Notices"), InlineKeyboardButton(f"التواصل: {bot_settings.get('Forward', '❌')}", callback_data="toggle_Forward"), InlineKeyboardButton(f"البوت: {bot_settings.get('BotS', '✅')}", callback_data="toggle_BotS")], [InlineKeyboardButton(f"التصفيه التلقائيه : {bot_settings.get('TSF', '❌')}", callback_data="toggle_TSF")], [InlineKeyboardButton(f"منع التكرار : {bot_settings.get('MNT', '❌')}", callback_data="toggle_MNT")], [InlineKeyboardButton("قسم الاشتراك الاجباري", callback_data="ChaneLL"), InlineKeyboardButton("قسم الاذاعه", callback_data="broDa")], [InlineKeyboardButton("قسم النسخه الاحتياطيه", callback_data="Bckup")], [InlineKeyboardButton("قسم الادمنيه", callback_data="Admins"), InlineKeyboardButton("قسم الحظر", callback_data="band")], [InlineKeyboardButton("قسم الأحصائيات", callback_data="count")], [InlineKeyboardButton("قسم الاعلانات", callback_data="EV1"), InlineKeyboardButton("قسم التمويل", callback_data="ET")], [InlineKeyboardButton("نقل ملكيه البوت", callback_data="sudo_transfer")]]
    return InlineKeyboardMarkup(keyboard)

def admin_panel(update: Update, context: CallbackContext) -> int:
    data_manager = context.bot_data['data_manager']
    query = update.callback_query
    text = "• اهلا بك في لوحه الأدمن الخاصه بالبوت 🤖\n\n- يمكنك التحكم في البوت الخاص بك من هنا\n\n~~~~~~~~~~~~~~~~~"
    keyboard = get_main_admin_keyboard(data_manager)
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

def show_stats(update: Update, context: CallbackContext):
    query = update.callback_query
    data_manager = context.bot_data['data_manager']
    js_data = data_manager.get('js')
    members_count = len(read_lines(context.bot_data['members_file']))
    groups_count = len(read_lines(context.bot_data['groups_file']))
    all_count = members_count + groups_count
    banned_count = len(js_data.get('bot', {}).get('band', []))
    end_m_count = len(js_data.get('other', {}).get('endm', []))
    new_users = js_data.get('other', {}).get('new', [])
    new_users_text = ""
    for i, user_id in enumerate(new_users, 1):
        new_users_text += f"{i} - [{user_id}](tg://user?id={user_id})\n"
    text = f"مرحبا بك في قسم الاحصائيات 📊\n\n• عدد المسخدمين الكلي : *{all_count}* \n• عدد المستخدمين في الخاص : *{members_count}*\n• عدد الكروبات والقنوات : *{groups_count}*\n• عدد المحظورين : *{banned_count}*\n• عدد المتفاعلين اليوم : *{end_m_count}*\n\nقائمة اخر الاعضاء الذين استخدموا البوت\n-------------- \n{new_users_text}"
    query.answer()
    query.edit_message_text(text=text, reply_markup=keyboards.get_back_button(), parse_mode='Markdown')

def show_channel_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    data_manager = context.bot_data['data_manager']
    js_data = data_manager.get('js')
    keyboard = keyboards.get_channel_menu_keyboard(js_data)
    text = "اهلا بك في قسم الاشتراك الاجباري"
    query.answer()
    query.edit_message_text(text=text, reply_markup=keyboard)
    return ConversationHandler.END

def add_channel_prompt(update: Update, context: CallbackContext):
    query = update.callback_query
    text = "قم بتوجيه رساله من القناه"
    query.answer()
    query.edit_message_text(text=text, reply_markup=keyboards.get_back_button("الغاء", "ChaneLL"))
    return ADD_CHANNEL

def add_channel_handler(update: Update, context: CallbackContext):
    message = update.message
    data_manager = context.bot_data['data_manager']
    if message.forward_from_chat:
        chat = message.forward_from_chat
        try:
            bot_member = context.bot.get_chat_member(chat.id, context.bot.id)
            if bot_member.status not in ['administrator', 'creator']:
                message.reply_text("البوت ليس ادمن في القناة", reply_markup=keyboards.get_back_button(callback_data="ChaneLL"))
                return ADD_CHANNEL
            js_data = data_manager.get('js')
            if chat.id not in js_data['sub']['ch']:
                js_data['sub']['ch'].append(chat.id)
                data_manager.set('js', js_data)
                message.reply_text("تم حفظ القناة", reply_markup=keyboards.get_back_button(callback_data="ChaneLL"))
            else:
                message.reply_text("هذه القناة مضافه بالفعل", reply_markup=keyboards.get_back_button(callback_data="ChaneLL"))
            return ConversationHandler.END
        except Exception as e:
            logger.error(f"Error adding channel: {e}")
            message.reply_text("حدث خطأ. حاول مرة أخرى.", reply_markup=keyboards.get_back_button(callback_data="ChaneLL"))
            return ADD_CHANNEL
    else:
        message.reply_text("الرجاء توجيه رسالة من قناة.", reply_markup=keyboards.get_back_button(callback_data="ChaneLL"))
        return ADD_CHANNEL

def view_channels(update: Update, context: CallbackContext):
    query = update.callback_query
    data_manager = context.bot_data['data_manager']
    js_data = data_manager.get('js')
    channels = js_data.get('sub', {}).get('ch', [])
    if not channels:
        query.answer("لم تقم بأضافه اي قناه", show_alert=True)
        return
    keyboard_buttons = []
    for channel_id in channels:
        try:
            chat = context.bot.get_chat(channel_id)
            link = chat.invite_link or f"https.t.me/{chat.username}" if chat.username else get_chat_link(context.bot, channel_id)
            keyboard_buttons.append([InlineKeyboardButton(chat.title, url=link), InlineKeyboardButton("🗑", callback_data=f"del_channel_{channel_id}")])
        except Exception as e:
            logger.warning(f"Could not get info for channel {channel_id}: {e}")
            keyboard_buttons.append([InlineKeyboardButton(f"ID: {channel_id} (Error)", callback_data=f"del_channel_{channel_id}")])
    keyboard_buttons.append([InlineKeyboardButton("➕", callback_data="add_channel")])
    keyboard_buttons.append([InlineKeyboardButton("رجوع", callback_data="ChaneLL")])
    text = "اليك القنوات"
    query.answer()
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard_buttons))

def delete_channel(update: Update, context: CallbackContext):
    query = update.callback_query
    channel_id_to_del = int(query.data.split("_")[2])
    data_manager = context.bot_data['data_manager']
    js_data = data_manager.get('js')
    if channel_id_to_del in js_data['sub']['ch']:
        js_data['sub']['ch'].remove(channel_id_to_del)
        data_manager.set('js', js_data)
        query.answer("تم حذف القناة", show_alert=True)
    view_channels(update, context)

def delete_all_channels(update: Update, context: CallbackContext):
    query = update.callback_query
    data_manager = context.bot_data['data_manager']
    js_data = data_manager.get('js')
    if not js_data.get('sub', {}).get('ch', []):
        query.answer("لم تقم بأضافه اي قناه", show_alert=True)
        return
    js_data['sub']['ch'] = []
    data_manager.set('js', js_data)
    query.answer("تم حذف كل القنوات", show_alert=True)
    show_channel_menu(update, context)

def show_ban_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    keyboard = keyboards.get_ban_menu_keyboard()
    text = 'اهلا بك في قسم الحظر'
    query.answer()
    query.edit_message_text(text=text, reply_markup=keyboard)
    return ConversationHandler.END

def ban_user_prompt(update: Update, context: CallbackContext):
    query = update.callback_query
    text = "حسنا عزيزي ارسل ايدي العضو لحظره ⛔"
    query.answer()
    query.edit_message_text(text=text, reply_markup=keyboards.get_back_button("الغاء", "band"))
    return BAN_USER

def ban_user_handler(update: Update, context: CallbackContext):
    message = update.message
    data_manager = context.bot_data['data_manager']
    try:
        user_id_to_ban = int(message.text)
        js_data = data_manager.get('js')
        banned_list = js_data['bot'].get('band', [])
        if user_id_to_ban not in banned_list:
            js_data['bot']['band'].append(user_id_to_ban)
            data_manager.set('js', js_data)
            message.reply_text("تم حظر العضو بنجاح", reply_markup=keyboards.get_back_button(callback_data="band"))
        else:
            message.reply_text("العضو محظور من قبل", reply_markup=keyboards.get_back_button(callback_data="band"))
        return ConversationHandler.END
    except ValueError:
        message.reply_text("هذا ليس ايدي صحيح. الرجاء ارسال الايدي الرقمي للمستخدم.", reply_markup=keyboards.get_back_button(callback_data="band"))
        return BAN_USER

def view_banned_users(update: Update, context: CallbackContext):
    query = update.callback_query
    data_manager = context.bot_data['data_manager']
    js_data = data_manager.get('js')
    banned_list = js_data.get('bot', {}).get('band', [])
    if not banned_list:
        query.answer("لايوجد محظورين", show_alert=True)
        return
    keyboard_buttons = []
    for user_id in banned_list:
        user_link = f"tg://user?id={user_id}"
        keyboard_buttons.append([InlineKeyboardButton(str(user_id), url=user_link), InlineKeyboardButton("🗑", callback_data=f"unban_{user_id}")])
    keyboard_buttons.append([InlineKeyboardButton("رجوع", callback_data="band")])
    text = 'اليك قائمه المحظورين'
    query.answer()
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard_buttons))

def unban_user(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id_to_unban = int(query.data.split("_")[1])
    data_manager = context.bot_data['data_manager']
    js_data = data_manager.get('js')
    if user_id_to_unban in js_data['bot']['band']:
        js_data['bot']['band'].remove(user_id_to_unban)
        data_manager.set('js', js_data)
        query.answer("تم الغاء حظر العضو", show_alert=True)
    view_banned_users(update, context)

def show_admin_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = update.effective_user.id
    sudo_id = context.bot_data['data_manager'].get('js')['bot']['sudo']
    if user_id != sudo_id:
        query.answer("عذرا عزيزي هذا القسم مخصص للمطور الاساسي فقط 🚫", show_alert=True)
        return ConversationHandler.END
    keyboard = keyboards.get_admin_menu_keyboard()
    text = 'اهلا بك في قسم الادمنيه'
    query.answer()
    query.edit_message_text(text=text, reply_markup=keyboard)
    return ConversationHandler.END

def add_admin_prompt(update: Update, context: CallbackContext):
    query = update.callback_query
    text = "حسنا عزيزي ارسل ايدي العضو لرفعه ادمن ⛔"
    query.answer()
    query.edit_message_text(text=text, reply_markup=keyboards.get_back_button("الغاء", "Admins"))
    return ADD_ADMIN

def add_admin_handler(update: Update, context: CallbackContext):
    message = update.message
    data_manager = context.bot_data['data_manager']
    try:
        user_id_to_add = int(message.text)
        js_data = data_manager.get('js')
        admin_list = js_data['bot'].get('admin', [])
        if user_id_to_add not in admin_list:
            js_data['bot']['admin'].append(user_id_to_add)
            data_manager.set('js', js_data)
            if user_id_to_add not in context.bot_data['admin_ids']:
                context.bot_data['admin_ids'].append(user_id_to_add)
            message.reply_text("تم رفع العضو بنجاح", reply_markup=keyboards.get_back_button(callback_data="Admins"))
        else:
            message.reply_text("العضو ادمن من قبل", reply_markup=keyboards.get_back_button(callback_data="Admins"))
        return ConversationHandler.END
    except ValueError:
        message.reply_text("هذا ليس ايدي صحيح. الرجاء ارسال الايدي الرقمي للمستخدم.", reply_markup=keyboards.get_back_button(callback_data="Admins"))
        return ADD_ADMIN

def view_admins(update: Update, context: CallbackContext):
    query = update.callback_query
    data_manager = context.bot_data['data_manager']
    js_data = data_manager.get('js')
    admin_list = js_data.get('bot', {}).get('admin', [])
    if not admin_list:
        query.answer("لايوجد ادمنيه", show_alert=True)
        return
    keyboard_buttons = []
    for user_id in admin_list:
        user_link = f"tg://user?id={user_id}"
        keyboard_buttons.append([InlineKeyboardButton(str(user_id), url=user_link), InlineKeyboardButton("🗑", callback_data=f"del_admin_{user_id}")])
    keyboard_buttons.append([InlineKeyboardButton("رجوع", callback_data="Admins")])
    text = 'اليك قائمه الادمنيه'
    query.answer()
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard_buttons))

def remove_admin(update: Update, context: CallbackContext):
    query = update.callback_query
    admin_id_to_del = int(query.data.split("_")[2])
    data_manager = context.bot_data['data_manager']
    js_data = data_manager.get('js')
    if admin_id_to_del in js_data['bot']['admin']:
        js_data['bot']['admin'].remove(admin_id_to_del)
        data_manager.set('js', js_data)
        if admin_id_to_del in context.bot_data['admin_ids']:
            context.bot_data['admin_ids'].remove(admin_id_to_del)
        query.answer("تم تنزيله من الادمنيه", show_alert=True)
    view_admins(update, context)

def show_ads_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    keyboard = keyboards.get_ads_menu_keyboard()
    text = "اهلا بك في قسم الاعلانات"
    query.answer()
    query.edit_message_text(text=text, reply_markup=keyboard)
    return ConversationHandler.END

def add_ad_prompt(update: Update, context: CallbackContext):
    query = update.callback_query
    text = "قم بأرسال اعلان جديد"
    query.answer()
    query.edit_message_text(text=text, reply_markup=keyboards.get_back_button("الغاء", "EV1"))
    return ADD_AD

def add_ad_handler(update: Update, context: CallbackContext):
    message = update.message
    data_manager = context.bot_data['data_manager']
    ad_update_json = update.to_json()
    js_data = data_manager.get('js')
    js_data['bot']['ads'] = ad_update_json
    data_manager.set('js', js_data)
    message.reply_text("تم وضع الاعلان في بوت ✅", reply_markup=keyboards.get_back_button(callback_data="EV1"))
    return ConversationHandler.END

def view_ad(update: Update, context: CallbackContext):
    query = update.callback_query
    data_manager = context.bot_data['data_manager']
    js_data = data_manager.get('js')
    ad_info = js_data.get('bot', {}).get('ads')
    if not ad_info:
        query.answer("انت لم تقم بأضافه اعلان لعرضه", show_alert=True)
        return
    try:
        ad_update_data = json.loads(ad_info)
        ad_message = ad_update_data['message']
        context.bot.copy_message(chat_id=query.message.chat_id, from_chat_id=ad_message['chat']['id'], message_id=ad_message['message_id'])
        query.answer()
    except Exception as e:
        logger.error(f"Error viewing ad: {e}")
        query.answer("خطأ في عرض الاعلان. قد يكون تالفًا.", show_alert=True)

def delete_ad(update: Update, context: CallbackContext):
    query = update.callback_query
    data_manager = context.bot_data['data_manager']
    js_data = data_manager.get('js')
    if 'ads' in js_data.get('bot', {}):
        del js_data['bot']['ads']
        data_manager.set('js', js_data)
        vs_data = data_manager.get('vs')
        if 'ads' in vs_data:
            vs_data['ads']['adss'] = []
            data_manager.set('vs', vs_data)
        query.answer("تم حذف الاعلان بنجاح ✅", show_alert=True)
        show_ads_menu(update, context)
    else:
        query.answer("انت لم تقم بأضافه اعلان لتحذفه", show_alert=True)

def run_broadcast_job(context: CallbackContext) -> None:
    job_context = context.job.context
    bot = context.bot
    chat_id, from_chat_id, message_id, target_group, broadcast_type, pin_message = job_context['chat_id'], job_context['from_chat_id'], job_context['message_id'], job_context['target_group'], job_context['broadcast_type'], job_context['pin_message']
    if target_group == 'p': users = read_lines(context.bot_data['members_file'])
    elif target_group == 'g': users = read_lines(context.bot_data['groups_file'])
    else: users = read_lines(context.bot_data['all_chats_file'])
    total_users, sent_count, failed_count = len(users), 0, 0
    progress_message = bot.send_message(chat_id, f"Initializing broadcast to {total_users} users...")
    for i, user_id in enumerate(users):
        try:
            if broadcast_type == 'copymessage': sent_msg = bot.copy_message(chat_id=user_id, from_chat_id=from_chat_id, message_id=message_id)
            else: sent_msg = bot.forward_message(chat_id=user_id, from_chat_id=from_chat_id, message_id=message_id)
            if pin_message:
                try: bot.pin_chat_message(chat_id=user_id, message_id=sent_msg.message_id)
                except Exception as e: logger.warning(f"Could not pin message for {user_id}: {e}")
            sent_count += 1
            time.sleep(0.1)
            if (i + 1) % 25 == 0: bot.edit_message_text(chat_id=chat_id, message_id=progress_message.message_id, text=f"Broadcast in progress...\nSent: {sent_count}/{total_users}\nFailed: {failed_count}")
        except Exception as e:
            logger.error(f"Broadcast failed for user {user_id}: {e}")
            failed_count += 1
    final_text = f"تم الاذاعه بنجاح ✅\n\nتم الاذاعه لـ*{total_users}* عضو\n\nعدد الحقيقي : *{sent_count}*\nعدد الوهمي : *{failed_count}*"
    bot.edit_message_text(chat_id=chat_id, message_id=progress_message.message_id, text=final_text, parse_mode='Markdown')

def show_broadcast_menu(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data_manager = context.bot_data['data_manager']
    js_data = data_manager.get('js')
    keyboard = keyboards.get_broadcast_menu_keyboard(js_data)
    text = "اهلا بك في قسم الاذاعه"
    query.answer()
    query.edit_message_text(text=text, reply_markup=keyboard)

def broadcast_prompt(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    _, broadcast_type, target_group = query.data.split(':')
    context.user_data['broadcast_info'] = {'type': broadcast_type, 'target': target_group}
    text = "حسنا عزيزي ارسل رسالتك 📎"
    query.answer()
    query.edit_message_text(text=text, reply_markup=keyboards.get_back_button("الغاء", "broDa"))
    return BROADCAST_MESSAGE

def broadcast_message_handler(update: Update, context: CallbackContext) -> int:
    message = update.message
    broadcast_info = context.user_data.get('broadcast_info')
    if not broadcast_info:
        message.reply_text("خطأ: لم يتم العثور على معلومات الإذاعة. الرجاء البدء من جديد.")
        return ConversationHandler.END
    data_manager = context.bot_data['data_manager']
    js_data = data_manager.get('js')
    pin_message = js_data.get('bot', {}).get('TBr') == '✅'
    job_context = {'chat_id': message.chat_id, 'from_chat_id': message.chat_id, 'message_id': message.message_id, 'target_group': broadcast_info['target'], 'broadcast_type': broadcast_info['type'], 'pin_message': pin_message}
    context.job_queue.run_once(run_broadcast_job, 0, context=job_context, name=f"broadcast_{message.chat_id}")
    message.reply_text("جاري الاذاعه..", reply_markup=keyboards.get_back_button("رجوع", "cancel"))
    context.user_data.pop('broadcast_info', None)
    return ConversationHandler.END

def run_daily_backup_job(context: CallbackContext) -> None:
    bot = context.bot
    data_manager = context.bot_data['data_manager']
    js_data = data_manager.get('js')
    sudo_id = js_data.get('bot', {}).get('sudo')
    if not sudo_id or js_data.get('bot', {}).get('backp') != '✅':
        logger.info("Daily backup skipped (disabled or no sudo id).")
        return
    logger.info("Running daily backup...")
    files_to_backup = [context.bot_data['members_file'], context.bot_data['groups_file'], context.bot_data['all_chats_file']]
    for file_path in files_to_backup:
        try: bot.send_document(chat_id=sudo_id, document=open(file_path, 'rb'))
        except Exception as e: logger.error(f"Failed to send backup file {file_path}: {e}")
    try:
        js_path = data_manager.files['js']
        with open(js_path, 'rb') as js_file:
            bot.send_document(chat_id=sudo_id, document=js_file, filename="Js.txt")
    except Exception as e: logger.error(f"Failed to send Js.json backup: {e}")

def show_backup_menu(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data_manager = context.bot_data['data_manager']
    js_data = data_manager.get('js')
    keyboard = keyboards.get_backup_menu_keyboard(js_data)
    text = "اهلا بك في قسم النسخ الاحتياطيه"
    query.answer()
    query.edit_message_text(text=text, reply_markup=keyboard)

def get_backup(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    bot = context.bot
    sudo_id = query.from_user.id
    data_manager = context.bot_data['data_manager']
    query.answer("جاري ارسال النسخه...")
    files_to_backup = [context.bot_data['members_file'], context.bot_data['groups_file'], context.bot_data['all_chats_file'], data_manager.files['js'], data_manager.files['ds'], data_manager.files['vs'], data_manager.files['sales']]
    for file_path in files_to_backup:
        try: bot.send_document(chat_id=sudo_id, document=open(file_path, 'rb'))
        except Exception as e:
            logger.error(f"Failed to send manual backup file {file_path}: {e}")
            bot.send_message(sudo_id, f"فشل في ارسال {file_path}")

def restore_backup(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data_manager = context.bot_data['data_manager']
    js_backup_path = "Users/Js.txt"
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

def upload_file_prompt(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    upload_type = query.data.replace("_prompt", "")
    if upload_type == "upload_members":
        context.user_data['upload_target'] = context.bot_data['members_file']
        state = UPLOAD_MEMBERS
    else:
        context.user_data['upload_target'] = context.bot_data['groups_file']
        state = UPLOAD_GROUPS
    context.user_data['upload_fallback'] = "Bckup"
    text = "قم بأرسال ملف الاعضاء بصيغه txt"
    query.answer()
    query.edit_message_text(text=text, reply_markup=keyboards.get_back_button("الغاء", "Bckup"))
    return state

def upload_file_handler(update: Update, context: CallbackContext) -> int:
    message = update.message
    doc = message.document
    target_file = context.user_data.get('upload_target')
    fallback_cb = context.user_data.get('upload_fallback', 'cancel')
    if not doc or not doc.file_name.endswith(".txt"):
        message.reply_text("عذرا هذا الملف ليس بصيغه txt", reply_markup=keyboards.get_back_button(callback_data=fallback_cb))
        return ConversationHandler.END
    try:
        file = doc.get_file()
        content = file.download_as_bytearray().decode('utf-8')
        write_text(target_file, content)
        append_line(context.bot_data['all_chats_file'], "\n" + content)
        message.reply_text("تم رفع النسخه", reply_markup=keyboards.get_back_button(callback_data=fallback_cb))
    except Exception as e:
        message.reply_text(f"فشل الرفع: {e}", reply_markup=keyboards.get_back_button(callback_data=fallback_cb))
    context.user_data.clear()
    return ConversationHandler.END
