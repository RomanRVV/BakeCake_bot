import datetime
from telegram import Update
from django.core.management.base import BaseCommand
from django.db.models import Q, Count
from BakeCake import settings
from bot.models import Cake, CakeOrder
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    ParseMode,
    LabeledPrice
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
                text=f"Описание компании", reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
            return 'GREETINGS'

        def make_order(update, _):
            query = update.callback_query
            keyboard = [
                [
                    InlineKeyboardButton("Скронстуировать самому", callback_data="make_cake"),
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

        def make_cake(update, _):
            query = update.callback_query
            keyboard = [
                [InlineKeyboardButton("На главную", callback_data="to_start"),],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.answer()
            text = 'Добавим конструктор'
            query.edit_message_text(
                text=text,
                reply_markup=reply_markup
            )
            return 'MAKE_CAKE'

        def choose_cake(update, context):
            query = update.callback_query
            cakes = Cake.objects.all()

            for cake in cakes:
                message = f"<b>{cake.name}</b>\n"
                message += f"{cake.description}\n"
                message += f"Цена: ${cake.price}\n"

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
            buttons.append([InlineKeyboardButton("Отмена", callback_data="cancel")])

            reply_markup = InlineKeyboardMarkup(buttons)

            query.message.reply_text(
                text="Выберите торт для заказа:",
                reply_markup=reply_markup
            )

            return 'CHOOSE_CAKE'

        def choose_delivery_date(update, context):
            query = update.callback_query
            query.answer()
            cake_id = update.callback_query.data.split('_')[-1]
            selected_cake = Cake.objects.get(id=cake_id)

            context.user_data['selected_cake'] = selected_cake
            delivery_date = update.callback_query.data.split('_')[1]

            context.user_data['delivery_date'] = delivery_date
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

            reply_markup = InlineKeyboardMarkup(buttons)

            query.edit_message_text(
                text="Выберите дату доставки:",
                reply_markup=reply_markup
            )
            return 'GET_DELIVERY_DATE'

        def choose_delivery_time(update, context):
            query = update.callback_query
            query.answer()
            delivery_date = update.callback_query.data.split('_')[1]
            context.user_data['delivery_date'] = delivery_date
            hours = ["10:00", "12:00", "14:00", "16:00", "18:00"]

            buttons = []
            for hour in hours:
                buttons.append([InlineKeyboardButton(hour, callback_data=f"time_{hour}")])

            buttons.append([InlineKeyboardButton("Отмена", callback_data="cancel")])

            reply_markup = InlineKeyboardMarkup(buttons)

            query.edit_message_text(
                text="Выберите время доставки:",
                reply_markup=reply_markup
            )

            return 'GET_DELIVERY_TIME'

        def get_contact_info(update, context):
            query = update.callback_query
            delivery_time = update.callback_query.data.split('_')[1]

            context.user_data['delivery_time'] = delivery_time
            selected_cake = context.user_data.get('selected_cake')
            user_first_name = update.effective_user.first_name
            context.user_data['username'] = user_first_name
            user_id = update.effective_user.id
            context.user_data['user_id'] = user_id
            query.edit_message_text(
                text=f"Привет, {user_first_name}! Вы выбрали торт {selected_cake.name}.\n"
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

            order = CakeOrder.objects.create(
                user_id=context.user_data['user_id'],
                user_name=context.user_data['username'],
                user_phone=phone,
                delivery_date=delivery_date,
                delivery_time=delivery_time,
                delivery_address=address,
                cake=selected_cake,
            )

            buttons = [
                [InlineKeyboardButton('Оплатить онлайн', callback_data='pay')],
                [InlineKeyboardButton('Отмена', callback_data='cancel')],
            ]
            reply_markup = InlineKeyboardMarkup(buttons)

            update.message.reply_text(
                f"Спасибо за ваш заказ!\n"
                f"Вы выбрали торт {selected_cake.name}.\n"
                f"Цена {selected_cake.price}\n"
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
            text = 'Цены на наши торты:\n'
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
                    text += f"Торт: {order.cake.name}\n"
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
                    CallbackQueryHandler(make_cake, pattern='make_cake'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),

                ],
                'CHOOSE_CAKE': [
                    CallbackQueryHandler(choose_delivery_date, pattern=r'select_cake_\d+'),
                ],
                'GET_DELIVERY_DATE': [
                    CallbackQueryHandler(choose_delivery_time, pattern=r'^date_'),
                    CallbackQueryHandler(choose_cake, pattern='cancel'),
                ],
                'GET_DELIVERY_TIME': [
                    CallbackQueryHandler(get_contact_info, pattern=r'^time_'),
                    CallbackQueryHandler(choose_cake, pattern='cancel'),
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
                'MAKE_CAKE': [
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
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
