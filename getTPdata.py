from passhash import b64_sha1
import http.cookiejar, urllib.request
import time
import datetime
import csv
from bs4 import BeautifulSoup
import getpass  
import os
import sys
from io import StringIO
import io
import pymysql

def downloadEPdata(user,password):
	print("Login...")
	temp_ps = b64_sha1(password)+'='
	PWDtemp = "**********"
	login_page = "https://ebpps.taipower.com.tw/EBPPS/action/conLogin.do?account="+user+"&myAction=password"  
	login_page_2 = "https://ebpps.taipower.com.tw/EBPPS/action/conLogin.do?myAction=check_PWD&old_hash="+temp_ps+"&words2=HYCAPI_INSTEAD&words="+PWDtemp
	# cookie登入
	cj = http.cookiejar.CookieJar()
	opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
	opener.open(login_page)
	opener.open(login_page_2)
	# 擷取資料
	
	print("Downloading...")
	t = time.time()
	Year = int(time.strftime('%Y', time.localtime(t)))
	Month = int(time.strftime('%m', time.localtime(t)))
	# 
	url="https://ebpps.taipower.com.tw/EBPPS/action/bill.do?myAction=queryBill&isAllInfo=no&queryType=byMonth&startDate=97%2F01&endDate="+str(Year)+"%2F"+str(Month)+"&qryOneCustNo=&Submit=%E6%9F%A5%E8%A9%A2"
	html = opener.open(url).read()
	# 處理html 9701
	print("Analyzing...")
	
	soup = BeautifulSoup(html)
	csv_content = soup.find_all(attrs={"name": "custInfoCSVFormat"})
	
	if csv_content != []:
		print("Parsing...")
		# write
		csv_content = csv_content[0]['value'].encode("utf8", 'ignore').decode('utf8')
		f = io.StringIO(csv_content)
		reader = csv.reader(f, delimiter=',')
		# del reader[0]
		next(reader)
		# connect to mysql
		conn = pymysql.connect(host='localhost', user='client', passwd='1qaz2wsx', db='dorm')
		cur = conn.cursor()
		cur.execute("SET NAMES 'UTF8'")
		#send to mysql
		for row in reader:
			# print('\t'.join(row))
			enum = row[0].replace('-','');
			# print(row[0]);

			# getTPdata from mysql check enum exist
			sql = """SELECT `electro_id`,`monthly` from `electronum`  where `electronum`.`electro_num` ='%s'""" % (enum.encode("utf8", 'ignore').decode('utf8')) ;
			# print(sql)
			cur.execute(sql)
			enumdata = cur.fetchone()
			if enumdata is not None:
				electro_id = enumdata[0]
				year = int(row[2].split('年')[0])+1911;
				month = int(row[2].split('年')[1].split('月')[0]);
				kwh = int(row[3]);
				efee = int(row[4].split('元')[0]);

				# check readd
				sql = """SELECT COUNT(`electrodata`.`electro_id`) as `count`from `electrodata`left join `electronum` on `electronum`.`electro_id` = `electrodata`.`electro_id` where `electronum`.`electro_num` = '%s' and `year` = '%d' and `month` = '%d'""" % (enum,year,month);
				cur.execute(sql)
				count = int(cur.fetchone()[0])
				# print(count)
				if count==0:
					if enumdata[1]==1: #bimonthly
						kwh = kwh/2;
						efee = efee/2;
						sql = """INSERT INTO `electrodata` (	`electro_id`,`kwh`,`efee`,`year`,`month`,`m_id`) VALUES(		'%s','%d',	'%d','%d','%d','0')""" % (electro_id,kwh,efee,year,month);
						cur.execute(sql)
						conn.commit()	
						if  month==1:
							year = year-1;
							month = 12;
						else:
							month = month-1;
						sql = """INSERT INTO `electrodata` (	`electro_id`,`kwh`,`efee`,`year`,`month`,`m_id`) VALUES(		'%s','%d',	'%d','%d','%d','0')""" % (electro_id,kwh,efee,year,month);
						cur.execute(sql)
						conn.commit()
						pass
						print('success')
					elif enumdata[1]==0 :#monthly
						sql = """INSERT INTO `electrodata` (	`electro_id`,`kwh`,`efee`,`year`,`month`,`m_id`) VALUES(		'%s','%d',	'%d','%d','%d','0')""" % (electro_id,kwh,efee,year,month);
						cur.execute(sql)
						conn.commit()	
						print('success')
						pass
					pass
				else:
					print('Wrong:There\'s a duplicate data.' )
					# duplicate
				pass
			else:
				print('Wrong:There\'s no this enum in database.' )
				# no enum
		# file = open("TPdata.csv", "w", encoding='utf8')
		# file.write(csv_content)
		# file.close()
		print("done")
	else:
		print("failed")

if len(sys.argv)==3:
	downloadEPdata(sys.argv[1],sys.argv[2])
	pass
else:
	print("failed")





