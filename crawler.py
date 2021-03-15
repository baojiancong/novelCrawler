import os
import requests
from bs4 import BeautifulSoup
import pymysql


biquge = "http://www.paoshuzw.com/xiaoshuodaquan/" #小说地址

#获取小说
def getBooks():
    req = requests.get(url = biquge)
    bf = BeautifulSoup(req.text)
    # 所有类型小说列表
    bookListAll = bf.find_all('div',class_="novellist")
    bookId = 0 
    for bookList in bookListAll:
        i = 0 
        for book in bookList.find_all('li'):
            if( i < 3):
                i+=1
                bookId+=1
                getNovelDeatil(book.text,book.find('a').get('href'),bookId)
                getChapterList(book.find('a').get('href'),bookId)



#获取小说详细信息  小说名称、简介、作者、图书封面、状态(连载中;已完结)
def getNovelDeatil(bookName,urlAction,bookId):
    req = requests.get(url = urlAction)
    req.encoding='utf-8'
    bf = BeautifulSoup(req.text)
    bookId = str(2021) + '-' + str(bookId)
    if(bf.find('div',class_="con_top")):
        bookType = bf.find('div',class_="con_top").find_all('a')[2].text
    else:
        bookType = '其他小说'
    bookName = bookName
    if(bf.find('div',id="info")):
        bookAuthor = bf.find('div',id="info").find_all('p')[0].text.replace('作    者：',"")
    else:
        bookAuthor = '匿名'
    if(bf.find('div',id="fmimg")):
        bookCover = bf.find('div',id="fmimg").find('img').get('src')
        bookState = bf.find('div',id="fmimg").find('span').get('class')[0]
        if(bookState == 'b'):
            bookState = '连载中'
        else:
            bookState = '已完结'
    else:
        bookCover = '',
        bookState = '连载中'
    if(bf.find('div',id="intro")):
        bookIntroduce = bf.find('div',id="intro").find_all('p')[1].text
    else:
        bookIntroduce = '暂无简介'
    
    db = pymysql.connect(
        host='47.102.201.120',
        port=3306,
        user='root',
        password='bjc19981110',
        database='wx_novel'
    )    
    cursor = db.cursor()

    sql =  "INSERT INTO novel_info (novel_id,novel_name,novel_author,novel_state,novel_type,novel_intro,novel_cover) VALUES ( %s,%s,%s,%s,%s,%s,%s ) ON DUPLICATE KEY UPDATE novel_author = IF(%s != '匿名',%s,novel_author),novel_state = IF(%s != '连载中',%s,novel_state),novel_type = IF(%s != '其他小说',%s,novel_type),novel_intro = IF(%s != '暂无简介' ,%s,novel_intro),novel_cover = IF(%s != '',%s,novel_cover)"
    # sql =  "INSERT INTO novel_info (novel_id,novel_name,novel_author,novel_state,novel_type,novel_intro,novel_cover) SELECT %s,%s,%s,%s,%s,%s,%s FROM dual WHERE not exists (select * from novel_info where novel_id = %s)"

    try:
        cursor.execute(sql,[bookId,bookName,bookAuthor,bookState,bookType,bookIntroduce,bookCover,bookAuthor,bookAuthor,bookState,bookState,bookType,bookType,bookIntroduce,bookIntroduce,bookCover,bookCover])
        print(cursor.rowcount)
        if(cursor.rowcount == 2):
            print(bookName + '  ========================>>>>  小说更新成功')
        elif(cursor.rowcount == 1):
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
    req = requests.get(url = urlAction)
    req.encoding='utf-8'
    bf = BeautifulSoup(req.text)

    # 小说章节列表

    if(bf.find('div',id="list")):
        chapterList = bf.find('div',id="list").find_all('a')
        chapterId = 0
        chapterNum = 0
        for chapter in chapterList:
            if(chapterNum<50):
                if("第" in chapter.text):
                    chapterId+=1
                    chapterNum+=1
                    chapterName = chapter.text
                    # chapterContent = writeContent('http://www.paoshuzw.com' + chapter.get('href'))
                    getChapterDeatil('http://www.paoshuzw.com' + chapter.get('href'),bookId,chapterId,chapterName)


def getChapterDeatil(urlAction,bookId,chapterId,chapterName):
    req = requests.get(url = urlAction)
    req.encoding='utf-8'
    bf = BeautifulSoup(req.text)
    chapterContent = bf.find('div',id = 'content')
    if(chapterContent):
        content = chapterContent.text.replace('\xa0'*3,'\n')
    else:
        content = '章节内容获取失败......'
    bookId = str(2021) + '-' + str(bookId)
    chapterId =  str(bookId) + '-' + str(chapterId)
    
    db = pymysql.connect(
        host='47.102.201.120',
        port=3306,
        user='root',
        password='bjc19981110',
        database='wx_novel'
    )    
    cursor = db.cursor()

    # sql =  "INSERT INTO chapter_info (novel_id,chapter_id,chapter_name,chapter_content) VALUES (%s,%s,%s,%s)"
    sql = "INSERT INTO chapter_info (novel_id,chapter_id,chapter_name,chapter_content) SELECT %s,%s,%s,%s FROM dual WHERE not exists (select * from chapter_info where chapter_id = %s)"

    try:
        cursor.execute(sql,[bookId,chapterId,chapterName,content,chapterId])
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
