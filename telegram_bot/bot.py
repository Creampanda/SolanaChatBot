import os
import logging
import requests
import emoji
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Set up logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

API_BASE_URL = f"http://api_service:{os.getenv('API_PORT', 8000)}"

# Dictionary to temporarily store user data
user_data = {}

# Emoji meanings for balance categories
meanings = {
    emoji.emojize(":blue_square:"): "Текущий баланс > 100% начального баланса",
    emoji.emojize(":green_square:"): "Текущий баланс > 90% начального баланса",
    emoji.emojize(":yellow_square:"): "Текущий баланс > 50% начального баланса",
    emoji.emojize(":orange_square:"): "Текущий баланс < 50% начального баланса",
    emoji.emojize(":red_square:"): "Текущий баланс равен 0",
    emoji.emojize(":white_large_square:"): "Не удалось получить баланс холдера",
}


# Function to categorize token balances
def categorize_balance(holder_info):
    categories_count = {emoji: 0 for emoji in meanings.values()}
    emojis = []
    for holder in holder_info:
        init_bal = holder["initial_balance"]
        curr_bal = holder["current_balance"]
        category_emoji = emoji.emojize(":white_large_square:")  # Default case
        if curr_bal > init_bal:
            category_emoji = emoji.emojize(":blue_square:")
        elif curr_bal > 0.9 * init_bal:
            category_emoji = emoji.emojize(":green_square:")
        elif curr_bal > 0.5 * init_bal:
            category_emoji = emoji.emojize(":yellow_square:")
        elif curr_bal > 0:
            category_emoji = emoji.emojize(":orange_square:")
        elif curr_bal == 0:
            category_emoji = emoji.emojize(":red_square:")
        emojis.append(category_emoji)
        categories_count[category_emoji] += 1
    return emojis, categories_count


# Function to format emojis into a displayable format
def format_emojis_for_display(emojis):
    # Ensure a fixed number of emojis for display
    if len(emojis) < 50:
        emojis += [emoji.emojize(":white_large_square:")] * (50 - len(emojis))
    elif len(emojis) > 50:
        emojis = emojis[:50]
    lines = [emojis[i : i + 5] for i in range(0, 50, 5)]
    return "\n".join("".join(line) for line in lines)


# Command handler to start the interaction
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Prompt user to enter the token address
    await update.message.reply_text("Please enter the token address.")


# Message handler to receive the address
async def receive_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    address = update.message.text.strip()
    user_id = update.effective_user.id
    user_data[user_id] = address  # Store address associated with user ID

    # Inline keyboard with options for further actions
    button_list = [
        InlineKeyboardButton("Get Token Info", callback_data="get_token_info"),
        InlineKeyboardButton("Add Token", callback_data="add_token"),
    ]
    reply_markup = InlineKeyboardMarkup([[button] for button in button_list])
    await update.message.reply_text("Select an action:", reply_markup=reply_markup)


# Callback query handler for buttons
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    address = user_data.get(user_id)  # Retrieve address from stored user data

    if address:
        if query.data == "get_token_info":
            response = requests.get(f"{API_BASE_URL}/get_token_info/{address}")
            text = (
                f"TokenInfo: {response.json()}"
                if response.status_code == 200
                else "Failed to retrieve token info."
            )
        elif query.data == "add_token":
            response = requests.post(f"{API_BASE_URL}/add_token/{address}")
            text = (
                f"Token added: {response.json()}" if response.status_code == 200 else "Failed to add token."
            )
        await query.edit_message_text(text)
    else:
        await query.edit_message_text("No address provided. Please send a token address first.")


# Registering all handlers and starting the bot
def main():
    application = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_address))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()


if __name__ == "__main__":
    main()
