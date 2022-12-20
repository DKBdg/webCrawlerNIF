import os,openpyxl, requests, docx,openpyxl,time
#from sys import getsizeof as gs

from bs4 import BeautifulSoup
from googletrans import Translator
from urllib.parse import urlparse,urljoin
import httpx
print(httpx._config)
#from background_task import background
#from background_task.models import Task,CompletedTask
#from .service import send_email,get_error
#from django.conf import settings
#from .models import SearchedLink




media_folder = os.path.join('.\\media',"crawler")
file_type_choices={'xlsx':'xlsx','doc':'docx','txt':'txt'}
file_number_choices = (10,50,100)

def get_filepath(object_id=None,file_number=None,file_type=None):
    
    print(object_id,file_number,file_type)
    file_number=int(file_number)
    if (file_number in file_number_choices) and (file_type in file_type_choices.keys() ) and file_number:
        ending = file_type_choices[file_type]
        return os.path.join(media_folder,f'File{object_id}_{file_number}.{ending}')

    raise Exception("Error input filename data")

class TextTranslator:
    def __init__(self):
        self.translator = Translator(service_urls=[
      'translate.google.cn'
      #'translate.google.co.kr',
    ],timeout  = httpx.Timeout(8))
    def translate(self,text,src='kk',dest_language = 'zh-cn'):
        try:
            res = self.translator.translate(text[0] + '.\n'+text[1], dest=dest_language).text
            res = res.split('\n')
            if len(res)>1:
                return True,(res[0],'\n'.join(res[1:]))
        except Exception as err:
            print("TRANSLATION ERROR:",err)
        return False,None
        
        
class TxtDocument:
    buffer=''
    def __init__(self,file=None):
        ob = open(file,'w+', encoding='utf-8')
        ob.close()
    def add(self,url,content,ending=True):
        self.buffer = self.buffer + content + '\n'+url + '\n'
        if ending:
            self.buffer+='_____________________________________\n'
        else:
            self.buffer+='\n'
    def save(self,file=None):
        with open(file,'a+', encoding='utf-8') as f:
            f.write(self.buffer)
        self.buffer = ''
    # def close(self):
    #   self.object.close()

class MyFilesClass:
    
    def __init__(self,object_id=None,file_number=None):
        self.document = {}
        self.files={}
        for key_type in file_type_choices.keys():
            self.files[key_type]=get_filepath(object_id = object_id,file_type=key_type,file_number=file_number)
        self.object_id = object_id
        print(self.files);self.xl=1
    def create(self):
        self.document['xlsx']=openpyxl.Workbook()
        self.document['doc']=docx.Document()
        self.document['txt'] = TxtDocument(self.files['txt'])
        for f in self.files.keys():
            if os.path.exists(self.files[f]):
                os.remove(self.files[f])
        self.document['xlsx'].remove(self.document['xlsx'].active)
        self.worksheet1 =self.document['xlsx'].create_sheet("Kazakh", 0)
        self.worksheet2 =self.document['xlsx'].create_sheet("Chinese",1)
        self.worksheet1.column_dimensions['A'].width=160
        self.worksheet1.column_dimensions['B'].width=120
        self.worksheet2.column_dimensions['A'].width=160
        self.worksheet2.column_dimensions['B'].width=120
        
        self.save()#<-min number
        #self.save()


    def add(self,n:int,content_url:list,orig_content:list,translated_content:list,auto_save=False):
        print("ADD:",n);
        if n==0:
            return;
        for i in range(0,n):
            translated = '\n'.join(translated_content[i])
            original = '\n'.join(orig_content[i])
            self.worksheet1.append([original,content_url[i]])
            self.worksheet1["A"+str(self.xl)].alignment = openpyxl.styles.Alignment(wrap_text=True)
            self.worksheet2.append([translated,content_url[i]])
            self.worksheet2["A"+str(self.xl)].alignment = openpyxl.styles.Alignment(wrap_text=True)

            self.document['doc'].add_heading(orig_content[i][0])
            self.document['doc'].add_paragraph(orig_content[i][1])
            self.document['doc'].add_paragraph(content_url[i])
            self.document['doc'].add_heading(translated_content[i][0])
            self.document['doc'].add_paragraph(translated_content[i][1])
            self.document['doc'].add_paragraph(content_url[i])

            self.document['txt'].add(content_url[i],original,ending=False)
            self.document['txt'].add(content_url[i],translated,ending=True);self.xl+=1
        
        if auto_save:
            self.save()
    def remove(self):
        self.document['xlsx'].remove(self.worksheet1)
        self.document['xlsx'].remove(self.worksheet2)

    def save(self):
        print("save")
        for key in self.files.keys():
            self.document[key].save(self.files[key])



