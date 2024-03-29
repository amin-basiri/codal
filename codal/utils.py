from django.utils.encoding import force_text
from django.apps import apps
from django.db import IntegrityError
import jdatetime
from dynamic_preferences.registries import global_preferences_registry
from django.utils import timezone
from pathlib import Path
from bs4 import BeautifulSoup

from codal import processor
from codal.models import Letter, Attachment, Task
from codal import signals


def serialize_instance(instance):
    """ Serialize Django model instance """
    model_name = force_text(instance._meta)
    return '{}:{}'.format(model_name, instance.pk)


def deserialize_instance(serialized_instance):
    """ Deserialize Django model instance """
    model_name, pk = serialized_instance.split(':')
    model = apps.get_model(model_name)
    return model._default_manager.get(pk=pk)


def persian_string_datetime_to_datetime(persian_datetime):
    try:
        date, time = persian_datetime.split()
        year, month, day = [int(n) for n in date.split('/')]
        hour, minute, second = [int(n) for n in time.split(':')]
        jd = jdatetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
        return jd.togregorian()
    except:
        now = timezone.now()
        return jdatetime.datetime.fromgregorian(year=now.year, month=now.month, day=now.day)


def update():
    global_preferences = global_preferences_registry.manager()
    update_from_date = global_preferences['update_from_date']

    max_page = processor.get_max_page(update_from_date=update_from_date)
    page = 1

    while page <= max_page:
        letters = processor.get_letters(page, update_from_date=update_from_date)
        for letter in letters:
            attachments = processor.get_letter_attachments(letter)
            try:
                _letter = Letter.objects.create(
                    attachment_url=letter['AttachmentUrl'],
                    company_name=letter['CompanyName'],
                    excel_url=letter['ExcelUrl'],
                    has_attachment=letter['HasAttachment'],
                    has_excel=letter['HasExcel'],
                    has_html=letter['HasHtml'],
                    has_pdf=letter['HasPdf'],
                    has_xbrl=letter['HasXbrl'],
                    is_estimate=letter['IsEstimate'],
                    code=letter['LetterCode'],
                    pdf_url=letter['PdfUrl'],
                    publish_datetime=persian_string_datetime_to_datetime(letter['PublishDateTime']),
                    sent_datetime=persian_string_datetime_to_datetime(letter['SentDateTime']),
                    symbol=letter['Symbol'],
                    title=letter['Title'],
                    tracing_no=letter['TracingNo'],
                    under_supervision=letter['UnderSupervision'],
                    url=letter['Url'],
                    xbrl_url=letter['XbrlUrl']
                )

                for attachment in attachments:
                    Attachment.objects.create(
                        url=attachment.get('url'),
                        letter=_letter,
                        name=attachment.get('name')
                    )
            except IntegrityError as e:
                continue

        page += 1


def jalali_datetime_to_structured_string(jd):
    year = str(jd.year)
    month = str(jd.month) if jd.month >= 10 else "0{}".format(jd.month)
    day = str(jd.day) if jd.day >= 10 else "0{}".format(jd.day)

    return "{}/{}/{}".format(year, month, day)


def get_excel_pdf_file_name(letter):
    name = letter.symbol + ' ' + letter.title
    name = name.replace('/', '-')
    return name


def process_folder_name(name):
    global_preferences = global_preferences_registry.manager()
    if global_preferences['replace_arabic_word_folder']:
        name = replace_arabic_word(name)
    if global_preferences['replace_arabic_number_folder']:
        name = replace_arabic_number(name)

    name = name.replace('/', '-')

    return name


def save_pdf_file(letter, content):
    global_preferences = global_preferences_registry.manager()
    folder_name = process_folder_name(letter.symbol)
    download_pdf_path = global_preferences['download_pdf_path']
    folder_path = "{path}/{folder}/".format(
        path=download_pdf_path,
        folder=folder_name)

    pdf_path = Path(folder_path)
    pdf_path.mkdir(parents=True, exist_ok=True)

    file_name = get_excel_pdf_file_name(letter)
    file_path = '{file}.pdf'.format(file=file_name)
    file_full_path = pdf_path / file_path

    with file_full_path.open("wb") as f:
        f.write(content)
        f.close()

    return file_full_path.resolve().__str__()


def save_excel_file(letter, content):
    global_preferences = global_preferences_registry.manager()
    folder_name = process_folder_name(letter.symbol)
    download_excel_path = global_preferences['download_excel_path']
    folder_path = "{path}/{folder}/".format(
        path=download_excel_path,
        folder=folder_name)

    excel_path = Path(folder_path)
    excel_path.mkdir(parents=True, exist_ok=True)

    file_name = get_excel_pdf_file_name(letter)
    file_path = '{file}.xls'.format(file=file_name)
    file_full_path = excel_path / file_path

    with file_full_path.open("wb") as f:
        f.write(content)
        f.close()

    return file_full_path.resolve().__str__()


def download_pdf_to_letter(letter):
    if letter.pdf_path:
        return

    downloaded_file = processor.download(letter.pdf_url)

    letter.pdf_path = save_pdf_file(letter, downloaded_file)
    letter.save(update_fields=['pdf_path'])


def download_excel_to_letter(letter):
    if letter.excel_path:
        return

    downloaded_file = processor.download(letter.excel_url)

    letter.excel_path = save_excel_file(letter, downloaded_file)
    letter.save(update_fields=['excel_path'])


def replace_arabic_word(text):
    text = text.replace('ي', 'ی')
    text = text.replace('ك', 'ک')
    return text


