from django.shortcuts import render
from .forms import CrawlForm
from newspaper import  Article

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


    if request.method == 'POST':
       form = CrawlForm(request.POST)
       if form.is_valid():
           link = form.cleaned_data['link']
           article = crawl(url=link)
           crawled_text_obj= CrawledText(url=link, original_title=article.title, original_text=article.text)
           crawled_text_obj.save()
    else:
        form = CrawlForm()

    return render(request, 'main/crawl.html', {'form': form})
