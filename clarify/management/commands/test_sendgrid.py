from django.conf import settings
from django.core.management.base import BaseCommand
import sendgrid
from sendgrid.helpers.mail import *


class Command(BaseCommand):
    help = "Test SendGrid."

    def handle(self, *args, **options):
        sg = sendgrid.SendGridAPIClient(
            apikey=settings.SENDGRID_API_KEY)
        from_email = Email("test@example.com")
        to_email = Email("adnan@clarify.school")
        subject = "Sending with SendGrid is Fun"
        content = Content("text/plain",
                          "and easy to do anywhere, even with Python")
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        print(response.status_code)
        print(response.body)
        print(response.headers)
