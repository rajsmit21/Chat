from telebot import TeleBot

# Bot Token (replace with your actual token)
TELEGRAM_TOKEN = "7754972192:AAH6iHnlnYYYx1nuZgwmCB2koOHWlCPZQEE"

# Initialize the bot
bot = TeleBot(TELEGRAM_TOKEN)

# In-memory queue and active chats storage
waiting_users = []
active_chats = {}

# Command to start the bot
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Welcome to Anonymous Chat Bot!\n"
                          "Use /chat to find a chat partner.\n"
                          "Use /leave to exit the current chat.\n"
                          "Use /status to check your chat status.")

# Command to join the chat queue
@bot.message_handler(commands=['chat'])
def join_chat(message):
    user_id = message.from_user.id

    # Check if the user is already in a chat
    if user_id in active_chats:
        bot.reply_to(message, "You're already in a chat! Type /leave to exit the current chat.")
        return

    # Check if the user is already in the queue
    if user_id in waiting_users:
        bot.reply_to(message, "You're already waiting for a chat partner.")
        return

    # If another user is waiting, start a chat
    if waiting_users:
        partner_id = waiting_users.pop(0)  # Get the first user in the queue

        # Start a chat by pairing both users
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id

        bot.send_message(user_id, "You've been connected to a chat partner! Type your messages below.")
        bot.send_message(partner_id, "You've been connected to a chat partner! Type your messages below.")

    else:
        # Add the user to the waiting list
        waiting_users.append(user_id)
        bot.reply_to(message, "You're now in the queue. Waiting for a chat partner...")

# Command to leave the chat or queue
@bot.message_handler(commands=['leave'])
def leave_chat(message):
    user_id = message.from_user.id

    # If the user is in the waiting queue, remove them
    if user_id in waiting_users:
        waiting_users.remove(user_id)
        bot.reply_to(message, "You've left the queue.")
        return

    # If the user is in an active chat, end the chat
    if user_id in active_chats:
        partner_id = active_chats.pop(user_id)
        active_chats.pop(partner_id, None)

        bot.send_message(partner_id, "Your chat partner has left. Type /chat to find a new partner.")
        bot.reply_to(message, "You've left the chat. Type /chat to find a new partner.")
    else:
        bot.reply_to(message, "You're not in a chat or the queue.")

# Command to check current status
@bot.message_handler(commands=['status'])
def status(message):
    user_id = message.from_user.id

    if user_id in active_chats:
        bot.reply_to(message, "You're currently in a chat.")
    elif user_id in waiting_users:
        bot.reply_to(message, "You're in the queue, waiting for a chat partner.")
    else:
        bot.reply_to(message, "You're not in the queue or in a chat. Type /chat to start.")

# Forward messages between chat partners
@bot.message_handler(func=lambda message: message.from_user.id in active_chats)
def forward_message(message):
    user_id = message.from_user.id
    partner_id = active_chats.get(user_id)

    if partner_id:
        bot.send_message(partner_id, message.text)

# Start polling
bot.polling()
