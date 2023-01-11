from django import  forms

class CrawlForm(forms.Form):
    link = forms.CharField(label="Link", max_length=250)

