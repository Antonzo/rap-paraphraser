#!/usr/bin/python3
# -*- coding: utf-8 -*-
import warnings
warnings.filterwarnings("ignore")

import io, cgi, cgitb, sys, re, gensim
import pymorphy2 as pm 

cgitb.enable()

if hasattr(sys.stdout, "buffer"):
  def bwrite(s):
    sys.stdout.flush()
    sys.stdout.buffer.write(s)
  write = sys.stdout.write
else:
  wrapper = io.TextIOWrapper(sys.stdout)
  def bwrite(s):
    wrapper.flush()
    sys.stdout.write(s)
  write = wrapper.write
write("Content-type: text/html; charset=utf-8\n\n")

import gensim
from gensim.test.utils import datapath

model = gensim.models.KeyedVectors.load_word2vec_format(datapath("/home/muam/muam.nichost.ru/cgi/model.bin"), binary=True)

m = pm.MorphAnalyzer()

def replace(x):
    return {
        'A':  'ADJ',
        'ANUM' : 'ADJ',
        'ADJF' : 'ADJ',
        'ADV' : 'ADV',
        'ADVB' : 'ADV',
        'COMP' : 'ADV',
        'GRND' : 'VERB',
        'INFN' : 'VERB',
        'NOUN' : 'NOUN',
        'PRED' : 'ADV',
        'PRTF' : 'ADJ',
        'PRTS' : 'VERB',
        'VERB' : 'VERB',
        'PREP' : 'PREP',
        'CONJ' : 'CONJ',
        'PRCL' : 'PRCL',
        'INTJ' : 'INTJ',
        'NUMR' : 'NUM',
        'NPRO' : 'PRON'
    }[x]

def new_tag_list(a):
      arr = []
      arr2 = []
      tup = tuple()
      if a.endswith('NOUN'):
        b = a.split('_')
        arr.append(m.parse(b[0])[0].tag.case)
        arr.append(m.parse(b[0])[0].tag.number)
        arr2.append(m.parse(b[0])[0].tag.gender)
        tup = (arr,arr2)
        return tup
      if a.endswith('VERB'):
        b = a.split('_')
        arr.append(m.parse(b[0])[0].tag.mood)
        arr.append(m.parse(b[0])[0].tag.number)
        arr.append(m.parse(b[0])[0].tag.tense)
        arr.append(m.parse(b[0])[0].tag.person)
        arr.append(m.parse(b[0])[0].tag.gender)
        arr2.append(m.parse(b[0])[0].tag.transitivity)
        tup = (arr,arr2)
        return tup
      if a.endswith('ADJ'):
        b = a.split('_')
        arr.append(m.parse(b[0])[0].tag.number)
        arr.append(m.parse(b[0])[0].tag.gender)
        arr.append(m.parse(b[0])[0].tag.case)
        tup = (arr,arr2)
        return tup
      else:
        return None

def my_tag_normal(str): 
    bb0 = m.parse(str)[0].normal_form 
    bb = m.parse(bb0)[0].tag.POS 
    if(bb is None): 
        bb1 = 'X' 
    else:
        try:
            bb1 = replace(bb)  
        except(Exception):
            bb1 = 'X'
    a1 = bb0 + '_' + bb1 
    return a1

def use_first_letter(word, flag):
    if flag:
        try:
            return word[0].upper() + word[1:]
        except:
            pass
    return word

def get_associat(word): 
    #word - слово
    lemma = my_tag_normal(word)
    features = new_tag_list(word+'_'+lemma.split('_')[1])
    if features is None:
        return word
    old_tl = features[0]
    nec = features[1]
    try:
        a = model.most_similar(positive=lemma)
    except(Exception):
        return word
    for x in a:
        w_arr = x[0].split('_')
        if w_arr[1] == lemma.split('_')[1] and float(x[1]) >= 0.5: #часть речи и косинусная близость
            if w_arr[1] == 'NOUN':
                if old_tl[0] is None:
                    old_tl[0] = 'nomn'
                if old_tl[1] is None:
                    old_tl[1] = 'sing'
                if (nec[0] is None or m.parse(w_arr[0])[0].tag.gender == nec[0]):
                    result = m.parse(w_arr[0])[0].inflect(set(old_tl))
                    if result is None:
                        continue
                    return m.parse(w_arr[0])[0].inflect(set(old_tl))[0]
                
            if w_arr[1] == 'VERB':
                
                
                if (old_tl[0] is None) or (old_tl[0] != 'impr'):
                    fl = True
                    for el in old_tl:
                        try:
                            if not(el is None):
                                fl = False
                                
                        except:
                            pass
                    if fl:
                        return w_arr[0]
                    
                    if old_tl[0] is None:
                        old_tl[0] = 'indc'
                    if old_tl[1] is None:
                        old_tl[1] = 'sing'
                    if old_tl[2] is None:
                        old_tl[2] = 'pres'
                    if old_tl[3] is None:
                        old_tl[3] = '1per'
                    try:
                        if old_tl[4] is None:
                            old_tl = old_tl[:4]
                    except:
                        pass
                else:
                    old_tl = old_tl[:2]
                if (nec[0] is None or m.parse(w_arr[0])[0].tag.transitivity == nec[0]):
                    result = m.parse(w_arr[0])[0].inflect(set(old_tl))
                    if result is None:
                        continue
                    return m.parse(w_arr[0])[0].inflect(set(old_tl))[0]
                
            if w_arr[1] == 'ADJ':
                if old_tl[0] is None:
                    old_tl[0] = 'sing'
                if old_tl[1] is None:
                    old_tl[1] = 'masc'
                if old_tl[2] is None:
                    old_tl[2] = 'gent' 
                result = m.parse(w_arr[0])[0].inflect(set(old_tl))
                if result is None:
                    
                    continue
                return m.parse(w_arr[0])[0].inflect(set(old_tl))[0]
    return word

