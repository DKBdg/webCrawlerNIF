from django import  forms

class CrawlForm(forms.Form):
    link = forms.CharField(label="Link", max_length=250)
    language = forms.CharField(label= ' The following information will be presented in: ', max_length=100)

