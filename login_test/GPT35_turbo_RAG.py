"""
https://note.com/npaka/n/nc20c2d2068ff
"""

# Open AIのAPIキーを設定
import os

# LlamaIndexのインポート
#from llama_index import SimpleDirectoryReader
#from llama_index import SimpleDirectoryReader
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
#from llama_index import QuestionAnswerPrompt, GPTSimpleVectorIndex
import re

from gpt_35_turbo_langchain_memo import make_kyotoben, make_osakaben, make_kobeben

"""
OpenAIのAPIキーを読み込む
"""
def get_open_ai_token_from_txt():
    f = open(r"C:\Users\sfSogoFurukawa\Desktop\Python練習\自然言語処理\openai_api_keys\key1_RCC.txt", 'r') 
    open_ai_token = f.read()
    return open_ai_token


def get_knowledge_from_data(dir_path):

    # ---------------------------------------------------------
    # 手順1（インデックスを用意）
    # ---------------------------------------------------------

    # dataフォルダ内の学習データを使い、インデックスを生成する
    #documents = SimpleDirectoryReader(input_dir="./data").load_data()
    documents = SimpleDirectoryReader(input_dir=dir_path).load_data()
    #index = VectorStoreIndex()
    #index.add_document(documents)
    #index.build()
    list_index = VectorStoreIndex.from_documents(documents)

    return list_index


def ans_from_rag_knowledge(list_index, question):
    # ---------------------------------------------------------
    # 手順2（インデックスを使って質問）
    # ---------------------------------------------------------
    # 質問を実行
    query_engine = list_index.as_query_engine()
    response = query_engine.query(question + "日本語で回答してください")

    """
    for i in response.response.split("。"):
        print(i + "。")
    """

    return response


def llm_preparation(near_spot_row):

    #APIキーの登録
    os.environ["OPENAI_API_KEY"] = get_open_ai_token_from_txt()

    """
	0     1     2    3        4    5     6    7     8     9
	種類, 名前, 地域, 口コミ数, URL, 住所, 概要, 説明, 経度, 緯度
	"""
    #選ばれた地域の1つの行
    sentences = near_spot_row.detail


    #一時的に保存する知識データファイルのパス
    temp_file_path = "llm_rag_knowledge\selected_nearest_spot.txt"
    with open(temp_file_path, "w", encoding="utf-8") as temp_file:
        temp_file.write(sentences)

    #知識を文章から索引へ変換する
    temp_dir_path = "llm_rag_knowledge"
    list_index = get_knowledge_from_data(temp_dir_path)


    prefecture = near_spot_row.pref

    if prefecture == 0: 
        kyotoben_llm = make_kyotoben()

        return list_index, kyotoben_llm, "京都"

    elif prefecture == 1:
        kobeben_llm = make_kobeben()

        return list_index, kobeben_llm

    else:
        osakaben_llm = make_osakaben()
        return list_index, osakaben_llm, "関西"


def llm_communication(list_index, hogen_llm, hogen_tag, reconized_text):

    question = reconized_text
    response = ans_from_rag_knowledge(list_index, question)
    #print("response=")
    #print(response)


    cl_text = f"""  ## 指示 
                    「{response} 」を{hogen_tag}弁の具体例を踏まえて言い換えてください.
                    言い換えた文章のみを回答してください
                """ 
    #print("cl_text=" + cl_text)
    res_text = hogen_llm.NLP_main(cl_text)
    #print("restext=" + res_text)

    fixed_res_text = ""
    pattern = '(?<=\「).*(?=\」)'
    if "「" in res_text and "」" in res_text:
        fixed_res_text = text_list_re_search = re.search(pattern, res_text).group() 
    
    else:
        fixed_res_text = res_text

    #print("fixed_res_text=" + fixed_res_text)

    return fixed_res_text




def main_use_test():
    from app import GPS_add_dis
    Top_10_nearest_spots = GPS_add_dis.getNearestSpotByDistance(34, 135)

    list_index, hogen_llm, hogen_tag = llm_preparation(Top_10_nearest_spots[0])

    #sentences = Top_10_nearest_spots[0][7]
    
    while True:
        print("hogen_tag=" + hogen_tag)

        reconized_text = input("質問を入力してください>")
        fixed_res_text = llm_communication(list_index, hogen_llm, hogen_tag, reconized_text)

        print("fixed_res_text=")
        print(fixed_res_text)

        

        




if __name__ == "__main__":
    main_use_test()
    #main_use_gpt_prompt()








