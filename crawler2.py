import os
import requests
from bs4 import BeautifulSoup
import pymysql
import time,datetime


biquge = "http://www.paoshuzw.com/xiaoshuodaquan/" #小说地址

headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'
}

#获取小说
def getBooks():
    req = requests.get(url = biquge)
    bf = BeautifulSoup(req.text)
    # 所有类型小说列表
    bookListAll = bf.find_all('div',class_="novellist")
    novelId = 0
    for bookList in bookListAll:
        i = 0 
        for book in bookList.find_all('li'):
            if( i < 3):
                i+=1
                novelId += 1
                getNovelDeatil(book.text,book.find('a').get('href'),novelId)
                getChapterList(book.find('a').get('href'),novelId)



#获取小说详细信息  小说名称、简介、作者、图书封面、状态(连载;完结)
def getNovelDeatil(bookName,urlAction,novelId):
    req = requests.get(url = urlAction)
    req.encoding='utf-8'
    bf = BeautifulSoup(req.text)
    bookType = bf.find('div',class_="con_top").find_all('a')[2].text.replace("小说","")
    bookName = bookName
    bookAuthor = bf.find('div',id="info").find_all('p')[0].text.replace('作    者：',"")
    bookCover = bf.find('div',id="fmimg").find('img').get('src')
    bookState = bf.find('div',id="fmimg").find('span').get('class')[0]
    if(bookState == 'b'):
        bookState = '连载'
    else:
        bookState = '完结'
    bookIntroduce = bf.find('div',id="intro").find_all('p')[1].text
    
    db = pymysql.connect(
        host='xxxxxxxxx',
        port=3306,
        user='root',
        password='xxxxxxxxx',
        database='xxxxxxxxxx'
    )    
    cursor = db.cursor()

    # sql =  "INSERT INTO novel_info (novel_id,novel_name,novel_author,novel_state,novel_type,novel_intro,novel_cover) VALUES (%s,%s,%s,%s,%s,%s,%s ) ON DUPLICATE KEY UPDATE novel_id = %s)"
    sql =  "INSERT INTO novel_info (novel_id,novel_name,novel_author,novel_state,novel_type,novel_intro,novel_cover) SELECT %s,%s,%s,%s,%s,%s,%s FROM dual WHERE not exists (select * from novel_info where novel_name = %s)"
    
    try:
        cursor.execute(sql,[novelId,bookName,bookAuthor,bookState,bookType,bookIntroduce,bookCover,bookName])
        print(cursor.rowcount)
        if(cursor.rowcount == 1):
            print(bookName + '  ========================>>>>  小说插入成功')
        else:
            print(bookName + '  小说已存在！')
        db.commit()
    except IOError:
        print(bookName + '  ========================>>>>  小说插入失败！！')
    cursor.close()
    # db.close()
    

# def writeContent(chapterUrl):
#     req = requests.get(url = chapterUrl)
#     req.encoding='utf-8'
#     bf = BeautifulSoup(req.text)
#     chapterContent = bf.find_all('div',id = 'content')
#     content = chapterContent[0].text.replace('\xa0'*3,'\n')
#     return content

def getChapterList(urlAction,bookId):
    req = requests.get(url = urlAction,headers = headers)
    req.encoding='utf-8'
    bf = BeautifulSoup(req.text)
    # 小说章节列表

    chapterList = bf.find('div',id="list").find_all('a')
    chapterNum = 0
    for chapter in chapterList:
        if(chapterNum<50):
            if("第" in chapter.text):
                chapterNum+=1
                chapterName = chapter.text
                # chapterContent = writeContent('http://www.paoshuzw.com' + chapter.get('href'))
                getChapterDeatil('http://www.paoshuzw.com' + chapter.get('href'),bookId,chapterName)
                time.sleep(1.5)


def getChapterDeatil(urlAction,bookId,chapterName):
    req = requests.get(url = urlAction)
    req.encoding='utf-8'
    bf = BeautifulSoup(req.text)
    chapterContent = bf.find('div',id = 'content')
    content = chapterContent.text.replace('\xa0'*3,'\n')
    
    db = pymysql.connect(
        host='47.102.201.120',
        port=3306,
        user='root',
        password='bjc19981110',
        database='wx_novel_copy'
    )    
    cursor = db.cursor()

    # sql =  "INSERT INTO chapter_info (novel_id,chapter_id,chapter_name,chapter_content) VALUES (%s,%s,%s,%s)"
    sql = "INSERT INTO chapter_info (novel_id,chapter_name,chapter_content) SELECT %s,%s,%s FROM dual WHERE not exists (select * from chapter_info where chapter_name = %s)"

    try:    
        cursor.execute(sql,[bookId,chapterName,content,chapterName])
        if(cursor.rowcount > 0):
            print(chapterName + '  ========================>>>>  章节插入成功！！')
        else:
            print(chapterName + '  ========================>>>>  章节已存在')
        db.commit()
    except IOError:
        print(chapterName + '  ========================>>>>  章节插入失败！！')
    cursor.close()
    # db.close()



if __name__ == "__main__":
    getBooks()
