import Levenshtein


#out_sampleリアルタイムで得たもの が リストのどれと最も近いのか調べる
def get_most_similer(out_sample, sample_list):
    lev_distance_list = []

    for sample in sample_list:
        lev_distance = Levenshtein.distance(out_sample, sample)
        lev_distance_list.append(lev_distance)

    min_idx = lev_distance_list.index(min(lev_distance_list))

    #リストの添え字と要素を返す
    return min_idx, sample_list[min_idx]




def detect_selected_num(reconized_text, spot_num=10):

    #数字, 漢字, ひらがなのリスト
    SELECE_LIST_NUM = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    SELECE_LIST_KANJI = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
    SELECE_LIST_HIRAGANA = ["いち", "に", "さん", "よん", "ご", "ろく", "なな", "はち", "きゅう", "じゅう"]

    SELECE_LIST_CHAR = []
    SELECE_LIST_CHAR.extend(SELECE_LIST_NUM[0:spot_num])
    SELECE_LIST_CHAR.extend(SELECE_LIST_KANJI[0:spot_num])
    SELECE_LIST_CHAR.extend(SELECE_LIST_HIRAGANA[0:spot_num])

    min_idx, _ = get_most_similer(reconized_text, SELECE_LIST_CHAR)

    #最大数で割ったときの剰余がその数字になる
    idx_mod = (min_idx+1) % spot_num

    #最終的に選択された数字
    selected_num = spot_num

    if idx_mod != 0:
        selected_num = idx_mod

    return selected_num



def detect_yes_or_no(reconized_text):

    ans_list = ["はい", "いいえ"]
    _, ans = get_most_similer(reconized_text, ans_list)

    return ans




def main_use_test():

    reconized_text = "5番"

    selected_num = detect_selected_num(reconized_text, spot_num=10)    

    print("selected_num=")
    print(selected_num)

if __name__ == "__main__":
    main_use_test()

