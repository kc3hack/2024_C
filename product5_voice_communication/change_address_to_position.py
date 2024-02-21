from cmath import pi
import csv
import urllib
import requests


"""
HatenaBlog, 国土地理院APIで住所から緯度・経度を取得(ジオコーディング), 
https://elsammit-beginnerblg.hatenablog.com/entry/2021/07/11/122916
"""

def convert_address_to_latitude_and_longitude(Address = "滋賀県蒲生郡日野町松尾1680（わたむきホール虹となり） "):

    makeUrl = "https://msearch.gsi.go.jp/address-search/AddressSearch?q=" #国土交通省のAPI
    s_quote = urllib.parse.quote(Address) #住所をURLに符号化する

    try: 
        response = response = requests.get(makeUrl + s_quote)
        position = response.json()[0]["geometry"]["coordinates"]

        return position[0], position[1] 


    except Exception:
        print("例外:その住所の経度と緯度を得ることができませんでした")

        return "No_longitude", "No_latitude" 



    
    




#概要, 説明(口コミ×5), 住所を取得
def get_many_kuchikomi_address(csv_path='extend_zyaran_data/include_data_activity1.csv'):

    """
    種類, 名前, 地域, 口コミ数, URL, 住所, 概要, 説明
    """

    PLAN_PAGE = "activity_plan/"
    KUCHIKOMI_PAGE = "kuchikomi/"

    row_list = [] 
    
    with open(csv_path) as file:
  
        reader_rows = csv.reader(file)
        for row in reader_rows:
            row_list.append(row)

            #住所を取得する
            address = row[5]

            #緯度と経度を取得し, 追加する
            latitude, longitude = convert_address_to_latitude_and_longitude(address)
            row.append(latitude)
            row.append(longitude)

        print("row_list=")
        print(row_list)

    
    """
    種類, 名前, 地域, 口コミ数, URL, 住所, 概要, 説明, 経度, 緯度
    """

    
    with open("more_" + csv_path, 'w', newline='', encoding='UTF-8') as file:


        writer_rows = csv.writer(file)
        print(file)
        print(writer_rows)

        #リストの長さだけデータの列がある
        for row in row_list:

            #print("write_row=")
            #print(row)
            writer_rows.writerow(row)
            

    
    



def main_use_test():

    
    for i in range(1, 2):
        
        extend_csv_path = "extend_zyaran_data/include_data_activity" + str(i+1) + ".csv"
        get_many_kuchikomi_address(extend_csv_path)



if __name__ == "__main__":
    #main_address()
    main_use_test()