import telebot
from telebot import types
from db import check_user
from db import reg_db
from db import delete_user
from db import get_info
from db import select_free
from db import add_user
from db import check_status
from db import add_second_user
from db import check_companion
from db import check_open
from db import close_chat
from db import edit_db
import os
import time
import pytz
from datetime import datetime
from config import GROUP, OWNER, CHANNEL, BOT_NAME, TOKEN


bot = telebot.TeleBot(f'{TOKEN}')


class User:  
    def __init__(self, user_id):
        self.user_id = user_id
        self.name = None
        self.age = None
        self.sex = None
        self.change = None


user_dict = {}  

@bot.message_handler(commands=['start'])
def welcome(message):
    if check_user(user_id=message.from_user.id)[0]:
        mark = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        mark.add('🔍 Mencari pasangan')
        mark.add('📰 Info Profile', '🗑 Hapus Profile')
        bot.send_message(message.from_user.id, f"*Selamat bergabung {BOT_NAME}🙊*\n\n_Semoga mendapat teman atau jodoh_\n\n*NOTE:*\nJOIN\n[👥 ɢʀᴏᴜᴘ](t.me/{GROUP}) | [ᴄʜᴀɴɴᴇʟ 📣](t.me/{CHANNEL}) | [📱ᴏᴡɴᴇʀ](t.me/{OWNER})",parse_mode="markdown",disable_web_page_preview=True, reply_markup=mark)
        bot.register_next_step_handler(message, search_prof)
    else:
        bot.send_message(message.from_user.id, "_👋Halo Pengguna Baru, Untuk Melanjutkan Isi Biodata Berikut!_",parse_mode="markdown")
        bot.send_message(message.from_user.id, "➡️ *Nama :*", parse_mode="markdown")
        bot.register_next_step_handler(message, reg_name)

@bot.message_handler(content_types=['text'])
def text_reac(message):  
    bot.send_message(message.chat.id, 'Error Occurred\nSilakan klik /start untuk mencoba kembali')

def reg_name(message):  
    if message.text != '':
        user = User(message.from_user.id)
        user_dict[message.from_user.id] = user
        user.name = message.text
        bot.send_message(message.from_user.id, "*Usia :*", parse_mode="markdown")
        bot.register_next_step_handler(message, reg_age)

    else:
        bot.send_message(message.from_user.id, "*Masukkan nama Anda :*", parse_mode="markdown")
        bot.register_next_step_handler(message, reg_name)


def reg_age(message):  
    age = message.text
    if not age.isdigit():
        msg = bot.reply_to(message, '_Use numbers, not letters!!_', parse_mode="markdown")
        bot.register_next_step_handler(msg, reg_age)
        return
    user = user_dict[message.from_user.id]
    user.age = age
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Pria👦', 'Wanita👩🏻')
    bot.send_message(message.from_user.id, '*Gender :*',parse_mode="markdown", reply_markup=markup)
    bot.register_next_step_handler(message, reg_sex)


def reg_sex(message):  
    sex = message.text
    user = user_dict[message.from_user.id]
    if (sex == u'Pria👦') or (sex == u'Wanita👩🏻'):
        user.sex = sex
        mark = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        mark.add('Pria👦', 'Wanita👩🏻', 'Pria dan wanita👀')
        bot.send_message(message.from_user.id, '*⏳You want to find a partner :*',parse_mode="markdown", reply_markup=mark)
        bot.register_next_step_handler(message, reg_change)

    else:
        bot.send_message(message.from_user.id, '_Please click on the keyboard!_',parse_mode="markdown")
        bot.register_next_step_handler(message, reg_sex)


def reg_change(message):  
    if (message.text == u'Pria👦') or (message.text == u'Wanita👩🏻') or (message.text == u'Pria dan wanita👀'):
        user = user_dict[message.from_user.id]
        user.change = message.text
        date1 = datetime.fromtimestamp(message.date, tz=pytz.timezone("asia/jakarta")).strftime("%d/%m/%Y %H:%M:%S").split()
        bot.send_message(message.from_user.id,
                         "🐱 - _YOUR BIO_ - 🐱\n\n*=> Nama :* " + str(user.name) + "\n*=> Usia :* " + str(user.age)+" Tahun" + "\n*=> Jenis kelamin :* " + str(user.sex) + "\n*=> Tipe Pasangan :* " + str(user.change)+ "\n*=> Daftar pada :\n        >Ate :* "+str(date1[0])+"\n    *    >time :* "+str(date1[1])+" WIB", parse_mode="markdown")
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add('Yes ✔️', 'Tidak ✖️')
        bot.send_message(message.from_user.id, "`Ingin mengubah data di atas??`",parse_mode="markdown", reply_markup=markup)
        bot.register_next_step_handler(message, reg_accept)
    else:
        bot.send_message(message.from_user.id, 'You can only click on the keyboard')
        bot.register_next_step_handler(message, reg_change)


