from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from vacancy import VACANCY_LIST


def menu_start():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("О нас", callback_data="about"),
        InlineKeyboardButton("Вакансии", callback_data="vacancy"),
        InlineKeyboardButton("Чаво", callback_data="faq"),      
        InlineKeyboardButton("Контакты", callback_data="contacts"),     
        InlineKeyboardButton("Помощь", url="https://t.me/vanoyan"),           
    )

    return markup

def town_board():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    list_butt = []

    for town in VACANCY_LIST:
        list_butt.append(InlineKeyboardButton(town, callback_data=f"town::{town}"))
    markup.add(*list_butt)


    return markup

def vacancy_board(count_vacancy):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("Выбрать", callback_data=f"choice::{count_vacancy}"),
        InlineKeyboardButton("▶️", callback_data="vacancy_next"), 
       
    )
    return markup

def offer_board():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("Подтвердить", callback_data=f"succ_offer"),
        InlineKeyboardButton("Отменить", callback_data="back"), 
       
    )
    return markup

def resident_board():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("Да", callback_data=f"resident::Да"),
        InlineKeyboardButton("Нет", callback_data="resident::Нет"), 
       
    )
    return markup

def add_manager(msg_id, user_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("Взять в работу", callback_data=f"add_manager::{msg_id}::{user_id}"),      
    )
    return markup

def back():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("Назад", callback_data=f"back"),      
    )
    return markup

# admin_board
def admin_board():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("Отчет", callback_data=f"report"),     
        InlineKeyboardButton("рассылка", callback_data=f"push_msg"),             
        # InlineKeyboardButton("рассылка по всем", callback_data=f"admin_lead"),     
        # InlineKeyboardButton("рассылка по НЕ лидам", callback_data=f"admin_lost"),
        # InlineKeyboardButton("рассылка по кнопке вакансии", callback_data=f"admin_vac"),
        # InlineKeyboardButton("рассылка по кнопке чаво", callback_data=f"admin_faq"),
        # InlineKeyboardButton("рассылка по кнопке контакты", callback_data=f"no_contacts"),
    )
    return markup

def choice_users():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(          
        InlineKeyboardButton("рассылка по всем", callback_data=f"admin_lead"),     
        InlineKeyboardButton("рассылка по НЕ лидам", callback_data=f"admin_lost"),
        InlineKeyboardButton("рассылка по кнопке вакансии", callback_data=f"admin_vac"),
        InlineKeyboardButton("рассылка по кнопке чаво", callback_data=f"admin_faq"),
        InlineKeyboardButton("рассылка по кнопке контакты", callback_data=f"admin_contacts"),
    )
    return markup