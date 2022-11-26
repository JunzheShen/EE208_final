from jieba import analyse
import jieba
 
# 创建停用词列表
def stopwordslist():
    stopwords = [line.strip() for line in open('./stopwords.txt',encoding='UTF-8').readlines()]
    stopwords += ['网易', '体育']
    return stopwords


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
    keyWords = analyse.extract_tags(tmp, topK=5, allowPOS=('ns', 'n', 'vn'))
    # print(keyWords)
    try:
        keyWords.remove(keyword)
    except:
        pass
    
    return keyWords
    # return ['皇马', '皇家', '射手榜', '利云度', '云度']
