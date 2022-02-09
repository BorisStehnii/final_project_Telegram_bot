
from telegram import Update, Bot, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext,\
    ConversationHandler, CallbackQueryHandler
from app import fapp, tg, Config, db
from app.models import client_wm
from flask import request
from app.telegram_config import ADMIN
import re


SEARCH = 'SEARCH'
UPDATE = 'UPDATE'
END = 'END'
NEW_DATA = 'NEW_DATA'
ORDER = 'ORDER'
EDIT = 'EDIT'
DATE, ADDRESS, PHONE, BRAND, BREAKING, REPAIR, INVOICE, COST, DEBT = range(9)


# меню функций бота
def menu_keyboard():
    keyboard = [[InlineKeyboardButton('Поиск по базе', callback_data="search")],
                [InlineKeyboardButton('Добавить в базу', callback_data="add_client")]]
    return InlineKeyboardMarkup(keyboard)


# меню кнопок для обновления данных
def menu_update_keyboard():
    keyboard = [[InlineKeyboardButton('Дата', callback_data=f'Дата'),
                 InlineKeyboardButton('Адрес', callback_data=f'Адрес'),
                 InlineKeyboardButton('Телефон', callback_data=f'Телефон'),
                 InlineKeyboardButton('Марка', callback_data=f'Марка')],
                [InlineKeyboardButton('Поломка', callback_data=f'Поломка'),
                 InlineKeyboardButton('Ремонт', callback_data=f'Ремонт'),
                 InlineKeyboardButton('Счёт', callback_data=f'Счёт'),
                 InlineKeyboardButton('Расходы', callback_data=f'Расходы'),
                 InlineKeyboardButton('Долг', callback_data=f'Долг')],
                [InlineKeyboardButton('Отмена', callback_data='back_menu')]]
    return InlineKeyboardMarkup(keyboard)


# кнопка вызова меню обновления данных
def button_update_menu(id_client):
    print(f"{id_client} Создание кнопки")
    button = [[InlineKeyboardButton('Обновить данные', callback_data=f'{id_client}')]]
    return InlineKeyboardMarkup(button)


# меню подтверждения данных
def menu_edit_or_write():

    keyboard = [[InlineKeyboardButton('Записать', callback_data='Записать'),
                 InlineKeyboardButton('Править', callback_data='Править')],
                [InlineKeyboardButton('Отмена', callback_data='Отмена')]]
    return InlineKeyboardMarkup(keyboard)


# Функция обработки кнопки Отмена в меню Записи или Правок
def handler_butt_cancel(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    context.bot.edit_message_text(chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  text='Запись прервана')
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Выбирай действие: ',
                             reply_markup=menu_keyboard()
                             )
    return ConversationHandler.END


#  Кнопка прерывания записи в базу или поиска
def button_back_menu():
    button = [[InlineKeyboardButton('Прервать и вернуться в главное меню', callback_data='menu')]]
    return InlineKeyboardMarkup(button)


# функция обработки кнопки возврата в предыдущее меню
def handler_back_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    id_client = context.user_data['id_client_update']
    query.answer()
    context.bot.edit_message_text(chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  text=query.message.text,
                                  reply_markup=button_update_menu(id_client))
    return SEARCH


# функци обработки кнопки вызова меню обновления данных
def handler_butt_upd_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    id_client = query.data
    context.user_data['id_client_update'] = id_client   # id клиента данные которого хотим обновить
    print(f"{id_client} Создание меню")
    query.answer()

    context.bot.edit_message_text(chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  text=query.message.text,
                                  reply_markup=menu_update_keyboard())
    return UPDATE


# функция обработки кнопок с типом обновляемой информации
def handler_butt_type_upd(update: Update, context: CallbackContext):
    query = update.callback_query
    name_button = query.data
    context.user_data['type_value'] = name_button   # тип обновляемых данных
    print(f"{name_button} Нажатие на тип ")
    query.answer()

    context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,
                                  text=query.message.text,
                                  reply_markup=button_update_menu(context.user_data['id_client_update']))
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'Введи новое значение параметра {name_button} ',
                             reply_markup=button_back_menu())
    return NEW_DATA


