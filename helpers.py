import os
from telegram import Bot, Chat
from telegram.error import TelegramError

# --- File I/O Helpers for .txt files ---

def read_lines(path: str) -> list[str]:
    """
    Reads all lines from a file and returns them as a list of strings.
    Equivalent to PHP's explode("\n", file_get_contents($path)).
    Creates the file if it doesn't exist.
    """
    if not os.path.exists(path):
        open(path, 'w').close()
        return []
    with open(path, 'r', encoding='utf-8') as f:
        # filter out empty lines
        return [line.strip() for line in f if line.strip()]

def append_line(path: str, content: str):
    """
    Appends a new line to a file.
    Equivalent to PHP's file_put_contents($path, $content . "\n", FILE_APPEND).
    """
    with open(path, 'a', encoding='utf-8') as f:
        f.write(str(content) + "\n")

def write_text(path: str, content: str):
    """
    Writes text to a file, overwriting existing content.
    Equivalent to PHP's file_put_contents($path, $content).
    """
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def read_text(path: str) -> str:
    """
    Reads the entire content of a file as a single string.
    Equivalent to PHP's file_get_contents($path).
    """
    if not os.path.exists(path):
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

# --- Telegram-related Helpers ---

def get_chat_link(bot: Bot, chat_id: int) -> str:
    """
    Gets a public or private link for a chat.
    Equivalent to the PHP function Slink/Slin.
    """
    try:
        chat = bot.get_chat(chat_id)
        if chat.username:
            return f"t.me/{chat.username}"
        elif chat.invite_link:
            return chat.invite_link
        else:
            # For private chats without a public link, try to create one
            # This only works for supergroups and channels where the bot is an admin
            try:
                invite_link = bot.export_chat_invite_link(chat_id)
                return invite_link
            except TelegramError:
                return f"tg://user?id={chat_id}" # Fallback for private user chats
    except TelegramError as e:
        logger.error(f"Error getting chat link for {chat_id}: {e}")
        return "N/A"
