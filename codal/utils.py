from django.utils.encoding import force_text
from django.apps import apps
from django.db import IntegrityError
from codal import processor
from codal.models import Letter
import jdatetime


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
