from django import forms
from django.conf import settings
from django.core.mail import send_mail

class Contact(forms.Form):
    name = forms.CharField(max_length=64, label='Name')
    email = forms.EmailField(max_length=64, label='Email Address')
    subject = forms.CharField(max_length=64, label='Subject')
    message = forms.CharField(max_length=64, label='Message', widget=forms.Textarea)

    def get_info(self):
        """
        Method that returns formatted email information
        """
        cleaned_data = super().clean()
        name = cleaned_data.get('name').strip()
        from_email = cleaned_data.get('email')
        subject = cleaned_data.get('subject')

        msg = f'{name} ({from_email}) said:'
        msg += f'\nSubject: {subject}\n\n'
        msg += cleaned_data.get('message')

        return subject, msg

    def send(self):
        subject, msg = self.get_info()

        send_mail(
            subject=subject,
            message=msg,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.RECIPIENT_ADDRESS]
        )