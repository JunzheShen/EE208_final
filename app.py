# SJTU EE208

import os
import sys
import SearchImg
import jieba
import lucene
import numpy as np
from flask import Flask, jsonify, redirect, render_template, request, url_for
import recommend
from java.io import File
from java.nio.file import Path
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.analysis.cjk import CJKAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import (BooleanClause, BooleanQuery, Explanation,
                                      IndexSearcher, PhraseQuery, TermQuery)
from org.apache.lucene.search.highlight import (Highlighter, QueryScorer,
                                                SimpleFragmenter,
                                                SimpleHTMLEncoder,
                                                SimpleHTMLFormatter)
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from org.apache.pylucene.search.similarities import (PythonClassicSimilarity,
                                                     PythonSimilarity)

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False


def parseCommand(command):
    '''
    input: C title:T site:S
    output: {'contents':C, 'sport':S, 'site':U}
    '''
    allowed_opt = ['sport', 'site']
    command_dict = {}
    opt = 'contents'
    for i in command.split(' '):
        if ':' in i:
            opt, value = i.split(':')[:2]
            opt = opt.lower()
            if opt in allowed_opt and value != '':
                command_dict[opt] = value
        else:
            command_dict[opt] = command_dict.get(opt, '') + i
    return command_dict

@app.before_first_request
def activate_VM():
    global vm_env
    vm_env = lucene.initVM(vmargs=['-Djava.awt.headless=true'])

def run(searcher, analyzer, command, limit):
        command_dict = parseCommand(command)
        command_dict['contents'] = ' '.join(jieba.lcut(command_dict['contents']))
        if 'site' in command_dict.keys():
            command_dict['site'] = command_dict['site'].split('.')
            command_dict['site'] = ' '.join(command_dict['site'])
        print ("Searching for:", command_dict)

        querys = BooleanQuery.Builder()
        for k,v in command_dict.items():
            query = QueryParser(k, analyzer).parse(v)
            querys.add(query, BooleanClause.Occur.MUST)
        scoreDocs = searcher.search(querys.build(), limit).scoreDocs
        print("%s total matching documents." % len(scoreDocs))

        t = list()

        for scoreDoc in scoreDocs:
            doc = searcher.doc(scoreDoc.doc)
            formatter = SimpleHTMLFormatter() #设置用于标记的html标签
            encoder = SimpleHTMLEncoder()
            scorer = QueryScorer(querys.build())
            highlighter = Highlighter(formatter, encoder, scorer)
            fragmenter = SimpleFragmenter(100)
            highlighter.setTextFragmenter(fragmenter)
            analyzer = WhitespaceAnalyzer()
            # print("------------------------")
            # print('path:', doc.get("path"))
            # print('name:', doc.get("name"))
            # print('title:', doc.get('title'))
            # print('url', doc.get('url'))
            # print('score:', scoreDoc.score)
            t.append({'time' : int(doc.get('time')), 'title' : doc.get('title'), 'url' : doc.get('url'), 'highlight' : highlighter.getBestFragment(analyzer, 'content', doc.get('contents'))})
        return t

@app.route('/', methods=['POST', 'GET'])
def search():
    if request.method == "POST":
        kw = request.form['keyword']
        return redirect(url_for('showres', keyword=kw))
    return render_template("index.html")

@app.route('/result', methods=['GET', 'POST'])
def showres():
    try:
        vm_env = lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    except:
        vm_env = lucene.getVMEnv()
    vm_env.attachCurrentThread()
    kw = request.args.get('keyword')
    limit = request.args.get('limit')
    if not limit:
        limit = 50
    else:
        limit = int(limit)
    sportType = request.args.get('sportType')
    if sportType and sportType != "无限制":
        kw += f" sport:{sportType}"
    print(kw)
    try:
        page_num = request.args.get('page_num')
    except:
        page_num = 1
    if not page_num:
        page_num = 1
    STORE_DIR = "index"
    directory = SimpleFSDirectory(File(STORE_DIR).toPath())
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = WhitespaceAnalyzer()
    search_res = run(searcher, analyzer, kw, limit)
    related_kw = recommend.getKey(search_res, kw)
    # del searcher
    # sort_by_time = 0 : 按相关度降序 1 : 按时间降序 2 : 按时间升序
    mode = request.args.get('mode')
    if mode == "0" or mode is None:
        pass
    elif mode == "1":
        search_res.sort(key = lambda x : x['time'], reverse = True)
    else:
        search_res.sort(key = lambda x : x['time']) # 默认由大到小
    return render_template("result_page.html", list_result = search_res, keyword = kw, page_num = int(page_num), length = len(search_res), recommend_lst = related_kw)

@app.route('/result_img', methods=['GET'])
def showres_img():
    limit = request.args.get('limit')
    if not limit:
        limit = 50
    else:
        limit = int(limit)
    try:
        page_num = request.args.get('page_num')
    except:
        page_num = 1
    if not page_num:
        page_num = 1
    keyword = request.args.get('keyword')
    STORE_DIR = "index_img_by_kw"
    try:
        vm=lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    except:
        vm=lucene.getVMEnv()
    vm.attachCurrentThread()
    directory = SimpleFSDirectory(File(STORE_DIR).toPath())
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = CJKAnalyzer()
    img_res=SearchImg.run(searcher, analyzer,keyword,limit)
    del searcher
    return render_template("result_img.html", keyword=keyword,img_res=img_res,length=len(img_res),page_num=int(page_num))

if __name__ == '__main__':
    app.run(debug=True, port=8081)

