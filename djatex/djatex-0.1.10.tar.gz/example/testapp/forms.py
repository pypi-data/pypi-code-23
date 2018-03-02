from django import forms

class ArticleForm(forms.Form):
    author = forms.CharField(label='Author', min_length=1, max_length=100)
    title = forms.CharField(label='Title', min_length=1, max_length=100)
    
