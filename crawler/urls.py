from django.conf.urls.static import static
from django.urls import path
from .views import *
urlpatterns = [
    path('', CrawlerIndex.as_view(),name='home'),
    path("search/",CrawlerSearch,name="search"),
    path('db/', CrawlerDb.as_view(),name='db'),
    
    path('download/', download,name='download'),
    #path('login/',login_user,name='login'),
    path('accounts/login/', CrawlerLogin,name='login'),
    path('accounts/logout/', CrawlerLogout,name='logout'),
    #path('register/', RegisterUser.as_view(),name='register')
    path('accounts/register/', CrawlerRegister,name='register')
]
if settings.DEBUG:
    urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)