# -*- coding: utf-8 -*-
# Copyright (c) 2021 Tachibana Securities Co., Ltd. All rights reserved.

# 2021.07.08,   yo.
# 2022.10.20 reviced,   yo.
# Python 3.6.8 / centos7.4
# API v4r3 で動作確認
# 立花証券ｅ支店ＡＰＩ利用のサンプルコード
# 機能: ログイン、注文約定詳細取得、ログアウト を行ないます。
#
# 利用方法: コード後半にある「プログラム始点」以下の設定項目を自身の設定に変更してご利用ください。
#
# == ご注意: ========================================
#   本番環境にに接続した場合、実際に市場に注文を出せます。
#   市場で約定した場合取り消せません。
# ==================================================
#

import urllib3
import datetime
import json
import time


#--- 共通コード ------------------------------------------------------

# request項目を保存するクラス。配列として使う。
# 'p_no'、'p_sd_date'は格納せず、func_make_url_requestで生成する。
class class_req :
    def __init__(self) :
        self.str_key = ''
        self.str_value = ''
        
    def add_data(self, work_key, work_value) :
        self.str_key = func_check_json_dquat(work_key)
        self.str_value = func_check_json_dquat(work_value)


# 口座属性クラス
class class_def_cust_property:
    def __init__(self):
        self.sUrlRequest = ''       # request用仮想URL
        self.sUrlMaster = ''        # master用仮想URL
        self.sUrlPrice = ''         # price用仮想URL
        self.sUrlEvent = ''         # event用仮想URL
        self.sZyoutoekiKazeiC = ''  # 8.譲渡益課税区分    1：特定  3：一般  5：NISA     ログインの返信データで設定済み。 
        self.sSecondPassword = ''   # 22.第二パスワード  APIでは第２暗証番号を省略できない。 関連資料:「立花証券・e支店・API、インターフェース概要」の「3-2.ログイン、ログアウト」参照
        self.sJsonOfmt = ''         # 返り値の表示形式指定
        


# 機能: システム時刻を"p_sd_date"の書式の文字列で返す。
# 返値: "p_sd_date"の書式の文字列
# 引数1: システム時刻
# 備考:  "p_sd_date"の書式：YYYY.MM.DD-hh:mm:ss.sss
def func_p_sd_date(int_systime):
    str_psddate = ''
    str_psddate = str_psddate + str(int_systime.year) 
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.month))[-2:]
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.day))[-2:]
    str_psddate = str_psddate + '-' + ('00' + str(int_systime.hour))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.minute))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.second))[-2:]
    str_psddate = str_psddate + '.' + (('000000' + str(int_systime.microsecond))[-6:])[:3]
    return str_psddate


# JSONの値の前後にダブルクオーテーションが無い場合付ける。
def func_check_json_dquat(str_value) :
    if len(str_value) == 0 :
        str_value = '""'
        
    if not str_value[:1] == '"' :
        str_value = '"' + str_value
        
    if not str_value[-1:] == '"' :
        str_value = str_value + '"'
        
    return str_value
    
    
# 受けたテキストの１文字目と最終文字の「"」を削除
# 引数：string
# 返り値：string
def func_strip_dquot(text):
    if len(text) > 0:
        if text[0:1] == '"' :
            text = text[1:]
            
    if len(text) > 0:
        if text[-1] == '\n':
            text = text[0:-1]
        
    if len(text) > 0:
        if text[-1:] == '"':
            text = text[0:-1]
        
    return text
    