# функция обновления данных в базе
def update_type_data(update: Update, context: CallbackContext):
    new_value = update.effective_message.text
    id_client = context.user_data['id_client_update']
    type_value = context.user_data['type_value']

    if type_value == 'Дата':
        date = re.search(r'(\s*)?(\d\d[- _:.]?\d\d[- _:.]?\d\d)(\s*)?', new_value)
        if date:
            client = client_wm.query.filter(id_client == client_wm.client_id).first()
            client.date = date
            db.session.add(client)
            db.session.commit()
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='Неверный формат. Введите дату вызова в формате "01.01.22":',
                                     reply_markup=button_back_menu())
            return NEW_DATA
    elif type_value == 'Адрес':
        address = new_value
        client = client_wm.query.filter(id_client == client_wm.client_id).first()
        client.address = address
        db.session.add(client)
        db.session.commit()
    elif type_value == 'Телефон':
        phone = re.search(r'(\s*)?(\+)?([- _():=+]?\d[- _():=+]?){9,14}(\s*)?', new_value)
        if phone:
            phone = "".join(re.findall(r'\d', phone[0]))
            client = client_wm.query.filter(id_client == client_wm.client_id).first()
            client.phone = phone
            db.session.add(client)
            db.session.commit()
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='Неверный формат. Введите телефон в формате "0500775210:',
                                     reply_markup=button_back_menu())
            return NEW_DATA
    elif type_value == 'Марка':
        brand = new_value
        client = client_wm.query.filter(id_client == client_wm.client_id).first()
        client.brand = brand
        db.session.add(client)
        db.session.commit()
    elif type_value == 'Поломка':
        breaking = new_value
        client = client_wm.query.filter(id_client == client_wm.client_id).first()
        client.breaking = breaking
        db.session.add(client)
        db.session.commit()
    elif type_value == 'Ремонт':
        repair = new_value
        client = client_wm.query.filter(id_client == client_wm.client_id).first()
        client.repair = repair
        db.session.add(client)
        db.session.commit()
    elif type_value == 'Счёт':
        invoice = new_value
        if invoice.isdigit():
            invoice = int(invoice)
            client = client_wm.query.filter(id_client == client_wm.client_id).first()
            client.invoice = invoice
            client.profit = invoice - client.cost
            db.session.add(client)
            db.session.commit()
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Счёт:', reply_markup=button_back_menu())
            return NEW_DATA
    elif type_value == 'Расходы':
        cost = new_value
        if cost.isdigit:

            cost = int(cost)
            client = client_wm.query.filter(id_client == client_wm.client_id).first()
            client.cost = cost
            client.profit = client.invoice - cost
            db.session.add(client)
            db.session.commit()
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Расходы:', reply_markup=button_back_menu())
            return NEW_DATA
    elif type_value == 'Долг':
        debt = new_value
        client = client_wm.query.filter(id_client == client_wm.client_id).first()
        client.debt = debt
        db.session.add(client)
        db.session.commit()

    client = client_wm.query.filter(client_wm.client_id == id_client).first()
    if client:
        text_msg = f""" Дата: {client.date}
                    Телефон: +38{client.phone}
                    Адрес: {client.address}
                    Марка: {client.brand}
                    Поломка: {client.breaking}
                    Ремонт: {client.repair}
                    Счёт: {client.invoice}    Расход: {client.cost}
                    Доход: {client.profit}
                    Задолженость: {client.debt}
                    """
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'{text_msg}',
                                 reply_markup=button_update_menu(f"{client.client_id}"))
        search(update, context)
    return SEARCH


# Функция выводит меню после срабатывания кнопки прерывания записи или поиска
def menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    context.bot.edit_message_text(chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  text=query.message.text)

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Выбирай действие: ',
                             reply_markup=menu_keyboard()
                             )
    return ConversationHandler.END


