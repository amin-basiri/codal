from django.utils.encoding import force_text
from django.apps import apps
from django.db import IntegrityError
import jdatetime
from dynamic_preferences.registries import global_preferences_registry
from django.utils import timezone
from pathlib import Path
from bs4 import BeautifulSoup

from codal import processor
from codal.models import Letter, Attachment, Task, Report
from codal import signals
from codal.backends import extractor
from codal.exceptions import ReportExtractorException


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


def convert_report_type_name(name):
    name = name.replace('(شامل مقادیر برآوردی)', '')
    name = name.replace('ترازنامه', 'ترازنامه')
    name = name.replace('صورت وضعیت مالی', 'ترازنامه')
    name = name.replace('سود و زیان جامع', 'سود و زیان جامع')
    name = name.replace('سود و زیان', 'سود و زیان')
    name = name.replace('جریان وجوه نقد', 'جریان وجوه نقد')
    name = name.replace('تغییرات در حقوق مالکانه', 'تغییرات در حقوق مالکانه')
    name = name.replace('آمار تولید و فروش اطلاعات', 'آمار تولید و فروش')
    name = name.replace('آمار تولید و فروش صورتهای', 'آمار تولید و فروش')
    name = name.replace('آمار تولید و فروش صورت‌های', 'آمار تولید و فروش')
    name = name.replace('گزارش فعالیت ماهانه دوره', 'گزارش فعالیت ماهانه')
    name = name.replace('گزارش تفسیری - صفحه 1', 'گزارش تفسیری - صفحه 1')
    name = name.replace('گزارش تفسیری - صفحه 2', 'گزارش تفسیری - صفحه 2')
    name = name.replace('گزارش تفسیری - صفحه 3', 'گزارش تفسیری - صفحه 3')
    name = name.replace('گزارش تفسیری - صفحه 4', 'گزارش تفسیری - صفحه 4')
    name = name.replace('گزارش تفسیری - صفحه 5', 'گزارش تفسیری - صفحه 5')
    name = name.replace('نظر حسابرس', 'نظر حسابرس')
    name = name.replace('پورتفوی شرکتهای پذیرفته', 'صورت وضعیت پرتفوی شرکتهای پذیرفته شده در بورس')
    name = name.replace('پرتفوی  شرکتهای پذیرفته', 'صورت وضعیت پرتفوی شرکتهای پذیرفته شده در بورس')
    name = name.replace('صورت ریزمعاملات سهام - واگذار شده ', 'صورت ریز معاملات سهام - واگذارشده')
    name = name.replace('صورت خالص دارایی', 'صورت خالص دارایی ها')
    name = name.replace('گردش خالص دارایی', 'گردش خالص دارایی ها')
    name = name.replace('درآمد حاصل از سرمایه‌گذاری‌ها', 'درآمد حاصل از سرمایه گذاری ها')
    name = name.replace('سود (زیان) ناخالص فعالیت بیمه‌ای (قبل از درآمد سرمایه‌گذاری از محل ذخایر فنی)',
                    'سود (زیان) ناخالص فعالیتهای بیمه ای')
    name = name.replace('صورت ریزمعاملات سهام - تحصیل شده', 'صورت ریز معاملات سهام - تحصیل شده')
    name = name.replace('صورت سرمایه گذاریها به تفکیک گروه صنعت', 'سرمایه گذاری ها به تفکیک گروه صنعت')
    name = name.replace('درآمد سود سهام محقق شده', 'درآمد سود سهام محقق شده')
    name = name.replace('جریان های نقدی', 'جریان وجوه نقد')
    name = name.replace('خالص ارزش هر واحد سرمایه گذاری', 'ارزش خالص هر واحد سرمایه گذاری')
    name = name.replace('آمار تولید و فروش گزارش', 'آمار تولید و فروش')
    name = name.replace('پورتفوی شرکتهای خارج', 'صورت وضعیت پرتفوی شرکتهای خارج از بورس')
    name = name.replace('پرتفوی  شرکتهای خارج', 'صورت وضعیت پرتفوی شرکتهای خارج از بورس')
    name = name.replace('پورتفوی صندوق', 'صورت وضعیت پورتفوی صندوق سرمایه گذاری ')
    name = name.replace('پرتفوی دوره', 'صورت وضعیت پورتفوی صندوق سرمایه گذاری ')
    name = name.replace('تلفیقی دوره', '')
    name = name.replace('تلفیقی سال', '')

    return name


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

        Report.objects.create(
            name=file_name,
            type=report_type,
            letter=letter,
            path=file_full_path.resolve(),
        )

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


def extract_letter_reports(letter):
    for report in letter.reports.all():
        try:
            extractor.extract(report)
        except ReportExtractorException:
            pass


def download(letter,
             download_pdf=False,
             download_content=False,
             download_excel=False,
             download_attachment=False,
             extract_report=False):
    if download_pdf:
        download_pdf_to_letter(letter)
    if download_excel:
        download_excel_to_letter(letter)
    if download_content:
        download_content_to_folder(letter)
    if download_attachment:
        download_attachment_to_letter(letter)
    if extract_report and download_content:
        extract_letter_reports(letter)


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