# 機能: URLエンコード文字の変換
# 引数1: 文字列
# 返値: URLエンコード文字に変換した文字列
# 
# URLに「#」「+」「/」「:」「=」などの記号を利用した場合エラーとなる場合がある。
# APIへの入力文字列（特にパスワードで記号を利用している場合）で注意が必要。
#   '#' →   '%23'
#   '+' →   '%2B'
#   '/' →   '%2F'
#   ':' →   '%3A'
#   '=' →   '%3D'
def func_replace_urlecnode( str_input ):
    str_encode = ''
    str_replace = ''
    
    for i in range(len(str_input)):
        str_char = str_input[i:i+1]

        if str_char == ' ' :
            str_replace = '%20'       #「 」 → 「%20」 半角空白
        elif str_char == '!' :
            str_replace = '%21'       #「!」 → 「%21」
        elif str_char == '"' :
            str_replace = '%22'       #「"」 → 「%22」
        elif str_char == '#' :
            str_replace = '%23'       #「#」 → 「%23」
        elif str_char == '$' :
            str_replace = '%24'       #「$」 → 「%24」
        elif str_char == '%' :
            str_replace = '%25'       #「%」 → 「%25」
        elif str_char == '&' :
            str_replace = '%26'       #「&」 → 「%26」
        elif str_char == "'" :
            str_replace = '%27'       #「'」 → 「%27」
        elif str_char == '(' :
            str_replace = '%28'       #「(」 → 「%28」
        elif str_char == ')' :
            str_replace = '%29'       #「)」 → 「%29」
        elif str_char == '*' :
            str_replace = '%2A'       #「*」 → 「%2A」
        elif str_char == '+' :
            str_replace = '%2B'       #「+」 → 「%2B」
        elif str_char == ',' :
            str_replace = '%2C'       #「,」 → 「%2C」
        elif str_char == '/' :
            str_replace = '%2F'       #「/」 → 「%2F」
        elif str_char == ':' :
            str_replace = '%3A'       #「:」 → 「%3A」
        elif str_char == ';' :
            str_replace = '%3B'       #「;」 → 「%3B」
        elif str_char == '<' :
            str_replace = '%3C'       #「<」 → 「%3C」
        elif str_char == '=' :
            str_replace = '%3D'       #「=」 → 「%3D」
        elif str_char == '>' :
            str_replace = '%3E'       #「>」 → 「%3E」
        elif str_char == '?' :
            str_replace = '%3F'       #「?」 → 「%3F」
        elif str_char == '@' :
            str_replace = '%40'       #「@」 → 「%40」
        elif str_char == '[' :
            str_replace = '%5B'       #「[」 → 「%5B」
        elif str_char == ']' :
            str_replace = '%5D'       #「]」 → 「%5D」
        elif str_char == '^' :
            str_replace = '%5E'       #「^」 → 「%5E」
        elif str_char == '`' :
            str_replace = '%60'       #「`」 → 「%60」
        elif str_char == '{' :
            str_replace = '%7B'       #「{」 → 「%7B」
        elif str_char == '|' :
            str_replace = '%7C'       #「|」 → 「%7C」
        elif str_char == '}' :
            str_replace = '%7D'       #「}」 → 「%7D」
        elif str_char == '~' :
            str_replace = '%7E'       #「~」 → 「%7E」
        else :
            str_replace = str_char

        str_encode = str_encode + str_replace
        
    return str_encode



# 機能： API問合せ文字列を作成し返す。
# 戻り値： url文字列
# 第１引数： ログインは、Trueをセット。それ以外はFalseをセット。
# 第２引数： ログインは、APIのurlをセット。それ以外はログインで返された仮想url（'sUrlRequest'等）の値をセット。
# 第３引数： 要求項目のデータセット。クラスの配列として受取る。
def func_make_url_request(auth_flg, \
                          url_target, \
                          work_class_req) :
    
    str_url = url_target
    if auth_flg == True :
        str_url = str_url + 'auth/'
    
    str_url = str_url + '?{\n\t'
    
    for i in range(len(work_class_req)) :
        if len(work_class_req[i].str_key) > 0:
            str_url = str_url + work_class_req[i].str_key + ':' + work_class_req[i].str_value + ',\n\t'
        
    str_url = str_url[:-3] + '\n}'
    return str_url



# 機能: API問合せ。通常のrequest,price用。
# 返値: API応答（辞書型）
# 第１引数： URL文字列。
# 備考: APIに接続し、requestの文字列を送信し、応答データを辞書型で返す。
#       master取得は専用の func_api_req_muster を利用する。
def func_api_req(str_url): 
    print('送信文字列＝')
    print(str_url)  # 送信する文字列

    # APIに接続
    http = urllib3.PoolManager()
    req = http.request('GET', str_url)
    print("req.status= ", req.status )

    # 取得したデータを、json.loadsを利用できるようにstr型に変換する。日本語はshift-jis。
    bytes_reqdata = req.data
    str_shiftjis = bytes_reqdata.decode("shift-jis", errors="ignore")

    print('返信文字列＝')
    print(str_shiftjis)

    # JSON形式の文字列を辞書型で取り出す
    json_req = json.loads(str_shiftjis)

    return json_req