# функция запуска и приветствия
def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f'Привет, {update.effective_user.username}. Выбирай действие:',
                             reply_markup=menu_keyboard())


# функция перехода в диалог поиска
def search(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Для поиска введите адрес, улицу или номер телефона:',
                             reply_markup=button_back_menu())
    return SEARCH


# функция поиска по телефону или адресу
def search_client(update: Update, context: CallbackContext):
    if re.search(r'(\s*)?(\+)?([- _():=+]?\d[- _():=+]?){9,14}(\s*)?', update.effective_message.text):
        msg_phone = re.search(r'(\s*)?(\+)?([- _():=+]?\d[- _():=+]?){9,14}(\s*)?', update.effective_message.text)[0]
        msg_phone = "".join(re.findall(r'\d', msg_phone))

        if len(msg_phone) > 10:
            msg_phone = msg_phone[-10:-1] + msg_phone[-1]

        clients = client_wm.query.filter(client_wm.phone.like(f'%{msg_phone}%')).all()
        if clients:
            for client in clients:
                text_msg = f""" Дата: {client.date}
                    Телефон: +38{client.phone}
                    Адрес: {client.address}
                    Марка: {client.brand}
                    Поломка: {client.breaking}
                    Ремонт: {client.repair}
                    Счёт: {client.invoice}    Расход: {client.cost}
                    Доход: {client.profit}
                    Задолженость: {client.debt}
                    """

                context.bot.send_message(chat_id=update.effective_chat.id, text=f'{text_msg}',
                                         reply_markup=button_update_menu(f"{client.client_id}"))

            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='Для поиска введите адрес, улицу или номер телефона:',
                                     reply_markup=button_back_menu())
            return SEARCH
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f'Не смог ничего найти. Попробуй ввести другой номер: ',
                                     reply_markup=button_back_menu())
            return SEARCH
    else:
        msg_address = update.effective_message.text
        clients = client_wm.query.filter(client_wm.address.like(f'%{msg_address}%')).all()

        if clients:
            for client in clients:
                text_msg = f""" Дата: {client.date}
                    Телефон: +38{client.phone}
                    Адрес: {client.address}
                    Марка: {client.brand}
                    Поломка: {client.breaking}
                    Ремонт: {client.repair}
                    Счёт: {client.invoice}    Расход: {client.cost}
                    Доход: {client.profit}
                    Задолженость: {client.debt}
                    """
                context.bot.send_message(chat_id=update.effective_chat.id, text=f'{text_msg}',
                                         reply_markup=button_update_menu(f"{client.client_id}"))

            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='Для поиска введите адрес, улицу или номер телефона:',
                                     reply_markup=button_back_menu())
            return SEARCH
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f'Не смог ничего найти. Попробуй изменить адрес для поиска: ',
                                     reply_markup=button_back_menu())
            return SEARCH


# функция поиска по телефону
def search_phone(update: Update, context: CallbackContext):
    msg_phone = re.search(r'(\s*)?(\+)?([- _():=+]?\d[- _():=+]?){9,14}(\s*)?', update.effective_message.text)[0]
    msg_phone = "".join(re.findall(r'\d', msg_phone))

    if len(msg_phone) > 10:
        msg_phone = msg_phone[-10:-1] + msg_phone[-1]

    clients = client_wm.query.filter(msg_phone == client_wm.phone).all()
    if clients:
        for client in clients:
            text_msg = f""" Дата: {client.date}
            Телефон: +38{client.phone}
            Адрес: {client.address}
            Марка: {client.brand}
            Поломка: {client.breaking}
            Ремонт: {client.repair}
            Счёт: {client.invoice}    Расход: {client.cost}
            Доход: {client.profit}
            Задолженость: {client.debt}
            """
            context.bot.send_message(chat_id=update.effective_chat.id, text=f'{text_msg}')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'Не смог ничего найти. Попробуй изменить поиск!')


