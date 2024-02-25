import requests
from bs4 import BeautifulSoup
import pandas
import csv
import os

"""
Kodai Blog, じゃらんの口コミをスクレイピングしてみる【Python】,
https://kodyblog.com/jalan-scraping/ 
"""

#じゃらん から 名前と口コミ数を取得する
def get_kuchikomi_many_spots_from_URL(URL):

    """
    <ul id="cassetteType" class="cassetteList-list">
    """

    """
    <p class="item-name">
		<a class="sptList-tit" href="//www.jalan.net/kankou/spt_guide000000213553/activity_plan/?showplan=ichiran_planall" target="_self">itoaware-いとあはれ-黒壁スクエア店</a>
	</p>
    """

    category = ""

    if "https://www.jalan.net/activity" in URL:
        category = "活動施設"

    print("category=" + category)


    r = requests.get(URL)
    c = r.content

    soup = BeautifulSoup(c, "html.parser")


    spot_names = soup.find_all("a", {"class":"sptList-tit"})
    spot_regions = soup.find_all("p", {"class":"item-categories"})
    spot_kuchikomi_nums = soup.find_all("span", {"class":"reviewCount"})
    spot_URLs = soup.find_all("a", {"class":"sptList-tit"})


    #print("spot_URLs=")
    #print(spot_URLs[0].get("href"))
    

    data_list =[ ]
    delete_str = "＞"

    for name, spot_region, kuchikomi_num, spot_URL in zip(spot_names, spot_regions, spot_kuchikomi_nums, spot_URLs):
        data = {}

        data["場所の種類"] = category
        
        data["場所の名前"] = name.text

        spot_region_html_txt = spot_region.text
        delete_str_idx = spot_region_html_txt.find(delete_str) 
        data["場所の地域"] = spot_region_html_txt[:delete_str_idx].replace("\n", "").replace("\t", "").replace(" ","")
        
        data["場所の口コミ数"] = int(kuchikomi_num.text.replace("(クチコミ", "").replace("件)", "").replace(",", ""))
        data_list.append(data)

        data["場所のURL"] = spot_URL.get("href")


    return data_list


#「隠れたえぇところ」と「有名な観光地」のリストを作成
#閾値で判別
def make_reject_list(data_list, reject_TH=150):

    include_data_list = []
    reject_data_list = []

    for data in data_list:

        if data["場所の口コミ数"] > reject_TH:
            reject_data_list.append(data)

        else:
            include_data_list.append(data)

    return include_data_list, reject_data_list


#1つのURLのスポットから住所を取得する
def get_address_from_one_spot_URL(plan_URL):

    r = requests.get(plan_URL)
    c = r.content

    soup = BeautifulSoup(c, "html.parser")

    """
    <p class="item-address mB5">滋賀県東近江市青野町4570</p>
    """

    address = soup.find("p", {"class":"item-address mB5"}).text

    return address



#1つのURLのスポットから概要を取得する
def get_abstruct_from_one_spot_URL(abstruct_URL):

    r = requests.get(abstruct_URL)
    c = r.content

    soup = BeautifulSoup(c, "html.parser")

    """
    <p class="jlnpc-item__catch">●名神八日市インター近く！滋賀県でいちご狩りといえば小杉豊農園へ♪
    <br>●関西エリア2020年度じゃらんいちごグランプリ《リピート率部門》で【敢闘賞】受賞！<br>●練乳無料サービスあります！持ち込みも可です♪</p>
    """

    abstruct = soup.find_all("p", {"class":"jlnpc-item__catch"})[0].text
    
    return abstruct


#1つのURLのスポットから住所を取得する
def get_address_from_one_spot_URL(plan_URL):

    r = requests.get(plan_URL)
    c = r.content

    soup = BeautifulSoup(c, "html.parser")

    """
    <p class="item-address mB5">滋賀県東近江市青野町4570</p>
    """

    try:
        address = soup.find("p", {"class":"item-address mB5"}).text

    except Exception:
        address = "NoneInfo"
        print("住所が書かれていません!")

    return address




#1つのURLのスポットから口コミを取得する
def get_kuchikomi_from_one_spot_URL(kuchikomi_URL):

    r = requests.get(kuchikomi_URL)
    c = r.content

    soup = BeautifulSoup(c, "html.parser")

    """
    <div class="item-reviewTextInner item-reviewLabel">
    <span class="item-experienceCheck">遊び体験済み</span>
    <span>シーズンには少し早い時期だったからか、土曜日なのにお客さんも少なくゆったりと回って
    「どのイチゴが美味しそうかなー」と吟味しながらイチゴ狩りを楽しめました。
    <br>とにかくイチゴがどれも立派。<br>贈答用と同じぐらいの大きなサイズで、形も綺麗。
    <br>味ももちろん美味しい。<br>1歳の娘も初めてのいちご狩りで大興奮しながら、
    大好物のイチゴをこれでもかっ！と言うほど食べてました。<br>またいちご狩りに行く時は、
    こちらの園に伺いたいと思います。<br>オススメのいちご園さんです！</span></div>
    """


    kuchikomis = soup.find_all("div", {"class":"item-reviewTextInner item-reviewLabel"})
    kuchikomi_sentence = ""

    KUCHIKOMI_NUM = 5

    #1000文字程度に収める
    for i, kuchikomi in enumerate(kuchikomis):
        if i == KUCHIKOMI_NUM:
            break

        kuchikomi_sentence += kuchikomi.text

    #print("len(kuchikomi_list)=" + str(len(kuchikomi_list)))

    return kuchikomi_sentence




