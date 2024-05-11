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

meanings = {
    emoji.emojize(":blue_square:"): "Текущий баланс > 100% начального баланса",
    emoji.emojize(":green_square:"): "Текущий баланс > 90% начального баланса",
    emoji.emojize(":yellow_square:"): "Текущий баланс > 50% начального баланса",
    emoji.emojize(":orange_square:"): "Текущий баланс < 50% начального баланса",
    emoji.emojize(":red_square:"): "Текущий баланс равен 0",
    emoji.emojize(":white_large_square:"): "Не удалось получить баланс холдера",
}


def categorize_balance(holder_info):
    categories_count = {emoji: 0 for emoji in meanings.values()}
    emojis = []
    for holder in holder_info:
        init_bal = holder["initial_balance"]
        curr_bal = holder["current_balance"]
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
        else:
            category_emoji = emoji.emojize(":white_large_square:")

        emojis.append(category_emoji)
        categories_count[category_emoji] += 1
    return emojis, categories_count


def format_emojis_for_display(emojis):
    if len(emojis) < 50:
        emojis += [emoji.emojize(":white_large_square:")] * (50 - len(emojis))
    elif len(emojis) > 50:
        emojis = emojis[:50]
    lines = [emojis[i : i + 5] for i in range(0, 50, 5)]
    return "\n".join("".join(line) for line in lines)


def format_token_info(token_data):
    message_text = "<b>Информация по токену:</b>\n"
    for pair in token_data["pairs"]:
        ts = pair.get("pairCreatedAt", "N/A")
        if isinstance(ts, int):
            timestamp_s = ts / 1000
            dt_object = datetime.fromtimestamp(timestamp_s)
            formatted_date = dt_object.strftime("%Y-%m-%d %H:%M:%S")
        message_text += (
            f"\n<b>Dex:</b> {pair['dexId']}"
            f"\n<b>Адрес токена:</b> {pair['baseToken']['address']}"
            f"\n<b>Ссылка на dexscreener:</b> <a href='{pair['url']}'>Посмотреть</a>"
            f"\n<b>Название токена:</b> {pair['baseToken']['name']} ({pair['baseToken']['symbol']})"
            f"\n<b>Цена в USD:</b> {pair['priceUsd']}"
            f"\n<b>Объём за 24 часа:</b> {pair['volume']['h24']}"
            f"\n<b>Объём за 6 часов:</b> {pair['volume']['h6']}"
            f"\n<b>Объём за 1 час:</b> {pair['volume']['h1']}"
            f"\n<b>Объём за 5 минут:</b> {pair['volume']['m5']}"
            f"\n<b>Ликвидность в USD:</b> {pair['liquidity']['usd']}"
            f"\n<b>FDV:</b> {pair['fdv']}"
            f"\n<b>Токен создан:</b> {formatted_date}\n"
        )
    return message_text


async def handle_token_info(update: Update, context: ContextTypes.DEFAULT_TYPE, address: str):
    response = requests.get(f"{API_BASE_URL}/get_token_info/{address}")
    if response.status_code == 200:
        token_data = response.json()
        message_text = format_token_info(token_data)
        if update.callback_query:
            await update.callback_query.edit_message_text(message_text, parse_mode="HTML")
        else:
            await update.message.reply_html(message_text)
    else:
        error_text = "Не удалось получить информацию по токену."
        if update.callback_query:
            await update.callback_query.edit_message_text(error_text)
        else:
            await update.message.reply_text(error_text)


# Handle token addition
async def handle_add_token(update: Update, context: ContextTypes.DEFAULT_TYPE, address: str):
    response = requests.post(f"{API_BASE_URL}/add_token/{address}")
    if response.status_code == 200:
        token_data = response.json()
        message_text = f"Токен добавлен: {token_data.get("address")}"
        if update.callback_query:
            await update.callback_query.edit_message_text(message_text)
        else:
            await update.message.reply_text(message_text)
    else:
        error_text = "Не удалось добавить токен."
        if update.callback_query:
            await update.callback_query.edit_message_text(error_text)
        else:
            await update.message.reply_text(error_text)


# Callback query handler for buttons
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    address = user_data.get(user_id)

    if address:
        try:
            if query.data == "get_token_info":
                await handle_token_info(update, context, address)
            elif query.data == "add_token":
                await handle_add_token(update, context, address)
        except Exception as e:
            await query.edit_message_text(f"Случилась ошибка: {str(e)}")
    else:
        await query.edit_message_text("Сначала пришлите адрес токена.")


# Error handling function to capture any uncaught exceptions
def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Случилась ошибка: {context.error}")
    try:
        raise context.error
    except AttributeError:
        logger.error('AttributeError: Update "%s" caused error "%s"', update, context.error)
    except Exception as e:
        logger.error('Unhandled error: "%s" caused by update "%s"', str(e), update)


# Setup start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please enter the token address.")


# Receive address and provide actions
async def receive_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    address = update.message.text.strip()
    user_id = update.effective_user.id
    user_data[user_id] = address

    buttons = [
        InlineKeyboardButton("Получить информацию по токену", callback_data="get_token_info"),
        InlineKeyboardButton("Добавить токен", callback_data="add_token"),
    ]
    reply_markup = InlineKeyboardMarkup([[button] for button in buttons])
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)


# Main function to run the bot
def main():
    app = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_address))
    app.add_handler(CallbackQueryHandler(button))
    app.add_error_handler(error_handler)
    app.run_polling()


if __name__ == "__main__":
    main()