# ログイン関数
# 引数1: p_noカウンター
# 引数2: アクセスするurl（'auth/'以下は付けない）
# 引数3: ユーザーID
# 引数4: パスワード
# 引数5: 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_login(int_p_no, url_base, str_userid, str_passwd, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p2/43 No.1 引数名:CLMAuthLoginRequest を参照してください。
    
    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sCLMID"'
    str_value = 'CLMAuthLoginRequest'
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sUserId"'
    str_value = str_userid
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    str_key = '"sPassword"'
    str_value = str_passwd
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_cust_property.sJsonOfmt    # "5"は "1"（1ビット目ＯＮ）と”4”（3ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # ログインとログイン後の電文が違うため、第１引数で指示。
    # ログインはTrue。それ以外はFalse。
    # このプログラムでの仕様。APIの仕様ではない。
    # URL文字列の作成
    str_url = func_make_url_request(True, \
                                     url_base, \
                                     req_item)
    # API問合せ
    json_return = func_api_req(str_url)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p2/43 No.2 引数名:CLMAuthLoginAck を参照してください。

    int_p_errno = int(json_return.get('p_errno'))    # p_erronは、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、利用方法、データ仕様」を参照ください。
    int_sResultCode = int(json_return.get('sResultCode'))
    # sResultCodeは、マニュアル
    # 「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、注文入力機能引数項目仕様」
    # (api_request_if_order_vOrO.pdf)
    # の p13/42 「6.メッセージ一覧」を参照ください。

    if int_p_errno ==  0 and int_sResultCode == 0:    # ログインエラーでない場合
        # ---------------------------------------------
        # ログインでの注意点
        # 契約締結前書面が未読の場合、
        # 「int_p_errno = 0 And int_sResultCode = 0」で、
        # sUrlRequest=""、sUrlEvent="" が返されログインできない。
        # ---------------------------------------------
        if len(json_return.get('sUrlRequest')) > 0 :
            # 口座属性クラスに取得した値をセット
            class_cust_property.sZyoutoekiKazeiC = json_return.get('sZyoutoekiKazeiC')
            class_cust_property.sUrlRequest = json_return.get('sUrlRequest')        # request用仮想URL
            class_cust_property.sUrlMaster = json_return.get('sUrlMaster')          # master用仮想URL
            class_cust_property.sUrlPrice = json_return.get('sUrlPrice')            # price用仮想URL
            class_cust_property.sUrlEvent = json_return.get('sUrlEvent')            # event用仮想URL
            bool_login = True
        else :
            print('契約締結前書面が未読です。')
            print('ブラウザーで標準Webにログインして確認してください。')
    else :  # ログインに問題があった場合
        print('p_errno:', json_return.get('p_errno'))
        print('p_err:', json_return.get('p_err'))
        print('sResultCode:', json_return.get('sResultCode'))
        print('sResultText:', json_return.get('sResultText'))
        print()
        bool_login = False

    return bool_login


# ログアウト
# 引数1: p_noカウンター
# 引数2: class_cust_property（request通番）, 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_logout(int_p_no, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/43 No.3 引数名:CLMAuthLogoutRequest を参照してください。
    
    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sCLMID"'
    str_value = 'CLMAuthLogoutRequest'  # logoutを指示。
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_cust_property.sJsonOfmt    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # ログインとログイン後の電文が違うため、第１引数で指示。
    # ログインはTrue。それ以外はFalse。
    # このプログラムでの仕様。APIの仕様ではない。
    # URL文字列の作成
    str_url = func_make_url_request(False, \
                                     class_cust_property.sUrlRequest, \
                                     req_item)
    # API問合せ
    json_return = func_api_req(str_url)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/43 No.4 引数名:CLMAuthLogoutAck を参照してください。

    int_sResultCode = int(json_return.get('sResultCode'))    # p_erronは、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、利用方法、データ仕様」を参照ください。
    if int_sResultCode ==  0 :    # ログアウトエラーでない場合
        bool_logout = True
    else :  # ログアウトに問題があった場合
        bool_logout = False

    return bool_logout

#--- 以上 共通コード -------------------------------------------------




