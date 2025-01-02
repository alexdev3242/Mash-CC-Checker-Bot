import requests
import telebot
import time
from telebot import types
from gatet import Tele  # Ensure this module is correctly installed or replace with the proper one
import os

# Bot token and initialization
token = '7584467985:AAEPjPxRZUAA-ro5bSQbbvmA3-xSZ29neQg'
bot = telebot.TeleBot(token, parse_mode="HTML")

# Subscribers list (authorized users)
subscriber = [
    '6181269269', 
    '5442332281', 
    '5991909954', 
    '7303810912', 
    '7886711162'
]

@bot.message_handler(commands=["start"])
def start(message):
    """Handler for /start command"""
    if str(message.chat.id) not in subscriber:
        bot.reply_to(message, "❌ Only For authorized users! Contact Admin @abirxdhackz")
        return
    bot.reply_to(message, "<b>Welcome To Mash  CC Checker\n Please send the Combo For check . \n\n Must Join @abir_x_official\nDeveloped By @abirxdhackz </b>")

@bot.message_handler(content_types=["document"])
def main(message):
    """Handler for processing uploaded files"""
    if str(message.chat.id) not in subscriber:
        bot.reply_to(message, "❌ Access Denied! Contact Admin @abirxdhackz")
        return

    # Status initialization
    declined = 0
    approved = 0
    processing_msg = bot.reply_to(message, "🔄 Checking Your Cards...⌛").message_id

    # Download and save the uploaded file
    file_data = bot.download_file(bot.get_file(message.document.file_id).file_path)
    with open("combo.txt", "wb") as combo_file:
        combo_file.write(file_data)

    try:
        with open("combo.txt", 'r') as file:
            card_lines = file.readlines()
            total_cards = len(card_lines)

            for card in card_lines:
                # Check for stop signal
                if os.path.exists("stop.stop"):
                    bot.edit_message_text(chat_id=message.chat.id, message_id=processing_msg, 
                                          text="⏹️ Processing Stopped! \nBot By: @abirxdhackz")
                    os.remove("stop.stop")
                    return

                # Fetch BIN details from binlist API
                try:
                    bin_data = requests.get(f'https://lookup.binlist.net/{card[:6]}').json()
                    bank = bin_data.get('bank', {}).get('name', 'Unknown')
                    country = bin_data.get('country', {}).get('name', 'Unknown')
                    country_emoji = bin_data.get('country', {}).get('emoji', '🌍')
                    scheme = bin_data.get('scheme', 'Unknown')
                    card_type = bin_data.get('type', 'Unknown')
                    bank_url = bin_data.get('bank', {}).get('url', 'N/A')
                except Exception:
                    bank, country, country_emoji, scheme, card_type, bank_url = ('Unknown',) * 6

                # Process the card through gateway (mocked by Tele module)
                try:
                    response = str(Tele(card))
                except Exception as e:
                    print(f"Error: {e}")
                    response = "ERROR"

                # Interpret response
                if 'risk' in response or 'declined' in response:
                    status = "❌ Declined"
                    declined += 1
                elif 'success' in response:
                    status = "✅ Approved"
                    approved += 1
                else:
                    status = "⚠️ Unknown Response"

                # Update the progress
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(
                    types.InlineKeyboardButton(f"🔹 Card: {card.strip()} ", callback_data='info'),
                    types.InlineKeyboardButton(f"🔹 Status: {status} ", callback_data='info'),
                    types.InlineKeyboardButton(f"🔹 Approved ✅: {approved} ", callback_data='info'),
                    types.InlineKeyboardButton(f"🔹 Declined ❌: {declined} ", callback_data='info'),
                    types.InlineKeyboardButton(f"🔹 Total Cards 📊: {total_cards} ", callback_data='info'),
                    types.InlineKeyboardButton(f"⏹ Stop", callback_data='stop')
                )

                bot.edit_message_text(chat_id=message.chat.id, message_id=processing_msg, 
                                      text=f"🔄 Processing Cards...\nPowered by @abirxdhackz | Credit: @abirxdhackz", 
                                      reply_markup=keyboard)

                # Send individual card details if approved
                if 'success' in response:
                    details = f"""
🔹 **Card**: `{card.strip()}`
🔹 **Status**: ✅ Approved
🔹 **BIN**: {card[:6]} - {scheme} - {card_type}
🔹 **Country**: {country} {country_emoji}
🔹 **Bank**: {bank}
🔹 **Bank URL**: {bank_url}
🔹 **Checked By**: @abirxdhackz
🔹 **Credit**: @ERR0R9
"""
                    bot.reply_to(message, details, parse_mode="Markdown")

    except Exception as e:
        print(f"Error: {e}")

    bot.edit_message_text(chat_id=message.chat.id, message_id=processing_msg, 
                          text="✅ Processing Completed!\nBot By: @abirxdhackz | Credit: @abirxdhackz")

@bot.callback_query_handler(func=lambda call: call.data == 'stop')
def stop_callback(call):
    """Handler for stop callback"""
    with open("stop.stop", "w") as file:
        pass
    bot.answer_callback_query(call.id, "⏹️ Processing will be stopped soon!")

# Bot execution
if __name__ == "__main__":
    print("+-------------------------------------------+")
    print("|         Bot Started Successfully!         |")
    print("+-------------------------------------------+")
    bot.polling()
