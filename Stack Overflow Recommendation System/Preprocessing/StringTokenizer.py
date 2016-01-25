from nltk import word_tokenize
from nltk.corpus import stopwords
import string
import sqlite3
import re

conn = sqlite3.connect("/Users/arpita/Downloads/android.stackexchange.com/android.db")
cursor = conn.cursor()


cursor.execute("Alter TABLE Questions ADD column title_tokens TEXT")
conn.commit()
cursor.execute("select Id,Title from Questions")

stop = stopwords.words('english')
data = cursor.fetchall()
for record in data:
	id = record[0]
	title = record[1]
	title = title.encode('ascii', 'ignore').decode('ascii')

	newTitle = ''
	list_words = word_tokenize(str(title).replace("\"",'').lower())
	
	for i in list_words:
		if i not in stop and i not in string.punctuation:
			newTitle = newTitle + ',' + i

	newTitle = re.sub(r'^,','',newTitle)
	cursor.execute("Update Questions set title_tokens = ? where Id = ?",(newTitle,id))
conn.commit()
conn.close()
