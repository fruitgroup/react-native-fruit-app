#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
xiao bu data analysis
'''
import os
import sys
import shutil
import csv
import re
import datetime
import time
import codecs

class DataParser(object):
    '''
     Data Parser
    '''
    MAX_COLUMNS = 58
    def __init__(self, raw_data):
        self.rawData = raw_data
        self.__data = []
        self.__header = []

    def __parse_data(self):
        '''  parse data from csv file  '''
        assert (self.rawData.__len__() > 0)
        for row in self.rawData:
            if row.__len__() == DataParser.MAX_COLUMNS:
                if self.__header.__len__() == 0:
                    self.__header = row
                else:
                    self.__data.append(row)

    def index_of_key(self, key):
        ''' find index of the specified key'''
        header = self.get_header()
        return header.index(key) if header.__contains__(key) else -1

    def filte_data(self, key, included_values):
        ''' filter data by key which value is  in the included_values ''' 
        index = self.index_of_key(key)
        assert index >= 0
        raw_data = self.get_data()
        filted_data = filter(lambda d: included_values.__contains__(d[index]), raw_data)
        filted_data.insert(0, self.get_header())
        return filted_data

    def get_header(self):
        '''
            getter: header
        '''
        if self.__header.__len__() == 0:
            self.__parse_data()
        return self.__header

    def get_data(self):
        ''' getter: data '''
        if self.__data.__len__() == 0:
            self.__parse_data()
        return self.__data
    
    def get_data_from_column_title(self, title, input_data):
        ''' get column data with title name '''
        index = self.index_of_key(title)
        assert index >= 0
        return map(lambda row: row[index], input_data)

class FruitLabel(object):
    ''' the fruit printing label object '''
    MAX_PRINTING_FRUIT = 5

    class Label(object):

        def __init__(self, tel, user, address, message):
            self.user = user
            self.tel = tel
            self.address = address
            self.message = message
            self.fruits = [] #{'name', 'amount', 'price'}  
        
    TITLES = ("序号", "姓名", "电话", "地址", "水果-1数量","水果-1", "水果-2数量", "水果-2", "水果-3数量", "水果-3", "水果-4数量", "水果-4", "水果-5数量", "水果-5", "总金额", "留言")
    
    def __init__(self, fruit_data):
        self.__labels = []
        self.fruit_data = fruit_data

    def __parser_data(self):
        data_parser = DataParser(self.fruit_data)
        label_data = data_parser.get_data()
        data_of_orders = data_parser.get_data_from_column_title(XiaoBuReport.TITLE_ORDER_ID, label_data)
        data_of_users = data_parser.get_data_from_column_title(XiaoBuReport.TITLE_USER_NAME, label_data)
        data_of_numbers = data_parser.get_data_from_column_title(XiaoBuReport.TITLE_USER_PHONE, label_data)
        data_of_addresss = data_parser.get_data_from_column_title(XiaoBuReport.TITLE_COMMUNITY_POINT, label_data)
        data_of_messages = data_parser.get_data_from_column_title(XiaoBuReport.TITLE_ORDER_MESSAGE, label_data)
        data_of_fruit_names = data_parser.get_data_from_column_title(XiaoBuReport.TITLE_PRODUCT_NAME, label_data)
        data_of_fruit_amounts = data_parser.get_data_from_column_title(XiaoBuReport.TITLE_PRODUCT_AMOUNT, label_data)
        data_of_fruit_prices = data_parser.get_data_from_column_title(XiaoBuReport.TITLE_PRODUCT_PRICE, label_data)

        sorted_data = {}
        for index, order_id in enumerate(data_of_orders):
            user_name =  data_of_users[index]
            tel_number = data_of_numbers[index]

            address = XiaoBuReport.format_community_name(data_of_addresss[index]) 
            if not sorted_data.has_key(order_id):
                fruit_label = FruitLabel.Label(tel_number, user_name, address, data_of_messages[index])
                sorted_data[order_id] = fruit_label
            
            sorted_data[order_id].fruits.append({'name': data_of_fruit_names[index], 'amount': data_of_fruit_amounts[index], 'price': data_of_fruit_prices[index]})
        
        self.__labels = sorted_data.values()

    def get_datas(self):
        rows = []
        if self.__labels.__len__() == 0:
            self.__parser_data()

        for idx, label in enumerate(self.__labels):
            fruits = label.fruits

            while fruits.__len__() > 0:
                fruit_infos = []
                total_prices = 0
                max_fruit_categories = FruitLabel.MAX_PRINTING_FRUIT
                for fruit in fruits[0:5]:
                    fruit_amount = fruit['amount']
                    fruit_price = fruit['price'] 
                    fruit_name = fruit['name']
                    fruit_infos.append(fruit_amount)
                    fruit_infos.append("x %s" % (fruit_name))
                    total_prices += (int(fruit_amount) * float(fruit_price))
                    max_fruit_categories -= 1

                #水果不够Max时用空字符填充。
                while max_fruit_categories > 0:
                    fruit_infos.append("")
                    fruit_infos.append("")
                    max_fruit_categories -= 1
                fruit_infos.append(total_prices)
                fruit_infos.append(label.message)

                row = [idx+1, label.user, label.tel, label.address]
                row.extend(fruit_infos)
                rows.append(row)
                fruits = fruits[5:]

        return rows

class XiaoBuReport(object):
    ''' Xiao bu report generator'''

    TITLE_ORDER_ID = '订单ID/采购单ID'
    TITLE_COMMUNITY_POINT = '自提网点'
    TITLE_ORDER_STATUS = '订单状态'
    TITLE_PRODUCT_NAME = '宝贝标题'
    TITLE_PRODUCT_AMOUNT = '宝贝总数量'
    TITLE_PRODUCT_PRICE = '商品价格'
    TITLE_USER_PAYMENT_AMOUNT = '买家实际支付商品金额'
    TITLE_USER_NAME = '预约人'
    TITLE_USER_PHONE = '预约电话'
    TITLE_ORDER_MESSAGE = '订单留言'
    TITLE_ORDER_CREATED_DATE= '订单创建时间'
    ORDER_STATUS_OF_DELIVERED = '交易完成'
    ORDER_STATUS_OF_UNDELIVERED = '等待商家发货'

    DRI_TEL_MAP = {
        '13689700006': '李海', 
        '15104030086': '黄旭玲', 
        '18842410372': '何志强',
        '15041205708': '冯兴龙',
        '13810992951': '刘鹤',
        '15304022399': '刘铁磊',
        '15940087939': '宋利燕',
        '13897932270': '王亚平',
        '13897926945': '陈志扬',
        '13322496960': '朱莹',
        '15998336739': '金吉营',
        '15004038283': '隋明发',
        '18640520539': '王鹭',
        '18040036608': '冮星光',
        '18624034797': '邓铁梅',
        }

    @staticmethod
    def format_community_name(title):
        ''' 格式化小区名 '''
        m = re.match('^(.*\s*[-]\s*.*?)\s+', title)
        name = m.group(1) if m else title
        return name.strip()

    def __init__(self, report_folder):
        self.__path = os.path.join(os.getcwd(),report_folder)
        self.__community_labels = {}

    def get_report_path(self):
        ''' get report folder path '''
        if not os.path.exists(self.__path):
            os.makedirs(self.__path)
        return self.__path
    
    def report_order_details_by_community(self, community_name, detail_data, csv_file_name):
        ''' report by community '''
        community_path = os.path.join(self.__path, community_name)
        detail_csv_path = os.path.join(community_path, csv_file_name)

        if  os.path.exists(community_path):
            shutil.rmtree(community_path)
        os.makedirs(community_path)
        Utils.write_data_to_csv(detail_data, detail_csv_path)

    def sort_data_by_fruit(self, fruit_data):
        data_parser = DataParser(fruit_data)
        datas = data_parser.get_data()
        fruit_names = data_parser.get_data_from_column_title(XiaoBuReport.TITLE_PRODUCT_NAME, datas)
        fruit_amounts = data_parser.get_data_from_column_title(XiaoBuReport.TITLE_PRODUCT_AMOUNT, datas)
        fruit_prices = data_parser.get_data_from_column_title(XiaoBuReport.TITLE_PRODUCT_PRICE, datas)
        assert fruit_names.__len__() == fruit_amounts.__len__()
        sorted_datas = {}
        for index, fruit in enumerate(fruit_names):
            if not sorted_datas.has_key(fruit):
                sorted_datas[fruit] = {'amount': int(fruit_amounts[index]), 'price': fruit_prices[index]}
            else:
                sorted_datas[fruit] = {'amount': sorted_datas[fruit]['amount'] + int(fruit_amounts[index]), 'price': fruit_prices[index]}
        return sorted_datas

    def __fruit_summary_data(self, fruit_data):
        sorted_datas = self.sort_data_by_fruit(fruit_data)
        row_datas = []
        all_keys = sorted_datas.keys()
        all_amounts = [sorted_datas[k]['amount'] for k in all_keys]
        all_prices = [sorted_datas[k]['price'] for k in all_keys]
        all_supplier_values = []
        all_total_prices = []
        for idx, x in enumerate(all_keys):
            m = re.match('^.*\/(\d+).*$', x)
            multiple = m.group(1) if m else 1
            all_supplier_values.append(int(multiple) * int(all_amounts[idx]))
            all_total_prices.append(float(all_prices[idx]) * int(all_amounts[idx]))
        all_keys.insert(0, '明细')
        all_amounts.insert(0, '系统下单数量')
        all_supplier_values.insert(0, '供应商数量')
        all_prices.insert(0, '水果单价') 
        all_total_prices.insert(0, '各水果销售总额数')

        row_datas.append(all_keys)
        row_datas.append(all_amounts) 
        row_datas.append(all_supplier_values) 
        row_datas.append(all_prices)
        row_datas.append(all_total_prices)

        return row_datas
    
    def __community_analysis_data(self, community_data):
        ''' 按小区分析营收情况 '''
        community_data_parser = DataParser(community_data)  
        datas = community_data_parser.get_data()
        index_of_community = community_data_parser.index_of_key(XiaoBuReport.TITLE_COMMUNITY_POINT)
        index_of_tel = community_data_parser.index_of_key(XiaoBuReport.TITLE_USER_PHONE)
        index_of_order = community_data_parser.index_of_key(XiaoBuReport.TITLE_ORDER_ID)
        index_of_price = community_data_parser.index_of_key(XiaoBuReport.TITLE_PRODUCT_PRICE)
        index_of_amount = community_data_parser.index_of_key(XiaoBuReport.TITLE_PRODUCT_AMOUNT)
        index_of_order_create_date = community_data_parser.index_of_key(XiaoBuReport.TITLE_ORDER_CREATED_DATE)
        analysis_entries = {}

        xiaobo_turnover = 0

        for row in datas:
            community_name = XiaoBuReport.format_community_name(row[index_of_community])
            user_payment_amount = float(row[index_of_price]) * float(row[index_of_amount])
            timestamp = time.mktime(time.strptime(row[index_of_order_create_date], '%Y-%m-%d %H:%M:%S'))
            user_tel = row[index_of_tel]
            m = re.match('.*\s+(\d+)\s*$', row[index_of_community])
            tel = m.group(1) if m else "未知电话"
            user = XiaoBuReport.DRI_TEL_MAP[tel] if XiaoBuReport.DRI_TEL_MAP.has_key(tel) else "未知负责人"


            if not analysis_entries.has_key(community_name):
                entry = {
                'tel': tel, 
                'user': user, 
                'community': community_name, 
                'community_turnover': 0, 
                'start_timestamp': timestamp,
                'end_timestamp': timestamp,
                'dri_payment': 0.0,
                'orders': [],
                }
                analysis_entries[community_name] = entry

            if not analysis_entries[community_name]['orders'].__contains__(row[index_of_order]):
                analysis_entries[community_name]['orders'].append(row[index_of_order]) 

            analysis_entries[community_name]['community_turnover'] += user_payment_amount
            analysis_entries[community_name]['start_timestamp'] = timestamp if analysis_entries[community_name]['start_timestamp'] > timestamp else analysis_entries[community_name]['start_timestamp']
            analysis_entries[community_name]['end_timestamp'] = timestamp if analysis_entries[community_name]['end_timestamp'] < timestamp else analysis_entries[community_name]['end_timestamp']

            if tel == user_tel:
                analysis_entries[community_name]['dri_payment'] += user_payment_amount

            xiaobo_turnover += user_payment_amount

        analysis_entries['xiaobu_turnover'] = xiaobo_turnover

        return analysis_entries

    def report_of_financial(self,financial_data, financial_file_path):
        ''' 财务报表 '''
        fruit_datas = self.__fruit_summary_data(financial_data)
        Utils.write_data_to_xls(fruit_datas, financial_file_path)

    def report_of_purchase(self, purchase_data, purchase_file_path):
        '''采购报表 '''
        fruit_datas = self.__fruit_summary_data(purchase_data)
        Utils.write_data_to_xls(fruit_datas[0:3], purchase_file_path)

    def report_printing_information(self, community_name, printing_data, xls_file_name):
        ''' 打印信息的报表 '''
        community_path = os.path.join(self.__path, community_name)
        full_xls_path = os.path.join(community_path, xls_file_name)
        fruit_lable = FruitLabel(printing_data)
        file_datas = fruit_lable.get_datas()
        self.__community_labels[community_name] = file_datas.__len__()
        file_datas.insert(0, FruitLabel.TITLES)
        Utils.write_data_to_xls(file_datas, full_xls_path)

    def report_of_sales(self, sales_data, sales_file_path):
        ''' 销售报表 '''
        sales_report_title =('序号', '小区名称', '小区负责人', '电话', '小布总营业额(元)', '小区营业额(元)', '负责人购买(元)', '营业额占比', '总利润', '小区负责人营收(元)', '统计时间段', '备注')
        sales_entries = self.__community_analysis_data(sales_data)
        xiaobu_turnover = sales_entries.pop('xiaobu_turnover')
        idx = 1
        report_data = [sales_report_title]
        for communities_data in sales_entries.values():
            community = communities_data['community']
            user = communities_data['user']
            tel = communities_data['tel']
            community_turnover = communities_data['community_turnover']
            dri_payment = communities_data['dri_payment']
            community_turnover_rate = "%.2f %%" % ((community_turnover / xiaobu_turnover) * 100)
            start_date = time.strftime('%Y-%m-%d', time.localtime(communities_data['start_timestamp']))
            end_date = time.strftime('%Y-%m-%d', time.localtime(communities_data['end_timestamp']))
            periods = "%s -%s" % (start_date, end_date)
            gross_profit = ""
            dri_revenue = ""
            mark = ""
            row_data = (idx, community, user, tel, xiaobu_turnover, community_turnover, dri_payment, community_turnover_rate, gross_profit,dri_revenue, periods, mark)
            report_data.append(row_data)
            idx += 1
        Utils.write_data_to_xls(report_data, sales_file_path)
    
    def report_of_revenue(self, revenue_data, revenue_file_path):
        ''' 营收报表 '''
        revenue_report_title =('序号', '小区名称', '小区负责人', '电话', '小区营业额(元)', '负责人购买(元)', '营业额比例', '小区利润收入', '下单数','标签总数（下单编号）', '时间', '备注')
        revenue_entries = self.__community_analysis_data(revenue_data)
        xiaobu_turnover = revenue_entries.pop('xiaobu_turnover')

        idx = 1
        report_data = [revenue_report_title]
        for communities_data in revenue_entries.values():
            community = communities_data['community']
            user = communities_data['user']
            tel = communities_data['tel']
            community_turnover = communities_data['community_turnover']
            dri_payment = communities_data['dri_payment']
            turnover_rate = "%.2f%%" % ((community_turnover / xiaobu_turnover)*100)
            community_profit = ""
            count_of_orders =  communities_data['orders'].__len__()
            report_date = time.strftime('%Y-%m-%d', time.localtime(communities_data['end_timestamp']))
            count_of_tags = self.__community_labels[community] if self.__community_labels.has_key(community) else 0 #communities_data['orders_of_count']
            mark = ""
            row_data = (idx, community, user, tel, community_turnover, dri_payment, turnover_rate, community_profit, count_of_orders, count_of_tags, report_date, mark)
            report_data.append(row_data)
            idx += 1
        Utils.write_data_to_xls(report_data, revenue_file_path)   
        
    def report_of_logistics(self, logistics_data, logistics_fiile_path):
        ''' 分装物流报表 '''
        row_datas=[]
        title = reduce(lambda t, v: list(set(t) | set(v.keys()))  ,logistics_data.values())
        for community_name, sorted_data in logistics_data.iteritems():
            row_data = map(lambda f: sorted_data[f]["amount"] if sorted_data.has_key(f) else 0, title)
            row_datas.append([community_name]+ row_data)
        title.insert(0, "明细")
        row_datas.insert(0, title)
        Utils.write_data_to_xls(row_datas, logistics_fiile_path)



class Utils(object):
    ''' utils '''

    @staticmethod
    def csv_data_from_file(csv_file_path):
        ''' read data from csv file '''
        csv_data = []
        with open (csv_file_path, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                csv_data.append([d.decode('gb18030').encode('utf8') for d in row])
        return csv_data

    @staticmethod
    def write_data_to_csv(datas, csv_file_path):
        ''' write data to csv file '''
        with open(csv_file_path, 'wb') as csvfile:
            csvfile.write(codecs.BOM_UTF8)
            spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for row in datas:
                spamwriter.writerow(row)
    
    @staticmethod
    def write_data_to_xls(datas, xls_file_path):
        ''' write data to xls file '''
        if datas.__len__() == 0: 
            return
        xls_start_template = '''<html>
        <head> <meta charset="UTF-8"> </head>
         <table border="1">
        '''
        xls_end_template = '''</table>
         </html>'''
        with open(xls_file_path, 'wb') as xlsfile:
            xlsfile.write(xls_start_template)
            xls_header_data = datas[0]
            xlsfile.write("<thead>\n<th>" + "</th><th>".join(xls_header_data) + "</th>\n</thead> \n")
            xls_body_data = datas[1:]

            if xls_body_data.__len__() > 0:
                xlsfile.write("<tbody>\n")
                for row in xls_body_data:
                    xlsfile.write("<tr><td>" + "</td><td>".join([str(d) for d in row]) + "</td></tr>\n")
                xlsfile.write("</tbody>\n")
            xlsfile.write(xls_end_template)

def main(input_file_path):
    ''' 程序入口 函数'''
    if not os.path.exists(input_file_path):
        print("警告：输入文件不存在！")
        return

    raw_data = Utils.csv_data_from_file(input_file_path)
    xbr = XiaoBuReport('小布报表')
    report_path = xbr.get_report_path()
    print("报表路径: " + xbr.get_report_path())

    Utils.write_data_to_csv(raw_data, os.path.join(report_path, os.path.basename(input_file_path)))

    data_parser = DataParser(raw_data)
    undelivered_orders = data_parser.filte_data(XiaoBuReport.TITLE_ORDER_STATUS, (XiaoBuReport.ORDER_STATUS_OF_UNDELIVERED))
    delivered_orders = data_parser.filte_data(XiaoBuReport.TITLE_ORDER_STATUS, (XiaoBuReport.ORDER_STATUS_OF_DELIVERED))
    both_delivered_and_undelivered_orders = data_parser.filte_data(XiaoBuReport.TITLE_ORDER_STATUS, (XiaoBuReport.ORDER_STATUS_OF_DELIVERED, XiaoBuReport.ORDER_STATUS_OF_UNDELIVERED))
    # 按小区分类生成相关的报表
    undelivered_data = undelivered_orders[1:]
    communities = set(data_parser.get_data_from_column_title(XiaoBuReport.TITLE_COMMUNITY_POINT, undelivered_data))
    community_index = data_parser.index_of_key(XiaoBuReport.TITLE_COMMUNITY_POINT)

    sorted_data_by_communities = {}
    for community in communities:
        community_name = XiaoBuReport.format_community_name(community)
        community_data = filter(lambda d: d[community_index] == community, undelivered_data)
        community_data.insert(0, data_parser.get_header())
        sorted_data_by_communities[community_name]=xbr.sort_data_by_fruit(community_data)
        xbr.report_order_details_by_community(community_name, community_data, '订单详情.csv')
        xbr.report_printing_information(community_name, community_data, '打印信息.xls')

    if sorted_data_by_communities.keys().__len__() > 0:
        xbr.report_of_logistics(sorted_data_by_communities, os.path.join(report_path, datetime.datetime.now().strftime('分装物流需求_%Y-%m-%d.xls')))
    else:
        print("警告：没有找到分装物流数据，分装物流报表生成失败!")

    if  delivered_orders.__len__() > 1: 
        xbr.report_of_sales(delivered_orders, os.path.join(report_path, datetime.datetime.now().strftime('小布销售统计_%Y-%m-%d.xls')))
    else:
        print("警告：没有找到销售数据，销售报表生成失败!")
   
    if both_delivered_and_undelivered_orders.__len__() > 1:
        xbr.report_of_sales(both_delivered_and_undelivered_orders, os.path.join(report_path, datetime.datetime.now().strftime('财务统计_%Y-%m-%d.xls')))
    else:
       print("警告：没有找到财务统计数据，财务统计报表生成失败!") 

    if undelivered_data.__len__() > 1:
        xbr.report_of_purchase(undelivered_orders, os.path.join(report_path, datetime.datetime.now().strftime('采购需求_%Y-%m-%d.xls'))) 
        xbr.report_of_financial(undelivered_orders, os.path.join(report_path, datetime.datetime.now().strftime('财务需求_%Y-%m-%d.xls'))) 
        xbr.report_of_revenue(undelivered_orders, os.path.join(report_path, datetime.datetime.now().strftime('小区单次营收统计_%Y-%m-%d.xls')))
    else:
        print("警告：没有找到待发货数据，采购报表生成失败!") 

if  __name__ == '__main__':
    if sys.argv.__len__() != 2:
        print("usage: <script> <input_csv_file>")
        sys.exit(-1)
    main(sys.argv[1])

 
