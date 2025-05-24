from django import forms
from django.core.mail.message import EmailMessage
from .models import Contato


class ContatoForm(forms.Form):
    nome = forms.CharField(label='Nome', max_length=100)
    email = forms.EmailField(label='E-mail', max_length=100)
    whatsapp = forms.CharField(label='WhatsApp', max_length=15)
    assunto = forms.CharField(label='Assunto', max_length=100)
    mensagem = forms.CharField(label='Mensagem', widget=forms.Textarea())

    def send_mail(self):
        nome = self.cleaned_data['nome']
        email = self.cleaned_data['email']
        whatsapp = self.cleaned_data['whatsapp']
        assunto = self.cleaned_data['assunto']
        mensagem = self.cleaned_data['mensagem']

        conteudo = f'Nome: {nome}\nE-mail: {email}\nWhatsApp: {whatsapp}\nAssunto: {assunto}\nMensagem: {mensagem}'

        Contato.objects.create(nome=nome, email=email, whatsapp=whatsapp)

        mail = EmailMessage(
            subject=assunto,
            body=conteudo,
            from_email='almazadelivery@gmail.com',
            to=['almazadelivery@gmail.com', ],
            headers={'Reply-To': email},
        )
        mail.send()


