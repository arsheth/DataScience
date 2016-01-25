from sklearn.feature_extraction.text import TfidfVectorizer
import sqlite3
import re
from sklearn.metrics.pairwise import cosine_similarity
import operator
import numpy


def strip_html(text):
    tag_re = re.compile(r'<[^>]+>')
    return tag_re.sub('', text)

def rangeresult(id, offset, result, stepsize, density,idx):
    if id in result[offset:offset+stepsize]:
        if offset == 0:
            print idx
            print id
        density[offset/stepsize] += 1
        return True
    return False

def compare(data,que):
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

    returnset = []
    max_value =  sorted(enumerate(relevant), key = operator.itemgetter(1), reverse=True)[:100]

    for k,v in max_value:
        if k == 0:
            continue
        id = key.get(k)
        returnset.append(id)


    return returnset,data_dict
    #return sorted(returnset.items(), key = operator.itemgetter(1), reverse = True)[:10]

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

    count = 0
    cursor.execute("select Id,Tags,title_tokens,Title,Body from Questions where  id IN (Select PostId from PostLinks where PostId in (Select id from Questions) and RelatedPostId in (Select Id from Questions) and LinkTypeId = 3) and ID = 130")
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

    print "built data dictionary"

    density = numpy.zeros(10)
    for dt in IdData:

        result = []
        result,data_dict = compare(data,str(dt[4].encode('ascii', 'ignore').decode('ascii'))+"\n"+str(dt[2])+"\n"+str(dt[1]))

        print dt[3]
        for row in result:
            print data_dict[row][0],data_dict[row][3]
        '''
        if dt[0] in related_dict.keys():
            for id in related_dict[dt[0]]:
                if id in result:
                    count += 1
        '''
        if dt[0] in related_dict.keys():
            for id in related_dict[dt[0]]:
                offset = 0
                stepsize = 10
                while(offset < 100 and offset < len(result)) :
                    if rangeresult(id, offset, result, stepsize, density,dt[0]): break
                    offset = offset + stepsize
            print density[:10]

    print len(IdData),'\t',density