# 参考資料（必ず最新の資料を参照してください。）
#マニュアル
#「立花証券・ｅ支店・ＡＰＩ（v4r2）、REQUEST I/F、機能毎引数項目仕様」
# (api_request_if_clumn_v4r2.pdf)
# p17/46 No.14 CLMOrderListDetail を参照してください。
#
# 14 CLMOrderListDetail
#  1	sCLMID	メッセージＩＤ	char*	I/O	"CLMOrderListDetail"
#  2	sOrderNumber	注文番号	char[8]	I/O	0～99999999、左詰め、マイナスの場合なし
#  3	sEigyouDay	営業日	char[8]	I/O	YYYYMMDD
#  4	sResultCode	結果コード	char[9]	O	０：ＯＫ、０以外：CLMMsgTable.sMsgIdで検索しテキストを表示。0～999999999、左詰め、マイナスの場合なし
#  5	sResultText	結果テキスト	char[512]	O	ShiftJis
#  6	sWarningCode	警告コード	char[9]	O	０：ＯＫ、０以外：CLMMsgTable.sMsgIdで検索しテキストを表示。0～999999999、左詰め、マイナスの場合なし
#  7	sWarningText	警告テキスト	char[512]	O	ShiftJis
#  8	sIssueCode	銘柄CODE	char[12]	O	銘柄コード（6501 等）
#  9	sOrderSizyouC	市場	char[2]	O	00：東証
# 10	sOrderBaibaiKubun	売買区分	char[1]	O	1：売、3：買、5：現渡、7：現引
# 11	sGenkinSinyouKubun	現金信用区分	char[1]	O	0：現物、2：新規(制度信用6ヶ月)、4：返済(制度信用6ヶ月)、6：新規(一般信用6ヶ月)、8：返済(一般信用6ヶ月)
# 12	sOrderBensaiKubun	弁済区分	char[2]	O	00：なし、26：制度信用6ヶ月、29：制度信用無期限、36：一般信用6ヶ月、39：一般信用無期限
# 13	sOrderCondition	執行条件	char[1]	O	0：指定なし、2：寄付、4：引け、6：不成
# 14	sOrderOrderPriceKubun	注文値段区分	char[1]	O	△：未使用、1：成行、2：指値、3：親注文より高い、4：親注文より低い
# 15	sOrderOrderPrice	注文単価	char[14]	O	0.0000～999999999.9999、左詰め、マイナスの場合なし、小数点以下桁数切詰
# 16	sOrderOrderSuryou	注文株数	char[13]	O	照会機能仕様書 ２－８．（３）、（B1）注文詳細 No.9。0～9999999999999、左詰め、マイナスの場合なし
# 17	sOrderCurrentSuryou	有効株数	char[13]	O	0～9999999999999、左詰め、マイナスの場合なし
# 18	sOrderStatusCode	状態コード	char[2]	O	[逆指値]、[通常+逆指値]注文時以外の状態
#   					0：受付未済
#   					1：未約定
#   					2：受付エラー
#   					3：訂正中
#   					4：訂正完了
#   					5：訂正失敗
#   					6：取消中
#   					7：取消完了
#   					8：取消失敗
#   					9：一部約定
#   					10：全部約定
#   					11：一部失効
#   					12：全部失効
#   					13：発注待ち
#   					14：無効
#   					15：切替注文
#   					16：切替完了
#   					17：切替注文失敗
#   					19：繰越失効
#   					20：一部障害処理
#   					21：障害処理
#   					
#   					[逆指値]、[通常+逆指値]注文時の状態
#   					15：逆指注文(切替中)
#   					16：逆指注文(未約定)
#   					17：逆指注文(失敗)
#   					50：発注中
# 19	sOrderStatus	状態	char[20]	O	
# 20	sOrderOrderDateTime	注文日付	char[14]	O	YYYYMMDDHHMMSS,00000000000000
# 21	sOrderOrderExpireDay	有効期限	char[8]	O	YYYYMMDD,00000000
# 22	sChannel	チャネル	char[1]	O	チャネル
#   					0：対面
#   					1：PC
#   					2：コールセンター
#   					3：コールセンター
#   					4：コールセンター
#   					5：モバイル
#   					6：リッチ
#   					7：スマホ・タブレット
#   					8：iPadアプリ
#   					9：HOST
# 23	sGenbutuZyoutoekiKazeiC	現物口座区分	char[1]	O	譲渡益課税Ｃ（現物）。 1：特定、3：一般、5：NISA
# 24	sSinyouZyoutoekiKazeiC	建玉口座区分	char[1]	O	譲渡益課税Ｃ（信用）。1：特定、3：一般、5：NISA
# 25	sGyakusasiOrderType	逆指値注文種別	char[1]	O	0：通常、1：逆指値、2：通常＋逆指値
# 26	sGyakusasiZyouken	逆指値条件	char[14]	O	0.0000～999999999.9999、左詰め、マイナスの場合なし、小数点以下桁数切詰
# 27	sGyakusasiKubun	逆指値値段区分	char[1]	O	△：未使用、0：成行、1：指値
# 28	sGyakusasiPrice	逆指値値段	char[14]	O	0.0000～999999999.9999、左詰め、マイナスの場合なし、小数点以下桁数切詰
# 29	sTriggerType	トリガータイプ	char[1]	O	0：未トリガー、1：自動、2：手動発注、3：手動失効。初期状態は「0」で、トリガー発火後は「1/2/3」のどれかに遷移する
# 30	sTriggerTime	トリガー日時	char[14]	O	YYYYMMDDHHMMSS,00000000000000
# 31	sUkewatasiDay	受渡日	char[8]	O	YYYYMMDD,00000000
# 32	sYakuzyouPrice	約定単価	char[14]	O	照会機能仕様書 ２－８．（３）、（B2）約定内容詳細 No.2。0.0000～999999999.9999、左詰め、マイナスの場合なし、小数点以下桁数切詰
# 33	sYakuzyouSuryou	約定株数	char[13]	O	0～9999999999999、左詰め、マイナスの場合なし
# 34	sBaiBaiDaikin	売買代金	char[16]	O	0～9999999999999999、左詰め、マイナスの場合なし
# 35	sUtidekiKubun	内出来区分	char[1]	O	△：約定分割以外、2：約定分割
# 36	sGaisanDaikin	概算代金	char[16]	O	0～9999999999999999、左詰め、マイナスの場合なし
# 37	sBaiBaiTesuryo	手数料	char[16]	O	0～9999999999999999、左詰め、マイナスの場合なし
# 38	sShouhizei	消費税	char[16]	O	0～9999999999999999、左詰め、マイナスの場合なし
# 39	sTatebiType	建日種類	char[1]	O	△：指定なし、1：個別指定、2：建日順、3：単価益順、4：単価損順
# 40	sSizyouErrorCode	市場/取次ErrorCode	char[6]	O
#                                       照会機能仕様書 ２－８．（３）、（C1）注文履歴 No.1。
#                                       株式明細.執行市場(2桁) + 株式注文約定履歴.取引所エラー／理由コード(4桁)。
#                                       ※取引所エラーがない場合は、null。
# 41	sZougen	リバース増減値	char[14]	O	項目は残すが使用しない
# 42	sOrderAcceptTime	市場注文受付時刻	char[14]	O	YYYYMMDDHHMMSS,00000000000000
#                                       照会機能仕様書 ２－８．（３）、（X） 以下は標準WebになくRich-I/Fにある項目 No.7。
#                                       株式明細.取引所受付／エラー時刻。
#                                       ※「通常＋逆指値」の場合は、最初の通常注文の市場注文受付時刻をセット
# 43	aYakuzyouSikkouList	約定失効リスト（※項目数に増減がある場合は、右記のカラム数も変更すること）	char[17]	O	以下レコードを配列で設定
# 44-1	sYakuzyouWarningCode	警告コード	char[9]	O	０：ＯＫ、０以外：CLMMsgTable.sMsgIdで検索しテキストを表示。0～999999999、左詰め、マイナスの場合なし
# 45-2	sYakuzyouWarningText	警告テキスト	char[512]	O	ShiftJis
# 46-3	sYakuzyouSuryou	約定数量	char[13]	O	0～9999999999999、左詰め、マイナスの場合なし
# 47-4	sYakuzyouPrice	約定価格	char[14]	O	0.0000～999999999.9999、左詰め、マイナスの場合なし、小数点以下桁数切詰
# 48-5	sYakuzyouDate	約定日時	char[14]	O	YYYYMMDDHHMMSS,00000000000000
# 49	aKessaiOrderTategyokuList	決済注文建株指定リスト（※項目数に増減がある場合は、右記のカラム数も変更すること）	char[17]	O	以下レコードを配列で設定
# 50-1	sKessaiWarningCode	警告コード	char[9]	O	０：ＯＫ、０以外：CLMMsgTable.sMsgIdで検索しテキストを表示。0～999999999、左詰め、マイナスの場合なし
# 51-2	sKessaiWarningText	警告テキスト	char[512]	O	ShiftJis
# 52-3	sKessaiTatebiZyuni	順位	char[9]	O	0～999999999、左詰め、マイナスの場合なし
# 53-4	sKessaiTategyokuDay	建日	char[8]	O	YYYYMMDD,00000000
# 54-5	sKessaiTategyokuPrice	建単価	char[14]	O	0.0000～999999999.9999、左詰め、マイナスの場合なし、小数点以下桁数切詰
# 55-6	sKessaiOrderSuryo	返済注文株数	char[13]	O	0～9999999999999、左詰め、マイナスの場合なし
# 56-7	sKessaiYakuzyouSuryo	約定株数	char[13]	O	0～9999999999999、左詰め、マイナスの場合なし
# 57-8	sKessaiYakuzyouPrice	約定単価	char[14]	O	0.0000～999999999.9999、左詰め、マイナスの場合なし、小数点以下桁数切詰
# 58-9	sKessaiTateTesuryou	建手数料	char[16]	O	照会機能仕様書 ２－８．（３）、（D1）決済注文建株指定詳細 No.15。0～9999999999999999、左詰め、マイナスの場合なし
# 59-10	sKessaiZyunHibu	順日歩	char[16]	O	照会機能仕様書 ２－８．（３）、（D1）決済注文建株指定詳細 No.16。0～9999999999999999、左詰め、マイナスの場合なし
# 60-11	sKessaiGyakuhibu	逆日歩	char[16]	O	照会機能仕様書 ２－８．（３）、（D1）決済注文建株指定詳細 No.17。0～9999999999999999、左詰め、マイナスの場合なし
# 61-12	sKessaiKakikaeryou	書換料	char[16]	O	照会機能仕様書 ２－８．（３）、（D1）決済注文建株指定詳細 No.18。0～9999999999999999、左詰め、マイナスの場合なし
# 62-13	sKessaiKanrihi	管理費	char[16]	O	照会機能仕様書 ２－８．（３）、（D1）決済注文建株指定詳細 No.19。0～9999999999999999、左詰め、マイナスの場合なし
# 63-14	sKessaiKasikaburyou	貸株料	char[16]	O	照会機能仕様書 ２－８．（３）、（D1）決済注文建株指定詳細 No.20。0～9999999999999999、左詰め、マイナスの場合なし
# 64-15	sKessaiSonota	その他	char[16]	O	照会機能仕様書 ２－８．（３）、（D1）決済注文建株指定詳細 No.21。0～9999999999999999、左詰め、マイナスの場合なし
# 65-16	sKessaiSoneki	決済損益/受渡代金	char[16]	O	照会機能仕様書 ２－８．（３）、（D1）決済注文建株指定詳細 No.22。-999999999999999～9999999999999999、左詰め、マイナスの場合あり




