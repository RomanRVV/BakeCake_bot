import datetime
import sqlite3
from django.core.management.base import BaseCommand
from django.db.models import Q, Count
from BakeCake import settings
from bot.models import Cake
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
)
# from phonenumbers import is_valid_number, parse


class Command(BaseCommand):
    help = 'Телеграм-бот'

    def __init__(self):
        # self.conn = sqlite3.connect('db.sqlite3')
        self.conn = sqlite3.connect('db.sqlite3', check_same_thread=False)
        self.cur = self.conn.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS cake(
                            prise INTEGER,
                            level INTEGER,
                            base TEXT,
                            topping TEXT
                            );
                        """)
        self.conn.commit()


    def handle(self, *args, **kwargs):
        # tg_token = settings.TOKEN
        tg_token = settings.tg_token
        updater = Updater(token=tg_token, use_context=True)
        dispatcher = updater.dispatcher

        def start_conversation(update, context):
            query = update.callback_query

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
                [
                    InlineKeyboardButton("Количество уровней", callback_data="choose_level_cake"),
                ],
                [
                    InlineKeyboardButton("На главную", callback_data="to_start"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.answer()
            text = 'Добавим конструктор'
            query.edit_message_text(
                text=text,
                reply_markup=reply_markup
            )
            return 'MAKE_CAKE'
        

        def choose_level_cake(update, _):
            query = update.callback_query
            keyboard = [
                [
                    InlineKeyboardButton("1 уровень", callback_data="choose_base_cake_1"),
                    InlineKeyboardButton("2 уровень +200р", callback_data="choose_base_cake"),
                    InlineKeyboardButton("3 уровень +200р", callback_data="choose_base_cake"),
                ],
                [
                    InlineKeyboardButton("Назад", callback_data="make_cake"),
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

        def choose_base_cake_1(update, _):
            query = update.callback_query
            keyboard = [
                [
                    InlineKeyboardButton("Ванильный бисквит", callback_data="choose_topping_cake"),
                ],
                [
                    InlineKeyboardButton("Шоколадный бисквит", callback_data="choose_topping_cake"),
                ],
                [
                    InlineKeyboardButton("Мраморный бисквит", callback_data="choose_topping_cake"),
                ],
                [
                    InlineKeyboardButton("Назад", callback_data="choose_level_cake"),
                    InlineKeyboardButton("На главную", callback_data="to_start"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.answer()
            level_1 = 1
            prise_level_1 = 200
            check_order(level_1)
            text = 'Выбор основы'
            query.edit_message_text(
                text=text,
                reply_markup=reply_markup
            )
            return 'CAKE_BASE_CHOICES'
        

        def choose_base_cake(update, _):
            query = update.callback_query
            keyboard = [
                [
                    InlineKeyboardButton("Ванильный бисквит", callback_data="choose_topping_cake"),
                ],
                [
                    InlineKeyboardButton("Шоколадный бисквит", callback_data="choose_topping_cake"),
                ],
                [
                    InlineKeyboardButton("Мраморный бисквит", callback_data="choose_topping_cake"),
                ],
                [
                    InlineKeyboardButton("Назад", callback_data="choose_level_cake"),
                    InlineKeyboardButton("На главную", callback_data="to_start"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.answer()
            text = 'Выбор основы'
            query.edit_message_text(
                text=text,
                reply_markup=reply_markup
            )
            return 'CAKE_BASE_CHOICES'
        
            
        def choose_topping(update, _):
            query = update.callback_query
            keyboard = [
                [
                    InlineKeyboardButton("Клиновый сироп +100р", callback_data="check_order"),
                ],
                [
                    InlineKeyboardButton("Карамельный сироп +100р", callback_data="check_order"),
                ],
                [
                    InlineKeyboardButton("Без топпинга", callback_data="check_order"),
                ],
                [
                    InlineKeyboardButton("Назад", callback_data="choose_base_cake"),
                    InlineKeyboardButton("На главную", callback_data="to_start"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.answer()
            text = 'Выбор топпинга'
            query.edit_message_text(
                text=text,
                reply_markup=reply_markup
            )
            
            return 'TOPPING_CHOICES'
        
        def check_order(update, _):
            query = update.callback_query
            keyboard = [
                [
                    InlineKeyboardButton("Проверить", callback_data="check_order"),
                ],
                [
                    InlineKeyboardButton("Назад", callback_data="choose_topping"),
                    InlineKeyboardButton("На главную", callback_data="to_start"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.answer()
            text = 'Проверьте заказ'
            query.edit_message_text(
                text=text,
                reply_markup=reply_markup
            )
            # self.cur.execute("INSERT INTO cake VALUES (?);", level)
            # self.conn.commit()
            # print(query.message.reply_markup)
            return 'CHECK_ORDER'
            

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


                keyboard = [[InlineKeyboardButton("Выбрать", callback_data=f"select_cake_{cake.id}")]]

                reply_markup = InlineKeyboardMarkup(keyboard)

                context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="Выберите торт:",
                    reply_markup=reply_markup
                )

            return 'CHOOSE_CAKE'

        def get_contact_info(update, context):
            user_phone = update.message.text
            selected_cake = context.user_data.get('selected_cake')

            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=f"Спасибо за ваш заказ!\n"
                     f"Вы выбрали торт {selected_cake.name}.\n"
                     f"Мы свяжемся с вами по номеру телефона: {user_phone}",
            )

            return 'END'

        def select_cake(update, context):
            query = update.callback_query
            cake_id = int(query.data.split('_')[2])

            selected_cake = Cake.objects.get(id=cake_id)

            context.user_data['selected_cake'] = selected_cake

            context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"Вы выбрали торт {selected_cake.name}. Чтобы оформить заказ, пожалуйста, укажите свой номер телефона.",
            )

            contact_handler = MessageHandler(Filters.text & ~Filters.command, get_contact_info)
            context.dispatcher.add_handler(contact_handler)

            return 'GET_CONTACT_INFO'

        def show_prices(update, _):
            query = update.callback_query
            keyboard = [
                [InlineKeyboardButton("Назад", callback_data="make_order")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.answer()
            text = 'Цены на наши торты '
            query.edit_message_text(
                text=text,
                reply_markup=reply_markup
            )
            return 'SHOW_PRICES'

        def show_orders(update, context):
            query = update.callback_query
            keyboard = [
                [
                    InlineKeyboardButton("На главный", callback_data="to_start"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.answer()
            text = 'Последнине записи: \n'
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
                'LEVEL_CAKE': [
                    CallbackQueryHandler(choose_base_cake, pattern='choose_base_cake'),
                    CallbackQueryHandler(choose_base_cake_1, pattern='choose_base_cake_1'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                ],
                'CAKE_BASE_CHOICES':[
                    CallbackQueryHandler(choose_level_cake, pattern='choose_level_cake'),
                    CallbackQueryHandler(choose_topping, pattern='choose_topping'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                ],
                'TOPPING_CHOICES':[
                    CallbackQueryHandler(choose_base_cake, pattern='choose_base_cake'),
                    CallbackQueryHandler(choose_base_cake_1, pattern='choose_base_cake_1'),
                    CallbackQueryHandler(check_order, pattern='check_order'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                ],
                'CHECK_ORDER':[
                    CallbackQueryHandler(choose_topping, pattern='choose_topping'),
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                ],
                'CHOOSE_CAKE': [
                    CallbackQueryHandler(select_cake, pattern=r'select_cake_\d+'),
                ],
                'MAKE_CAKE': [
                    CallbackQueryHandler(start_conversation, pattern='to_start'),
                    CallbackQueryHandler(choose_level_cake, pattern='choose_level_cake'),
                    CallbackQueryHandler(choose_topping, pattern='choose_topping_cake'),
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


            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )

        dispatcher.add_handler(conv_handler)
        start_handler = CommandHandler('start', start_conversation)
        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(CallbackQueryHandler(start_conversation, pattern='to_start'))
        updater.start_polling()
        updater.idle()
