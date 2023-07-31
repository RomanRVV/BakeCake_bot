import datetime
import telegram
from bot.models import *
from telegram import Update
from django.core.management.base import BaseCommand
from django.db.models import Q, Count
from BakeCake import settings
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    ParseMode,
    LabeledPrice,
    InputMediaPhoto
)
from telegram.ext import (
    Updater,
    Filters,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
)

# from phonenumbers import is_valid_number, parse


from phonenumbers import is_valid_number, parse
import calendar
from datetime import date, timedelta

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


class Command(BaseCommand):
    help = 'Телеграм-бот'

    def handle(self, *args, **kwargs):
        # tg_token = settings.TOKEN
        tg_token = settings.tg_token
        updater = Updater(token=tg_token, use_context=True)
        dispatcher = updater.dispatcher

        def start_conversation(update, context):
            query = update.callback_query
            user_first_name = update.effective_user.first_name
            user_id = update.effective_user.id
            context.user_data['user_first_name'] = user_first_name
            context.user_data['user_id'] = user_id

            keyboard = [
                [
                    InlineKeyboardButton("Заказать торт", callback_data='to_make_order'),

                ],
                [
                    InlineKeyboardButton("Мои заказы", callback_data="to_show_orders"),
                    InlineKeyboardButton("О нас", callback_data="to_common_info"),
                ],

            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.effective_message.reply_text(
                text=f"Описание компании",
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML)
            return 'GREETINGS'

        def make_order(update, _):
            query = update.callback_query
            keyboard = [
                [
                    InlineKeyboardButton("Сконструировать самому", callback_data="make_cake"),
                ],
                [
                    InlineKeyboardButton("Наши торты", callback_data="choose_cake"),
                    InlineKeyboardButton("Цены", callback_data="service_prices")
                ],
                [
                    InlineKeyboardButton("На главную", callback_data="to_start"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.answer()
            query.edit_message_text(
                text="Как вы хотите записаться", reply_markup=reply_markup
            )
            return 'MAKE_ORDER'

        def choose_level_cake(update, _):
            query = update.callback_query
            keyboard = [
                [
                    InlineKeyboardButton("1 уровень", callback_data="choose_level_cake_1"),
                    InlineKeyboardButton("2 уровня", callback_data="choose_level_cake_2"),
                    InlineKeyboardButton("3 уровня", callback_data="choose_level_cake_3"),
                ],
                [
                    InlineKeyboardButton("На главную", callback_data="to_start"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.answer()
            text = 'Выбор уровней'
            query.edit_message_text(
                text=text,
                reply_markup=reply_markup
            )
            return 'LEVEL_CAKE'

        def choose_shape_cake(update, context):
            query = update.callback_query
            if query.data == 'choose_level_cake_1':
                context.chat_data['level_cake'] = 'one'
                context.chat_data['level_cake_price'] = 400
            elif query.data == 'choose_level_cake_2':
                context.chat_data['level_cake'] = 'two'
                context.chat_data['level_cake_price'] = 750
            else:
                context.chat_data['level_cake'] = 'three'
                context.chat_data['level_cake_price'] = 1100
            price = context.chat_data['level_cake_price']
            keyboard = [
                [
                    InlineKeyboardButton("Квадрат", callback_data="choose_shape_cake_1"),
                    InlineKeyboardButton("Круг", callback_data="choose_shape_cake_2"),
                    InlineKeyboardButton("Прямоугольник", callback_data="choose_shape_cake_3"),
                ],
                [
                    InlineKeyboardButton("Назад", callback_data="choose_level_cake"),
                    InlineKeyboardButton("На главную", callback_data="to_start"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.answer()
            text = f'Выбор формы\nЦена торта-{price}руб.'
            query.edit_message_text(
                text=text,
                reply_markup=reply_markup
            )
            return 'CAKE_SHAPE_CHOICES'

        def choose_base_cake(update, context):
            query = update.callback_query
            if query.data == 'choose_shape_cake_1':
                context.chat_data['cake_shape'] = 'square'
                context.chat_data['cake_shape_price'] = 600
            elif query.data == 'choose_shape_cake_2':
                context.chat_data['cake_shape'] = 'circle'
                context.chat_data['cake_shape_price'] = 400
            else:
                context.chat_data['cake_shape'] = 'rectangle'
                context.chat_data['cake_shape_price'] = 1000
            price = context.chat_data['level_cake_price']+context.chat_data['cake_shape_price']
            keyboard = [
                [
                    InlineKeyboardButton("Ванильный бисквит", callback_data="choose_base_cake_1"),
                    InlineKeyboardButton("Шоколадный бисквит", callback_data="choose_base_cake_2"),
                ],
                [
                    InlineKeyboardButton("Мраморный бисквит", callback_data="choose_base_cake_3"),
                    InlineKeyboardButton("Медовое печенье", callback_data="choose_base_cake_4"),
                ],
                [
                    InlineKeyboardButton("Назад", callback_data="choose_level_cake"),
                    InlineKeyboardButton("На главную", callback_data="to_start"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.answer()
            text = f'Выбор основы\nЦена торта-{price}руб.'
            query.edit_message_text(
                text=text,
                reply_markup=reply_markup
            )
            return 'CAKE_BASE_CHOICES'

        def choose_topping(update, context):
            query = update.callback_query
            if query.data == 'choose_base_cake_1':
                context.chat_data['base_cake'] = 'vanila'
                context.chat_data['base_cake_price'] = 200
            elif query.data == 'choose_base_cake_2':
                context.chat_data['base_cake'] = 'choco'
                context.chat_data['base_cake_price'] = 200
            elif query.data == 'choose_base_cake_3':
                context.chat_data['base_cake'] = 'marble'
                context.chat_data['base_cake_price'] = 300
            else:
                context.chat_data['base_cake'] = 'honey_biscuits'
                context.chat_data['base_cake_price'] = 300
        
            price = context.chat_data['level_cake_price']+context.chat_data['cake_shape_price']\
                    +context.chat_data['base_cake_price']

            keyboard = [
                [
                    InlineKeyboardButton("Клиновый сироп", callback_data="choose_topping_cake_1"),
                    InlineKeyboardButton("Карамельный сироп", callback_data="choose_topping_cake_2"),
                ],
                [
                    InlineKeyboardButton("Молочный шоколад", callback_data="choose_topping_cake_3"),
                    InlineKeyboardButton("Черничный сироп", callback_data="choose_topping_cake_4"),
                ],
                [
                    InlineKeyboardButton("Клубничный сироп", callback_data="choose_topping_cake_5"),
                    InlineKeyboardButton("Белый соус", callback_data="choose_topping_cake_6"),
                ],
                [
                    InlineKeyboardButton("Без топпинга", callback_data="choose_topping_cake_0"),
                ],
                [
                    InlineKeyboardButton("Назад", callback_data="choose_base_cake"),
                    InlineKeyboardButton("На главную", callback_data="to_start"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.answer()
            text = f'Выбор топпинга\nЦена торта-{price}руб.'
            query.edit_message_text(
                text=text,
                reply_markup=reply_markup
            )
            
            return 'TOPPING_CHOICES'

        def add_berries(update, context):
            query = update.callback_query
            if query.data == 'choose_topping_cake_1':
                context.chat_data['topping'] = 'wedge'
                context.chat_data['topping_price'] = 200
            elif query.data == 'choose_topping_cake_2':
                context.chat_data['topping'] = 'caramel'
                context.chat_data['topping_price'] = 180
            elif query.data == 'choose_topping_cake_3':
                context.chat_data['topping'] = 'milk_choco'
                context.chat_data['topping_price'] = 200
            elif query.data == 'choose_topping_cake_4':
                context.chat_data['topping'] = 'blueberry_syrup'
                context.chat_data['topping_price'] = 350 
            elif query.data == 'choose_topping_cake_5':
                context.chat_data['topping'] = 'strawberry_syrup'
                context.chat_data['topping_price'] = 300
            elif query.data == 'choose_topping_cake_6':
                context.chat_data['topping'] = 'white_sauce'
                context.chat_data['topping_price'] = 200   
            else:
                context.chat_data['topping'] = ''
                context.chat_data['topping_price'] = 0
            price = context.chat_data['level_cake_price'] + context.chat_data['base_cake_price']\
                    +context.chat_data['cake_shape_price']+context.chat_data['topping_price']
            keyboard = [
                [
                    InlineKeyboardButton("Ежевика", callback_data="choose_berries_1"),
                    InlineKeyboardButton("Малина", callback_data="choose_berries_2"),
                ],
                [
                    InlineKeyboardButton("Голубика", callback_data="choose_berries_3"),
                    InlineKeyboardButton("Клубника", callback_data="choose_berries_4"),
                ],
                [
                    InlineKeyboardButton("Без ягод", callback_data="choose_berries_0"),
                ],
                [
                    InlineKeyboardButton("Назад", callback_data="choose_topping"),
                    InlineKeyboardButton("На главную", callback_data="to_start"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.answer()
            text = f'Выберите ягоды\nЦена торта-{price}руб.'
            query.edit_message_text(
                text=text,
                reply_markup=reply_markup
            )

            return 'BERRIES_CHOICES'

        def add_inscription(update, context):
            query = update.callback_query
            context.chat_data['cake_id'] = ''
            if query.data == 'choose_berries_1':
                context.chat_data['berries'] = 'blackberry'
                context.chat_data['berries_price'] = 400
            elif query.data == 'choose_berries_2':
                context.chat_data['berries'] = 'raspberry'
                context.chat_data['berries_price'] = 300
            elif query.data == 'choose_berries_3':
                context.chat_data['berries'] = 'blueberry'
                context.chat_data['berries_price'] = 450
            elif query.data == 'choose_berries_4':
                context.chat_data['berries'] = 'strawberry'
                context.chat_data['berries_price'] = 500
            else:
                context.chat_data['berries'] = ''
                context.chat_data['berries_price'] = 0
            price = context.chat_data['level_cake_price'] + context.chat_data['base_cake_price'] \
                    +context.chat_data['cake_shape_price']+context.chat_data['topping_price']\
                    +context.chat_data['berries_price']
            context.chat_data['inscription'] = ''
            context.chat_data['inscription_price'] = 0
            keyboard = [
                [
                    InlineKeyboardButton("Да", callback_data="inscription_yes"),
                ],
                [
                    InlineKeyboardButton("Нет", callback_data="inscription_no"),
                ],
                [
                    InlineKeyboardButton("Назад", callback_data="add_berries"),
                    InlineKeyboardButton("На главную", callback_data="to_start"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.answer()
            text = f'Вы хотите добавить надпись к торту?\nЦена торта-{price}руб.'
            query.edit_message_text(
                text=text,
                reply_markup=reply_markup
            )

            return 'INSCRIPTION_CHOICES'

        def get_inscription(update, _):
            query = update.callback_query
            keyboard = [
                [
                    InlineKeyboardButton("Назад", callback_data="add_inscription"),
                    InlineKeyboardButton("На главную", callback_data="to_start"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.answer()
            text = 'Напишите надпись, которая должна появиться на торте'
            query.edit_message_text(
                text=text,
                reply_markup=reply_markup
            )
            return 'GET_INSCRIPTION'

        def check_order(update, context):
            query = update.callback_query
            if update.message:
                question_text = update.message.text
                context.chat_data['inscription'] = question_text
                context.chat_data['inscription_price'] = 500
            total_price = context.chat_data['level_cake_price'] + context.chat_data['base_cake_price'] \
                    +context.chat_data['cake_shape_price']+context.chat_data['topping_price']\
                    +context.chat_data['berries_price']+context.chat_data['inscription_price']
            context.chat_data['price'] = total_price

            keyboard = [
                [
                    InlineKeyboardButton("Оформить заказ", callback_data="to_order"),
                ],
                [
                    InlineKeyboardButton("Назад", callback_data="check_order"),
                    InlineKeyboardButton("На главную", callback_data="to_start"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            text = f'Цена за ваш торт {total_price} руб.'

            if not update.message:
                query.edit_message_text(
                    text=text,
                    reply_markup=reply_markup
                )
            else:
                update.message.reply_text(text=text,
                                          reply_markup=reply_markup,
                                          parse_mode=ParseMode.HTML, )

            return 'CHECK_ORDER'

        def order(update, context):
            query = update.callback_query
            CakeConstructor.objects.create(num_of_level=context.chat_data['level_cake'],
                                           base_of_cake=context.chat_data['base_cake'],
                                           topping=context.chat_data['topping'],
                                           berries=context.chat_data['berries'],
                                           inscription=context.chat_data['inscription'],
                                           cake_shape=context.chat_data['cake_shape'],
                                           price=context.chat_data['price']
                                           )
            keyboard = [
                [

                    InlineKeyboardButton("Выбрать дату", callback_data="choose_date"),
                ],
                [
                    InlineKeyboardButton("На главную", callback_data="to_start")
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.answer()
            text = 'Для продолжения оформления заказа выберите дату доставки'
            query.edit_message_text(
                text=text,
                reply_markup=reply_markup
            )

            return 'ORDER'

        def choose_cake(update, context):
            query = update.callback_query
            cakes = Cake.objects.all()

            for cake in cakes:
                message = f"<b>{cake.name}</b>\n"
                message += f"{cake.description}\n"
                message += f"Цена: {cake.price}\n"

                if cake.image:
                    context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=cake.image,
                        caption=message,
                        parse_mode=ParseMode.HTML
                    )
                else:
                    context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text=message,
                        parse_mode=ParseMode.HTML
                    )

            buttons = [[InlineKeyboardButton(cake.name, callback_data=f"select_cake_{cake.id}")] for cake in cakes]
            buttons.append([InlineKeyboardButton("Назад", callback_data="make_order")])

            reply_markup = InlineKeyboardMarkup(buttons)

            query.message.reply_text(
                text="Выберите торт для заказа:",
                reply_markup=reply_markup
            )

            return 'CHOOSE_CAKE'

        def add_inscription_for_prepared_cakes(update, context):
            query = update.callback_query
            context.chat_data['cake_id'] = update.callback_query.data.split('_')[-1]
            context.chat_data['inscription'] = ''
            context.chat_data['inscription_price'] = 0
            keyboard = [
                [
                    InlineKeyboardButton("Да", callback_data="inscription_yes"),
                ],
                [
                    InlineKeyboardButton("Нет", callback_data="inscription_no"),
                ],
                [
                    InlineKeyboardButton("На главную", callback_data="to_start"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.answer()
            text = f'Вы хотите добавить надпись к торту?\nЦена торта увеличится на 500 рублей.'
            query.edit_message_text(
                text=text,
                reply_markup=reply_markup
            )

            return 'INSCRIPTION_CHOICES_FOR_PREPARED_CAKES'

        def get_inscription_for_prepared_cakes(update, _):
            query = update.callback_query
            keyboard = [
                [
                    InlineKeyboardButton("Назад", callback_data="add_inscription"),
                    InlineKeyboardButton("На главную", callback_data="to_start"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.answer()
            text = 'Напишите надпись, которая должна появиться на торте'
            query.edit_message_text(
                text=text,
                reply_markup=reply_markup
            )
            return 'GET_INSCRIPTION_FOR_PREPARED_CAKES'

        def choose_delivery_date(update, context):
            query = update.callback_query

            cake_id = context.chat_data['cake_id']
            if update.message:
                question_text = update.message.text
                context.chat_data['inscription'] = question_text
                context.chat_data['inscription_price'] = 500
            try:
                selected_cake = Cake.objects.get(id=cake_id)
            except ValueError:

                selected_cake = CakeConstructor.objects.get(num_of_level=context.chat_data['level_cake'],
                                                            base_of_cake=context.chat_data['base_cake'],
                                                            topping=context.chat_data['topping'],
                                                            berries=context.chat_data['berries'],
                                                            inscription=context.chat_data['inscription'],
                                                            cake_shape=context.chat_data['cake_shape']
                                                            )

            context.user_data['selected_cake'] = selected_cake

            price_cake = selected_cake.price
            context.user_data['price_cake'] = price_cake
            today = datetime.date.today()

            current_week_start = today - datetime.timedelta(days=today.weekday())

            buttons = []

            for _ in range(4):
                row = []
                for day_offset in range(7):
                    date = current_week_start + datetime.timedelta(days=day_offset)
                    if date < today:
                        row.append(InlineKeyboardButton(' ', callback_data='ignore'))
                    else:
                        date_str = date.strftime("%d.%m")
                        row.append(InlineKeyboardButton(date_str, callback_data=f"date_{date}"))
                buttons.append(row)
                current_week_start += datetime.timedelta(days=7)

            buttons.append([InlineKeyboardButton("Отмена", callback_data="cancel")])
            text = "Выберите дату доставки:"
            reply_markup = InlineKeyboardMarkup(buttons)
            if not update.message:
                query.edit_message_text(
                    text=text,
                    reply_markup=reply_markup
                )
            else:
                update.message.reply_text(text=text,
                                          reply_markup=reply_markup,
                                          parse_mode=ParseMode.HTML, )

            return 'GET_DELIVERY_DATE'

        def choose_delivery_time(update, context):
            query = update.callback_query
            query.answer()
            delivery_date = update.callback_query.data.split('_')[1]
            context.user_data['delivery_date'] = delivery_date
            hours = ["10:00", "12:00", "14:00", "16:00", "18:00"]

            buttons = []
            current_time = datetime.datetime.now().strftime('%H:%M')
            for hour in hours:
                if delivery_date == datetime.datetime.now().strftime('%Y-%m-%d') and hour <= current_time:
                    continue
                buttons.append([InlineKeyboardButton(hour, callback_data=f"time_{hour}")])

            if not buttons:
                next_day = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                buttons.append([InlineKeyboardButton(f"На {next_day}", callback_data=f"time_{next_day}")])

            buttons.append([InlineKeyboardButton("Отмена", callback_data="cancel")])

            reply_markup = InlineKeyboardMarkup(buttons)

            query.edit_message_text(
                text="Выберите время доставки:",
                reply_markup=reply_markup
            )

            return 'GET_DELIVERY_TIME'

        def ask_for_consent(update, context):
            query = update.callback_query
            query.answer()
            delivery_time = update.callback_query.data.split('_')[1]
            context.user_data['delivery_time'] = delivery_time
            user_consent = context.user_data.get('user_consent', False)
            if user_consent:
                return handle_consent(update, context, consent_given=True)
            else:
                keyboard = [
                    [
                        InlineKeyboardButton("Да, согласен/согласна", callback_data="consent_yes"),
                    ],
                    [
                        InlineKeyboardButton("Нет, не согласен/согласна", callback_data="consent_no"),
                    ],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                query.edit_message_text(
                    text="Вы готовы предоставить персональные данные для заказа?",
                    reply_markup=reply_markup,
                )

            return 'ASK_FOR_CONSENT'


        def get_contact_info(update, context):
            query = update.callback_query
            user_first_name = update.effective_user.first_name
            context.user_data['username'] = user_first_name
            user_id = update.effective_user.id
            context.user_data['user_id'] = user_id
            query.edit_message_text(
                text=f"Привет, {user_first_name}! "
                     f"Введите ваш номер телефона:",
            )

            return 'GET_PHONE_NUMBER'

        def get_phone_number(update, context):
            user_phone = update.message.text
            context.user_data['phone'] = user_phone

            update.message.reply_text(
                "Введите адрес доставки:"
            )

            return 'GET_ADDRESS'

        def get_address(update, context):
            address = update.message.text
            context.user_data['address'] = address

            selected_cake = context.user_data.get('selected_cake')
            delivery_date = context.user_data.get('delivery_date')
            delivery_time = context.user_data.get('delivery_time')
            phone = context.user_data.get('phone')
            address = context.user_data.get('address')

            delivery_datetime = datetime.datetime.strptime(delivery_date, "%Y-%m-%d")
            now = datetime.datetime.now()
            if delivery_datetime <= now + datetime.timedelta(hours=24):
                selected_cake.price *= 0.8

            try:
                order = CakeOrder.objects.create(
                    user_id=context.user_data['user_id'],
                    user_name=context.user_data['username'],
                    user_phone=phone,
                    delivery_date=delivery_date,
                    delivery_time=delivery_time,
                    delivery_address=address,
                    cake=selected_cake,
                    order_price=selected_cake.price+context.chat_data['inscription_price'],
                    inscription=context.chat_data['inscription'],
                    user_consent = True
                )
            except ValueError:
                order = CakeOrder.objects.create(
                    user_id=context.user_data['user_id'],
                    user_name=context.user_data['username'],
                    user_phone=phone,
                    delivery_date=delivery_date,
                    delivery_time=delivery_time,
                    delivery_address=address,
                    designer_cake=selected_cake,
                    order_price=selected_cake.price+context.chat_data['inscription_price'],
                    inscription=context.chat_data['inscription'],
                    user_consent=True
                )

            buttons = [
                [InlineKeyboardButton('Оплатить онлайн', callback_data='pay')],
                [InlineKeyboardButton('Отмена', callback_data='cancel')],
            ]
            reply_markup = InlineKeyboardMarkup(buttons)

            update.message.reply_text(
                f"Спасибо за ваш заказ!\n"
                "Информация о Вашем торте:\n"
                f"Цена {order.order_price}\n"
                f"Дата доставки: {delivery_date}\n"
                f"Время доставки: {delivery_time}\n"
                f"Номер телефона: {phone}\n"
                f"Адрес доставки: {address}\n\n"
                f"Выберите действие:",
                reply_markup=reply_markup,
            )

            return 'SEND_INVOICE'

        def send_invoice(update, context):
            selected_cake = context.user_data.get('selected_cake')
            price_in_rubles = float(selected_cake.price)
            amount_in_kopecks = int(price_in_rubles * 100)

            token = '381764678:TEST:57788'
            chat_id = update.effective_message.chat_id
            context.user_data['invoice_sended'] = True

            keyboard = [
                [InlineKeyboardButton('Оплатить', pay=True)],
                [InlineKeyboardButton('На главную', callback_data='to_start')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_invoice(
                chat_id=chat_id,
                title=selected_cake.name,
                description='Цена торта',
                payload='payload',
                provider_token=token,
                currency='RUB',
                need_phone_number=False,
                need_email=False,
                is_flexible=False,
                prices=[
                    LabeledPrice(label='Цена торта', amount=amount_in_kopecks)
                ],
                start_parameter='test',
            )
            return 'SUCCESS_PAYMENT'

        def show_prices(update, _):
            query = update.callback_query
            cakes = Cake.objects.all()
            text = 'Цены на готовые наши торты:\n'
            for cake in cakes:
                text += f"Название-{cake.name}: Цена в рублях-{cake.price}\n"
            keyboard = [
                [InlineKeyboardButton("Назад", callback_data="make_order")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.answer()
            query.edit_message_text(
                text=text,
                reply_markup=reply_markup
            )
            return 'SHOW_PRICES'

        def show_orders(update, context):
            query = update.callback_query
            user_id = query.from_user.id

            user_orders = CakeOrder.objects.filter(user_id=user_id)

            if user_orders.exists():
                text = "Ваши заказы:\n"
                for order in user_orders:
                    if order.cake:
                        cake_name = order.cake.name
                    else:
                        cake_name = order.designer_cake.name
                    text += f"Торт: {cake_name}\n"
                    text += f"Цена заказа: {order.order_price}\n"
                    text += f"Дата доставки: {order.delivery_date}\n"
                    text += f"Время доставки: {order.delivery_time}\n"
                    text += f"Номер телефона: {order.user_phone}\n"
                    text += f"Адрес доставки: {order.delivery_address}\n\n"
            else:
                text = "У вас пока нет заказов."

            keyboard = [
                [InlineKeyboardButton("На главный", callback_data="to_start")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.answer()
            query.edit_message_text(
                text=text, reply_markup=reply_markup
            )
            return 'SHOW_ANSWER'

        def show_common_info(update, context):
            query = update.callback_query
            keyboard = [
                [
                    InlineKeyboardButton("На главную", callback_data="to_start"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.answer()
            query.edit_message_text(
                text="Информация о пекарне, что делаем и т.д", reply_markup=reply_markup
            )
            return 'COMMON_INFO'

        def cancel(update, _):
            user = update.message.from_user
            update.message.reply_text(
                'До новых встреч',
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start_conversation)],
            states={
                'GREETINGS': [
                    CallbackQueryHandler(make_order, pattern='to_make_order'),
                    CallbackQueryHandler(show_orders, pattern='to_show_orders'),
                    CallbackQueryHandler(show_common_info, pattern='to_common_info'),
                ],
                'MAKE_ORDER': [
                    CallbackQueryHandler(show_prices, pattern='service_prices'),
                    CallbackQueryHandler(choose_cake, pattern='choose_cake'),
                    CallbackQueryHandler(choose_level_cake, pattern='make_cake'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),

                ],
                'LEVEL_CAKE': [
                    CallbackQueryHandler(choose_shape_cake, pattern='choose_level_cake_1'),
                    CallbackQueryHandler(choose_shape_cake, pattern='choose_level_cake_2'),
                    CallbackQueryHandler(choose_shape_cake, pattern='choose_level_cake_3'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                ],
                'CAKE_SHAPE_CHOICES': [
                    CallbackQueryHandler(choose_level_cake, pattern='choose_level_cake'),
                    CallbackQueryHandler(choose_base_cake, pattern='choose_shape_cake_1'),
                    CallbackQueryHandler(choose_base_cake, pattern='choose_shape_cake_2'),
                    CallbackQueryHandler(choose_base_cake, pattern='choose_shape_cake_3'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                ],
                'CAKE_BASE_CHOICES': [
                    CallbackQueryHandler(choose_shape_cake, pattern='choose_level_cake'),
                    CallbackQueryHandler(choose_topping, pattern='choose_base_cake_1'),
                    CallbackQueryHandler(choose_topping, pattern='choose_base_cake_2'),
                    CallbackQueryHandler(choose_topping, pattern='choose_base_cake_3'),
                    CallbackQueryHandler(choose_topping, pattern='choose_base_cake_4'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                ],
                'TOPPING_CHOICES': [
                    CallbackQueryHandler(choose_base_cake, pattern='choose_base_cake'),
                    CallbackQueryHandler(add_berries, pattern='choose_topping_cake_1'),
                    CallbackQueryHandler(add_berries, pattern='choose_topping_cake_2'),
                    CallbackQueryHandler(add_berries, pattern='choose_topping_cake_3'),
                    CallbackQueryHandler(add_berries, pattern='choose_topping_cake_4'),
                    CallbackQueryHandler(add_berries, pattern='choose_topping_cake_5'),
                    CallbackQueryHandler(add_berries, pattern='choose_topping_cake_6'),
                    CallbackQueryHandler(add_berries, pattern='choose_topping_cake_0'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                ],
                'BERRIES_CHOICES': [
                    CallbackQueryHandler(choose_topping, pattern='choose_topping'),
                    CallbackQueryHandler(add_inscription, pattern='choose_berries_1'),
                    CallbackQueryHandler(add_inscription, pattern='choose_berries_2'),
                    CallbackQueryHandler(add_inscription, pattern='choose_berries_3'),
                    CallbackQueryHandler(add_inscription, pattern='choose_berries_4'),
                    CallbackQueryHandler(add_inscription, pattern='choose_berries_0'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                ],
                'INSCRIPTION_CHOICES': [
                    CallbackQueryHandler(add_berries, pattern='add_berries'),
                    CallbackQueryHandler(get_inscription, pattern='inscription_yes'),
                    CallbackQueryHandler(check_order, pattern='inscription_no'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                ],
                'GET_INSCRIPTION': [
                    CallbackQueryHandler(add_inscription, pattern='add_inscription'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                    MessageHandler(Filters.text & ~Filters.command, check_order),
                ],
                'CHECK_ORDER': [
                    CallbackQueryHandler(add_inscription, pattern='check_order'),
                    CallbackQueryHandler(order, pattern='to_order'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                ],
                'ORDER': [
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                    CallbackQueryHandler(choose_delivery_date, pattern='choose_date')
                ],
                'CHOOSE_CAKE': [
                    CallbackQueryHandler(add_inscription_for_prepared_cakes, pattern=r'select_cake_\d+'),
                    CallbackQueryHandler(make_order, pattern='make_order')
                ],
                'INSCRIPTION_CHOICES_FOR_PREPARED_CAKES':[
                    CallbackQueryHandler(get_inscription_for_prepared_cakes, pattern='inscription_yes'),
                    CallbackQueryHandler(choose_delivery_date, pattern='inscription_no'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                ],
                'GET_INSCRIPTION_FOR_PREPARED_CAKES': [
                    CallbackQueryHandler(add_inscription_for_prepared_cakes, pattern='add_inscription'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                    MessageHandler(Filters.text & ~Filters.command, choose_delivery_date),
                ],
                'GET_DELIVERY_DATE': [
                    CallbackQueryHandler(choose_delivery_time, pattern=r'^date_'),
                    CallbackQueryHandler(start_conversation, pattern='cancel'),
                ],
                'GET_DELIVERY_TIME': [
                    CallbackQueryHandler(ask_for_consent, pattern=r'^time_'),
                    CallbackQueryHandler(start_conversation, pattern='cancel'),
                ],
                'ASK_FOR_CONSENT': [
                    CallbackQueryHandler(get_contact_info, pattern='consent_yes'),
                    CallbackQueryHandler(start_conversation, pattern='consent_no'),
                ],
                'GET_CONTACT_INFO': [
                    MessageHandler(Filters.text & ~Filters.command, get_contact_info),
                ],
                'GET_PHONE_NUMBER': [
                    MessageHandler(Filters.text & ~Filters.command, get_phone_number),
                ],
                'GET_ADDRESS': [
                    MessageHandler(Filters.text & ~Filters.command, get_address),
                ],
                'CALL_SALON': [
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                ],

                'SHOW_PRICES': [
                    CallbackQueryHandler(make_order, pattern='make_order')
                ],

                'COMMON_INFO': [
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                ],
                'SEND_INVOICE': [
                    CallbackQueryHandler(send_invoice, pattern='pay'),
                    CallbackQueryHandler(choose_cake, pattern='cancel'),

                ],



            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )

        dispatcher.add_handler(conv_handler)
        start_handler = CommandHandler('start', start_conversation)
        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(CallbackQueryHandler(start_conversation, pattern='to_start'))
        updater.start_polling()
        updater.idle()