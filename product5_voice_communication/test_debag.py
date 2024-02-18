import Levenshtein


def detect_selected_num(reconized_text, spot_num=10):

    #数字, 漢字, ひらがなのリスト
    SELECE_LIST_NUM = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    SELECE_LIST_KANJI = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
    SELECE_LIST_HIRAGANA = ["いち", "に", "さん", "よん", "ご", "ろく", "なな", "はち", "きゅう", "じゅう"]

    SELECE_LIST_CHAR = []
    SELECE_LIST_CHAR.extend(SELECE_LIST_NUM[0:spot_num])
    SELECE_LIST_CHAR.extend(SELECE_LIST_KANJI[0:spot_num])
    SELECE_LIST_CHAR.extend(SELECE_LIST_HIRAGANA[0:spot_num])

    lev_distance_list = []

    for char in SELECE_LIST_CHAR: 
        lev_distance = Levenshtein.distance(char, reconized_text)
        lev_distance_list.append(lev_distance)

    min_idx = lev_distance_list.index(min(lev_distance_list))

    #最大数で割ったときの剰余がその数字になる
    idx_mod = (min_idx+1) % spot_num

    #最終的に選択された数字
    selected_num = spot_num

    if idx_mod != 0:
        selected_num = idx_mod

    return selected_num


def main_use_test():

    reconized_text = "にばんめ"

    selected_num = detect_selected_num(reconized_text, spot_num=10)    

    print("selected_num=")
    print(selected_num)

if __name__ == "__main__":
    main()