# --------------------------
# 機能: 注文約定詳細取得
# 返値: API応答（辞書型）
# 引数1: p_no
# 引数2: 注文番号
# 引数3: 営業日
# 引数4: class_cust_property（request通番）, 口座属性クラス
# 備考:
#       注文約定詳細は、注文番号、営業日の省略不可。
def func_get_orderlist_detail(int_p_no,
                                str_sOrderNumber,
                                str_sEigyouDay,
                                class_cust_property):

    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # コマンド
    str_key = '"sCLMID"'
    str_value = 'CLMOrderListDetail'  # 注文約定一覧詳細を指定。
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 注文番号　省略不可
    str_key = '"sOrderNumber"'
    str_value = str_sOrderNumber      # 注文番号は、注文約定一覧で取得できる。
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 営業日　省略不可
    str_key = '"sEigyouDay"'
    str_value = str_sEigyouDay        # yyyymmdd 営業日
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_cust_property.sJsonOfmt    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # URL文字列の作成
    str_url = func_make_url_request(False, \
                                     class_cust_property.sUrlRequest, \
                                     req_item)

    json_return = func_api_req(str_url)

    return json_return





    
# ======================================================================================================
# ==== プログラム始点 =================================================================================
# ======================================================================================================

# --- 利用時に変数を設定してください -------------------------------------------------------

