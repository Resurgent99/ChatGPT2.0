import openai
import telebot
from telebot import types

bot = telebot.TeleBot('6908138976:AAFRntt7y7ADke7UUpbR6NfokGUPufYlXBU')
openai.api_key = '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'

message_history = []

@bot.message_handler(commands=['start'])
def start(message):
    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn3 = types.KeyboardButton('/start')
    keyboard_markup.add(btn3)
    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=keyboard_markup)

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("ChatGPT", callback_data='chatgpt')
    btn2 = types.InlineKeyboardButton("DALL-E", callback_data='dall-e')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}, какую помощь тебе оказать?', reply_markup=markup)



@bot.callback_query_handler(func=lambda call: call.data == 'chatgpt')
def gpt_btn(call):
    bot.send_message(call.message.chat.id, 'Ну что, давайте пообщаемся')



@bot.callback_query_handler(func=lambda call: call.data == 'dall-e')
def dalle_btn(call):
    global message_history
    message_history.append({
        "role": "assistant",
        "content": 'DALL-E',
    })
    bot.send_message(call.message.chat.id, 'Введите запрос для DALL-E')

def dalle(message):
    prompt = message.text.strip()
    if len(prompt) == 0:
        bot.send_message(message.chat.id, "Введите запрос")
        return

    try:
        response = openai.Image.create(
            prompt=prompt, n=1, size="1024x1024", model="dall-e-3"
        )
    except:
        bot.send_message(message.chat.id, "Произошла ошибка, попробуйте позже!")
        return

    bot.send_photo(
        message.chat.id,
        response["data"][0]["url"],
        reply_to_message_id=message.message_id,
    )
    start(message)


def gpt(message):
    global message_history
    message_history.append({
        "role": "user",
        "content": message.text,})

    client = openai.ChatCompletion.create(
        messages=message_history,
        model="gpt-3.5-turbo",
        max_tokens=150,
        temperature=0.7,
        n=1,
        stop=None,
        timeout=15,
    )

    if client and client.choices:
        reply = client.choices[0].message['content'].strip()
    else:
        reply = 'Ты что-то попутал'

    bot.send_message(message.chat.id, reply)

    message_history.append({
        "role": "assistant",
        "content": reply,
    })

@bot.message_handler(content_types=['text'])
def message_handler(message):
    if message.text:
        global message_history
        if message_history and message_history[-1].get("content") == 'DALL-E':
            dalle(message)
            message_history = []
        else:
            gpt(message)

bot.polling(none_stop=True)