# -*- coding: utf-8 -*-
import telebot
from telebot import types, logger #pytelegrambotapi
import sys
import logging
import msg
import os
import keybords
from config import TOKEN, GROUP_ID, ADMIN_LIST
from sqliteormmagic import SQLiteDB
import sqliteormmagic as som
import datetime
import pytz
import pandas as pd
from vacancy import VACANCY_LIST

db_users = SQLiteDB('users.db')

def get_msk_time() -> datetime:
    time_now = datetime.datetime.now(pytz.timezone("Europe/Moscow"))
    time_now = time_now.strftime('%Y-%m-%d %H:%M:%S')
    return time_now
# sys.stdout = open("stdout.txt", "a", encoding="utf-8")
# # sys.stderr = open("stderr.txt", "a", encoding="utf-8")

# логирование

# logger = telebot.logger
# logging.basicConfig(level=logging.DEBUG, filename="system.log",filemode="a",
#                     format="%(asctime)s %(levelname)s %(message)s", encoding='utf-8')
# handler = logging.FileHandler('log_res.txt', mode='a', encoding='utf-8')
# logger.addHandler(handler)
# telebot.logger.setLevel(level=logging.DEBUG)


bot = telebot.TeleBot(token=TOKEN, parse_mode='HTML', skip_pending=True)    
bot.set_my_commands(
    commands=[
        telebot.types.BotCommand("start", "Запуск бота"),
    ],)


