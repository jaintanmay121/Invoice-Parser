import os
import time
from AbbyyOnlineSdk import *

def setup_processor():
    if "ABBYY_APPID" in os.environ:
        processor.ApplicationId = os.environ["ABBYY_APPID"]
    if "ABBYY_PWD" in os.environ:
        processor.Password = os.environ["ABBYY_PWD"]
    # Proxy settings
    if "http_proxy" in os.environ:
        proxy_string = os.environ["http_proxy"]
        print("Using http proxy at {}".format(proxy_string))
        processor.Proxies["http"] = proxy_string
    if "https_proxy" in os.environ:
        proxy_string = os.environ["https_proxy"]
        print("Using https proxy at {}".format(proxy_string))
        processor.Proxies["https"] = proxy_string


def recognize_file(file_path):
    print("Uploading..")
    settings = ProcessingSettings()
    task = processor.process_image(file_path, settings)
    if task is None:
        print("Error")
        return
    if task.Status == "NotEnoughCredits":
        print("Not enough credits to process the document. Please add more pages to your application's account.")
        return
    while task.is_active():
        time.sleep(5)
        task = processor.get_task_status(task)
    if task.Status == "Completed":
        if task.DownloadUrl is not None:
            processor.download_result(task)


import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk import word_tokenize, pos_tag, ne_chunk


def inv(text):
    
    sentences=nltk.sent_tokenize(a)
    sentences=[nltk.word_tokenize(el) for el in sentences]
    sentences=[nltk.pos_tag(el) for el in sentences]
    
    try:
        index=[]
        for i in range(len(sentences)):
            for j in range(len(sentences[i])):
                if sentences[i][j][0].lower()=='invoice' and sentences[i][j+1][0].lower()=='no':
                    index=[i,j]
                    break
        
        st=[]
        for i in range(len(sentences[index[0]])-index[1]):
            st.append(sentences[index[0]][index[1]][0])
            index[1]=index[1]+1
        for i in range(len(sentences[index[0]+1])):
            st.append(sentences[index[0]+1][i][0])
            index[1]=index[1]+1
            
        st
        
        text=' '.join(st)
        
        pattern = re.compile(r' [0-9]{3,4} ')
        inv = pattern.findall(text)
        return inv[0].strip()
    except:
        try:
            invo= re.search(r'[A-Z]{2,2}-[0-9]{3,4}',text).group()
            print(invo)
            return invo
        except:
            return None
    
def getPhone(text):
    try:
        pattern = re.compile(r'([+(]?\d+[)\-]?[ \t\r\f\v]*[(]?\d{2,}[()\-]?[ \t\r\f\v]*\d{2,}[()\-]?[ \t\r\f\v]*\d*[ \t\r\f\v]*\d*[ \t\r\f\v]*)')
        phone = pattern.findall(text)
        phone = [re.sub(r'[,.]', '', el) for el in phone if len(re.sub(r'[()\-.,\s+]', '', el))>6]
        phone = [re.sub(r'\D$', '', el).strip() for el in phone]
        phone = [el for el in phone if len(re.sub(r'\D','',el)) <= 13 and len(re.sub(r'\D','',el))>=10]
        ph=[]
        for i in range(len(phone)):
            if len(phone[i])>=8 and len(phone[i])<15:
                phone[i]=phone[i].replace(' ','')
                ph.append(phone[i])
        return ph
    except:
        return None
        
def getEmail(text):    
    try:
        pattern = re.compile(r'\S*@\S*')
        email = pattern.findall(text)
        return email[0]
    except:
        return None

def getDate(text):    
    try:
        if (re.search(r'\d{1,2}-[A-Za-z]{3}-[0-9]{4}',text)!=None):
            pattern=re.compile(r'\d{1,2}-[A-Za-z]{3}-[0-9]{4}')
            date = pattern.findall(text)
        elif (re.search(r'\d{1,2} [A-Za-z]{3}-[0-9]{4}',text)!=None):
            pattern=re.compile(r'\d{1,2} [A-Za-z]{3}-[0-9]{4}')
            date = pattern.findall(text)
        else:
            date = re.search(r'(\d+/\d+/\d+)',a).group()
        return date
    except:
        return None


def getCost(text):    
    try:
        pattern=re.compile(r'\d*\,\d*\.\d*')
        pattern1=re.compile(r'\d*\.\d*\.\d*')
        list1=pattern.findall(text)
        list2=pattern1.findall(text)
        list1.extend(list2)        
        return max(list1)
    except:
        try:
            return re.search(r'(\$\s?[0-9,]+(\.[0-9]{2})?)',text).group()
        except:
            return None
        
def getDetails(text):
    
    date=getDate(text)
    mail=getEmail(text)
    tel=getPhone(text)
    invoice=inv(text)
    cost=getCost(text)
    dict={
        'date':date,
        'mail':mail,
        'Phone':tel,
        'Cost':cost, 
        'Invoice No':invoice
    }
    return dict



def invoiceocr(fname):
    global processor
    processor = AbbyyOnlineSdk()
    setup_processor()
    recognize_file(fname)
    global a
    with open('file.txt','r') as fp:
        a=fp.read()
    dic=getDetails(a)
    print(dic)
    return dic['date'],dic['mail'],dic['Phone'],dic['Cost'],dic['Invoice No']