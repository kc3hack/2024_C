import requests
from bs4 import BeautifulSoup
import pandas

"""
Kodai Blog, じゃらんの口コミをスクレイピングしてみる【Python】,
https://kodyblog.com/jalan-scraping/ 
"""


def get_kuchikomi_from_URL(URL):

    r = requests.get(URL)
    c = r.content

    soup = BeautifulSoup(c, "html.parser")

    count=soup.find_all("div", {"class":"jlnpc-kuchikomi__sortNav__count"})
    body=soup.find_all("p",{"class":"jlnpc-kuchikomiCassette__postBody"})
    date=soup.find_all("p",{"class":"jlnpc-kuchikomiCassette__postDate"})
    score=soup.find_all("div",{"class":"jlnpc-kuchikomiCassette__totalRate"})

    l=[]
    for d, b, s in zip(date, body, score):
        data={}
        data["スコア"]=s.text
        data["口コミ"]=b.text
        data["投稿日"]=d.text.replace('投稿日：', '')
        l.append(data)

    print("count[0]=")
    #print(count[0])

    delete_str = "<span>"

    target_html_txt = str((count[0].find_all('p')[0]))
    idx = target_html_txt.find(delete_str) 

    count = int(target_html_txt[:idx].replace("<p>", "").replace(",", ""))

    print(count)

    return count, l








def main_use_test():

    URL = "https://www.jalan.net/yad358756/kuchikomi/?screenId=UWW3001&yadNo=358756&stayMonth=&dateUndecided=1&stayYear=&stayDay=&minPrice=0&maxPrice=999999&rootCd=7701&callbackHistFlg=1&smlCd=260502&distCd=01&ccnt=lean-kuchikomi-tab"    

    count, kuchikomi = get_kuchikomi_from_URL(URL)

    print("kuchikomi=")
    print(kuchikomi)

    print("count=" + str(count))
    
    
if __name__ == "__main__":
    main_use_test()