#Анализ текста и вывод результата
def text_analys():
    res = {'first': '', 'second': '', 'last': ''}
    form = cgi.FieldStorage()
    text = form.getfirst("text", "")
    res['first'] = text
    if text != "":
        #m = pm.MorphAnalyzer() #hi! how are you?
        cur_i = 0
        for w in re.split('[ ?!\\.\\,:;\\(\\)\\n"]', text):
            if res['last'] != "":
                res['second'] += res['last']
                res['last'] = ''
             
            len_w = len(w)
            #сохраняем фрагмент текста, в котором возможно будет замена
            if cur_i+len_w+1 > len(text):
                res['last'] = text[cur_i:cur_i+len_w]
            else:
                res['last'] = text[cur_i:cur_i+len_w+1] 
            cur_i += len_w + 1

            if w == "":
                continue 

            #убираем тире в начале слова
            if w[0] == '-':
                word = str(w[1:])
            else:
                word = w
            #уберем пробельные символы
            word = word.strip()
            if word == "" or word == "-":
                continue

            try:
                word2 = get_associat(word) #слово, замененное сетью на реп-эквивалент
            except:
                word2 = word
            if word == word2:
                res['second'] += res['last']
            else:
                res['second'] += res['last'].replace(word, "<b>"+word2+"</b>",1)
            res['last'] = ''
            
        if res['last'] != "":
            res['second'] += res['last']
            res['last'] = ''
    return res

#text_result = text_analys()
#bwrite((text_result['first']).encode())
#bwrite((text_result['second']).encode())

bwrite("""
<!DOCTYPE HTML>
<html>
    <head>
        <meta charset="utf-8" />
        <style>
            body {
                font-family: Slab serif;
                font-size: 15pt;
                background: #94b8c5
            }
            textarea {
                width: 100%;
                height: 235px;
                background: #edeef0
            }
            div p {
                text-align: center;
                white-space: normal;
            }
            #res {
                white-space: pre; 
                border: 1px solid black; 
                height: 230px;
                padding: 5px;
                overflow-y: auto;
                font-family: Serif;
                border-color: rgb(169, 169, 169);
                font-size: 13.3333px;
            }
            h1, h2 {text-align: center; }
            input { margin-left: 40%; }
            a, a:visited, a:active { color: white; text-decoration: none; }
            a:hover { color: red; text-decoration: underline; }
        </style>
        <script type = "text/javascript">
            function fclear() {
                document.getElementById("text").value = "";
                document.getElementById("res").innerHTML = "";
            }
        </script>

    </head>
    <body>
        <h1>Rap-Paraphraser</h1>
        <div  id = "desc" align="center">
            <p class="blocktext" style ="text-align:center; width: 70%">
                Добро пожаловать на сервис для перефразирования текста любого типа (в том числе и одного слова) в семантическом поле русского репа с добавлением реп-сленга.
                Алгоритм перефразирования основан на использовании нейронной сети Word2Vec, обученной на текстах более, чем 9500 песен русских исполнителей, 
                которая находит близкие по семантике слова в контексте русского репа.
            </p>
        </div>
        <div style = "width: 100%; height: 300px;">
            <div style = "width: 48%; float: left; height: 250px;">
                <p>Введите текст:</p>
                <form action="rephrase.py" method="POST">
                    <textarea name = "text" id = "text">""".encode())
text_result = text_analys()
bwrite((text_result['first'] + "</textarea>").encode())
bwrite("""
                    <br/><br />
                    <input type = "submit" value = "Отправить!" name = "go"/> <button id = "clear" onclick="fclear()" type = "button">Очистить</button><br />
                </form>
            </div>
            <div style = "width: 48%; float: right; margin-right: 2%;">
                <p>Измененный текст:</p>
                <div id = "res" style="background: #edeef0;">""".encode())
bwrite(text_result['second'].encode())
bwrite("""
            </div>
            </div>
        </div>  
        <br/>       
        <div style = "width: 48%;float: right;"><a href="http://www.muam.nichost.ru/">Перейти на стартовую страницу</a>
        <br/><a href="associate.py" style="text-align: left;">Перейти к подбору слов-ассоциатов</a>
        </div> 
    </body>
</html>""".encode())