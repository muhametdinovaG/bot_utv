# -*- coding: utf-8 -*-

import logging
import telebot
import time

from django.conf import settings
from django.utils import timezone as tz

from modules.content.models import Material
from modules.twitter.twitter import send_post

URL = 'https://api.telegram.org/bot' + settings.TELEGRAM_TOKEN + '/'

LOGGER = logging.getLogger(__name__)


def bot_handler():
    """
    Формирование и отправка сообщения в телеграм канал
    :return:
    """
    date_before = tz.now() - tz.timedelta(hours=1)
    bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)
    if settings.PROXY_HOST != '':
        telebot.apihelper.proxy = {
            'http': 'socks5://{}:{}@{}:{}'.format(settings.PROXY_USER, settings.PROXY_PASS, settings.PROXY_HOST,
                                                  settings.PROXY_PORT),
            'https': 'socks5://{}:{}@{}:{}'.format(settings.PROXY_USER, settings.PROXY_PASS, settings.PROXY_HOST,
                                                   settings.PROXY_PORT)
        }
    while True:
        material = Material.objects.published()\
            .actual()\
            .filter(cities__alias='ufa', sections__alias='novosti', notify=False, actual_date__gte=date_before)\
            .order_by('-actual_date').first()
        if material is not None:
            try:
                alias = settings.BASE_HOST + material.get_absolute_url()

                markup = telebot.types.InlineKeyboardMarkup()
                my_btn = telebot.types.InlineKeyboardButton(text='Читать новость', url=alias)

                markup.add(my_btn)
                message = "{}.\n{}".format(material.name, material.description)

                if len(message) <= 200:
                    bot.send_chat_action(settings.CHANNEL_ID, 'upload_photo')
                    bot.send_photo(settings.CHANNEL_ID, material.screen, caption=message, reply_to_message_id=None, reply_markup=markup)

                material.notify = True
                material.save()

            except Exception as e:
                LOGGER.error("Telegram error: {0}".format(e))

            try:
                if material.notify_twitter != True:
                    send_post(material)
                    material.notify_twitter = True
                    material.save()
            except:
                LOGGER.error("Twitter error: {0}".format(e))

        time.sleep(settings.SLEEP_TIME)