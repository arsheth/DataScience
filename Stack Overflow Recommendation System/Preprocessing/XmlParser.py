__author__ = 'arpita'
import sqlite3
import os
import xml.etree.cElementTree as etree
import logging

ANATHOMY = {
'PostLinks':{
    'Id':'INTEGER',
    'CreationDate':'DATETIME',
    'PostId':'INTEGER',
    'RelatedId':'INTEGER',
    'LinkTypeId':'INTEGER',
    },
}
def dump_files(file_names, anathomy,
    dump_path='/Users/arpita/Downloads/cs.stackexchange.com/',
    dump_database_name = 'cs.db',
    create_query='CREATE TABLE IF NOT EXISTS [{table}]({fields})',
    insert_query='INSERT INTO {table} ({columns}) VALUES ({values})',
    log_filename='so-parser.log'):

 logging.basicConfig(filename=os.path.join(dump_path, log_filename),level=logging.INFO)
 db = sqlite3.connect(os.path.join(dump_path, dump_database_name))

 for file in file_names:
  print "Opening {0}.xml".format(file)
  with open(os.path.join(dump_path, file + '.xml')) as xml_file:
   tree = etree.iterparse(xml_file)
   table_name = file

   sql_create = create_query.format(
        table=table_name,
        fields=", ".join(['{0} {1}'.format(name, type) for name, type in anathomy[table_name].items()]))
   print('Creating table {0}'.format(table_name))

   try:
    logging.info(sql_create)
    db.execute(sql_create)
   except Exception, e:
    logging.warning(e)

   for events, row in tree:
    try:
     logging.debug(row.attrib.keys())

     db.execute(insert_query.format(
        table=table_name,
        columns=', '.join(row.attrib.keys()),
        values=('?, ' * len(row.attrib.keys()))[:-2]),
        row.attrib.values())
     print ".",
    except Exception, e:
     logging.warning(e)
     print "x",
    finally:
     row.clear()
   print "\n"
   db.commit()
   del(tree)

if __name__ == '__main__':
 dump_files(ANATHOMY.keys(), ANATHOMY)