# 接続先 設定 --------------
# デモ環境（新バージョンになった場合、適宜変更）
my_url = 'https://demo-kabuka.e-shiten.jp/e_api_v4r2/'
##my_url = 'https://demo-kabuka.e-shiten.jp/e_api_v4r3/'

# 本番環境（新バージョンになった場合、適宜変更）
# ＊＊！！実際に市場に注文が出るので注意！！＊＊
# my_url = 'https://kabuka.e-shiten.jp/e_api_v4r3/'


# ＩＤパスワード設定 ---------
my_userid = 'MY_USERID' # 自分のuseridに書き換える
my_passwd = 'MY_PASSWD' # 自分のpasswordに書き換える
my_2pwd = 'MY_2PASSWD'  # 自分の第２passwordに書き換える

# コマンド用パラメーター -------------------    
my_sOrderNumber  = '12345678'    # 注文番号 省略不可
my_sEigyouDay    = '20221024'    # 営業日 省略不可 yyyymmdd
# 注文約定詳細は、注文番号、営業日は省略不可。



# --- 以上設定項目 -------------------------------------------------------------------------


class_cust_property = class_def_cust_property()     # 口座属性クラス

# ID、パスワード、第２パスワードのURLエンコードをチェックして変換
my_userid = func_replace_urlecnode(my_userid)
my_passwd = func_replace_urlecnode(my_passwd)
class_cust_property.sSecondPassword = func_replace_urlecnode(my_2pwd)