# функция поиска по адресу
def search_address(update: Update, context: CallbackContext):
    msg_address = update.effective_message.text
    clients = client_wm.query.filter(client_wm.address.like(f'%{msg_address}%')).all()

    if clients:
        for client in clients:
            text_msg = f""" Дата: {client.date}
            Телефон: +38{client.phone}
            Адрес: {client.address}
            Марка: {client.brand}
            Поломка: {client.breaking}
            Ремонт: {client.repair}
            Счёт: {client.invoice}    Расход: {client.cost}
            Доход: {client.profit}
            Задолженость: {client.debt}
            """
            context.bot.send_message(chat_id=update.effective_chat.id, text=f'{text_msg}')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'Не смог ничего найти. Попробуй изменить поиск!')


# функция перехода в диалог записи нового клиента
def add_client(update: Update, context: CallbackContext):
    context.user_data['edit'] = False
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Введите дату вызова в формате "01.01.22":',
                             reply_markup=button_back_menu()
                             )
    return DATE


# запись даты вызова клиента
def date_client(update: Update, context: CallbackContext):
    date = re.search(r'(\s*)?(\d\d[- _:.]?\d\d[- _:.]?\d\d)(\s*)?', update.effective_message.text)

    if date:
        context.user_data["date"] = date[0]
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Неверный формат. Введите дату вызова в формате "01.01.22":',
                                 reply_markup=button_back_menu()
                                 )
        return DATE

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Введите  адрес клиена в формате "Кирова 185 к 3:',
                             reply_markup=button_back_menu()
                             )
    if context.user_data['edit']:
        return order_after(update, context)
    return ADDRESS


# запись адреси клиента
def address_client(update: Update, context: CallbackContext):
    context.user_data["address"] = update.effective_message.text

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Введите телефон в формате "0500775210:',
                             reply_markup=button_back_menu()
                             )
    if context.user_data['edit']:
        return order_after(update, context)
    return PHONE


# запись телефона клиента
def phone_client(update: Update, context: CallbackContext):
    phone = re.search(r'(\s*)?(\+)?([- _():=+]?\d[- _():=+]?){9,14}(\s*)?', update.effective_message.text)

    if phone:
        phone = "".join(re.findall(r'\d', phone[0]))
        context.user_data["phone"] = phone
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Неверный формат. Введите телефон в формате "0500775210:',
                                 reply_markup=button_back_menu()
                                 )
        return PHONE

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Введите марку машинки:',
                             reply_markup=button_back_menu()
                             )
    if context.user_data['edit']:
        return order_after(update, context)
    return BRAND


# запись марки машинки клиента
def brand_client(update: Update, context: CallbackContext):
    context.user_data["brand"] = update.effective_message.text

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Поломка:',
                             reply_markup=button_back_menu())
    if context.user_data['edit']:
        return order_after(update, context)
    return BREAKING


# запись поломки
def breaking_client(update: Update, context: CallbackContext):
    context.user_data["breaking"] = update.effective_message.text

    context.bot.send_message(chat_id=update.effective_chat.id, text='Ремонт:', reply_markup=button_back_menu())
    if context.user_data['edit']:
        return order_after(update, context)
    return REPAIR


# запись проделаного ремонта
def repair_client(update: Update, context: CallbackContext):
    context.user_data["repair"] = update.effective_message.text

    context.bot.send_message(chat_id=update.effective_chat.id, text='Счёт:', reply_markup=button_back_menu())
    if context.user_data['edit']:
        return order_after(update, context)
    return INVOICE


# запись счёта клиента
def invoice_client(update: Update, context: CallbackContext):
    invoice = update.effective_message.text
    if invoice.isdigit():
        context.user_data["invoice"] = int(invoice)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Счёт:', reply_markup=button_back_menu())
        return INVOICE
    context.bot.send_message(chat_id=update.effective_chat.id, text='Расходы:', reply_markup=button_back_menu())

    return COST


