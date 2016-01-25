__author__ = 'arpita'
import sqlite3
import re

def process_tag_text(text):
    #tag_re = re.compile(r'<[^>]+>')
    return ','.join(re.findall(r'<([^>]+)',text))


def processText(database_name = "/Users/arpita/Downloads/softwarerecs.stackexchange.com/softwarerecs.db", log_filename='parser_text.log'):
    db = sqlite3.connect(database_name)


    cur = db.cursor()
    cur.execute('create index "id_idx" on posts(Id)')
    db.commit()
    cur.execute('SELECT Id,Tags,Title FROM posts where PostTypeId = 1')

    rows = cur.fetchall()
    for row in rows:
        tag_text = process_tag_text(str(row[1]))
        cur.execute("UPDATE posts SET tags=? WHERE Id=?", (tag_text, row[0]))

    db.commit()
    db.close()



if __name__ == '__main__':
    processText()
