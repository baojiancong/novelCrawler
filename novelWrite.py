import os
import requests
from bs4 import BeautifulSoup
import pymysql


biquge = "https://www.biquwu.cc" #小说地址
dist = "E:/novels/" #本地存放地址

#生成小说编号
# def createNovelId():   
#     # novelId = {
#     #     '分类：玄幻小说': 0,
#     #     '分类：武侠小说': 1,
#     #     '分类：都市小说': 2,
#     #     '分类：历史小说': 3,
#     #     '分类：科幻小说': 4,
#     #     '分类：灵异小说': 5,
#     # }
#     novel_id = str(datetime.datetime.now().year) + str(math.floor(1e5 * random.random()))
#     return novel_id

#写入小说名称、简介、作者、图书封面、类型(0:玄幻,1:武侠,2:都市,3:历史,4:科幻,5:灵异,6:其他)、状态(连载:1,完结:2)
def getDeatil(bookNum,urlAction):
    req = requests.get(url = biquge + urlAction)
    bf = BeautifulSoup(req.text)
    bookCover = bf.find_all('img')[0].get('src')
    bookInfo = bf.find('div',id="info")
    bookName = bookInfo.find('h1').text
    bookType = bookInfo.find_all('p')[0].text
    if bookInfo.find_all('p')[1].text == '状    态：连载':
        bookState = 1
    else:
        bookState = 2 
    bookAuthor = bookInfo.find_all('p')[2].text
    bookIntroduce = bf.find('div',id='intro').find_all('p')[0].text
   
    db = pymysql.connect(
    host='47.102.201.120',
    port=3306,
    user='root',
    password='bjc19981110',
    database='wx_novel'
    )
    cursor = db.cursor()

    sql = "INSERT INTO novelinfo (novel_id,novel_name,novel_cover,novel_introduce,novel_author,novel_type,novel_state) SELECT %s,%s,%s,%s,%s,%s,%s FROM dual WHERE not exists (select * from novelinfo where novel_name = %s)"

    try:
        cursor.execute(sql,[bookNum,bookName,(biquge + bookCover),bookIntroduce,bookAuthor,bookType,bookState,bookName])
        if(cursor.rowcount):
            print(bookName + "=======================>>> 小说相关信息插入成功")
        else:
            print(bookName + "=======================>>> 该小说信息已存在")
        db.commit()
    except IOError:
        print(bookName + '=================>>>  小说相关信息插入失败')
    cursor.close()
    # db.close()

def getChapterDeatil(novel_id,chapterId,c_name,contentURL):
    chapter_content = writeContent(contentURL)
    chapter_name = c_name
    chapter_id = novel_id + "_" + str(chapterId)

    db = pymysql.connect(
    host='47.102.201.120',
    port=3306,
    user='root',
    password='bjc19981110',
    database='wx_novel'
    )

    cursor = db.cursor()

    sql = "INSERT INTO chapterinfo (novel_id,chapter_id,chapter_name,chapter_content) SELECT %s,%s,%s,%s FROM dual WHERE not exists (select * from chapterinfo where chapter_name = %s)"

    try:
        cursor.execute(sql,[novel_id,chapter_id,chapter_name,chapter_content,chapter_name])
        if(cursor.rowcount):
            print(chapter_name + "=======================>>> 小说章节插入成功")
            db.commit()
        else:
            print(chapter_name + "=======================>>> 该小说章节已存在")

    except IOError:
        print(chapter_name + '=================>>>  小说章节插入失败')
    cursor.close()
    # db.close()

#获得小说列表
def getBooks():
    req = requests.get(url = biquge)
    bf = BeautifulSoup(req.text)
    bookList = bf.find('ol',class_="ranklist ranklist_txt")
    i = 0 
    for book in bookList.find_all('a'):
        i += 1 
        bookNum = str(2021) + str(i)
        getDeatil(bookNum,book.get('href'))  
        getChapter(bookNum,book.text,book.get('href'))

      
#获得章节列表
def getChapter(bookNum,bookName,bookUrl):
    req = requests.get(url = biquge + bookUrl)
    bf = BeautifulSoup(req.text)
    chapterList = bf.find('div',class_="listmain")
    chapterId = 0
    for chapter in chapterList.find_all('a'):
        chapterId += 1
        if("第" in chapter.text):
            getChapterDeatil(bookNum,chapterId,chapter.text,chapter.get('href'))

def writeContent(chapterUrl):
    req = requests.get(url = biquge + chapterUrl)
    bf = BeautifulSoup(req.text)
    chapterContent = bf.find_all('div',class_ = 'showtxt')
    content = chapterContent[0].text.replace('\xa0'*7,'\n')
    return content

if __name__ == "__main__":
    getBooks()

  

  