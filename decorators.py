from functools import wraps
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

# Local Imports
from helpers import get_chat_link

def check_subscription(func):
    """
    Decorator to check if a user is subscribed to the required channels.
    """
    @wraps(func)
    def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        user = update.effective_user
        if not user:
            return

        data_manager = context.bot_data['data_manager']
        js_data = data_manager.get('js')

        # Admins are exempt
        if user.id in context.bot_data.get('admin_ids', []):
            return func(update, context, *args, **kwargs)

        required_channels = js_data.get('sub', {}).get('ch', [])
        if not required_channels:
            return func(update, context, *args, **kwargs)

        sub_message = js_data.get('bot', {}).get('subK', "انت غير مشترك بقناه البوت ◽\nاشترك ثم ارسل /start")
        use_single_message = js_data.get('bot', {}).get('SubC', '✅') == '✅'

        unsubscribed_channels = []
        for channel_id in required_channels:
            try:
                member = context.bot.get_chat_member(chat_id=channel_id, user_id=user.id)
                if member.status in ['left', 'kicked']:
                    unsubscribed_channels.append(channel_id)
            except Exception as e:
                # Bot might not be admin or channel doesn't exist
                print(f"Could not check subscription for channel {channel_id}: {e}")
                continue # Skip this channel

        if not unsubscribed_channels:
            return func(update, context, *args, **kwargs)

        # User is not subscribed
        if use_single_message:
            links_text = ""
            for channel_id in unsubscribed_channels:
                try:
                    chat = context.bot.get_chat(channel_id)
                    link = get_chat_link(context.bot, channel_id)
                    links_text += f"- [{chat.title}]({link})\n"
                except:
                    pass
            full_message = f"{sub_message}\n\n{links_text}"
            update.message.reply_text(full_message, parse_mode='Markdown', disable_web_page_preview=True)
        else:
            # Send one message for the first unsubscribed channel found
            channel_id_to_show = unsubscribed_channels[0]
            try:
                chat = context.bot.get_chat(channel_id_to_show)
                link = get_chat_link(context.bot, channel_id_to_show)
                keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(chat.title, url=link)]])
                full_message = f"{sub_message}\n\n- [{chat.title}]({link})"
                update.message.reply_text(full_message, reply_markup=keyboard, parse_mode='Markdown', disable_web_page_preview=True)
            except Exception as e:
                 update.message.reply_text(sub_message)

        # Stop further execution
        return

    return wrapped
