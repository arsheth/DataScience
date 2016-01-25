__author__ = 'arpita'
import sys
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models
import string
import re
import numpy
import gensim
import sqlite3
import os.path
from collections import Counter
import math
from collections import OrderedDict
import operator

def getTopicForQuery (question):
    temp = question.lower()
    punctuation_string = string.punctuation
    en_stop = stopwords.words('english')
    for i in range(len(punctuation_string)):
        temp = temp.replace(punctuation_string[i], '')

    words = re.findall(r'\w+', temp, flags = re.UNICODE | re.LOCALE)

    important_words = []
    important_words = filter(lambda x: x not in en_stop, words)

    dictionary = corpora.Dictionary.load('../questions2.dict')

    ques_vec = []
    ques_vec = dictionary.doc2bow(important_words)

    lda = gensim.models.LdaModel.load('../FinalLdaTitle.lda')
    topic_vec = []
    topic_vec = lda[ques_vec]
    return topic_vec




def loadMap(filename, delim='\t'):
    file_handle = open(filename,'r')
    map_ = {}
    for line in file_handle:
        pair = line.strip('\n').split(delim)
        map_[pair[0]] = createValueDict(pair[1])
    file_handle.close()
    return map_

def buildVector(iterable1, iterable2):
    counter1 = Counter(iterable1)
    counter2= Counter(iterable2)

    all_items = set(counter1.keys()).union( set(counter2.keys()) )
    vector1 = [counter1[k] for k in all_items]
    vector2 = [counter2[k] for k in all_items]
    return vector1, vector2

def cosine_similarity(queryScoreDict, dataScoreDict):
    vector1, vector2 = buildVector(queryScoreDict, dataScoreDict)

    for i in range(len(vector1)):
        dot = vector1[i] * vector2[i]
    sum_vector1 = 0.0

    for i in range(len(vector1)):
        sum_vector1 += sum_vector1 + float(vector1[i]*vector1[i])
    norm_vector1 = float(math.sqrt(sum_vector1))

    #Normalize the second vector
    sum_vector2 = 0.0
    for i in range(len(vector2)):
        sum_vector2 += sum_vector2 + float(vector2[i]*vector2[i])
    norm_vector2 = float(math.sqrt(sum_vector2))

    if norm_vector1 != 0 and norm_vector2 != 0:
        return dot/float(norm_vector1*norm_vector2)
    return 0.0

def createValueDict(value):
    dict_ = {}
    for topics in value.split(","):

        if len(topics) > 1:
            topics = str(topics)
            split_probab = topics.split(":")
            probab = split_probab[0]
            word = split_probab[1]
            dict_[word] = float(probab)

    return dict_

def strip_html(text):
    tag_re = re.compile(r'<[^>]+>')
    return tag_re.sub('', text)

def buildDataDictionary(data):
    data_dict = {}
    for record in data:
        id = record[0]
        '''
        tags = record[1].encode('ascii', 'ignore').decode('ascii')

        title = record[3]
        title = title.encode('ascii', 'ignore').decode('ascii')
        '''
        data_dict[id] = record[0:]

    return data_dict

if __name__ == '__main__':
    try:
        conn = sqlite3.connect("/Users/arpita/Downloads/android.stackexchange.com/android.db")
        cursor = conn.cursor()
        cursor.execute("select Id,Tags,title_tokens,Title,Body,ViewCount,Score,IfNULL(FavoriteCount,0) from Questions where AnswerCount != 0 limit 1000")
        data = cursor.fetchall()
        data_dict = buildDataDictionary(data)

    except:
        print 'Error in connection.'
        exit(-1)


    print len(data)

    if not os.path.isfile('lda_features2.txt'):
        outfile = open('lda_features2.txt','w')
        for row in data:
            topics = getTopicForQuery(row[3]+" "+row[1])
            '''
            temp = ""
            for i in range(len(topics)):
                temp += str(topics[i][0])+":"+topics[i][1]+","
            '''
            outfile.write(str(row[0])+"\t"+str(topics)+"\n")
        outfile.close()


    matrix = loadMap('lda_features2.txt')
    print matrix['112358']

    cursor.execute("select Id,Tags,title_tokens,Title,Body from Questions where  id IN (Select PostId from PostLinks where PostId in (Select id from Questions) and RelatedPostId in (Select Id from Questions) and LinkTypeId = 3) limit 10")
    IdData = cursor.fetchall()


    cursor.execute("select PostId,RelatedPostId from PostLinks where LinkTypeid=3 and PostId IN (Select id from Questions) and RelatedPostId in (Select Id from Questions)")
    related = cursor.fetchall()
    related_dict = {}

    for record in related:
        id = record[0]
        present = []
        present.append(record[1])
        if id in related_dict.keys():
            present = related_dict[id]
            present.append(record[1])

        related_dict[id] = present

    count = 0
    for dt in IdData:
        query_topic = getTopicForQuery(dt[3]+dt[1])
        temp = ""
        for i in range(len(query_topic)):
            temp += str(query_topic[i][0])+":"+query_topic[i][1]+","
        query = createValueDict(temp)
        resultArray = {}
        for id in matrix:
            result = cosine_similarity(query,matrix[id])
            resultArray[id] = result
        relevant = {}
        relevant = OrderedDict(sorted(resultArray.items(), key = operator.itemgetter(1), reverse=True)[:10])

        print "Question:",dt[3]
        print "lda vector\t",query

        for key,val in relevant.items():
            print "id\ttitle:",key,data_dict[int(key)]
            print "lda vector\t",matrix[int(key)]
        if dt[0] in related_dict.keys():
            for id in related_dict[dt[0]]:
                #print " id in related\t", id,"\n"
                if id in relevant:
                    count += 1

        print count
    print len(IdData),'\t',count