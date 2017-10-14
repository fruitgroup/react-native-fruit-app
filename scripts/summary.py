#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import os
import shutil
import csv
from string import Template

header = []

summaryTitle = ['宝贝标题', '宝贝总数']
orderStatus = ['等待商家发货']

sIdx = 3  #订单状态
pIdx = 25 #自提网点
telIdx = 27 #预约电话
uIdx = 28  #预约人
tIdx = 34 #宝贝标题
priceIdx = 35 # 商品价格
cIdx = 37 #宝贝总数量 
messageIdx = 41 #订单留言

maxColumn = 58 # 总列数
sortedData = {} #保存水果提取地信息
productName = {} 

def gbk2utf8(string):
    return string.decode('gb18030').encode('utf8')

def loadData(csvPath):
    global header
    with open (csvPath, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            if len(row) == maxColumn:
                #print (gbk2utf8(",".join(row))) 
                if len(header) == 0:
                    header= row 
                    h = [gbk2utf8(d) for d in header]
                    sIdx = h.index("订单状态")
                    uIdx = h.index("预约人")
                    pIdx = h.index("自提网点")
                    tIdx = h.index("宝贝标题")
                    cIdx = h.index("宝贝总数量")
                    priceIdx = h.index("商品价格")
                    messageIdx = h.index("订单留言")
                    telIdx = h.index("预约电话")
                    #print (gbk2utf8(",".join(row))) 
                elif(gbk2utf8(row[sIdx]) in orderStatus):
                    if len(row[pIdx]) > 0:
                        userAddress = row[pIdx]
                        if not sortedData.has_key(userAddress):
                            sortedData[userAddress] = {'rawData':[], 'fruitCardData': {}}
                        sortedData[userAddress]['rawData'].append(row) #[gbk2utf8(d) for d in row]
                        
                        userName = row[uIdx]
                        fruitName = row[tIdx]
                        fruitAmount = row[cIdx]
                        fruitPrice = row[priceIdx]

                        userTel = row[telIdx]
                        userMessage = row[messageIdx]

                        uniqueKey = userTel

                        if not sortedData[userAddress]['fruitCardData'].has_key(uniqueKey):
                            sortedData[userAddress]['fruitCardData'][uniqueKey] = {'userInfo': {'userName':userName, 'userTel': userTel, 'userAddress': userAddress, 'userMessage':userMessage}, 'fruitInfo': []}
                            # userInfo[userName] = {'userTel': userTel, 'userAddress': userAddress, 'userMessage':userMessage}
                        sortedData[userAddress]['fruitCardData'][uniqueKey]['fruitInfo'].append({'fruitName': fruitName, "fruitAmount": fruitAmount, "fruitPrice": fruitPrice})
                    
                    if len(row[tIdx]) > 0:
                        if not productName.has_key(row[tIdx]):
                            productName[row[tIdx]] = []
                        productName[row[tIdx]].append(row[cIdx])



def dumpCellSummary(outputPath, header,data):
    summary = {}
    with open(outputPath, 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow([gbk2utf8(d) for d in header]);
        for row in data:
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

def dumpFruit(outputPath,fruitCardData):
    #print(fruitCardData)
    html_start_template = '''
    <html>
<head>
    <meta charset="UTF-8">
</head>
<table border="1">
    <thead>
        <th>序号</th>
        <th>姓名</th>
        <th>电话</th>
        <th>地址</th>
        <th>水果-1</th>
        <th>水果-2</th>
        <th>水果-3</th>
        <th>水果-4</th>
        <th>水果-5</th>
        <th>水果-6</th>
        <th>总金额</th>
        <th>留言</th>
    </thead>

    <tbody>
    '''
    html_end_template = '''
        </tbody>
</table>

</html>
    '''
    with open(outputPath, 'w') as html:
        html.write(html_start_template)
        fruitDataIndex = 0
        for k, v in fruitCardData.iteritems():
            userName = gbk2utf8(v['userInfo']["userName"])
            address = gbk2utf8(v['userInfo']["userAddress"])
            message = gbk2utf8(v['userInfo']["userMessage"])
            tel = v['userInfo']["userTel"]
            #print(address,tel, message, userName)

            fruitData = []
            fruitInfo = v['fruitInfo']
            while True:
                #最多存放6行水果信息
                if (len(fruitInfo) > 6):
                    fruitData.append(fruitInfo[0:6])
                    fruitInfo =fruitInfo[6:]
                else:
                    fruitData.append(fruitInfo)
                    break

            for fruit in fruitData:
                fruitDataIndex += 1
                html.write(Template('''
                       <tr>
            <td>$orderList</td>
            <td>$userName</td>
            <td>$tel</td>
            <td>$address</td>
            ''').safe_substitute({'userName': userName, 'tel': tel, 'address': address, 'orderList': str(fruitDataIndex)}))

                totalPrice = 0
                maxFruitData = 6
                for cardInfo in fruit:
                    maxFruitData -= 1
                    fruitName =  gbk2utf8(cardInfo ['fruitName'])
                    fruitAmount = cardInfo['fruitAmount']
                    fruitPrice = cardInfo['fruitPrice']
                    totalPrice += float(fruitPrice)
                    html.write(Template('''<td>$fruitAmount x  $fruitName </td>''').safe_substitute({'fruitName': fruitName, 'fruitAmount': fruitAmount}))
                
                # 补空缺
                while maxFruitData > 0:
                    maxFruitData -= 1
                    html.write('''<td></td>''')
 
                html.write(Template('''
            <td>$totalPrice</td>
            <td>$message</td>
            </tr> ''').safe_substitute({'totalPrice': totalPrice, 'message': message}))         
                    
        html.write(html_end_template)

if __name__ == '__main__':
    loadData(sys.argv[1])
    #print(productName)
    # summary of product
    outputDir = os.path.join(os.getcwd(), '订单信息')
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    print("==> 输出路径：" + outputDir);

    csvPath = os.path.join(outputDir, '宝贝汇总.csv')
    with open(csvPath, 'w') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(summaryTitle);
        for k, v in productName.iteritems():
            if len(v) > 0:
                spamwriter.writerow([gbk2utf8(k),reduce(lambda x,y:int(x)+int(y),v)]);

    # summary
    for k, v in sortedData.iteritems():
        directory = gbk2utf8(k)
        filePath = os.path.join(outputDir, directory)
        if os.path.exists(filePath):
            shutil.rmtree(filePath)
        os.makedirs(filePath)
        fullPath = os.path.join(filePath, '订单摘要.csv')
        xlsPath = os.path.join(filePath, '订单打印信息.xls')
        dumpCellSummary(fullPath, header, v['rawData'])
        dumpFruit(xlsPath, v['fruitCardData'])
        #print(filePath)


