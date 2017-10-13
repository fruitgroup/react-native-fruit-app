#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import os
import csv
from string import Template

header = []

summaryTitle = ['宝贝标题', '宝贝总数']
orderStatus = ['等待商家发货']

sIdx = 3  #订单状态
uIdx = 4  #买家会员名
pIdx = 25 #自提网点
telIdx = 27 #预约电话
tIdx = 34 #宝贝标题
priceIdx = 35 # 商品价格
cIdx = 37 #宝贝总数量 
messageIdx = 41 #订单留言

maxColumn = 58 # 总列数
pickupData = {} #保存水果提取地信息
productName = {} 
userCardInfo = {} #保存用户卡片信息
userInfo = {} #保存用户信息

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
                    uIdx = h.index("买家会员名")
                    pIdx = h.index("自提网点")
                    tIdx = h.index("宝贝标题")
                    cIdx = h.index("宝贝总数量")
                    priceIdx = h.index("商品价格")
                    messageIdx = h.index("订单留言")
                    telIdx = h.index("预约电话")
                    #print (gbk2utf8(",".join(row))) 
                elif(gbk2utf8(row[sIdx]) in orderStatus):
                    if len(row[pIdx]) > 0:
                        if not pickupData.has_key(row[pIdx]):
                            pickupData[row[pIdx]] = []
                        pickupData[row[pIdx]].append(row) #[gbk2utf8(d) for d in row]

                    if len(row[tIdx]) > 0:
                        if not productName.has_key(row[tIdx]):
                            productName[row[tIdx]] = []
                        productName[row[tIdx]].append(row[cIdx])

                    if len(row[uIdx]) > 0:
                        userName = row[uIdx]
                        fruitName = row[tIdx]
                        fruitAmount = row[cIdx]
                        fruitPrice = row[priceIdx]

                        userTel = row[telIdx]
                        userMessage = row[messageIdx]
                        userAddress = row[pIdx]
                        if not userCardInfo.has_key(userName):
                            userCardInfo[userName] = []
                            userInfo[userName] = {'userTel': userTel, 'userAddress': userAddress, 'userMessage':userMessage}

                        userCardInfo[userName].append({'fruitName': fruitName, "fruitAmount": fruitAmount, "fruitPrice": fruitPrice})


if __name__ == '__main__':
    loadData(sys.argv[1])
    #print(productName)
    # summary of product
    filepath = '宝贝汇总.csv'
    htmlpath = '打印订单信息.html'
    
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

    # summary user card info
    html_start_template = '''
    <head>
	<meta charset="UTF-8">
	<title>用户订单</title>
	<style>
		* {
			margin: 0px;
			padding: 0px;
		}

		p {
			margin: 0px 5px;
		}

		div.card {
			margin: 50px 50px;
			width: 70mm;
			height: 50mm;
			border: 1px dashed #000;
			background-color: white;
			position: relative;
		}

		p.user-name {
			font-weight: bold;
			font-size: 20px;
		}

		p.user-info, p.fruit-info {
			font-size: 11px;
			overflow: hidden;
			text-overflow: ellipsis;
			white-space: nowrap;
		}

		p.total {
			font-size: 14px;
			font-weight: bold;
			text-align: right;
			position: absolute;
			bottom: 5px;
			right: 10px;
		}

		p.fruit-categroy-title {
			font-weight: bold;
			font-size: 12px;
			margin-top: 8px;
		}

		ul {
			margin-top: 2px;
			font-size: 11px;
		}

		ul li {
			margin-left: 5px;
			list-style-type: none;
		}

		span {
			overflow: hidden;
			text-overflow: ellipsis;
			white-space: nowrap;	
			display: inline-block;
		}
		span.fruitname {
			width: 40mm;
		}

		span.amount,
		span.price {
			width: 15mm;
		}
	</style>
</head>

<body>
	
    '''
    html_end_template = '''
    	
</body>

</html>

    '''
    with open(htmlpath, 'w') as html:
        html.write(html_start_template)
        for k, v in userCardInfo.iteritems():
            userName = gbk2utf8(k)
            address = gbk2utf8(userInfo[k]["userAddress"])
            message = gbk2utf8(userInfo[k]["userMessage"])
            tel = userInfo[k]["userTel"]
            #print(address,tel, message, userName)

            fruitData = []
            while True:
                if (len(v) > 4):
                    fruitData.append(v[0:4])
                    v = v[4:]
                else:
                    fruitData.append(v)
                    break

            for fruit in fruitData:
                html.write(Template('''
                <div class="card">
                <p class="user-name">$userName</p>
            <p class="user-info">电话：$tel</p>
            <p class="user-info">留言：$message</p>
            <p class="user-info ">地址：$address</p>
            <p class="fruit-categroy-title ">水果种类</p>
                ''').safe_substitute({'userName': userName, 'tel': tel, 'message': message, 'address': address}))

                totalPrice = 0
                for cardInfo in fruit:
                    fruitName =  gbk2utf8(cardInfo ['fruitName'])
                    fruitAmount = cardInfo['fruitAmount']
                    fruitPrice = cardInfo['fruitPrice']
                    totalPrice += float(fruitPrice)

                    html.write(Template('''
                        <p class="fruit-info"><span class="fruitname">$fruitName</span><span class="amount">x$fruitAmount</span> <span class="price">$fruitPrice元</span></p>
                ''').safe_substitute({'fruitName': fruitName, 'fruitAmount': fruitAmount, 'fruitPrice': fruitPrice }))    
                        
                
                html.write(Template('''
                    <p class="total">共计：$totalPrice元</p>
                    </div>
                ''').safe_substitute({'totalPrice': totalPrice}))         
                    
        html.write(html_end_template)
    print("==> 订单打印文件：" + os.getcwd() + "/" + htmlpath);