def main():
    @bot.message_handler(commands=['start'])
    def start_fnc(message):
        db_users.create_table('users', [
        ("from_user_id", 'INTEGER UNIQUE'), 
        ("from_user_username", 'TEXT'), 
        ("reg_time", 'TEXT'), 
        ("town", 'TEXT'),   
        ("vacancy_id", 'INTEGER'),          
        ("vacancy_text", 'TEXT'),        
        ("mail", 'TEXT'),                  
        ("fio", 'TEXT'), 
        ("phone", 'TEXT'),         
        ("resident", 'TEXT'), 
        ("age", 'TEXT'), 
        ("about_time", 'TEXT'),  
        ("vacancy_time", 'TEXT'),  
        ("faq_time", 'TEXT'),      
        ("contacts_time", 'TEXT'),               
         ])
        
        db_users.ins_unique_row('users', [
            ("from_user_id", message.from_user.id), 
            ("from_user_username", message.from_user.username), 
            ("reg_time", get_msk_time()),                 
            ("town", '0'),   
            ("vacancy_id", '0'),          
            ("vacancy_text", '0'),        
            ("mail", '0'),                  
            ("fio", '0'), 
            ("phone", '0'),         
            ("resident", '0'), 
            ("age", '0'), 
            ("about_time", '0'),  
            ("vacancy_time", '0'),  
            ("faq_time", '0'),      
            ("contacts_time", '0'),             
            ])
        bot.send_message(chat_id=message.from_user.id, text=msg.start_msg,reply_markup=keybords.menu_start())

    @bot.message_handler(commands=['admin'])
    def admin_panel(message):
        if message.from_user.id in ADMIN_LIST:
            db_users.create_table('admins', [
            ("from_user_id", 'INTEGER UNIQUE'), 
            ("from_user_username", 'TEXT'), 
            ("reg_time", 'TEXT'), 
            ("text_msg", 'TEXT'),   
            ("last_push", 'TEXT'),                       
            ])
        
        db_users.ins_unique_row('admins', [
            ("from_user_id", message.from_user.id), 
            ("from_user_username", message.from_user.username), 
            ("reg_time", get_msk_time()),                 
            ("text_msg", '0'),   
            ("last_push", '0'),         
            ])
        bot.send_message(chat_id=message.from_user.id, text='Приветсвую тебя хозяин!',reply_markup=keybords.admin_board())
   

    @bot.callback_query_handler(func=lambda call: True)
    def callback_query(call):
        if call.from_user.id in ADMIN_LIST:
            if call.data == 'report':
                connection = som.create_connection('users.db')
                query = f"""
                SELECT * FROM users;
                """
                all_users = pd.read_sql_query(query, connection)
                all_users.to_excel('report.xlsx',index=False)
                connection.close()
                with open('report.xlsx', mode='rb') as filename:
                    bot.send_document(chat_id=call.from_user.id, document=filename, caption='Отчет по соискателм в прикрепленном файле')
            
            elif call.data == 'push_msg':
                m = bot.send_message(chat_id=call.from_user.id, text="Введите текст сообщения ⤵️")
                bot.register_next_step_handler(m, choice_users) 

            elif 'admin' in call.data:
                res = db_users.find_elements_in_column(table_name='admins', key_name=call.from_user.id, column_name='from_user_id')
                res = res[0]
                text_msg = res[3]
                connection = som.create_connection('users.db')
                if 'lead' in call.data:
                    query = f"""
                    SELECT from_user_id FROM users;
                    """
                elif 'lost' in call.data:
                    query = f"""
                    SELECT from_user_id FROM users WHERE resident != '0';
                    """

                elif 'vac' in call.data:
                    query = f"""
                    SELECT from_user_id FROM users WHERE vacancy_time != '0';
                    """

                elif 'faq' in call.data:
                    query = f"""
                    SELECT from_user_id FROM users WHERE faq_time != '0';
                    """

                elif 'contacts' in call.data:
                    query = f"""
                    SELECT from_user_id FROM users WHERE contacts_time != '0';
                    """
                all_users = som.execute_query_select(connection, query=query, params=[])
                connection.close()
                bot.send_message(chat_id=call.from_user.id, text=f'Запускаю рассылку...')
                for user in all_users:
                    bot.send_message(chat_id=user[0], text=text_msg)

                bot.send_message(chat_id=call.from_user.id, text=f'Рассылка закончена, отправлено {len(all_users)} шт.')

           

        if call.data == 'about':
            print(f"call.data {call.data}")
            db_users.upd_element_in_column(table_name='users', upd_par_name='about_time', key_par_name=get_msk_time(), upd_column_name='from_user_id', key_column_name=call.from_user.id)
            bot.send_message(chat_id=call.from_user.id, text=msg.about_msg,reply_markup=keybords.menu_start())
        
        elif call.data == 'vacancy':
            print(f"call.data {call.data}")
            db_users.upd_element_in_column(table_name='users', upd_par_name='vacancy_time', key_par_name=get_msk_time(), upd_column_name='from_user_id', key_column_name=call.from_user.id)
            bot.send_message(chat_id=call.from_user.id, text=msg.town_msg,reply_markup=keybords.town_board())
        
        elif 'town' in call.data:
            town = call.data.split("::")[1]
            db_users.upd_element_in_column(table_name='users', upd_par_name='town', key_par_name=town, upd_column_name='from_user_id', key_column_name=call.from_user.id)
            res = db_users.find_elements_in_column(table_name='users', key_name=call.from_user.id, column_name='from_user_id')
            print(res)
            res = res[0]
            count_vacancy = res[4]
            if count_vacancy >= len(VACANCY_LIST[town]) :
                count_vacancy = 0
            bot.send_message(chat_id=call.from_user.id, text=VACANCY_LIST[town][count_vacancy]['vacancy'], reply_markup=keybords.vacancy_board(count_vacancy=count_vacancy))
            count_vacancy +=1
            db_users.upd_element_in_column(table_name='users', upd_par_name='vacancy_id', key_par_name=count_vacancy, upd_column_name='from_user_id', key_column_name=call.from_user.id)
        
        elif call.data == 'vacancy_next':
            res = db_users.find_elements_in_column(table_name='users', key_name=call.from_user.id, column_name='from_user_id')
            print(res)
            res = res[0]
            count_vacancy = res[4]
            town= res[3]
            print(len(VACANCY_LIST[town]))
            if count_vacancy >= len(VACANCY_LIST[town]) :
                count_vacancy = 0
            
            bot.send_message(chat_id=call.from_user.id, text=VACANCY_LIST[town][count_vacancy]['vacancy'], reply_markup=keybords.vacancy_board(count_vacancy=count_vacancy))
            count_vacancy +=1
            db_users.upd_element_in_column(table_name='users', upd_par_name='vacancy_id', key_par_name=count_vacancy, upd_column_name='from_user_id', key_column_name=call.from_user.id)
        
        elif 'choice' in call.data:
            res = db_users.find_elements_in_column(table_name='users', key_name=call.from_user.id, column_name='from_user_id')
            print(res)
            res = res[0]
            count_vacancy = int(call.data.split("::")[1])
            town= res[3]
            db_users.upd_element_in_column(table_name='users', upd_par_name='vacancy_id', key_par_name=count_vacancy, upd_column_name='from_user_id', key_column_name=call.from_user.id)
            db_users.upd_element_in_column(table_name='users', upd_par_name='vacancy_text', key_par_name=VACANCY_LIST[town][count_vacancy]['vacancy'], upd_column_name='from_user_id', key_column_name=call.from_user.id)
            bot.send_message(chat_id=call.from_user.id, text=VACANCY_LIST[town][count_vacancy]['offer'], reply_markup=keybords.offer_board())
        
        elif call.data == 'succ_offer':
            m = bot.send_message(chat_id=call.from_user.id, text=msg.email_msg)
            bot.register_next_step_handler(m, get_mail)

        elif call.data == 'faq':
            print(f"call.data {call.data}")
            db_users.upd_element_in_column(table_name='users', upd_par_name='faq_time', key_par_name=get_msk_time(), upd_column_name='from_user_id', key_column_name=call.from_user.id)
            bot.send_message(chat_id=call.from_user.id, text=msg.faq_msg,reply_markup=keybords.menu_start())
        
        elif call.data == 'contacts':
            print(f"call.data {call.data}")       
            db_users.upd_element_in_column(table_name='users', upd_par_name='contacts_time', key_par_name=get_msk_time(), upd_column_name='from_user_id', key_column_name=call.from_user.id)
            bot.send_message(chat_id=call.from_user.id, text=msg.contacts_msg,reply_markup=keybords.menu_start())

        elif 'resident' in call.data:
            resident = call.data.split('::')[1]
            db_users.upd_element_in_column(table_name='users', upd_par_name='resident', key_par_name=resident, upd_column_name='from_user_id', key_column_name=call.from_user.id)
            bot.send_message(chat_id=call.from_user.id, text=msg.success_voronka_msg,reply_markup=keybords.back())
            res = db_users.find_elements_in_column(table_name='users', key_name=call.from_user.id, column_name='from_user_id')
            print(res)
            res = res[0]
            text = f"""
Когда <b>{get_msk_time()}</b>
Username <b>@{call.from_user.username}</b>
Город <b>{res[3]}</b>
email <b>{res[6]}</b>
ФИО <b>{res[7]}</b>
Тел. <b>{res[8]}</b>
Возраст <b>{res[10]}</b>
Резидент <b>{res[9]}</b>
Вакансия 
<b>{res[5]}</b>
"""         

            bot.send_message(chat_id=GROUP_ID, text=text, reply_markup=keybords.add_manager(msg_id=call.message.id, user_id=call.from_user.id))
        
        elif 'add_manager' in call.data:
            print(f"call.data {call.data}")
            # msg_id = int(call.data.split('::')[1])
            user_id = call.data.split('::')[2]
            bot.delete_message(chat_id=GROUP_ID, message_id=call.message.id)
            print(user_id)
            res = db_users.find_elements_in_column(table_name='users', key_name=int(user_id), column_name='from_user_id')
            print(res)
            res = res[0]
            text = f"""
***ЗАЯВКА***       
Когда <b>{get_msk_time()}</b>
Username <b>@{call.from_user.username}</b>
Город <b>{res[3]}</b>
email <b>{res[6]}</b>
ФИО <b>{res[7]}</b>
Тел. <b>{res[8]}</b>
Возраст <b>{res[10]}</b>
Резидент <b>{res[9]}</b>
Вакансия 
<b>{res[5]}</b>
***********************
Принял в работу менеджер
@{call.from_user.username}
"""    
            bot.send_message(chat_id=GROUP_ID, text=text)
        elif call.data == 'back':
            bot.send_message(chat_id=call.from_user.id, text=msg.start_msg,reply_markup=keybords.menu_start())

    # @bot.message_handler(content_types=['text'])
    def get_mail(message):
        print(f"message {message.text}")
        mail = message.text.strip()
        db_users.upd_element_in_column(table_name='users', upd_par_name='mail', key_par_name=mail, upd_column_name='from_user_id', key_column_name=message.from_user.id)
        m = bot.send_message(chat_id=message.from_user.id, text=msg.fio_msg)
        bot.register_next_step_handler(m, get_fio)

    def get_fio(message):
        print(f"message {message.text}")
        fio = message.text.strip()
        db_users.upd_element_in_column(table_name='users', upd_par_name='fio', key_par_name=fio, upd_column_name='from_user_id', key_column_name=message.from_user.id)
        m = bot.send_message(chat_id=message.from_user.id, text=msg.phone_msg)
        bot.register_next_step_handler(m, get_phone)

    def get_phone(message):
        print(f"message {message.text}")
        phone = message.text.strip()
        db_users.upd_element_in_column(table_name='users', upd_par_name='phone', key_par_name=phone, upd_column_name='from_user_id', key_column_name=message.from_user.id)
        m = bot.send_message(chat_id=message.from_user.id, text=msg.age_msg)
        bot.register_next_step_handler(m, get_age)   

    def get_age(message):
        print(f"message {message.text}")
        age = message.text.strip()
        db_users.upd_element_in_column(table_name='users', upd_par_name='age', key_par_name=age, upd_column_name='from_user_id', key_column_name=message.from_user.id)
        bot.send_message(chat_id=message.from_user.id, text=msg.resident_msg, reply_markup=keybords.resident_board())


    def choice_users(message):
        print(f"message {message.text}")
        msg = message.text.strip()
        db_users.upd_element_in_column(table_name='admins', upd_par_name='text_msg', key_par_name=msg, upd_column_name='from_user_id', key_column_name=message.from_user.id)
        
        bot.send_message(chat_id=message.from_user.id, text="Выберите категорию пользователей ⤵️", reply_markup=keybords.choice_users())
                  
            
            
            
    bot.infinity_polling()

if __name__ == "__main__":
    main()

    