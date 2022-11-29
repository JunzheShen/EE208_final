from jieba import analyse
import jieba
 
# 创建停用词列表
def stopwordslist():
    stopwords = [line.strip() for line in open('./stopwords.txt',encoding='UTF-8').readlines()]
    stopwords += ['网易', '体育']
    return stopwords

def frequency_sort(items):
    # your code here
    _set = set()
    for i in items:
        if i not in _set:
            _set.add(i)
    _set = list(_set)
    lst = []
    dic = {}
    # # print(lst1)
    for i in _set:
        dic[i] = items.count(i)
    dic = dict(sorted(dic.items(), key=lambda x:x[1], reverse=True))
    # #print(dic)
    count = 0
    for k, v in dic.items():
        # for i in range(v):
            lst.append(k)
    # # print(lst)
    return lst


def getKey(reslist, keyword, maxiter=100):
    text = ""
    i = 0
    for resitem in reslist:
        if i > maxiter:
            break
        else:
            i += 1
        text += resitem["title"]
    text = jieba.lcut(text)
    stopwords = stopwordslist()
    tmp = ''
    for word in text:
        if word not in stopwords:
            if word != '\t':
                tmp += word
    # keyWords = analyse.extract_tags(tmp, topK=5, allowPOS=('ns', 'n'))
    keyWords = []
    count = 0
    for i in frequency_sort(jieba.lcut(tmp)):
        if count == 5: break
        elif (not i.isspace()) and (len(i) > 1):
            count += 1
            keyWords.append(i)

    try:
        keyWords.remove(keyword)
    except:
        pass
    
    return keyWords
