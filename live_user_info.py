import requests
import json
import time
import sqlite3
#import random
from multiprocessing import Process
from bs4 import BeautifulSoup
conn_live=sqlite3.connect('/Users/yohane/Documents/DataBase/Bilibili_live_info.db')
cursor_live=conn_live.cursor()
live_url=('http://api.live.bilibili.com/live/getInfo?roomid={}')
live_tag='http://live.bilibili.com/{}'



HEADER = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
    'Connection': 'keep-alive',
    'Accept-Encoding': 'gzip, deflate, sdch'
}



HEADER_JSON={
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, sdch',
    'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
    'Cache-Control':'max-age=0',
    'Host':'api.live.bilibili.com',
    'Upgrade-Insecure-Requests':1,
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
}



conn=sqlite3.connect('/Users/yohane/Documents/DataBase/Bilibili_User_info.db')
cursor=conn.cursor()
'''
proxies_conn=sqlite3.connect('/Users/yohane/Documents/DataBase/IP_PROXY.db')
proxies_cursor=proxies_conn.cursor()
results=proxies_cursor.execute('SELECT * FROM IP_POOL')
IP_POOL=[]
for ip_address in results:
     IP_POOL.append(ip_address)
cursor.execute('DELETE FROM USER_INFO')
for i in results:
     IP_POOL.append(i)
proxies={
    'http':str(random.choice(IP_POOL)).replace('(','').replace(')','').replace(',','').replace("'",'')
}
'''



def Get_time():
    current_time = int(round(time.time() * 1000))
    return current_time

headers={
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'http://space.bilibili.com/12132144/',
    'Origin': 'http://space.bilibili.com',
    'Host': 'space.bilibili.com',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6'
}




def Get_user_info():
    try:
        for User_counts in range(1,30000000):
            data_list={
                'mid':User_counts,
                '_':Get_time()
            }
            target_url='http://space.bilibili.com/ajax/member/GetInfo'
            wb_data=requests.post(target_url,data=data_list,headers=headers)
            '''
            try:
                wb_data=requests.post(target_url,data=data_list,headers=headers
            except ConnectionError:
                wb_data=requests.post(target_url,data=data_list,headers=headers,proxies=proxies)   这里挂代理行不通,水平有限修正不了.
            '''
            info_list=json.loads(wb_data.content.decode('utf-8'))
            if info_list['status']==True:
                    face_img=info_list['data']['face']
                    name=info_list['data']['name']
                    uid=info_list['data']['mid']
                    sex=info_list['data']['sex']
                    sign=info_list['data']['sign']
                    desc=info_list['data']['official_verify']['desc']
                    fans=info_list['data']['fans']
                    focus=info_list['data']['friend']
                    level_info=info_list['data']['level_info']['current_level']
                    if info_list['data']['place'] :    ##考虑到短路求值的特性没有用逻辑运算
                        place=info_list['data']['place']
                    else:
                        place='None'
                    if info_list['data']['regtime']:
                        regtime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(info_list['data']['regtime']))
                    else:
                        regtime='None'
                    if info_list['data']['birthday']:
                        birthday=info_list['data']['birthday']
                    else:
                        birthday='None'
                    cursor.execute("INSERT INTO USER_INFO(face_img,name,udi,sex,sign,desc,place,fans,focus,birthday,level_info,regtime) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",(face_img,name,uid,sex,sign,desc,place,fans,focus,birthday,level_info,regtime))
    except Exception as e:
        print (e)
        
        
        
        
def Get_Live_info():
    try:
        for roomid in range(1001,1000000):
            List_Tag=[]
            wb_data=requests.get(live_url.format(roomid)).content
            wb=requests.get(live_tag.format(roomid),headers=HEADER)
            soup=BeautifulSoup(wb.text,'lxml')
            live_tag_select=soup.find_all('div',class_='live-tag')
            if soup.find('a',class_='bili-link'):
                live_category=soup.find('a',class_='bili-link').text
            else:
                live_category='None'
            if live_tag_select:
                for result in live_tag_select:
                    if result:
                        List_Tag.append(result.text)
            live_info=json.loads(wb_data.decode('utf-8'))
            TAGS=' '.join(List_Tag)
            if live_info['code']!=-400:
                fans=live_info['data']['FANS_COUNT']
                name=live_info['data']['ANCHOR_NICK_NAME']
                gift_counts=live_info['data']['RCOST']
                cursor_live.execute("INSERT INTO LIVE_INFO(FANS,NAME,GIFTS,TAG,category) VALUES (?,?,?,?,?)",(fans,name,gift_counts,TAGS,live_category))
            List_Tag=[]
            TAGS=''
    except Exception as e:
        print(e)
        
        
        
        
Procs=Process(target=Get_Live_info())
p=Process(target=Get_user_info())
Procs.start()
p.start()
Procs.join()
p.join()
'''
    proxies_cursor.close()
    proxies_conn.commit()
    proxies_conn.close()
'''
cursor_live.close()
conn_live.commit()
conn_live.close()
cursor.close()
conn.commit()
conn.close()
