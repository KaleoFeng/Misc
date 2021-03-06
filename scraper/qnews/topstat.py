#!/usr/bin/env python
#  -*- coding:utf-8 -*-

import io
import json
import pymysql
import sys
import time
import urllib.parse
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

def requestPost(url, headers, params):
    data = urllib.parse.urlencode(params).encode('utf-8')
    req = urllib.request.Request(url=url, headers=headers, data=data, method='POST')
    rsp = urllib.request.urlopen(req)
    result = json.loads(rsp.read().decode('utf-8'))
    return result

def writeIntoFile(jsonName, records):
    jsonFile = open(jsonName, 'w')
    json.dump(records, jsonFile, indent=4)
    jsonFile.close()
    print('Write into json file[%s] done' % jsonName)

def writeIntoDB(tableName, records):
    db = pymysql.connect(host ='127.0.0.1', user = 'root', passwd = '123456', db = 'album', charset = 'utf8mb4')
    cursor = db.cursor()

    # Current time, ingore seconds
    now = int(time.time())
    now -= now % 60

    # Write each record
    for record in records:
        sql = "INSERT INTO %s VALUES(0, '%d', '%s', '%d', '%d')" % (tableName, record['id'], record['name'], record['count'], now)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
            print('Insert record[%d] error!' % record['id'])
    
    db.close()
    print('Write into db table[%s] done' % tableName)

# Crawl data
url = 'http://yc.static.qq.com/?service=App.StarList_ApiStarListsl7.RankingList'
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Connection': 'close',
    'Referer': 'http://news.qq.com/zt2018/cwei/app.htm?ADTAG=wx.pyq&listid=17&uid=151656&sid=640&have=true&appinstall=0&from=singlemessage&isappinstalled=0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
}
params = {
    'seasonId': 17,
    'userId': ''
}
result = requestPost(url, headers, params)

# Filter data
stats = {}
stats['list'] = []
for info in result['data']['list']:
    stat = {} 
    stat['id'] = int(info['id'])
    stat['count'] = int(info['count'])
    stat['name'] = info['name']
    stats['list'].append(stat)
    print(stat)

# Write into mysql db
writeIntoDB('tab_qnews_topstat', stats['list'])

# Write into json file
statTime = time.strftime('%Y-%m-%d-%H-%M', time.localtime(time.time()))
jsonName = 'qnews_topstat_' + statTime + '.json'
writeIntoFile(jsonName, stats)
