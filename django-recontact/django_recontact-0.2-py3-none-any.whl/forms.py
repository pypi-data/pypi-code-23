from django.forms import Form, CharField, EmailField, Textarea, TextInput, EmailInput

class RecontactForm(Form):
    """
    Django form which collects data for a contact email message.
    """
    sender = CharField(label='', widget=TextInput(
        attrs={'placeholder': 'Your Name',
               'class': 'recontact'}))
    reply_to=EmailField(label='', widget=EmailInput(
        attrs={'placeholder': 'Your email address',
               'class': 'recontact'}))
    subject = CharField(label='', widget=TextInput(
        attrs={'placeholder': 'Subject',
               'class': 'recontact'}))
    message = CharField(label='', widget=Textarea(
        attrs={'placeholder': 'Message',
               'class': 'recontact'}))
