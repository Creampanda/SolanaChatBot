import os
import logging
import emoji
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Set up logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

API_BASE_URL = f"http://api_service:{os.getenv('API_PORT', 8000)}"

meanings = {
    emoji.emojize(":blue_square:"): "Текущий баланс > 100% начального баланса",
    emoji.emojize(":green_square:"): "Текущий баланс > 90% начального баланса",
    emoji.emojize(":yellow_square:"): "Текущий баланс > 50% начального баланса",
    emoji.emojize(":orange_square:"): "Текущий баланс < 50% начального баланса",
    emoji.emojize(":red_square:"): "Текущий баланс равен 0",
    emoji.emojize(":white_large_square:"): "Не удалось получить баланс холдера",
}


def categorize_balance(holder_info):
    categories_count = {
        emoji.emojize(":blue_square:"): 0,
        emoji.emojize(":green_square:"): 0,
        emoji.emojize(":yellow_square:"): 0,
        emoji.emojize(":orange_square:"): 0,
        emoji.emojize(":red_square:"): 0,
        emoji.emojize(":white_large_square:"): 0,
    }
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
    # Ensure there are exactly 50 emojis to format into 10 lines of 5
    if len(emojis) < 50:
        emojis += [emoji.emojize(":white_large_square:")] * (50 - len(emojis))
    elif len(emojis) > 50:
        emojis = emojis[:50]

    # Split the list of emojis into 10 lines of 5 each
    lines = [emojis[i : i + 5] for i in range(0, 50, 5)]
    return "\n".join("".join(line) for line in lines)


async def format_and_send_token_info(update: Update, token_data):
    """Formats the token data into a readable string and sends it as a message."""

    message_text = "<b>Информация по токену:</b>\n"
    for pair in token_data["pairs"]:
        ts = pair.get("pairCreatedAt", "N/A")
        if isinstance(ts, int):
            timestamp_s = ts / 1000

            # Convert Unix timestamp to datetime
            dt_object = datetime.fromtimestamp(timestamp_s)

            # Format the datetime object as a string in the desired format
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
        if pair["dexId"] == "raydium":
            break
    await update.message.reply_html(message_text)


# Command to get token information
async def get_token_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Пожалуйста, укажите адрес токена.")
        return
    address = context.args[0]
    response = requests.get(f"{API_BASE_URL}/get_token_info/{address}")
    if response.status_code == 200:
        token_data = response.json()
        await format_and_send_token_info(update, token_data)
    else:
        await update.message.reply_text("Не удалось достать информацию по токену.")
    address = context.args[0]
    response = requests.post(f"{API_BASE_URL}/get_holders_info/{address}")
    if response.status_code == 200:
        holders_data = response.json()
        emojis, categories_count = categorize_balance(holders_data)
        formatted_ans = format_emojis_for_display(emojis)
        category_summary = "\n".join(
            [f"{key} - {value} holders" for key, value in categories_count.items() if value > 0]
        )
        meanings_text = "\n".join([f"{emoji} - {meaning}" for emoji, meaning in meanings.items()])
        await update.message.reply_text(f"Холдеры: \n{formatted_ans}\Обозначения: \n{meanings_text}\nКатегории:\n{category_summary}")
    else:
        await update.message.reply_text("Не удалось достать информацию по холдерам.")


# Command to add a new token
async def add_token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Пожалуйста, укажите адрес токена.")
        return
    address = context.args[0]
    response = requests.post(f"{API_BASE_URL}/add_token/{address}")
    if response.status_code == 200:
        token_data = response.json()
        await update.message.reply_text(f"Токен добавлен: {token_data}")
    else:
        await update.message.reply_text("Не удалось добавить токен.")


def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"An error occurred: {context.error}")


def main() -> None:
    application = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()

    # Handlers for each command
    application.add_handler(CommandHandler("get_token_info", get_token_info))
    application.add_handler(CommandHandler("add_token", add_token))
    application.add_error_handler(error_handler)
    # Run the bot
    application.run_polling()


if __name__ == "__main__":
    main()
