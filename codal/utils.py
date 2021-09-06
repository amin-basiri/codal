from django.utils.encoding import force_text
from django.apps import apps
from django.db import IntegrityError
import jdatetime
from django.core.files.uploadedfile import SimpleUploadedFile
from dynamic_preferences.registries import global_preferences_registry

from codal import processor
from codal.models import Letter


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
        return jdatetime.datetime.now().togregorian()


def update():

    max_page = processor.get_max_page()
    page = 1

    while page <= max_page:
        letters = processor.get_letters(page)
        for letter in letters:
            try:
                Letter.objects.create(
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
            except IntegrityError as e:
                continue

        page += 1


def jalali_datetime_to_structured_string(jd):
    year = str(jd.year)
    month = str(jd.month) if jd.month >= 10 else "0{}".format(jd.month)
    day = str(jd.day) if jd.day >= 10 else "0{}".format(jd.day)

    return "{}/{}/{}".format(year, month, day)


def download_pdf_to_letter(letter):
    letter.pdf = SimpleUploadedFile("{}-{}.pdf".format(letter.symbol, letter.code),
                                    processor.download(letter.pdf_url),
                                    content_type="application/pdf")
    letter.save()


def download_excel_to_letter(letter):
    letter.excel = SimpleUploadedFile("{}-{}.xls".format(letter.symbol, letter.code),
                                    processor.download(letter.excel_url),
                                    content_type="application/vnd.ms-excel")
    letter.save()


def process_content(content):
    pass
    # TODO Process Content Of Letter


def process_folder_name(name):
    pass
    # TODO Process Folder Name


def process_file_name(name):
    pass
    # TODO Process File Name


def download_content_to_folder(letter):
    global_preferences = global_preferences_registry.manager()

    content = process_content(processor.download(letter.url, return_text=True))
    folder_name = process_folder_name(letter.symbol)
    file_name = process_file_name(letter.title)

    with open('{}/{}/{}.html'.format(global_preferences['download_content_path'],
                                     folder_name,
                                     file_name)) as f:
        f.write(content)
        f.close()


def download_attachment_to_letter(letter):
    pass
    # TODO Download Attachments Of Letter


def download(letter, download_pdf=False, download_content=False, download_excel=False, download_attachment=False):
    if download_pdf:
        download_pdf_to_letter(letter)
    if download_excel:
        download_excel_to_letter(letter)
    if download_content:
        download_content_to_folder(letter)
    if download_attachment:
        download_attachment_to_letter(letter)