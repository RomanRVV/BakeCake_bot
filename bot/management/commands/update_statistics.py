from django.test import TestCase
from bot.models import *
import requests
import argparse
from urllib.parse import urlparse
from BakeCake import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Обновляет статистику по кликам'
    
    def handle(self, *args, **kwargs):
        def count_clicks(token, link):
            bitlink_parse = urlparse(link)
            bitlink = bitlink_parse._replace(scheme='').geturl()
            url = f'https://api-ssl.bitly.com/v4/bitlinks/{bitlink}/clicks/summary'
            headers = {
                "Authorization": f"Bearer {token}"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            clicks_count = response.json()['total_clicks']
            return clicks_count

        bitly_token = settings.bitly_token

        while True:
            links = LinkStatistics.objects.all()
            for link in links:
                clicks_count = count_clicks(bitly_token, link.bitlink)
                link.transitions = clicks_count
                link.save()
