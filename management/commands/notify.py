# coding: utf8
from django.core.management.base import BaseCommand
from modules.telebot.bot import bot_handler


class Command(BaseCommand):
    help = 'Send news to telegram channel'

    def handle(self, *args, **options):
        bot_handler()