def replace_arabic_number(text):
    text = text.replace('۰', '0')
    text = text.replace('۱', '1')
    text = text.replace('۲', '2')
    text = text.replace('۳', '3')
    text = text.replace('۴', '4')
    text = text.replace('۵', '5')
    text = text.replace('۶', '6')
    text = text.replace('۷', '7')
    text = text.replace('۸', '8')
    text = text.replace('۹', '9')
    return text


def process_content(content):
    global_preferences = global_preferences_registry.manager()
    if global_preferences['replace_arabic_word_content']:
        content = replace_arabic_word(content)
    if global_preferences['replace_arabic_number_content']:
        content = replace_arabic_number(content)
    return content


def process_file_name(name, symbol, report_type=""):
    global_preferences = global_preferences_registry.manager()
    remove_text = global_preferences['remove_name_word'].split('*')

    for text in remove_text:
        name = name.replace(text, "")

    name = name.replace('/', '-')

    name = symbol + ' ' + report_type + ' ' + name if report_type else symbol + ' ' + name

    return name


def download_content_to_folder(letter):
    global_preferences = global_preferences_registry.manager()

    content_page = processor.download(letter.url, javascript=True)
    folder_name = process_folder_name(letter.symbol)

    soup = BeautifulSoup(content_page.text, 'html.parser')
    options = soup.select('#ddlTable option')

    download_content_path = global_preferences['download_content_path']
    folder_path = "{path}/{folder}/".format(
        path=download_content_path,
        folder=folder_name)
    content_path = Path(folder_path)
    content_path.mkdir(parents=True, exist_ok=True)

    for o in options:
        response = processor.download(letter.url + '&sheetId={}'.format(o['value']), javascript=True)
        report_type = o.text[0:o.text.find('\n')-1]
        file_name = process_file_name(letter.title, letter.symbol, report_type=report_type)
        file_path = '{file}.html'.format(file=file_name)
        file_full_path = content_path / file_path

        try:
            f = file_full_path.open("w", encoding='utf-8')
        except OSError as exc:
            if exc.errno == 36:
                file_name = process_file_name("", letter.symbol, report_type=report_type)
                file_path = '{file}.html'.format(file=file_name)
                file_full_path = content_path / file_path
                f = file_full_path.open("w", encoding='utf-8')
            else:
                raise exc
        response.html.render(timeout=20)
        proceed_content = process_content(response.html.html)
        f.write(proceed_content)
        f.close()

    if not options:
        file_name = process_file_name(letter.title, letter.symbol)
        file_path = '{file}.html'.format(file=file_name)
        file_full_path = content_path / file_path

        try:
            f = file_full_path.open("w", encoding='utf-8')
        except OSError as exc:
            if exc.errno == 36:
                file_name = process_file_name("", letter.symbol)
                file_path = '{file}.html'.format(file=file_name)
                file_full_path = content_path / file_path
                f = file_full_path.open("w", encoding='utf-8')
            else:
                raise exc
        content_page.html.render(timeout=20)
        proceed_content = process_content(content_page.html.html)
        f.write(proceed_content)
        f.close()


def get_attachment_file_name(letter, attachment_file_name, attachment, has_title=True):
    attachment_exp = attachment_file_name[attachment_file_name.rfind('.'):]

    name = letter.symbol + ' ' + letter.title + ' ' + attachment.name + attachment_exp if has_title \
            else letter.symbol + ' ' + attachment.name + attachment_exp
    name = name.replace('/', '-')
    name = name.replace(u'\uf022', '')
    name = name.replace(u'\xa0', '')
    name = name.replace('"', '')
    return name


def save_attachment_file(letter, content, attachment, attachment_file_name):
    global_preferences = global_preferences_registry.manager()
    folder_name = process_folder_name(letter.symbol)
    download_attachment_path = global_preferences['download_attachment_path']
    folder_path = "{path}/{folder}/".format(
        path=download_attachment_path,
        folder=folder_name)

    attachment_path = Path(folder_path)
    attachment_path.mkdir(parents=True, exist_ok=True)

    file_path = get_attachment_file_name(letter, attachment_file_name, attachment)
    file_full_path = attachment_path / file_path

    try:
        f = file_full_path.open("wb")
    except OSError as exc:
        if exc.errno == 36:
            file_path = get_attachment_file_name(letter, attachment_file_name, attachment, has_title=False)
            file_full_path = attachment_path / file_path
            f = file_full_path.open("wb")
        else:
            raise exc

    f.write(content)
    f.close()

    return file_full_path.resolve().__str__()


def download_attachment_to_letter(letter):
    for attachment in letter.attachments.filter(status=Attachment.Statuses.RETRIEVED):
        attachment.set_downloading()

        attachment_name_content = processor.download(attachment.url, return_attachment_filename=True)

        attachment.path = save_attachment_file(letter,
                                               attachment_name_content[1],
                                               attachment,
                                               attachment_name_content[0])
        attachment.save(update_fields=['path'])

        attachment.set_downloaded()


def download(letter,
             download_pdf=False,
             download_content=False,
             download_excel=False,
             download_attachment=False):
    if download_pdf:
        download_pdf_to_letter(letter)
    if download_excel:
        download_excel_to_letter(letter)
    if download_content:
        download_content_to_folder(letter)
    if download_attachment:
        download_attachment_to_letter(letter)


def handle_task_complete(error, task_type):
    current_task = Task.objects.get(status=Task.Statuses.RUNNING,
                                    task_type=task_type, )

    if error:
        current_task.set_erred(error)
    else:
        current_task.set_done()

    signals.task_done.send(
        sender=Task,
        task=current_task
    )
