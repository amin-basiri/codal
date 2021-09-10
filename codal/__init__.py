from __future__ import absolute_import

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app
from django.utils.functional import cached_property
from dynamic_preferences.registries import global_preferences_registry
import time
import requests
import re
from bs4 import BeautifulSoup


class Processor:

    def __init__(self):
        self.DOWNLOAD_TASK_ID = None
        self.UPDATE_TASK_ID = None
        self._session = requests.session()
        self.max_request_retry = 5
        self.retry_interval = 5
        self.verify_ssl = False
        self.search_url = 'https://search.codal.ir/api/search/v2/q?PageNumber={page_number}&FromDate={from_date}'
        self.base_url = 'https://codal.ir/'
        self.attachment_url = 'https://codal.ir/Reports/'

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

    def _search(self, page_number=1):
        global_preferences = global_preferences_registry.manager()
        return self.get(self.search_url.format(
                    page_number=page_number,
                    from_date=global_preferences['update_from_date'])).json()

    def download(self, url, return_text=False, return_attachment_filename=False):
        retry = 1

        while retry <= self.max_request_retry:
            try:
                response = self.session.get(self.base_url + url)
            except requests.exceptions.RequestException as e:
                if retry < self.max_request_retry:
                    time.sleep(self.retry_interval)
                    retry += 1
                else:
                    raise e

            if return_text:
                return response.text
            elif return_attachment_filename:
                file_name = re.findall("filename=(.+)", response.headers['content-disposition'])[0]
                return file_name.encode('iso8859-1').decode('utf-8'), response.content
            return response.content

    def get_max_page(self,):
        return self._search()['Page']

    def get_letters(self, page_number):
        return self._search(page_number=page_number)['Letters']

    def get_letter_attachments_url(self, letter):
        if letter['HasAttachment']:
            urls = []
            attachment_page = self.get(self.attachment_url + letter['AttachmentUrl']).text
            soup = BeautifulSoup(attachment_page, 'html.parser')
            for tr in soup.select("table table table tr[onclick]"):
                action = tr['onclick']
                urls.append(action[13:action.find("')")])
            return urls
        else:
            return []


processor = Processor()