#1つのURLのスポットから口コミと数を取得するテスト
def get_kuchikomi_and_count_from_one_spot_URL_test(URL):

    r = requests.get(URL)
    c = r.content

    soup = BeautifulSoup(c, "html.parser")
    
    """
    <div class="item-reviewTextInner item-reviewLabel">
    """

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


#DBに直接入れるのが難しいので, CSVで保存する
def save_data_list_as_csv(data_list, csv_path):

    with open(csv_path, 'w', newline='') as file:
        writer = csv.writer(file)

        #リストの長さだけデータの列がある
        for data in data_list:
            
            #1データを1行とする
            data_value_list = []
            for data_value in data.values():
                data_value_list.append(data_value)
            writer.writerow(data_value_list)




#主函数
def main_many_spot_datas():

    page_n = 1
    include_data_csv_path = "zyaran_data/include_data_activity" + str(page_n) + ".csv"
    reject_data_csv_path = "zyaran_data/reject_data_activity" + str(page_n) + ".csv"

    """
    while文で1度に複数頁のスクレイピングをすると文字化けするので,
    1回1回実行して取ってくる
    """
    while True:

        if os.path.exists(include_data_csv_path) or os.path.exists(reject_data_csv_path):
            page_n += 1
            include_data_csv_path = "zyaran_data/include_data_activity" + str(page_n) + ".csv"
            reject_data_csv_path = "zyaran_data/reject_data_activity" + str(page_n) + ".csv"

        else:
            break

    print("page_n=" + str(page_n))


    include_data_csv_path = "zyaran_data/include_data_activity" + str(page_n) + ".csv"
    reject_data_csv_path = "zyaran_data/reject_data_activity" + str(page_n) + ".csv"

        
    data_list = []

    URL = ""

    #1頁目のURL
    if page_n == 1:
        URL = "https://www.jalan.net/activity/search/?dateUndecided=1&screenId=OUW1601&activeSort=0&refineKbn=0&selKenArea=270000,280000,260000,250000,290000,300000&influxKbn=1"

    #2頁め以降のURL
    elif page_n > 1:
        URL = "https://www.jalan.net/activity/search/page_" + str(page_n) + "/?dateUndecided=1&screenId=OUW1601&activeSort=0&refineKbn=0&selKenArea=270000,280000,260000,250000,290000,300000&influxKbn=1"


    #1頁分のデータを取得
    data_list = get_kuchikomi_many_spots_from_URL(URL)

    print("data_list=")
    print(data_list)


    include_data_list, reject_data_list = make_reject_list(data_list, reject_TH=150)

    print("include_data_list=")
    print(include_data_list)
    if len(include_data_list) != 0:
        save_data_list_as_csv(include_data_list, include_data_csv_path)


    print("reject_data_list=")
    print(reject_data_list)
    if len(reject_data_list) != 0: 
        save_data_list_as_csv(reject_data_list, reject_data_csv_path)


    """
    print("kuchikomi=")
    print(kuchikomi)

    print("count=" + str(count))
    """

    """
    URL = "https://www.jalan.net/yad358756/kuchikomi/?screenId=UWW3001&yadNo=358756&stayMonth=&dateUndecided=1&stayYear=&stayDay=&minPrice=0&maxPrice=999999&rootCd=7701&callbackHistFlg=1&smlCd=260502&distCd=01&ccnt=lean-kuchikomi-tab"    

    count, kuchikomi = get_kuchikomi_from_URL(URL)

    print("kuchikomi=")
    print(kuchikomi)

    print("count=" + str(count))
    """
    

#概要, 説明(口コミ×5), 住所を取得
def main_a_spot_kuchikomi_address(csv_path='zyaran_data/include_data_activity1.csv'):

    PLAN_PAGE = "activity_plan/"
    KUCHIKOMI_PAGE = "kuchikomi/"

    row_list = [] 
    
    with open(csv_path) as file:
        #種類, 名前, 地域, 口コミ数, URL

        reader_rows = csv.reader(file)
        
        for row in reader_rows:
            #print(row)
            plan_URL = "https:" + row[4] #予約プランのURL
            print("plan_URL=" + plan_URL)
            address = get_address_from_one_spot_URL(plan_URL)
            print("address=" + address)

            
            plan_pos = plan_URL.find(PLAN_PAGE) 
            abstruct_URL = plan_URL[:plan_pos] #概要のURL
            print("abstruct_URL=" + abstruct_URL)
            abstruct = get_abstruct_from_one_spot_URL(abstruct_URL)
            print("abstruct=" + abstruct)


            kuchikomi_URL = abstruct_URL + KUCHIKOMI_PAGE
            print("kuchikomi_URL=" + kuchikomi_URL)
            kuchikomi_sentence = get_kuchikomi_from_one_spot_URL(kuchikomi_URL)
            print("kuchikomi_sentence=")
            print(kuchikomi_sentence)

            print("\n")


            row.append(address)
            row.append(abstruct)
            row.append(kuchikomi_sentence)
            row_list.append(row)


        print("row_list=")
        print(row_list)

    

    with open("extend_" + csv_path, 'w', newline='', encoding='UTF-8') as file:
        writer_rows = csv.writer(file)

        #リストの長さだけデータの列がある
        for row in row_list:
            
            writer_rows.writerow(row)


    
if __name__ == "__main__":
    #main_many_spot_datas()
    main_a_spot_kuchikomi_address(csv_path='zyaran_data/include_data_activity5.csv')