# запись расходов на клиента
def cost_client(update: Update, context: CallbackContext):
    cost = update.effective_message.text
    if cost.isdigit:
        context.user_data["cost"] = int(cost)
        context.user_data["profit"] = context.user_data["invoice"] - context.user_data["cost"]
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Расходы:', reply_markup=button_back_menu())
        return COST
    if context.user_data['edit']:
        return order_after(update, context)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Задолженость:',
                             reply_markup=button_back_menu())

    return DEBT


# запись долга клиента
def debt_client(update: Update, context: CallbackContext):
    context.user_data["debt"] = update.effective_message.text
    text_msg = f""" Новый клиент:
        Дата: {context.user_data["date"]}
        Телефон: +38{context.user_data["phone"]}
        Адрес: {context.user_data["address"]}
        Марка: {context.user_data["brand"]}
        Поломка: {context.user_data["breaking"]}
        Ремонт: {context.user_data["repair"]}
        Счёт: {context.user_data["invoice"]}    Расход: {context.user_data["cost"]}
        Доход: {context.user_data["profit"]}
        Задолженость: {context.user_data["debt"]}
        """

    context.user_data['edit'] = False
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'{text_msg}',
                             reply_markup=menu_edit_or_write())
    if context.user_data['edit']:
        return order_after(update, context)
    return ORDER


# обработка кнопки править перед записью
def edit(update: Update, context: CallbackContext):
    context.user_data['edit'] = True
    query = update.callback_query
    query.answer()
    context.bot.edit_message_text(chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  text=query.message.text,
                                  reply_markup=menu_update_keyboard())
    return EDIT


# обработка кнопки запись в базу
def write(update: Update, context: CallbackContext):
    client_new = client_wm(date=context.user_data["date"],
                           address=context.user_data["address"],
                           phone=context.user_data["phone"],
                           brand=context.user_data["brand"],
                           breaking=context.user_data["breaking"],
                           repair=context.user_data["repair"],
                           invoice=context.user_data["invoice"],
                           cost=context.user_data["cost"],
                           profit=context.user_data["profit"],
                           debt=context.user_data["debt"])
    db.session.add(client_new)
    db.session.commit()
    text_msg = f""" Новый клиент записан
                    Дата: {context.user_data["date"]}
                    Телефон: +38{context.user_data["phone"]}
                    Адрес: {context.user_data["address"]}
                    Марка: {context.user_data["brand"]}
                    Поломка: {context.user_data["breaking"]}
                    Ремонт: {context.user_data["repair"]}
                    Счёт: {context.user_data["invoice"]}    Расход: {context.user_data["cost"]}
                    Доход: {context.user_data["profit"]}
                    Задолженость: {context.user_data["debt"]}
                    """
    query = update.callback_query
    query.answer()
    context.bot.edit_message_text(chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  text=f'{text_msg}',
                                  reply_markup=menu_keyboard())
    return ConversationHandler.END


# обработка кнопопок правок типа данны клиента
def handler_butt_type_edit(update: Update, context: CallbackContext):
    query = update.callback_query
    type_edit = query.data
    query.answer()

    context.bot.edit_message_text(chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  text=query.message.text)

    if type_edit == "Дата":
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'Введи новое значение параметра {type_edit}',
                                 reply_markup=button_back_menu())
        return DATE
    elif type_edit == "Адрес":
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'Введи новое значение параметра {type_edit}',
                                 reply_markup=button_back_menu())
        return ADDRESS
    elif type_edit == "Телефон":
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'Введи новое значение параметра {type_edit}',
                                 reply_markup=button_back_menu())
        return PHONE
    elif type_edit == "Марка":
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'Введи новое значение параметра {type_edit}',
                                 reply_markup=button_back_menu())
        return BRAND
    elif type_edit == "Поломка":
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'Введи новое значение параметра {type_edit}',
                                 reply_markup=button_back_menu())
        return BREAKING
    elif type_edit == "Ремонт":
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'Введи новое значение параметра {type_edit}',
                                 reply_markup=button_back_menu())
        return REPAIR
    elif type_edit == "Счёт":
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'Введи новое значение параметра {type_edit}',
                                 reply_markup=button_back_menu())
        return INVOICE
    elif type_edit == "Расходы":
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'Введи новое значение параметра {type_edit}',
                                 reply_markup=button_back_menu())
        return COST
    elif type_edit == "Долг":
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'Введи новое значение параметра {type_edit}',
                                 reply_markup=button_back_menu())
        return DEBT
    elif type_edit == "back_menu":
        context.bot.edit_message_text(chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      text=query.message.text,
                                      reply_markup=menu_edit_or_write())
        return ORDER


