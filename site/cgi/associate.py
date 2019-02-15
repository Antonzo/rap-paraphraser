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

#возвращает список пар <слово_тег, косинусная близость>
#Далее при проходе по списку и выводу резульата теги стоит убрать
def text_analys():
    form = cgi.FieldStorage()
    text = form.getfirst("text", "")
    res = {'first': '', 'second': ''}
    if text == "":
        return res
    word = re.split('[?!., ]', text)[0]
    res['first'] = word
    lemma = my_tag_normal(word.lower())
    #print(lemma)
    try:
        for x in model.most_similar(positive=lemma):
            res['second'] += x[0].split('_')[0] + " (" + str(x[1]) + ")\n"
    except(Exception):
        res['second'] = '<слова-ассоциаты не найдены>'
    return res

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
                margin-left: 25%;
                width: 50%;
                height: 20px;
                background: #edeef0
            }
            div p {
                text-align: center;
                white-space: normal;
            }
            #res {
                white-space: pre; 
                border: 1px solid black; 
                height: 60px;
                padding: 5px;
                overflow-y: auto;
                font-family: Serif;
                border-color: rgb(169, 169, 169);
                font-size: 13.3333px;
            }

            h1, h2 {text-align: center; }
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
    <body link="black" vlink="black" alink="black">
        <h1>Rap-Paraphraser</h1>
        <div  id = "desc" align="center">
            <p class="blocktext" style ="text-align:center; width: 65%">
                Добро пожаловать на сервис для поиска ассоциатов в семантическом поле русского репа с добавлением реп-сленга.
                Алгоритм поиска основан на использовании нейронной сети Word2Vec, обученной на текстах более, чем 9500 песен русских исполнителей, 
                которая находит близкие по семантике слова в контексте русского репа.
            </p>
        </div>
        <div style = "margin-left: 25%; width: 50%; height: 50px;">
            <div style = "width: 45%; float: left; height: 250px;">
                <p>Введите слово:</p>
                <form action="associate.py" method="POST">
                    <div style = "text-align: center;">
                        <input type = "text" name = "text" id = "text" style = "width: 70%;" value = \"""".encode())
text_result = text_analys()
bwrite((text_result['first'] + '"/>').encode())
bwrite("""
                        <br/>
                        <div style = "text-align: center; margin-top: 5px;">
                            <input type = "submit" value = "Поиск" name = "go"/> <button id = "clear" onclick="fclear()" type = "button">Очистить</button>
                        </div>
                    </div><br />
                </form>
            </div>
            <div style = "width: 45%; float: right; margin-right: 5%;">
                <p>Слова ассоциаты:</p>
                <div id = "res" style="background: #edeef0; height: 200px;">""".encode())
bwrite(text_result['second'].encode())
bwrite("""
            </div>
            <div style = "width: 100%;float: right;"><a href="http://www.muam.nichost.ru/">Перейти на стартовую страницу</a>
            <br/><a href="rephrase.py" style="text-align: left;">Перейти к перефразировке текста</a></div>
        </div>  
        <br/><br/>     
    </body>
</html>""".encode())