max_number_of_iterate=150
errors=[]
iterate_add_number = 30

def search(requested_url=None,object_id=None,main_domain=None,article_data=None):
    print("START WORK")
    print(article_data)
    main_domain = requested_url
    res_raw_links = link_gathering(requested_url,main_domain)
    length_of_res_links = len(res_raw_links)
    if length_of_res_links > max_number_of_iterate:
        length_of_res_links=max_number_of_iterate
    print("RES_LINK:",length_of_res_links)
    documents = []

    a = sorted(file_number_choices,reverse=True)
    for i in range(len(a)):
        documents.append( MyFilesClass(object_id=object_id,file_number=a[i]) )
        documents[i].create()
    print(documents[0].files)
    del a;
    index = 0
    success_number=0
    old_success_number=0
    s1=time.time()
    translator = TextTranslator()
    for required_number in file_number_choices:
        file_number = required_number#30,50,100
        if file_number>length_of_res_links:
            file_number = length_of_res_links
        if success_number>=file_number:
            break
        content_url=[]
        orig_content=[]
        translated_content=[]
        print("LOOK at",required_number,"->",file_number)
        while((file_number!= success_number) and (index<length_of_res_links)):
            st,res_raw_content = content_gathering(res_raw_links[index],article_data)
            print(index,")",res_raw_links[index],st)
            if st:
                st,tt = translator.translate(res_raw_content)
                print("TRANSLATE",st)
                if st:
                    orig_content.append(res_raw_content)
                    translated_content.append(tt)
                    content_url.append(res_raw_links[index])

                success_number+=1
            index+=1
            if success_number%iterate_add_number==0:
                if success_number!=old_success_number:
                    old_success_number = success_number
                    print("Iterate at",index,"(",success_number,")")
                    st,tt = translator.translate(res_raw_content)
                    for i in range(len(documents)):
                        documents[i].add(len(content_url),content_url,orig_content,translated_content,auto_save=True)
                    content_url=[]
                    orig_content=[]
                    translated_content=[]

        for i in range(len(documents)):
            print("simple save to",i,' ',required_number,"(",success_number,")")
            documents[i].add(len(content_url),content_url,orig_content,translated_content,auto_save=True) 
        documents.pop()
    s2=time.time()
    print("COMPLETED AT ",s2-s1,"s")
    


def link_gathering(a,main_domain):
    basa = []
    response = requests.get(a)
    response.raise_for_status()

    soup=BeautifulSoup(response.content, 'lxml')
    del response;
    for i in soup.find_all("a"):
        href_object =i.get('href')
        if (href_object is None) or ('img' in href_object) or ('image' in href_object) or ('#' in href_object) or ('ia' in href_object):
            errors.append("IMG  "+this_domain)
            continue
        if href_object.startswith('http'):
            this_domain=None
            try:
                this_domain = urlparse(href_object)
                this_domain = this_domain.scheme + "://"+this_domain.hostname
            except:
                errors.append(href_object)
                continue
            if not (this_domain.startswith(main_domain)):
                errors.append(this_domain)
                continue
            basa.append(this_domain)
        else:
            basa.append(urljoin(main_domain, href_object))
    basa=list(set(basa))
    return basa


def content_gathering(link,article_data):
    response=None
    try:
        response = requests.get(link)
        if response.status_code!=200:
            ptint("DONT WORK"+link)
            return False,None
    except:
        print("DONT WORK"+link)
        return False,None
    soup = BeautifulSoup(response.content, 'lxml')
    div_block_objects=soup.find("div", class_=article_data["article_news_block"])
    if (not div_block_objects) or len(div_block_objects)==0:
        print("NO ARTCILE BLOCK"+link)
        return False,None
    div_title_objects=div_block_objects.find("div", class_=article_data["article_news_title"])#news_block
    if not div_title_objects:
        print("NO ARTCILE TITLE "+article_data["article_news_title"]+link)
        return False,None
    if div_title_objects.find("h1"):
        content_title = div_title_objects.find("h1").get_text()
    else:
        content_title = div_title_objects.get_text()
    
    div_body_objects=div_block_objects.find("div", class_=article_data["article_news_body"])#news_block
    content_body=''
    for p_objects in div_body_objects.find_all('p'):
        for k in p_objects:
            content_body+=k.get_text()
    return True,(content_title,content_body)

if __name__ == '__main__':
    url='https://www.inform.kz'
    ee = {
        'article_news_block':"article_container",
        "article_news_title":'title_article_bl',
        "article_news_body":'body_article_bl'
    }
    search(requested_url=url,object_id=1,main_domain=url,article_data=ee)
