import csv
import urllib
import requests
import os
import numpy as np
from geopy.distance import geodesic

"""
HatenaBlog, 国土地理院APIで住所から緯度・経度を取得(ジオコーディング), 
https://elsammit-beginnerblg.hatenablog.com/entry/2021/07/11/122916
"""

class GPS_Address_Distance:

    def __init__(self):
        self.spot_row_list = []
        self.spot_reject_row_list = []



    def convert_address_to_latitude_and_longitude(self, Address = "滋賀県蒲生郡日野町松尾1680（わたむきホール虹となり） "):

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
    def get_many_kuchikomi_address(self, csv_path='extend_zyaran_data/include_data_activity1.csv'):

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

                #経度と緯度を取得し, 追加する
                longitude, latitude = self.convert_address_to_latitude_and_longitude(address)
                row.append(longitude)
                row.append(latitude)
                

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
                

    
    
    #距離が最も近い10個のスポットを取得する
    def get_nearest_spots_by_distance(self, my_latitude, my_longitude):

        """
        0     1     2    3        4    5     6    7     8     9
        種類, 名前, 地域, 口コミ数, URL, 住所, 概要, 説明, 経度, 緯度
        """

        csv_num = 1

        #スポットリストが空のときのみ取得する
        if len(self.spot_row_list) == 0:
            print("初回:CSVからスポットリストを読み込みます")

            while True:
                
                more_extend_csv_path = "more_extend_zyaran_data/include_data_activity" + str(csv_num) + ".csv"

                #あれば, csvファイルを開き, データを読み込む
                if os.path.exists(more_extend_csv_path):

                    with open(more_extend_csv_path, encoding="utf-8") as file:

                        reader_rows = csv.reader(file)
                        for row in reader_rows:
                            row.append(csv_num) #どのファイルのものか分かるようにする

                            #緯度と経度が数字データとして含まれる場合のみ追加する
                            if row[9] != "No_longitude" and row[8] != "No_latitude":
                                self.spot_row_list.append(row)

                            else:
                                self.spot_reject_row_list.append(row)

                        print("self.spot_row_list=")
                        #print(self.spot_row_list)

                    csv_num += 1

                #なければ, 読込みを終了する
                else:
                    break

            print("csv_num=" + str(csv_num))


       

        #自分の位置と隠れスポットの位置を持つリスト
        distance_between_mypos_and_spots = np.empty(0)
        

        for row in self.spot_row_list:
            try:
                spot_latitude = float(row[9]) #緯度
                spot_longitude = float(row[8]) #経度

                spot_pos = (spot_latitude, spot_longitude)
                my_pos = (my_latitude, my_longitude)

                #print("spot_pos=" + str(spot_pos))
                #print("my_pos=" + str(my_pos))

                distance_m = geodesic(spot_pos, my_pos).m  
                #distance_between_mypos_and_spots.append(distance_m)
                distance_between_mypos_and_spots = np.append(distance_between_mypos_and_spots, distance_m)

            except Exception:
                print("緯度と経度の情報がありません")

    
        for reject_row in self.spot_reject_row_list:
            print("reject_row=")
            #print(reject_row)        

        #print("distance_between_mypos_and_spots=")
        #print(distance_between_mypos_and_spots) 

        #配列の長さが同じ => 添え字の対応関係が保たれていることを確認する
        #print("len(distance_between_mypos_and_spots)=" + str(len(distance_between_mypos_and_spots)))
        #print("len(self.spot_row_list)=" + str(len(self.spot_row_list)))

    
        #距離の昇順に添え字を並び変える
        spots_index_sorted_by_distances = np.argsort(distance_between_mypos_and_spots)
        #print("spots_index_sorted_by_distances")
        #print(spots_index_sorted_by_distances)

        
        """
        0     1     2    3        4    5     6    7     8     9
        種類, 名前, 地域, 口コミ数, URL, 住所, 概要, 説明, 経度, 緯度
        """
        #距離の近さ 上位10まで取り出す
        Top_10_nearest_spots = []
        for i in range(10):
            spot = self.spot_row_list[spots_index_sorted_by_distances[i]]
            #print("名前:" + spot[1] + ", 住所:" + spot[5] + ", (緯度=" + spot[9] + ", 経度=" + spot[8] + ")")
            Top_10_nearest_spots.append(spot)


        return Top_10_nearest_spots

       
        


    


    def main_use_test(self):

        
        for i in range(1, 2):
            
            extend_csv_path = "extend_zyaran_data/include_data_activity" + str(i+1) + ".csv"
            self.get_many_kuchikomi_address(extend_csv_path)



if __name__ == "__main__":
    GPS_add_dis = GPS_Address_Distance()
    GPS_add_dis.get_nearest_spots_by_distance(34, 138)

    #main_address()
    #main_use_test()
    