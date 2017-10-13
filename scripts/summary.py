#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import os
import csv

header = []

summaryTitle = ['宝贝标题', '宝贝总数']
orderStatus = ['等待商家发货']

sIdx = 3  #订单状态
pIdx = 25 #自提网点
tIdx = 34 #宝贝标题
cIdx = 37 #宝贝数量 

maxColumn = 57 # 总列数
pickupData = {}
productName = {}

def gbk2utf8(string):
    return string.decode('gb18030').encode('utf8')

def loadData(csvPath):
    global header
    with open (csvPath, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            if len(row) == maxColumn:
                if len(header) == 0:
                    header= row #[gbk2utf8(d) for d in row]
                elif(gbk2utf8(row[sIdx]) in orderStatus):
                    if len(row[pIdx]) > 0:
                        if not pickupData.has_key(row[pIdx]):
                            pickupData[row[pIdx]] = []
                        pickupData[row[pIdx]].append(row) #[gbk2utf8(d) for d in row]

                    if len(row[tIdx]) > 0:
                        if not productName.has_key(row[tIdx]):
                            productName[row[tIdx]] = []
                        productName[row[tIdx]].append(row[cIdx])

if __name__ == '__main__':
    loadData(sys.argv[1])

    # summary of product
    filepath = '宝贝汇总.csv'
    print("==> 输出路径：" + os.getcwd() + "/" +filepath);
    with open(filepath, 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(summaryTitle);
        for k, v in productName.iteritems():
            if len(v) > 0:
                spamwriter.writerow([gbk2utf8(k),reduce(lambda x,y:int(x)+int(y),v)]);

    # summary of pickup place
    for k, v in pickupData.iteritems():
        summary = {}
        filePath = gbk2utf8(k) + '.csv'
        print(filePath)
        with open(filePath, 'wb') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow([gbk2utf8(d) for d in header]);
            for row in v:
                spamwriter.writerow([gbk2utf8(d) for d in row]);
                if len(row[tIdx]) > 0:
                    if not summary.has_key(row[tIdx]):
                        summary[row[tIdx]] = []
                    summary[row[tIdx]].append(row[cIdx])

            spamwriter.writerow(['============>']);
            spamwriter.writerow(['Summary']);
            spamwriter.writerow(['============>']);
            for k,v in summary.iteritems():
                if len(v) > 0:
                    spamwriter.writerow([gbk2utf8(k),reduce(lambda x,y:int(x)+int(y),v)]);