# 返り値の表示形式指定
class_cust_property.sJsonOfmt = '5'
# "5"は "1"（1ビット目ＯＮ）と”4”（3ビット目ＯＮ）の指定となり
# ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定

print('-- login -----------------------------------------------------')
# 送信項目、戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
# p2/46 No.1 引数名:CLMAuthLoginRequest を参照してください。
int_p_no = 1
# ログイン処理
bool_login = func_login(int_p_no, my_url, my_userid, my_passwd,  class_cust_property)

# ログインOKの場合
if bool_login :
    
    
    print()
    print('-- 注文約定詳細 の照会 -------------------------------------------------------------')
    int_p_no = int_p_no + 1
    json_return = func_get_orderlist_detail(int_p_no,
                                              my_sOrderNumber,
                                              my_sEigyouDay,
                                              class_cust_property)
    # 送信項目、戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p17/46 No.14 CLMOrderListDetail を参照してください。
        
    print("結果コード= ", json_return.get("sResultCode"))           # 5
    print("結果テキスト= ", json_return.get("sResultText"))  # 6
    print('銘柄CODE:\t', json_return.get('sIssueCode'))
    print('市場:\t', json_return.get('sOrderSizyouC'))
    print('売買区分:\t', json_return.get('sOrderBaibaiKubun'))
    print('現金信用区分:\t', json_return.get('sGenkinSinyouKubun'))
    print('弁済区分:\t', json_return.get('sOrderBensaiKubun'))
    print('執行条件:\t', json_return.get('sOrderCondition'))
    print('注文値段区分:\t', json_return.get('sOrderOrderPriceKubun'))
    print('注文単価:\t', json_return.get('sOrderOrderPrice'))
    print('注文株数:\t', json_return.get('sOrderOrderSuryou'))
    print('有効株数:\t', json_return.get('sOrderCurrentSuryou'))
    print('状態コード:\t', json_return.get('sOrderStatusCode'))
    print('状態:\t', json_return.get('sOrderStatus'))
    print('注文日付:\t', json_return.get('sOrderOrderDateTime'))
    print('有効期限:\t', json_return.get('sOrderOrderExpireDay'))
    print('チャネル:\t', json_return.get('sChannel'))
    print('現物口座区分:\t', json_return.get('sGenbutuZyoutoekiKazeiC'))
    print('建玉口座区分:\t', json_return.get('sSinyouZyoutoekiKazeiC'))
    print('逆指値注文種別:\t', json_return.get('sGyakusasiOrderType'))
    print('逆指値条件:\t', json_return.get('sGyakusasiZyouken'))
    print('逆指値値段区分:\t', json_return.get('sGyakusasiKubun'))
    print('逆指値値段:\t', json_return.get('sGyakusasiPrice'))
    print('トリガータイプ:\t', json_return.get('sTriggerType'))
    print('トリガー日時:\t', json_return.get('sTriggerTime'))
    print('受渡日:\t', json_return.get('sUkewatasiDay'))
    print('約定単価:\t', json_return.get('sYakuzyouPrice'))
    print('約定株数:\t', json_return.get('sYakuzyouSuryou'))
    print('売買代金:\t', json_return.get('sBaiBaiDaikin'))
    print('内出来区分:\t', json_return.get('sUtidekiKubun'))
    print('概算代金:\t', json_return.get('sGaisanDaikin'))
    print('手数料:\t', json_return.get('sBaiBaiTesuryo'))
    print('消費税:\t', json_return.get('sShouhizei'))
    print('建日種類:\t', json_return.get('sTatebiType'))
    print('市場/取次ErrorCode:\t', json_return.get('sSizyouErrorCode'))
    print('リバース増減値:\t', json_return.get('sZougen'))
    print('市場注文受付時刻:\t', json_return.get('sOrderAcceptTime'))
    print()
    print()
    
    print('==========================')
    list_aYakuzyouSikkouList = json_return.get("aYakuzyouSikkouList")
    print('約定失効リスト = aYakuzyouSikkouList')
    print('件数:', len(list_aYakuzyouSikkouList))
    print()
    # 'aYakuzyouSikkouList'の返値の処理。
    # データ形式は、"aYakuzyouSikkouList":[{...},{...}, ... ,{...}]
    for i in range(len(list_aYakuzyouSikkouList)):
        print('No.', i+1, '---------------')
        print('警告コード:\t', list_aYakuzyouSikkouList[i].get('sYakuzyouWarningCode'))
        print('警告テキスト:\t', list_aYakuzyouSikkouList[i].get('sYakuzyouWarningText'))
        print('約定数量:\t', list_aYakuzyouSikkouList[i].get('sYakuzyouSuryou'))
        print('約定価格:\t', list_aYakuzyouSikkouList[i].get('sYakuzyouPrice'))
        print('約定日時:\t', list_aYakuzyouSikkouList[i].get('sYakuzyouDate'))
    print()
    print()

    print('==========================')
    list_aKessaiOrderTategyokuList = json_return.get("aKessaiOrderTategyokuList")
    print('決済注文建株指定リスト= aYakuzyouSikkouList')
    print('件数:', len(list_aKessaiOrderTategyokuList))
    print()
    # 'aKessaiOrderTategyokuList'の返値の処理。
    # データ形式は、"aYakuzyouSikkouList":[{...},{...}, ... ,{...}]
    for n in range(len(list_aKessaiOrderTategyokuList)):
        print('No.', n+1, '---------------')
        print('警告コード:\t', list_aKessaiOrderTategyokuList[n].get('sKessaiWarningCode'))
        print('警告テキスト:\t', list_aKessaiOrderTategyokuList[n].get('sKessaiWarningText'))
        print('順位:\t', list_aKessaiOrderTategyokuList[n].get('sKessaiTatebiZyuni'))
        print('建日:\t', list_aKessaiOrderTategyokuList[n].get('sKessaiTategyokuDay'))
        print('建単価:\t', list_aKessaiOrderTategyokuList[n].get('sKessaiTategyokuPrice'))
        print('返済注文株数:\t', list_aKessaiOrderTategyokuList[n].get('sKessaiOrderSuryo'))
        print('約定株数:\t', list_aKessaiOrderTategyokuList[n].get('sKessaiYakuzyouSuryo'))
        print('約定単価:\t', list_aKessaiOrderTategyokuList[n].get('sKessaiYakuzyouPrice'))
        print('建手数料:\t', list_aKessaiOrderTategyokuList[n].get('sKessaiTateTesuryou'))
        print('順日歩:\t', list_aKessaiOrderTategyokuList[n].get('sKessaiZyunHibu'))
        print('逆日歩:\t', list_aKessaiOrderTategyokuList[n].get('sKessaiGyakuhibu'))
        print('書換料:\t', list_aKessaiOrderTategyokuList[n].get('sKessaiKakikaeryou'))
        print('管理費:\t', list_aKessaiOrderTategyokuList[n].get('sKessaiKanrihi'))
        print('貸株料:\t', list_aKessaiOrderTategyokuList[n].get('sKessaiKasikaburyou'))
        print('その他:\t', list_aKessaiOrderTategyokuList[n].get('sKessaiSonota'))
        print('決済損益/受渡代金:\t', list_aKessaiOrderTategyokuList[n].get('sKessaiSoneki'))
        print()
        
            
    print()
    print('-- logout -------------------------------------------------------------')
    # 送信項目、戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/46 No.3 引数名:CLMAuthLogoutRequest を参照してください。
    int_p_no = int_p_no + 1
    bool_logout = func_logout(int_p_no, class_cust_property)
   
else :
    print('ログインに失敗しました')
