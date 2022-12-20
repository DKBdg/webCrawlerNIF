
import os

from django.conf import settings
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
# from django.contrib import messages
from django.shortcuts import render, redirect
from . import tasks
from .service import get_error
from django.utils.decorators import method_decorator

from .models import SearchedLink
from .forms import SearchedLinkForm, RegisterUserForm,LoginUserForm, DownloadForm
from django.urls import reverse_lazy

from . import views
from django.urls import path
from django.http import HttpResponse,JsonResponse

from django.views.generic import ListView,CreateView,View
from django.contrib.auth.forms import AuthenticationForm

file_content_types={
    'xlsx':"vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "doc":'vnd.openxmlformats-officedocument.wordprocessingml.document',
    'txt':'force-download'
}

class CrawlerIndex(View):

    def get(self,request):
        context = { 
            'form_search': SearchedLinkForm(),
            'form_download' : DownloadForm()
        }
        if not request.user.is_authenticated:
            context['form_login']=LoginUserForm()
        return render(request,'crawler/index.html',context)




def download(request):
    if request.method=='GET':
        return redirect("home")
    print(request.POST)
    if not request.user.is_authenticated:
        return JsonResponse({'msg':"Пожалуйста авторезуйтесь"},status=401)
    downloadform = DownloadForm(request.POST)
    if not downloadform.is_valid():
        return JsonResponse({'msg':"Ошибка валидации"},status=403)
    requested_object_id = request.session.get('requested_object_id',None)
    print(requested_object_id,downloadform.cleaned_data)
    if requested_object_id!=None:
        item_ = get_error(SearchedLink,id=requested_object_id)
        print(item_)
        if item_:
            if not item_.is_ready:
                return JsonResponse({'msg':"Идет поиск и сборка информации...",'success':False},status=200)
            file_number = downloadform.cleaned_data.get('file_number',None)
            file_type = downloadform.cleaned_data.get('file_type',None)
            if not (file_type and file_number):
                return JsonResponse({'msg':"Ошибка валидации(Недостаточно данных ввода)",'success':False},status=500)
            file_path = tasks.get_filepath(object_id=requested_object_id,file_number=file_number,file_type=file_type)
            print(file_path)
            if not os.path.exists(file_path):
                return JsonResponse({'msg':"Не смог найти файл",'success':False},status=403)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                print("AJAX request")
                return JsonResponse({'success':True,'msg':''},status=200)
            response=None

            with open(file_path,'rb') as f:
                file_content = f.read()
                response = HttpResponse(
                    file_content,content_type='application/'+file_content_types[file_type]
                )
                response['Content-Length'] = len(file_content)
            response['success']=True
            response['Content-Disposition'] = 'attachment; filename=file.'+file_type
            return response
    return JsonResponse({'msg':"С начало Введите url страницы в поиске"},status=200)

def CrawlerSearch(request):
    if not request.user.is_authenticated:
        return JsonResponse({'msg':"Пожалуйста авторезуйтесь","success":False},status=500)
    urlg=SearchedLinkForm(request.POST)
    print(request.POST)
    if urlg.is_valid():
        print(urlg.cleaned_data)
        requested_url= urlg.cleaned_data['url']
        #requested_url = request.POST.get('requested_url')
        print("requested url:",requested_url)
        item_ = get_error(SearchedLink,url=requested_url)
        print("ITEM:",item_)
        if not item_:
            item_ = urlg.save()
            article_data = {"article_news_title":urlg.cleaned_data.get('article_news_title'),
            "article_news_body":urlg.cleaned_data.get("article_news_body"),
            "article_news_block":urlg.cleaned_data.get("article_news_block")}
            
            tasks.search(article_data=article_data,requested_url=requested_url,object_id = item_.pk,schedule=1,verbose_name="CrawlerSearch", creator=request.user)
            #start_search(requested_url=requested_url,object_id = m.pk,schedule=1,verbose_name="CrawlerSearch", creator=request.user)
            
            request.session['requested_object_id'] = item_.pk
            return JsonResponse({'success':True,'msg':"Начало поиска и сборки информации\nПодождите несколько секунд..."},status=200)
        if not item_.is_ready:
            return JsonResponse({'success':True,'msg':"Идет поиск и сборка информации..."},status=200)
        request.session['requested_object_id'] = item_.pk
        return JsonResponse({'success':True,'msg':"Поиск завершен"},status=200)
    return JsonResponse({'success':False,'msg':"Ошибка валидации"},status=500)

def CrawlerLogin(request):
    if request.method=='POST':
        print(request.POST)
        urlg = LoginUserForm(request,request.POST)

        if urlg.is_valid():

            login(request, urlg.get_user())
            return redirect('home')
        print('Not valid urlg',urlg.errors,urlg.errors.items,urlg.errors.as_data())
    else:
        urlg = AuthenticationForm(request)
    context={
        'form_search':SearchedLinkForm(),
        'form_login':urlg,
        'form_download' : DownloadForm()
    }
    return render(request,'crawler/index.html',context)

class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'crawler/login.html'
    success_url=reverse_lazy("home")
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Авторизация"
        return context

    def get_success_url(self):
        return reverse_lazy('home')

def CrawlerRegister(request):
    if request.method=='POST':
        urlg = RegisterUserForm(request.POST)
        if urlg.is_valid():
            user = urlg.save()
            login(request,user)
            return redirect('home')
    else:
        urlg = RegisterUserForm()
    context={
        'form_register':urlg,
        'form_search':SearchedLinkForm(),
        'form_login':LoginUserForm(),
        'form_download' : DownloadForm()
        
    }
    return render(request,'crawler/index.html',context)



class RegisterUser(CreateView):
    
    template_name = 'crawler/index.html'
    success_url=reverse_lazy("login")
    context_object_name = 'form_register'
    form_class =  RegisterUserForm
    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        return context
    def form_valid(self, form):
        user=form.save()
        login(self.request,user)
        return  redirect("home")
def CrawlerLogout(request):
    logout(request)
    return redirect("login")

class CrawlerDb(ListView):
    model=SearchedLinkForm
    template_name = 'crawler/delme.html'
    context_object_name = 'db_list'#instead of object_list
    #extra_context = {"title":"DB"}
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "DB"
        return context