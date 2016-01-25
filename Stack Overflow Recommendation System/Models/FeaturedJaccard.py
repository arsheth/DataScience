__author__ = 'arpita'
import sqlite3
from collections import OrderedDict
import operator
import pandas
import numpy as np
from sklearn import preprocessing
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity





def compare(data, question,body, tag):
    #newTitle = tokenize_string(question.encode('ascii', 'ignore').decode('ascii'))
    qset = set(str(tag).split(',')).union(str(question).split(','))
    data_dict = {}

    columns = ['Id', 'JS', 'ViewCount','Score','FavoriteCount']
    df = pandas.DataFrame(columns=columns)
    for record in data:
        id = record[0]
        tags = record[1].encode('ascii', 'ignore').decode('ascii')

        title = record[2]
        title = title.encode('ascii', 'ignore').decode('ascii')
        data_dict[id] = record[0:]

        compareSet = set(str(tags).split(',')).union(str(title).split(','))
        js = jaccard_similarity(qset,compareSet)
        if js > 0.0:
            df.loc[id] = np.array([id,js,record[5],record[6],record[7]])


    min_max_scaler = preprocessing.MinMaxScaler()
    df['ViewCount'] = min_max_scaler.fit_transform(df['ViewCount'])
    df['Score'] = min_max_scaler.fit_transform(df['Score'])
    df['FavoriteCount'] = min_max_scaler.fit_transform(df['FavoriteCount'])
    df['FinalScore'] = df['JS'] + df['ViewCount'] + df['Score'] + df['FavoriteCount']
    df = df.sort_index(by='FinalScore', ascending=0)
    print df

def jaccard_similarity(x,y):
    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))

    return intersection_cardinality/float(union_cardinality)

if __name__ == '__main__':
    try:
        conn = sqlite3.connect("/Users/arpita/Downloads/android.stackexchange.com/android.db")
        cursor = conn.cursor()
        cursor.execute("select Id,Tags,title_tokens,Title,Body,ViewCount,Score,IfNULL(FavoriteCount,0) from Questions where AnswerCount != 0 limit 100")
        data = cursor.fetchall()
    except Exception,e:
        print 'Error in connection.',e
        exit(-1)

    compare(data[1:],data[0][2],data[0][1])
    conn.close()