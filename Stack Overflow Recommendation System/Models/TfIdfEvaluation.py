'''
Created on Nov 14, 2015

@author: shreya
'''
import string
import sqlite3
import re
import pandas
import warnings
import numpy as np
from sklearn import preprocessing
import Models.LdaEvaluation as ldapred
import operator
from sklearn.metrics.pairwise import cosine_similarity
from collections import OrderedDict
import gensim
from sklearn.feature_extraction.text import TfidfVectorizer



def strip_html(text):
    tag_re = re.compile(r'<[^>]+>')
    return tag_re.sub('', text)

def tfidfcompare(data,que):
    documents = {}
    data_dict = {}


    for record in data:
        body = strip_html(record[4])
        documents[record[0]] = body+"\n"+str(record[2])+"\n"+str(record[1])
        data_dict[record[0]] = record[0:]

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

    relevant = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix)[0]

    returnset = {}
    max_value =  sorted(enumerate(relevant), key = operator.itemgetter(1), reverse=True)
    #print "max:",max_value

    for k,v in max_value:
        if k == 0:
            continue
        id = key.get(k)
        returnset[id] = v

    return returnset,data_dict


def compare(data, question,body,tag,df):

    tfidfScore,data_dict = tfidfcompare(data,question+"\n"+body+"\n"+tag)

    for record in data:
        id = record[0]
        df['TfIdf'][df.Id == id] = tfidfScore[id]


    df['FinalScore'] = df['ViewCount'] + df['Score'] + df['FavoriteCount'] + df['TfIdf']
    df = df.sort_index(by='FinalScore', ascending=0)
    return df[:100]

def jaccard_similarity(x,y):

    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))

    return intersection_cardinality/float(union_cardinality)

def rangeresult(id, offset, result, stepsize, density,idx):
    if id in result[offset:offset+stepsize]:
        if offset == 0:
            print idx
            print id
        density[offset/stepsize] += 1
        return True
    return False


if __name__ == '__main__':
    try:
        conn = sqlite3.connect("/Users/arpita/Downloads/android.stackexchange.com/android.db")
        cursor = conn.cursor()
        cursor.execute("select Id,Tags,title_tokens,Title,Body,ViewCount,Score,IfNULL(FavoriteCount,0) from Questions where AnswerCount != 0")
        data = cursor.fetchall()
    except:
        print 'Error in connection.'
        exit(-1)

    cursor.execute("select Id,Tags,title_tokens,Title,Body from Questions where  id IN (Select PostId from PostLinks where PostId in (Select id from Questions) and RelatedPostId in (Select Id from Questions) and LinkTypeId = 3) limit 5")
    IdData = cursor.fetchall()

    cursor.execute("select PostId,RelatedPostId from PostLinks where LinkTypeid=3 and PostId IN (Select id from Questions) and RelatedPostId in (Select Id from Questions)")
    related = cursor.fetchall()
    related_dict = {}

    conn.close()
    density = np.zeros(10)
    for record in related:
        id = record[0]
        present = []
        present.append(record[1])
        if id in related_dict.keys():
            present = related_dict[id]
            present.append(record[1])
        related_dict[id] = present

    #count = 0
    columns = ['Id', 'ViewCount','Score','FavoriteCount','TfIdf']
    df = pandas.DataFrame(columns=columns)

    for record in data:
        id = record[0]
        df.loc[id] = np.array([id,record[5],record[6],record[7],0.0])

    min_max_scaler = preprocessing.MinMaxScaler()
    warnings.filterwarnings("ignore")
    df['ViewCount'] = min_max_scaler.fit_transform(df['ViewCount'])
    df['Score'] = min_max_scaler.fit_transform(df['Score'])
    df['FavoriteCount'] = min_max_scaler.fit_transform(df['FavoriteCount'])


    for dt in IdData:

        result = compare(data,dt[2],dt[4],dt[1],df)

        if dt[0] in related_dict.keys():
            for id in related_dict[dt[0]]:
                offset = 0
                stepsize = 10
                while(offset < 100 and offset < len(result)) :
                    if rangeresult(id, offset, result['Id'], stepsize, density,dt[0]): break
                    offset = offset + stepsize
            print density[:10]
    print len(IdData),'\t',density

