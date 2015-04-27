from passhash import b64_sha1
import http.cookiejar, urllib.request
import time
import datetime
import csv
from bs4 import BeautifulSoup
import getpass  
import os
import tkinter as tk

def login():
	global ent_id,ent_ps
	user = ent_id.get()
	password = ent_ps.get()
	
	if user != '' and password != '':
		downloadEPdata(user,password)
	else:
		lbl_state.configure(text="請輸入帳號或密碼!!!")

def downloadEPdata(user,password):
	lbl_state.configure(text="登入中...")
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
	
	lbl_state.configure(text="下載資料中...")
	t = time.time()
	Year = int(time.strftime('%Y', time.localtime(t)))
	Month = int(time.strftime('%m', time.localtime(t)))
	url="https://ebpps.taipower.com.tw/EBPPS/action/bill.do?myAction=queryBill&isAllInfo=no&queryType=byMonth&startDate=97%2F01&endDate="+str(Year)+"%2F"+str(Month)+"&qryOneCustNo=&Submit=%E6%9F%A5%E8%A9%A2"
	html = opener.open(url).read()
	# 處理html
	lbl_state.configure(text="處理中...")
	
	soup = BeautifulSoup(html)
	csv_content = soup.find_all(attrs={"name": "custInfoCSVFormat"})
	if csv_content != []:
		# write
		csv_content = csv_content[0]['value']
		file = open("TPdata.csv", "w", encoding='Big5')
		file.write(csv_content)
		file.close()
		lbl_state.configure(text="成功!\n檔案 TPdata.csv 已存到資料夾中")
	else:
		lbl_state.configure(text="失敗!!!\n可能是帳號打錯 或是 台電已經更新網頁\n若此問題持續發生 請聯絡網管")


#initial
window = tk.Tk()
window.title('台電電費資料下載小工具')
window.geometry('300x200')

#create a lbl
lbl_id = tk.Label(window,text='帳號')
# Entry
ent_id = tk.Entry(window)
# btn
lbl_ps = tk.Label(window,text='密碼')
# Entry
ent_ps = tk.Entry(window,show="*")
# btn
btn = tk.Button(window,text='提交',command=login)
#create a lbl
lbl_state = tk.Label(window,text='')
#pack(add)
lbl_id.pack()
ent_id.pack()
lbl_ps.pack()
ent_ps.pack()
btn.pack()
lbl_state.pack()

# # 登入
# print('<<台電電費資料下載小工具>>\n若登入成功會在將檔案放在此程式所在的資料夾\n請再將此檔案匯至系統中\n\n')
# user = input('請輸入帳號:')
# user = user.upper();
# password = getpass.getpass('請輸入密碼:') 

window.mainloop()



