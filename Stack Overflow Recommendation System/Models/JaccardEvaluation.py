'''
Created on Nov 14, 2015

@author: shreya
'''
import string
from sklearn.feature_extraction.text import TfidfVectorizer
import sqlite3
import re
from sklearn.metrics.pairwise import cosine_similarity
import sys
import operator
import collections
from collections import OrderedDict
from pattern.vector import Document, Model, TFIDF, TF, LEMMA, PORTER, COSINE, KMEANS, HIERARCHICAL

from nltk import word_tokenize
import numpy as np
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import matplotlib.pyplot as plt
import math

#tokenizing the incoming question
def tokenize_string(question):
    stop = stopwords.words('english')
    newTitle = ''

    list_words = word_tokenize(question.replace("\"",'').lower())
    for i in list_words:
        if i not in stop and i not in string.punctuation:
          newTitle = newTitle + ',' + i

    newQuestion = re.sub(r'^,','',newTitle)

    return newQuestion

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

        title = record[2]
        title = title.encode('ascii', 'ignore').decode('ascii')
        data_dict[id] = record[0:]
        compare_dict[id] = set(str(tags).split(',')).union(str(title).split(','))

        documents[id] = strip_html(str(record[4].encode('ascii', 'ignore').decode('ascii')))

    return data_dict, compare_dict,documents

#fn for jaccard similarity
def compare(question, tag,compare_dict):
    qset = set(str(tag).split(',')).union(str(question).split(','))
    jaccard_matrix = {}

    for k,v in compare_dict.items():
        js = jaccard_similarity(qset,compare_dict[k])
        if js > 0.0:
            jaccard_matrix[k] = js

    relevant = {}
    relevant = OrderedDict(sorted(jaccard_matrix.items(), key = operator.itemgetter(1), reverse=True)[:3000])
    return relevant.keys()

def jaccard_similarity(x,y):

    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))

    return intersection_cardinality/float(union_cardinality)


#fn for tf idf compare
def tfidfCompare(que,documents):

    counter = 1
    values = []
    values.append(que)
    key = {}
    key[0] = "que"
    for k,v in documents.items():
        values.append(v)
        key[counter] = k
        counter+=1

    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(values)


    #question_matrix = tfidf_vectorizer.fit_transform(question_array)
    #print question_matrix
    #(4, 11)
    relevant = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix)[0]

    returnset = []
    max_value = sorted(enumerate(relevant), key = operator.itemgetter(1), reverse=True)[:10]
    for k,v in max_value:
        if k == 0:
            continue
        id = key.get(k)
        returnset.append(id)
    return returnset

def rangeresult(id, offset, result, stepsize, density):
    if id in result[offset:offset+stepsize]:
        density[offset/stepsize] += 1
        return True

    return False


if __name__ == '__main__':
    try:
        conn = sqlite3.connect("/Users/arpita/Downloads/android.stackexchange.com/android.db")
        cursor = conn.cursor()
        cursor.execute("select Id,Tags,title_tokens,Title,Body from Questions where AnswerCount!=0")
        data = cursor.fetchall()
        print "data:",len(data)
    except:
        print 'Error in connection.'
        exit(-1)

    density = np.zeros(300)

    cursor.execute("select Id,Tags,title_tokens,Title,Body from Questions where  id IN (Select PostId from PostLinks where PostId in (Select id from Questions) and RelatedPostId in (Select Id from Questions) and LinkTypeId = 3) and Id=130")
    IdData = cursor.fetchall()
    print(len(IdData))

    cursor.execute("select PostId,RelatedPostId from PostLinks where LinkTypeid=3 and PostId IN (Select id from Questions) and RelatedPostId in (Select Id from Questions)")
    related = cursor.fetchall()
    print len(related)
    related_dict = {}

    conn.close()

    for record in related:
        id = record[0]
        present = []
        present.append(record[1])
        if id in related_dict.keys():
            present = related_dict[id]
            present.append(record[1])
        related_dict[id] = present

    print "built related dictionary"

    data_dict,compare_dict,documents = buildDataDictionary(data)
    print "built data dictionary"

    for dt in IdData:

        #jaccard similarity
        result = []
        result = compare(dt[2],dt[1],compare_dict)
        print dt[3]
        for row in result:
            print data_dict[row][0],data_dict[row][3]

        #tfidf
        #result = []
        #result = tfidfCompare(str(dt[4].encode('ascii', 'ignore').decode('ascii')),documents)

        if dt[0] in related_dict.keys():
         for id in related_dict[dt[0]]:
            offset = 0
            stepsize = 10

            while(offset < len(result)) :

                if rangeresult(id, offset, result, stepsize, density): break
                offset = offset + stepsize

    print len(IdData),'\t',density





