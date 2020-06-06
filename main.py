from fastapi import FastAPI, Request, BackgroundTasks
import json
import pickledb

import requests
from bs4 import BeautifulSoup as bs
import lxml
from pprint import pprint

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.headless = True

app = FastAPI()
user_db = pickledb.load('user.db', True)

@app.get("/")
def read_root(request: Request):
    client_host = request.client.host
    return {"client_host": f"{client_host} recorded"}

@app.post("/etl_login")
async def etl_login(request: Request, background_tasks: BackgroundTasks):
    body = json.loads(await request.body())
    print(body)
    user_id = body["userRequest"]["user"]["id"]
    etl_id = body["action"]["detailParams"]["etl_id"]["origin"]
    etl_password = body["action"]["detailParams"]["etl_password"]["origin"]
    
    print(etl_id)
    print(etl_password)
    
    #await etl_login_webdriver(user_id, etl_id, etl_password)
    background_tasks.add_task(etl_login_webdriver, user_id, etl_id, etl_password)
    
    
    print("get_data")
    
    simpleText = {
    	    "version": "2.0",
    	    "template": {
    	        "outputs": [
    	            {
    	                "simpleText": {
    	                    "text": "로그인 중, 잠시만 기다려주세요!\n5초 후에 로그인 확인을 입력해주세요!~!"
    	                }
    	            }
    	        ]
    	    }
	    }
    return simpleText
    
@app.post("/check_login")
async def check_login(request: Request):
    # comment
    body = await request.body()
    body_json = json.loads(body)
   
    login = user_db.get("if_login")
    
    simpleText = {
    	    "version": "2.0",
    	    "template": {
    	        "outputs": [
    	            {
    	                "simpleText": {
    	                    "text": login
    	                }
    	            }
    	        ]
    	        
    }
  
}
    	    
	   
    return simpleText
    
    
@app.post("/short_notice")
async def all_notice(request:Request):
    body = await request.body()
    body_json = json.loads(body)
    
    get_short = user_db.get("short_notices")
    
    simpleText = {
    	    "version": "2.0",
    	    "template": {
    	        "outputs": [
    	            {
    	                "simpleText": {
    	                    "text": get_short +'\n새로 업데이트된 공지가 있다면 사이트를 통해서 확인해주세용~!~'
    	                }
    	            }
    	        ]
    	    }
	    }
    return simpleText
    
@app.post("/long_notice")
async def all_notice(request:Request):
    body = await request.body()
    body_json = json.loads(body)
    
    get_long = user_db.get("long_notices")
    
    simpleText = {
    	    "version": "2.0",
    	    "template": {
    	        "outputs": [
    	            {
    	                "simpleText": {
    	                    "text": get_long +'\n새로 업데이트된 공지가 있다면 사이트를 통해서 확인해주세용~!~'
    	                }
    	            }
    	        ]
    	    }
	    }
    return simpleText

    
    

    


def etl_login_webdriver(user_id, etl_id, etl_pw):
    
    driver = webdriver.Chrome(options=options)
    driver.get("https://etl.snu.ac.kr/login.php")
    driver.find_element_by_name('si_id').send_keys(etl_id)
    driver.find_element_by_name('si_pwd').send_keys(etl_pw)
    driver.find_element_by_name('loginbutton').click()
    soup = bs(driver.page_source, 'lxml')
    
    redirect = 'https://sso.snu.ac.kr/snu/ssologin_proc.jsp?si_redirect_address=http://etl.snu.ac.kr/'
    driver.get(redirect)
    
    if '로그아웃' in bs(driver.page_source,'lxml').get_text()==False:
        answer = '로그인 정보가 잘못되었습니다. 다시 입력해주세요'
        
    else: 
        answer= '로그인 되었습니다. \n어떤 공지를 확인하고싶으세요? \n1)간략한공지(공지사항, 과제) \n2)전체공지(공지사항, 질의응답 외 기타 게시글'
        
    user_db.set("if_login", answer)
    
    
    
    soup = bs(driver.page_source, 'lxml')
    sample=soup.find_all('h3')
    classes = []
    for h3 in sample:
        classes.append(h3.getText())
        class_str = ', '.join(classes)
    
     #print(soup)
    print(class_str)
    #driver.quit()
    
    
    
    ub_notification = "http://etl.snu.ac.kr/local/ubnotification/"
    driver.get(ub_notification)
    soup = bs(driver.page_source, 'lxml')
    notices=soup.find_all('div', {'class':'media'})
    short_notices = []
    
    for notice in notices:
        short_notices.append(notice.getText())
        short_notice_str= ', '.join(short_notices)
        
    short_notice_str = short_notice_str.split(sep='., ')
    short_notice_enter= ''
    for line in short_notice_str:
        short_notice_enter += (line + '\n\n')
    
    print(short_notice_enter)
    
    
    driver.get(redirect)
    driver.find_element_by_class_name('more').click()
    soup = bs(driver.page_source, 'lxml')
    all_lines = soup.find_all('tr')[1:]
    lines= []
    for line in all_lines:
        lines.append(line)
    
    long_notices= []
    for line in lines:
        long_notices.append((line.find_all("td")[1].get_text()))
        long_notice_str = ', '.join(long_notices)
        long_notice_str =' '.join(long_notice_str.split())
        
    long_notice_str.split()
    long_notice_str=' '.join(long_notice_str.split())
    long_notice_str =long_notice_str.split(sep=', ')
    long_notice_enter= ''
    for line in long_notice_str:
        long_notice_enter += (line +'\n\n')
        
    print(long_notice_enter)
    
    
    
    
    
    class_key = user_id + "_class"
    user_db.set(class_key, class_str)
    user_db.set("short_notices", short_notice_enter)
    user_db.set("long_notices", long_notice_enter);
    

    driver.quit()