def order_after(update: Update, context: CallbackContext):
    text_msg = f""" Новый клиент: 
            Дата: {context.user_data["date"]}
            Телефон: +38{context.user_data["phone"]}
            Адрес: {context.user_data["address"]}
            Марка: {context.user_data["brand"]}
            Поломка: {context.user_data["breaking"]}
            Ремонт: {context.user_data["repair"]}
            Счёт: {context.user_data["invoice"]}    Расход: {context.user_data["cost"]}
            Доход: {context.user_data["profit"]}
            Задолженость: {context.user_data["debt"]}
            """

    context.user_data['edit'] = False
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'{text_msg}',
                             reply_markup=menu_edit_or_write())
    return ORDER

# def debt_client(update: Update, context: CallbackContext):
#     context.user_data["debt"] = update.effective_message.text
#
#     client_new = client_wm(date=context.user_data["date"],
#                            address=context.user_data["address"],
#                            phone=context.user_data["phone"],
#                            brand=context.user_data["brand"],
#                            breaking=context.user_data["breaking"],
#                            repair=context.user_data["repair"],
#                            invoice=context.user_data["invoice"],
#                            cost=context.user_data["cost"],
#                            profit=context.user_data["profit"],
#                            debt=context.user_data["debt"])
#     db.session.add(client_new)
#     db.session.commit()
#
#     clients = client_wm.query.filter(context.user_data['phone'] == client_wm.phone).all()
#     if clients:
#         for client in clients:
#             text_msg = f""" Новый клиент записан
#                 Дата: {client.date}
#                 Телефон: +38{client.phone}
#                 Адрес: {client.address}
#                 Марка: {client.brand}
#                 Поломка: {client.breaking}
#                 Ремонт: {client.repair}
#                 Счёт: {client.invoice}    Расход: {client.cost}
#                 Доход: {client.profit}
#                 Задолженость: {client.debt}
#                 """
#             context.bot.send_message(chat_id=update.effective_chat.id, text=f'{text_msg}',
#                                      reply_markup=button_update_menu(f"{client.client_id}"))
#     return menu(update, context)


