from django.shortcuts import render
from .forms import CrawlForm
from newspaper import  Article
from googletrans import  Translator

from .models import CrawledText


def index(request):
    return render(request, 'main/index.html', {})


def about(request):
    return render(request, 'main/about.html', {})

def crawl(request):
    def crawl(url):
        article = Article(url)
        article.download()
        article.parse()
        return article

    def detect(text):
        translator = Translator()
        return translator.detect(text).lang
    def translate(text, lang):
        translator = Translator()
        return translator.translate(text, dest=lang).text


    if request.method == 'POST':
       form = CrawlForm(request.POST)
       if form.is_valid():
            link = form.cleaned_data['link']
            language = form.cleaned_data['language']
            article = crawl(url=link)
            crawled_text_obj = CrawledText(url=link, original_text=article.text, original_title= article.title)
            if detect(article.text) == language:
               crawled_text_obj.is_translated = False
            else:
                crawled_text_obj.is_translated=True
                crawled_text_obj.translated_text = translate(article.text, language)
                crawled_text_obj.translated_title = translate(article.title, language)

                crawled_text_obj.save()
    else:
        form = CrawlForm()

    return render(request, 'main/crawl.html', {'form': form})

