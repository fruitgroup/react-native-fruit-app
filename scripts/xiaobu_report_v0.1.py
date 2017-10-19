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
# from string import Template

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
        self.__data = filter(lambda d: included_values.__contains__(d[index]), raw_data)

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
        data_of_users = data_parser.get_data_from_column_title('预约人', label_data)
        data_of_numbers = data_parser.get_data_from_column_title('预约电话', label_data)
        data_of_addresss = data_parser.get_data_from_column_title('自提网点', label_data)
        data_of_messages = data_parser.get_data_from_column_title('订单留言', label_data)
        data_of_fruit_names = data_parser.get_data_from_column_title('宝贝标题', label_data)
        data_of_fruit_amounts = data_parser.get_data_from_column_title('宝贝总数量', label_data)
        data_of_fruit_prices = data_parser.get_data_from_column_title('商品价格', label_data)


        sorted_data = {}
        for index, tel_number in enumerate(data_of_numbers):

            if not sorted_data.has_key(tel_number):
                fruit_label = FruitLabel.Label(tel_number, data_of_users[index], data_of_addresss[index], data_of_messages[index])
                sorted_data[tel_number] = fruit_label
            
            sorted_data[tel_number].fruits.append({'name': data_of_fruit_names[index], 'amount': data_of_fruit_amounts[index], 'price': data_of_fruit_prices[index]})
        
        for fruit_label in sorted_data.values():
            if not fruit_label.fruits.__len__() > FruitLabel.MAX_PRINTING_FRUIT:
                self.__labels.append(fruit_label)
            else:
                sub_fruit_label = FruitLabel.Label(fruit_label.tel, fruit_label.user, fruit_label.address, fruit_label.message)
                sub_fruit_label.fruits = fruit_label.fruits[FruitLabel.MAX_PRINTING_FRUIT:]
                fruit_label.fruits = fruit_label.fruits[:FruitLabel.MAX_PRINTING_FRUIT]
                self.__labels.append(fruit_label)
                self.__labels.append(sub_fruit_label)

    def get_datas(self):
        rows = []
        if self.__labels.__len__() == 0:
            self.__parser_data()

        for idx, label in enumerate(self.__labels):
            fruit_infos = []
            total_prices = 0
            max_fruit_categories = FruitLabel.MAX_PRINTING_FRUIT
            for fruit in label.fruits:
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

        return rows

class XiaoBuReport(object):
    ''' Xiao bu report generator'''
    def __init__(self, report_folder):
        self.__path = os.path.join(os.getcwd(),report_folder)

    def get_report_path(self):
        ''' get report folder path '''
        if not os.path.exists(self.__path):
            os.makedirs(self.__path)
        return self.__path
    
    def report_by_community(self, community_name, detail_data, csv_file_name):
        ''' report by community '''
        community_path = os.path.join(self.__path, community_name)
        detail_csv_path = os.path.join(community_path, csv_file_name)

        if  os.path.exists(community_path):
            shutil.rmtree(community_path)
        os.makedirs(community_path)

        with open(detail_csv_path, 'wb') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for row in detail_data:
                spamwriter.writerow(row)

    @staticmethod
    def fruit_summary_data(fruit_data):
        data_parser = DataParser(fruit_data)
        datas = data_parser.get_data()
        fruit_names = data_parser.get_data_from_column_title('宝贝标题', datas)
        fruit_amounts = data_parser.get_data_from_column_title('宝贝总数量', datas)
        fruit_prices = data_parser.get_data_from_column_title('商品价格', datas)
        assert fruit_names.__len__() == fruit_amounts.__len__()
        sorted_datas = {}
        for index, fruit in enumerate(fruit_names):
            if not sorted_datas.has_key(fruit):
                sorted_datas[fruit] = {'amount': int(fruit_amounts[index]), 'price': fruit_prices[index]}
            else:
                sorted_datas[fruit] = {'amount': sorted_datas[fruit]['amount'] + int(fruit_amounts[index]), 'price': fruit_prices[index]}

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

        row_datas.append( all_keys)
        row_datas.append(all_amounts) 
        row_datas.append(all_supplier_values) 
        row_datas.append(all_prices)
        row_datas.append(all_total_prices)

        return row_datas

    def report_of_financial(self,financial_data, csv_file_path):
        ''' 财务报表 '''
        fruit_datas = XiaoBuReport.fruit_summary_data(financial_data)
        Utils.write_data_to_csv(fruit_datas, csv_file_path)

    def report_of_purchase(self, purchase_data, csv_file_path):
        '''采购部分报表 '''
        fruit_datas = XiaoBuReport.fruit_summary_data(purchase_data)
        Utils.write_data_to_csv(fruit_datas[0:3], csv_file_path)

    def report_summary_by_fruit(self, fruit_summary_data, csv_file_full_path):
        with open(csv_file_full_path, 'wb') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(('水果种类', '总数'))
            for k, v in fruit_summary_data.iteritems():
                spamwriter.writerow((k, v))
 
    def report_printing_information(self, printing_data, xls_file_ful_path):
        ''' 打印信息的报表 '''
        fruit_lable = FruitLabel(printing_data)
        with open(xls_file_ful_path, 'wb') as xlsfile:
            spamwriter = csv.writer(xlsfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(FruitLabel.TITLES)
            for row in fruit_lable.get_datas():
                spamwriter.writerow(row)

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
            spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for row in datas:
                spamwriter.writerow(row)

if  __name__ == '__main__':
    CSV_DATA_PATH = sys.argv[1]
    raw_data = Utils.csv_data_from_file(CSV_DATA_PATH)
    yz = DataParser(raw_data)
    yz.filte_data('订单状态', ('等待商家发货'))
    yz_data = yz.get_data()
    yz_header = yz.get_header()

    xbr = XiaoBuReport('订单信息')
    report_path = xbr.get_report_path()
    print(xbr.get_report_path())

    xbr.report_of_purchase(raw_data, os.path.join(report_path, datetime.datetime.now().strftime('采购需求_%Y-%m-%d.csv'))) 
    xbr.report_of_financial(raw_data, os.path.join(report_path, datetime.datetime.now().strftime('财务需求_%Y-%m-%d.csv'))) 

    communities = set(yz.get_data_from_column_title('自提网点', yz_data))
    community_index = yz.index_of_key('自提网点')

    for community in communities:
        community_data = filter(lambda d: d[community_index] == community, yz_data)
        community_data.insert(0, yz.get_header())
        xbr.report_by_community(community, community_data, '订单详情.csv')
        full_path_of_fruit_printing = os.path.join(report_path, community, '打印信息.csv') 
        xbr.report_printing_information(community_data,full_path_of_fruit_printing)