@fapp.route(f'/index', methods=['GET', 'POST'])
def index():
    updater = Updater(token=Config.TBOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    start_cmd = CommandHandler('start', start, Filters.user(username=ADMIN['USER_NAME']))

    conv_search = ConversationHandler(
        entry_points=[
            CommandHandler('search', search, Filters.user(username=ADMIN['USER_NAME'])),
            CallbackQueryHandler(search, pattern='search')
        ],
        states={
            SEARCH: [
                MessageHandler(Filters.text & (~Filters.command), search_client, pass_user_data=True),
                CallbackQueryHandler(menu, pattern='menu'),
                # CallbackQueryHandler(handler_back_menu, pattern="back_menu"),
                CallbackQueryHandler(handler_butt_upd_menu)     # button_update_menu(f"{client.client_id}")
            ],
            UPDATE: [
                CallbackQueryHandler(menu, pattern='menu'),
                CallbackQueryHandler(handler_back_menu, pattern="back_menu"),    # Сигнал от кнопки назад в меню
                CallbackQueryHandler(handler_butt_type_upd, pattern="Дата"),
                CallbackQueryHandler(handler_butt_type_upd, pattern="Адрес"),
                CallbackQueryHandler(handler_butt_type_upd, pattern="Телефон"),
                CallbackQueryHandler(handler_butt_type_upd, pattern="Марка"),
                CallbackQueryHandler(handler_butt_type_upd, pattern="Поломка"),
                CallbackQueryHandler(handler_butt_type_upd, pattern="Ремонт"),
                CallbackQueryHandler(handler_butt_type_upd, pattern="Счёт"),
                CallbackQueryHandler(handler_butt_type_upd, pattern="Расходы"),
                CallbackQueryHandler(handler_butt_type_upd, pattern="Долг")
            ],
            NEW_DATA: [
                CallbackQueryHandler(menu, pattern='menu'),
                MessageHandler(Filters.text & (~Filters.command), update_type_data, pass_user_data=True),
            ]
        },
        fallbacks=[
            CommandHandler('cancel', menu, Filters.user(username=ADMIN['USER_NAME'])),
            CallbackQueryHandler(menu, pattern='menu')
        ],
    )
    conv_add_client = ConversationHandler(
        entry_points=[
            CommandHandler('add_client', add_client, Filters.user(username=ADMIN['USER_NAME'])),
            CallbackQueryHandler(add_client, pattern='add_client')
        ],
        states={
            DATE: [
                MessageHandler(Filters.text & (~Filters.command), date_client, pass_user_data=True),
            ],
            ADDRESS: [
                MessageHandler(Filters.text & (~Filters.command), address_client, pass_user_data=True),
            ],
            PHONE: [
                MessageHandler(Filters.text & (~Filters.command), phone_client, pass_user_data=True),
            ],
            BRAND: [
                MessageHandler(Filters.text & (~Filters.command), brand_client, pass_user_data=True),
            ],
            BREAKING: [
                MessageHandler(Filters.text & (~Filters.command), breaking_client, pass_user_data=True),
            ],
            REPAIR: [
                MessageHandler(Filters.text & (~Filters.command), repair_client, pass_user_data=True),
            ],
            INVOICE: [
                MessageHandler(Filters.text & (~Filters.command), invoice_client, pass_user_data=True),
            ],
            COST: [
                MessageHandler(Filters.text & (~Filters.command), cost_client, pass_user_data=True),
            ],
            DEBT: [
                MessageHandler(Filters.text & (~Filters.command), debt_client, pass_user_data=True),
            ],
            ORDER: [
                CallbackQueryHandler(edit, pattern='Править'),
                CallbackQueryHandler(write, pattern='Записать'),
            ],
            EDIT: [
                CallbackQueryHandler(handler_butt_type_edit, pattern="Дата"),
                CallbackQueryHandler(handler_butt_type_edit, pattern="Адрес"),
                CallbackQueryHandler(handler_butt_type_edit, pattern="Телефон"),
                CallbackQueryHandler(handler_butt_type_edit, pattern="Марка"),
                CallbackQueryHandler(handler_butt_type_edit, pattern="Поломка"),
                CallbackQueryHandler(handler_butt_type_edit, pattern="Ремонт"),
                CallbackQueryHandler(handler_butt_type_edit, pattern="Счёт"),
                CallbackQueryHandler(handler_butt_type_edit, pattern="Расходы"),
                CallbackQueryHandler(handler_butt_type_edit, pattern="Долг"),
                CallbackQueryHandler(handler_butt_type_edit, pattern="back_menu")
            ]
        },
        fallbacks=[
            CommandHandler('cancel', menu, Filters.user(username=ADMIN['USER_NAME'])),
            CallbackQueryHandler(menu, pattern='menu'),
            CallbackQueryHandler(handler_butt_cancel, pattern='Отмена')
        ],
    )

    dispatcher.add_handler(start_cmd)
    dispatcher.add_handler(conv_search)
    dispatcher.add_handler(conv_add_client)

    # dispatcher.add_handler(CallbackQueryHandler(handler_butt_upd_menu, pattern="button_update_menu"))
    CallbackQueryHandler(handler_back_menu, pattern="back_menu")
    # dispatcher.add_handler(CallbackQueryHandler())

    updater.start_polling()
    return 'ok'



