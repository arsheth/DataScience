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
from sklearn.metrics.pairwise import cosine_similarity
import operator
import warnings

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
    print "important words\t",important_words
    ques_vec = dictionary.doc2bow(important_words)

    lda = gensim.models.LdaModel.load('../FinalLdaTitleTFIDF.lda')
    topic_vec = []
    topic_vec = lda[ques_vec]
    return topic_vec

def loadMap(filename, delim='\t'):
    file_handle = open(filename,'r')
    map_ = {}
    for line in file_handle:
        pair = line.strip('\n').split(delim)
        map_[int(pair[0])] = createValueDict(pair[1])
    file_handle.close()
    return map_

def buildVectorNew(queryVector, dataVector):

    vector1_array = numpy.zeros(30)
    vector2_array = numpy.zeros(30)

    for key in queryVector:
        vector1_array[int(key)] = float(queryVector[key])

    for key in dataVector:
        vector2_array[int(key)] = float(dataVector[key])

    return vector1_array, vector2_array

def sim(queryScoreDict, dataScoreDict):
    vector1, vector2 = buildVectorNew(queryScoreDict, dataScoreDict)
    warnings.filterwarnings("ignore")
    relevant = cosine_similarity(vector1, vector2)[0]
    return relevant[0]

def createValueDict(value):
    dict_ = {}
    for topics in value.split(","):

        if len(topics) > 1:
            topics = str(topics)
            split_probab = topics.split(":")
            probab = split_probab[1]
            word = split_probab[0]
            dict_[word] = float(probab)

    return dict_

def strip_html(text):
    tag_re = re.compile(r'<[^>]+>')
    return tag_re.sub('', text)

def buildDataDictionary(data):
    data_dict = {}
    compare_dict = {}
    documents = {}
    for record in data:
        id = record[0]
        tags = record[1].encode('ascii', 'ignore').decode('ascii')

        title = record[3]
        title = title.encode('ascii', 'ignore').decode('ascii')
        data_dict[id] = record
        #documents[id] = strip_html(str(record[4].encode('ascii', 'ignore').decode('ascii')))

    return data_dict

if __name__ == '__main__':
    try:
        conn = sqlite3.connect("/Users/arpita/Downloads/android.stackexchange.com/android.db")
        cursor = conn.cursor()
        cursor.execute("select Id,Tags,title_tokens,Title,Body,ViewCount,Score,IfNULL(FavoriteCount,0) from Questions")
        data = cursor.fetchall()
        data_dict = buildDataDictionary(data)

    except:
        print 'Error in connection.'
        exit(-1)


    print len(data)

    if not os.path.isfile('lda_features2.txt'):
        outfile = open('lda_features2.txt','w')
        for row in data:
            topic_vec = getTopicForQuery(row[3]+"\n"+row[1]+"\n"+row[4])
            sorted_vec = sorted(topic_vec, key = operator.itemgetter(1), reverse=True)
            '''
            temp = ""
            for i in range(len(sorted_vec)):
                #print sorted_vec
                temp += str(sorted_vec[i][0])+":"+str(sorted_vec[i][1])+","
            '''
            outfile.write(str(row[0])+"\t"+str(sorted_vec)+"\n")
        outfile.close()

    cursor.execute("select Id,Tags,title_tokens,Title,Body from Questions where  id IN (Select PostId from PostLinks where PostId in (Select id from Questions) and RelatedPostId in (Select Id from Questions) and LinkTypeId = 3) limit 100")
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
        query_topic = getTopicForQuery(dt[3]+"\n"+dt[1]+"\n"+ dt[4])
        sort_vec = sorted(query_topic, key = operator.itemgetter(1), reverse=True)


        print "Id\tmain vec:\t",dt[0], sort_vec
        print "title of query\t",dt[3]

        for id in related_dict[dt[0]]:

            related_topic = getTopicForQuery(data_dict[id][3]+"\n"+data_dict[id][1]+"\n"+data_dict[id][4])
            rel_vec = sorted(related_topic, key = operator.itemgetter(1), reverse=True)

            sim = gensim.matutils.cossim(rel_vec, sort_vec)
            if sim==1.0:
                count = count+1
                print "Id\trelated:\t",id, rel_vec
                print "related title\t",data_dict[id][3]

        '''
        #query = createValueDict(temp)

        relevant = {}
        print sort_vec
        infile = open('lda_features2.txt','r')
        for line in infile:
            id,rel_vec = line.split('\t')
            print id,dt[0]
            print rel_vec
            sim = gensim.matutils.cossim(rel_vec, sort_vec)
            if sim==1.0:
                count = count+1
                relevant[dt[0]] = id

        #relevant = OrderedDict(sorted(resultArray.items(), key = operator.itemgetter(1), reverse=True)[:10])

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

        '''
    print count, len(IdData)
    #print relevant