def reg_accept(message):  
    if (message.text == u'Yes ✔️') or (message.text == u'Tidak ✖️'):
        if message.text == u'Yes ✔️':
            tw = types.ReplyKeyboardRemove()
            bot.send_message(message.from_user.id, "*Masuk kembali🕹\nNamamu :*", parse_mode="markdown", reply_markup=tw)
            bot.register_next_step_handler(message, reg_name)
        else:
            if not check_user(user_id=message.from_user.id)[0]:
                user = user_dict[message.from_user.id]
                reg_db(user_id=user.user_id, name=user.name, old=user.age, gender=user.sex, change=user.change)
                bot.send_message(message.from_user.id, "_Berhasil...✅\nAkun Kamu Telah Terdaftar!_", parse_mode="markdown")
            else:
                if message.from_user.id in user_dict.keys():
                    user = user_dict[message.from_user.id]
                    edit_db(user_id=user.user_id, name=user.name, old=user.age, gender=user.sex, change=user.change)
            welcome(message)


def search_prof(message):  
    if (message.text == u'🔍 Mencari pasangan') or (message.text == u'📰 Info Profile') or (
            message.text == u'🗑 Hapus Profil'):
        if message.text == u'🔍 Mencari pasangan':
            bot.send_message(message.from_user.id, '🚀 Mencari pasangan untuk Anda . . .')
            search_partner(message)
        elif message.text == u'📰 Info Profile':
            user_info = get_info(user_id=message.from_user.id)
            bot.send_message(message.from_user.id,
                             "📍Data Profile📍\n\n*Nama :* " + str(user_info[2]) +"\n*ID :* `"+str(message.from_user.id)+"`" +"\n*Usia :* " + str(
                                 user_info[3]) +" Tahun" + "\n*Jenis kelamin :* " + str(user_info[4]) + "\n*Couple Type :* " + str(user_info[5]),parse_mode="markdown")
            mark = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            mark.add('Yes ✔️', 'Tidak ✖️')
            bot.send_message(message.from_user.id, '_Ingin Mengubah Data Profil Anda??_',parse_mode="markdown", reply_markup=mark)
            bot.register_next_step_handler(message, reg_accept)
        else:
            delete_user(user_id=message.from_user.id)
            tw = types.ReplyKeyboardRemove()
            bot.send_message(message.from_user.id, '_Tunggu sebentar..Menghapus Profil❗️_', parse_mode="markdown")
            bot.send_message(message.from_user.id, '_Berhasil..Profil Anda Dihapus✅_', parse_mode="markdown", reply_markup=tw)
            welcome(message)
    else:
        bot.send_message(message.from_user.id, 'Klik pada keyboard')
        bot.register_next_step_handler(message, search_prof)


def search_partner(message): 
    is_open = check_open(first_id=message.from_user.id)
    if is_open[0][0]:  
        bot.register_next_step_handler(message, chat)

    else:
        select = select_free()
        success = False
        if not select:
            add_user(first_id=message.from_user.id)
        else:
            for sel in select:
                if check_status(first_id=message.from_user.id, second_id=sel[0]) or message.from_user.id == sel[0]:
                    print(message.from_user.id, 'Join @AsmSafone Bot Made By @AmiFutami')
                    continue

                else:
                    print(sel[0])
                    print(message.from_user.id)
                    mark2 = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                    mark2.add('❌ Exit')
                    add_second_user(first_id=sel[0], second_id=message.from_user.id)
                    user_info = get_info(user_id=sel[0])
                    bot.send_message(message.from_user.id,
                                     "⚠️*Pasangan Ditemukan*⚠️\n\n*Usia :* " + str(user_info[3])+" Tahun" + "\n*Jenis kelamin :* " + str(user_info[4]),parse_mode="markdown", reply_markup=mark2)
                    user_info = get_info(user_id=message.from_user.id)
                    bot.send_message(sel[0],
                                     "⚠️*Pasangan Ditemukan*⚠️\n\n*Usia :* " + str(user_info[3])+" Tahun" + "\n*Jenis kelamin :* " + str(user_info[4]),parse_mode="markdown", reply_markup=mark2)
                    success = True
                    break
        if not success:
            time.sleep(2)
            search_partner(message)
        else:
            bot.register_next_step_handler(message, chat)

def chat(message):  
    if message.text == "❌ Exit" or message.text == "/exit":
        mark1 = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        mark1.add('🔍 Mencari pasangan')
        mark1.add('📰 Info Profile', '🗑 Hapus Profile')
        companion = check_companion(first_id=message.from_user.id)
        bot.send_message(message.from_user.id, "_You left the chat_",parse_mode="markdown", reply_markup=mark1)
        bot.send_message(companion, "_Your Spouse Left the Conversation_", parse_mode="markdown", reply_markup=mark1)
        close_chat(first_id=message.from_user.id)
        welcome(message)
        return
    elif not check_open(first_id=message.from_user.id)[0][0]:
        welcome(message)
        return
    companion = check_companion(first_id=message.from_user.id)
    bot.send_message(companion, message.text)
    bot.register_next_step_handler(message, chat)

print("BOT IS READY TO JOIN @AsmSafone")
bot.polling()
