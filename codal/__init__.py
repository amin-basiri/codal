from django.utils.functional import cached_property
from requests_html import HTMLSession
import time
import requests
import re
from bs4 import BeautifulSoup
import logging

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

__all__ = ('celery_app',)


class Processor:

    def __init__(self):
        self._session = requests.session()
        self._js_session = HTMLSession()
        self.max_request_retry = 5
        self.retry_interval = 5
        self.verify_ssl = False
        self.search_url = 'https://search.codal.ir/api/search/v2/q?PageNumber={page_number}&FromDate={from_date}'
        self.base_url = 'https://codal.ir/'
        self.attachment_url = 'https://codal.ir'
        self.download_attachment_prefix = 'Reports/'

    @cached_property
    def js_session(self):
        return self._js_session

    @cached_property
    def session(self):
        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
        })
        return self._session

    def get(self, url):
        retry = 1

        while retry <= self.max_request_retry:
            try:
                return self.session.get(url, verify=self.verify_ssl)
            except requests.exceptions.RequestException as e:
                if retry < self.max_request_retry:
                    time.sleep(self.retry_interval)
                    retry += 1
                else:
                    raise e

    def _search(self, page_number=1, update_from_date=""):
        return self.get(self.search_url.format(
                    page_number=page_number,
                    from_date=update_from_date)).json()

    def download(self, url, return_text=False, return_attachment_filename=False, javascript=False):
        retry = 1

        while retry <= self.max_request_retry:
            try:
                if javascript:
                    response = self.js_session.get(self.base_url + url, verify=self.verify_ssl)
                    return response
                else:
                    response = self.session.get(self.base_url + url)

                if return_text:
                    return response.text
                elif return_attachment_filename:
                    file_name = re.findall("filename=(.+)", response.headers.get('content-disposition', ""))[0]
                    return file_name.encode('iso8859-1').decode('utf-8'), response.content
                return response.content

            except requests.exceptions.RequestException as e:
                if retry < self.max_request_retry:
                    time.sleep(self.retry_interval)
                    retry += 1
                else:
                    raise e

    def get_max_page(self, update_from_date=""):
        return self._search(update_from_date=update_from_date)['Page']

    def get_letters(self, page_number, update_from_date):
        return self._search(page_number=page_number, update_from_date=update_from_date)['Letters']

    def get_letter_attachments(self, letter):
        if letter['HasAttachment']:
            attachments = []
            attachment_page = self.get(self.attachment_url + letter['AttachmentUrl']).text
            soup = BeautifulSoup(attachment_page, 'html.parser')
            for tr in soup.select("table table table tr[onclick]"):
                action = tr['onclick']
                attachments.append({
                    'url': self.download_attachment_prefix + action[13:action.find("')")],
                    'name': tr.select('td')[1].text,
                })
            return attachments
        else:
            return []


processor = Processor()

logging.basicConfig(filename="Logs.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
