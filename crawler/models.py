from django.db import models
from django.urls import reverse

class SearchedLink(models.Model):
    url=models.CharField(default='s',max_length=50)
    article_news_block = models.CharField(default= 'article_news_block', max_length=50,verbose_name='Блок')#'article_news_block', first arguement
    article_news_title = models.CharField(default='article_news_title', max_length=50,verbose_name='Название')
    article_news_body = models.CharField(default='article_news_body', max_length=50,verbose_name='Контент')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    is_ready = models.BooleanField(default=False,verbose_name='Готовность к скачиванию')
    def __str__(self):
        return self.url
    class Meta:
        verbose_name = "Ссылка"
        verbose_name_plural = "Ссылки"
        #ordering = ['-time_update','-time_create']

    # def get_absolute_url(self):
    #     return reverse('db', args=(self.pk,))
