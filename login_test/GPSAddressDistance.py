import urllib
import requests
from app import Spot, db
import numpy as np
from geopy.distance import geodesic
#地点を追加するときに住所から座標を取得する。エラーがある場合-65535を出して終了(正直戻り値の型変えたくない)
def addressToChoords(address: str):
    makeUri = "https://msearch.gsi.go.jp/address-search/AddressSearch?q="
    quote = urllib.parse.quote(address)
    try:
        responce = responce = requests.get(makeUri + quote)
        pos = responce.json()[0]["geometry"]["coordinates"]
        return pos[1], pos[0]
    except Exception as e:
        print(f"住所から座標の取得に失敗しました。<住所：{address}, 例外：({e.__class__.__name__}:{e.args})>")
        return -65535, -65535

#距離が最も近い10個のスポットを取得する。
def getNearestSpotByDistance(my_lati : float, my_long : float):
    choords = db.session.query(Spot.longitude, Spot.latitude).all()
    distanceList = np.empty(0)
    for choordData in choords:
        spotChoordsTuple = (choordData.latitude, choordData.longitude)
        print(f"spotChoordTuple > {spotChoordsTuple}")
        myPosTuple = (my_lati, my_long)
        print(f"myPosTuple > {myPosTuple}")
        distance = geodesic(spotChoordsTuple, myPosTuple).m
        print(f"distance > {distance}")
        distanceList = np.append(distanceList, distance)
    spotsIndexSortedByDistance = np.argsort(distanceList)[::1]
    top10NearestSpots = []
    for i in range(10):
        allData = db.session.query(Spot).all()
        spot = allData[spotsIndexSortedByDistance[i]]
        top10NearestSpots.append(spot)
    return top10NearestSpots

if __name__ == "__main__":
    #getNearestSpotByDistance(lat, long)
    pass