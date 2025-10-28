# Loau Bot - Python Version

This is a Python conversion of the original `loau-bot.php` Telegram bot. The project aims to replicate 100% of the original features while improving the code structure and maintainability.

The bot has two main components, which were merged in the original PHP file and are now separated into modules:
1.  **Main Admin Bot:** A powerful panel for a bot administrator to manage users, send broadcasts, enforce channel subscriptions, and more.
2.  **Number-Selling Bot:** A public-facing bot that allows users to collect points via referrals and purchase temporary phone numbers for various services using those points.

## Features

- **Admin Panel:**
  - View comprehensive bot statistics.
  - Broadcast messages (copy or forward) to users, groups, or all chats.
  - Manage a forced-subscription list of channels.
  - Ban/unban users from the bot.
  - Promote/demote other admins (Sudo only).
  - Set a sitewide ad for new users.
  - Manage daily backups and restore from them.
- **Number-Selling System:**
  - User-friendly menu for browsing available numbers by service.
  - Points-based economy with a referral system.
  - Admin panel for adding/removing numbers for sale.
  - Integration with an external API (`api-jack.ml`) for purchasing numbers.
- **Background Tasks:**
  - Reliable broadcasting via a job queue.
  - Automatic daily backups of user data.

## Project Structure

- `loau_bot.py`: The main entry point for the bot. Initializes the `python-telegram-bot` updater and registers all handlers.
- `admin.py`: Contains all the handler logic for the main bot's admin panel.
- `sales_bot.py`: Contains all the handler logic for the number-selling bot (both user and admin sides).
- `api_client.py`: A client to interact with the external `5sim` API.
- `keyboards.py`: Functions to generate all the `InlineKeyboardMarkup` objects used in the bot.
- `helpers.py`: Utility functions.
- `decorators.py`: Contains the `@check_subscription` decorator.
- `requirements.txt`: Lists all the required Python packages.
- **Data Files:** The bot uses several `.json` and `.txt` files in the `Users/` and `stats/` directories to store its state. These are created automatically on first run.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Install dependencies:**
    Make sure you have Python 3.8+ installed.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure the Bot:**
    - Open `loau_bot.py` and set the `TOKEN` variable to your bot's token from BotFather.
    - Set the `SUDO_ID` to your numerical Telegram user ID.
    - Open `sales_bot.py` and set `SALES_ADMIN_ID` (if different from `SUDO_ID`) and the `TOKENSIM` API key.

4.  **Run the Bot:**
    ```bash
    python3 loau_bot.py
    ```

The bot will start, create the necessary data files if they don't exist, and begin polling for updates.
