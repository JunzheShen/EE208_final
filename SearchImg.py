
INDEX_DIR = "IndexFiles.index"

import sys, os, lucene
from bs4 import BeautifulSoup
from matplotlib.ticker import Formatter

from java.io import File
from java.nio.file import Path
from org.apache.lucene.analysis.cjk import CJKAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.util import Version
from org.apache.lucene.search import BooleanQuery
from org.apache.lucene.search import BooleanClause
from org.apache.lucene.search.highlight import Highlighter
from org.apache.lucene.search.highlight import InvalidTokenOffsetsException
from org.apache.lucene.search.highlight import QueryScorer
from org.apache.lucene.search.highlight import SimpleFragmenter
from org.apache.lucene.search.highlight import SimpleHTMLFormatter

def parseCommand(command):
    allowed_opt = []
    command_dict = {}
    opt = 'contents'
    for i in command.split(' '):
        command_dict['title'] = command_dict.get('title', '') + ' ' + i
        command_dict[opt] = command_dict.get(opt, '') + ' ' + i
    print (command_dict)
    return command_dict

def run(searcher, analyzer, command, limit):
    print()
    print ("Hit enter with no input to quit.")
    if command == '':
        return

    print()
    print ("Searching for:", command)
    command_dict = parseCommand(command)
    querys = BooleanQuery.Builder()
    for k,v in command_dict.items():
        query = QueryParser(k, analyzer).parse(v)
        querys.add(query, BooleanClause.Occur.MUST)
    scoreDocs = searcher.search(querys.build(), limit).scoreDocs
    print("%s total matching documents." % len(scoreDocs))

    list1=[]

    formatter=SimpleHTMLFormatter("<font color='red'>","</font>")
    scorer=QueryScorer(querys.build())
    highlighter=Highlighter(formatter,scorer)
    highlighter.setTextFragmenter(SimpleFragmenter(35))

    for i, scoreDoc in enumerate(scoreDocs):
        doc = searcher.doc(scoreDoc.doc)
        content=doc.get("contents")
        soup=BeautifulSoup(content)
        listimg=[]
        for j in soup.findAll('img'):
            src1=j.get('src','')
            if(src1!="https://static.ws.126.net/163/f2e/product/post_nodejs/static/logo.png"):
                listimg.append(src1)
        hlcontent=highlighter.getBestFragment(analyzer,"content",content)
        list1.append({'img':listimg,'highlight':hlcontent,'path':doc.get("path"), 'title':doc.get("title"),'url':doc.get("url"),'name':doc.get("name")})
    return list1    

if __name__ == '__main__':
    STORE_DIR = "index"
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print ('lucene', lucene.VERSION)
    #base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    directory = SimpleFSDirectory(File(STORE_DIR).toPath())
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = CJKAnalyzer()#Version.LUCENE_CURRENT)
    run(searcher, analyzer)
    del searcher
