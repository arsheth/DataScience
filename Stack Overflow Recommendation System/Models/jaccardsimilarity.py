from nltk import word_tokenize
from nltk.corpus import stopwords
from math import*
import sqlite3
import string
import re
import sys
import operator
from collections import OrderedDict


def tokenize_string(question):
    stop = stopwords.words('english')
    newTitle = ''

    list_words = word_tokenize(question.replace("\"",'').lower())
    for i in list_words:
        if i not in stop and i not in string.punctuation:
          newTitle = newTitle + ',' + i

    newTitle = re.sub(r'^,','',newTitle)

    return newTitle


def compare(data, question, tag):
    newTitle = tokenize_string(question.encode('ascii', 'ignore').decode('ascii'))
    qset = set(str(tag).split(',')).union(str(newTitle).split(','))
    jaccard_matrix = {}
    data_dict = {}

    for record in data:
        id = record[0]
        tags = record[1].encode('ascii', 'ignore').decode('ascii')

        title = record[2]
        title = title.encode('ascii', 'ignore').decode('ascii')
        data_dict[id] = record[0:]

        compareSet = set(str(tags).split(',')).union(str(title).split(','))
        js = jaccard_similarity(qset,compareSet)
        if js > 0.0:
            jaccard_matrix[id] = js

    relevant = {}
    relevant = OrderedDict(sorted(jaccard_matrix.items(), key = operator.itemgetter(1), reverse=True)[:10])
    result = []


    for k, v in relevant.items():
        if k in data_dict:
            #print data_dict[k][2],'\n'
            result.append(data_dict[k])

    return result

def jaccard_similarity(x,y):

    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))

    return intersection_cardinality/float(union_cardinality)

if __name__ == '__main__':
    conn = sqlite3.connect("/Users/arpita/Downloads/android.stackexchange.com/android.db")
    cursor = conn.cursor()
    cursor.execute("select Id,Tags,title_tokens,Title,Body from Questions where AnswerCount!=0")
    data = cursor.fetchall()

    cursor.execute("select Id,Tags,title_tokens,Title,Body from Questions where Id = 130")
    query = cursor.fetchone()

    print query[3]
    result = compare(data,query[3],query[1])
    for row in result:
        print row[3], row[0]