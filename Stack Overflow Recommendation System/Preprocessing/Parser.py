'''
Created on Nov 11, 2015

@author: shreya
'''

import sqlite3
import os
import xml.etree.cElementTree as etree
import logging
import re



Tables = {
#   
# 'badges': {
#  'Id':'INTEGER',
#  'UserId':'INTEGER',
#  'Name':'TEXT',
#  'Date':'DATETIME',
# },
# 'comments': {
#  'Id':'INTEGER',
#  'PostId':'INTEGER',
#  'Score':'INTEGER',
#  'Text':'TEXT',
#  'CreationDate':'DATETIME',
#  'UserId':'INTEGER',
# },
'PostLinks':{
    'Id':'INTEGER',
    'CreationDate':'DATETIME',
    'PostId':'INTEGER',
    'RelatedPostId':'INTEGER',
    'LinkTypeId':'INTEGER',
    },
 
 #==============================================================================
  'Posts': {
   'Id':'INTEGER',
   'PostTypeId':'INTEGER', # 1: Question, 2: Answer
   'ParentID':'INTEGER', # (only present if PostTypeId is 2)
   'AcceptedAnswerId':'INTEGER', # (only present if PostTypeId is 1)
   'CreationDate':'DATETIME',
   'Score':'INTEGER',
   'ViewCount':'INTEGER',
   'Body':'TEXT',
   'OwnerUserId':'INTEGER', # (present only if user has not been deleted)
   'LastEditorUserId':'INTEGER',
   'LastEditorDisplayName':'TEXT', #="Rich B"
   'LastEditDate':'DATETIME', #="2009-03-05T22:28:34.823"
   'LastActivityDate':'DATETIME', #="2009-03-11T12:51:01.480"
   'CommunityOwnedDate':'DATETIME', #(present only if post is community wikied)
   'Title':'TEXT',
   'Tags':'TEXT',
   'AnswerCount':'INTEGER',
   'CommentCount':'INTEGER',
   'FavoriteCount':'INTEGER',
   'ClosedDate':'DATETIME',
  },
 #==============================================================================
#  'votes': {
#   'Id':'INTEGER',
#   'PostId':'INTEGER',
#   'UserId':'INTEGER',
#   'VoteTypeId':'INTEGER',
#            # -   1: AcceptedByOriginator
#            # -   2: UpMod
#            # -   3: DownMod
#            # -   4: Offensive
#            # -   5: Favorite
#            # -   6: Close
#            # -   7: Reopen
#            # -   8: BountyStart
#            # -   9: BountyClose
#            # -  10: Deletion
#            # -  11: Undeletion
#            # -  12: Spam
#            # -  13: InformModerator
#   'CreationDate':'DATETIME',
#   'BountyAmount':'INTEGER'
#  },
#  'users': {
#   'Id':'INTEGER',
#   'Reputation':'INTEGER',
#   'CreationDate':'DATETIME',
#   'DisplayName':'TEXT',
#   'LastAccessDate':'DATETIME',
#   'WebsiteUrl':'TEXT',
#   'Location':'TEXT',
#   'Age':'INTEGER',
#   'AboutMe':'TEXT',
#   'Views':'INTEGER',
#   'UpVotes':'INTEGER',
#   'DownVotes':'INTEGER',
#   'EmailHash':'TEXT'
#   },
}



def dump_files(file_names, anathomy, 
    dump_path='/Users/arpita/Downloads/softwarerecs.stackexchange.com/',
    dump_database_name = 'softwarerecs.db',
    create_query='CREATE TABLE IF NOT EXISTS [{table}]({fields})',
    insert_query='INSERT INTO {table} ({columns}) VALUES ({values})',
    log_filename='parser.log'):

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
     
     #print str(row.attrib['PostTypeId'])
     
     #print row.attrib.values()
     #if str(row.attrib['PostTypeId'])=='1'  :   
     db.execute(insert_query.format(
            table=table_name, 
            columns=', '.join(row.attrib.keys()), 
            values=('?, ' * len(row.attrib.keys()))[:-2]),
            row.attrib.values())
     print ".",
    except Exception, e:
        logging.warning(e)
        print e,
    finally:
        row.clear()
   print "\n"
   db.commit()
   del(tree)

if __name__ == '__main__':
 dump_files(Tables.keys(), Tables)
