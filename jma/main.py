# import asyncio
# import requests
# import flet as ft
# from flet import Dropdown, dropdown, ElevatedButton, Column, ListView, Text
# from datetime import datetime
# import sqlite3

# # グローバルイベントループの設定
# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)

# # 日本気象庁のAPIから地域リストを取得する関数
# def get_area_list():
#     url = "https://www.jma.go.jp/bosai/common/const/area.json"
#     response = requests.get(url)
#     response.raise_for_status()
#     return response.json()

# # 地域ごとの天気情報を取得する非同期関数
# async def get_weather_forecast(region_code):
#     url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{region_code}.json"
#     response = await asyncio.to_thread(requests.get, url)
#     response.raise_for_status()
#     return response.json()

# # 日付フォーマットを変換する関数
# def format_date(date_str):
#     date = datetime.fromisoformat(date_str)
#     return date.strftime("%m月%d日")

# # データベースに天気データを保存する関数
# def save_weather_to_db(location, datetime, weather, temperature_max, temperature_min, humidity, wind_speed):
#     # データベースに再接続
#     con = sqlite3.connect(path + db_name)
#     cur = con.cursor()

#     # データを挿入するSQL
#     sql_insert = """
#     INSERT INTO weather_reports (location, datetime, weather, temperature_max, temperature_min, humidity, wind_speed)
#     VALUES (?, ?, ?, ?, ?, ?, ?);
#     """

#     # データ挿入
#     cur.execute(sql_insert, (location, datetime, weather, temperature_max, temperature_min, humidity, wind_speed))

#     # コミット処理（データ操作を反映させる）
#     con.commit()

#     # DBへの接続を閉じる
#     con.close()

# # 特定のエリアの天気情報を表示
# def show_area_weather(e, area_data, temperature_data):
#     if area_data:
#         weathers = area_data.get("weathers", [])
#         timeDefines = area_data.get("timeDefines", [])
#         max_temps = temperature_data.get("tempsMax", []) if temperature_data else []
#         min_temps = temperature_data.get("tempsMin", []) if temperature_data else []
#         if weathers and timeDefines:
#             weather_messages = []
#             for i, (date, weather) in enumerate(zip(timeDefines[:3], weathers[:3])):
#                 formatted_date = format_date(date)
#                 weather = weather.replace('　', '')  # 全角スペースを削除する
#                 max_temp = f"{max_temps[i]}℃" if i < len(max_temps) and max_temps[i] else "-℃"
#                 min_temp = f"{min_temps[i]}℃" if i < len(min_temps) and min_temps[i] else "-℃"
#                 weather_messages.append(f"{formatted_date} の天気: {weather}\n最高気温: {max_temp}, 最低気温: {min_temp}")
#             weather_text.value = "\n\n".join(weather_messages)
#         else:
#             weather_text.value = "天気情報が取得できませんでした。"
#     else:
#         weather_text.value = "天気情報が取得できませんでした。"
#     page.update()

# # 地域選択後の処理（非同期関数）
# async def on_dropdown_change_async(selected_region_name):
#     region_codes = regions[selected_region_name]
#     area_buttons.controls.clear()

#     for region_code in region_codes:
#         weather_data = await load_forecast(region_code)
#         if weather_data:
#             for area in weather_data[0]['timeSeries'][0]['areas']:
#                 if "weathers" in area:
#                     area_name = area['area']['name']
#                     # 都道府県名を追加
#                     area_full_name = f"{area_names.get(region_code, '未知の地域')} - {area_name}"
#                     print(f"ボタンが追加される予定の地域: {area_full_name}")
#                     area_button = ElevatedButton(text=area_full_name, on_click=lambda e, area=area, temp_data=weather_data[1]['timeSeries'][1] if len(weather_data[1]['timeSeries']) > 1 else None: show_area_weather(e, area, temp_data))
#                     area_buttons.controls.append(area_button)
#                 # 時間定義を保存しておく
#                 area["timeDefines"] = weather_data[0]['timeSeries'][0]['timeDefines']

#     page.update()

# # 地域選択後の同期ラッパー関数
# def on_dropdown_change(e):
#     selected_region_name = e.control.value
#     asyncio.run_coroutine_threadsafe(on_dropdown_change_async(selected_region_name), loop)

# # 地域ごとの天気情報をロードする非同期関数
# async def load_forecast(region_code):
#     try:
#         weather_data = await get_weather_forecast(region_code)
#         print(f"地域コード {region_code} の天気情報: {weather_data[0]['timeSeries'][0]['areas']}")
#         return weather_data
#     except requests.exceptions.HTTPError as ex:
#         print(f"HTTPエラーが発生しました: {ex}")
#         return None

# # メイン関数
# def main(pg):
#     global area_buttons, weather_text, regions, page, area_names
#     page = pg
#     page.title = "天気予報アプリケーション - 地域ごとの天気"

#     area_data = get_area_list()

#     # 都道府県名のマッピング
#     area_names = {code: info["name"] for code, info in area_data["offices"].items()}

#     regions = {
#         "北海道地方": ["011000", "012000", "013000", "014030", "014100", "015000", "016000", "017000"],
#         "東北地方": ["020000", "030000", "040000", "050000", "060000", "070000"],
#         "関東甲信地方": ["080000", "090000", "100000", "110000", "120000", "130000", "140000", "190000", "200000"],
#         "東海地方": ["210000", "220000", "230000", "240000"],
#         "北陸地方": ["150000", "160000", "170000", "180000"],
#         "近畿地方": ["250000", "260000", "270000", "280000", "290000", "300000"],
#         "中国地方（山口県を除く）": ["310000", "320000", "330000", "340000"],
#         "四国地方": ["360000", "370000", "380000", "390000"],
#         "九州北部地方（山口県を含む）": ["400000", "410000", "420000", "430000", "440000", "350000"],
#         "九州南部・奄美地方": ["450000", "460100", "460040"],
#         "沖縄地方": ["471000", "472000", "473000", "474000"]
#     }

#     dropdown_items = [dropdown.Option(region) for region in regions.keys()]

#     dropdown_list = Dropdown(options=dropdown_items, on_change=on_dropdown_change, width=400)
#     area_buttons = Column()
#     weather_text = Text(value="天気予報がここに表示されます", expand=True)

#     # スクロール可能なListViewにラップ
#     scrollable_area = ListView(
#         controls=[area_buttons],
#         expand=True,
#         height=400,
#         width=400
#     )

#     page.add(dropdown_list)
#     page.add(scrollable_area)
#     page.add(weather_text)
#     page.update()

#     global loop
#     if not loop.is_running():
#         loop.run_forever()

# # アプリケーション実行
# ft.app(target=main)


import asyncio
import requests
import flet as ft
import sqlite3
from flet import Dropdown, dropdown, ElevatedButton, Column, ListView, Text
from datetime import datetime

# グローバルイベントループの設定
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# データベースのパスと名前
db_name = 'weather.db'
db_path = './'

# SQLiteデータベースのセットアップとテーブル作成
def setup_database():
    conn = sqlite3.connect(db_path + db_name)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS weather_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location TEXT NOT NULL,
        datetime TEXT NOT NULL,
        weather TEXT,
        temperature_max REAL,
        temperature_min REAL,
        humidity REAL,
        wind_speed REAL
    )
    ''')

    conn.commit()
    conn.close()

# データベースからデータを読み込む関数
def fetch_weather_reports():
    conn = sqlite3.connect(db_path + db_name)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM weather_reports')
    rows = cursor.fetchall()
    
    conn.close()
    return rows

# 日本気象庁のAPIから地域リストを取得する関数
def get_area_list():
    url = "https://www.jma.go.jp/bosai/common/const/area.json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# 地域ごとの天気情報を取得する非同期関数
async def get_weather_forecast(region_code):
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{region_code}.json"
    response = await asyncio.to_thread(requests.get, url)
    response.raise_for_status()
    return response.json()

# 天気データをデータベースに保存する関数
def save_weather_to_db(location, datetime, weather, temperature_max, temperature_min, humidity, wind_speed):
    conn = sqlite3.connect(db_path + db_name)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO weather_reports (location, datetime, weather, temperature_max, temperature_min, humidity, wind_speed)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (location, datetime, weather, temperature_max, temperature_min, humidity, wind_speed))
    
    conn.commit()
    conn.close()

# 日付フォーマットを変換する関数
def format_date(date_str):
    date = datetime.fromisoformat(date_str)
    return date.strftime("%m月%d日")

# 特定のエリアの天気情報を表示
def show_area_weather(location, area_data, temperature_data):
    if area_data:
        weathers = area_data.get("weathers", [])
        timeDefines = area_data.get("timeDefines", [])
        max_temps = temperature_data.get("tempsMax", []) if temperature_data else []
        min_temps = temperature_data.get("tempsMin", []) if temperature_data else []
        if weathers and timeDefines:
            weather_messages = []
            for i, (date, weather) in enumerate(zip(timeDefines[:3], weathers[:3])):
                formatted_date = format_date(date)
                weather = weather.replace('　', '')  # 全角スペースを削除する
                max_temp = f"{max_temps[i]}℃" if i < len(max_temps) and max_temps[i] else "-℃"
                min_temp = f"{min_temps[i]}℃" if i < len(min_temps) and min_temps[i] else "-℃"
                weather_messages.append(f"{formatted_date} の天気: {weather}\n最高気温: {max_temp}, 最低気温: {min_temp}")
                # 天気データをデータベースに保存
                save_weather_to_db(location, formatted_date, weather, max_temps[i] if max_temps else None, min_temps[i] if min_temps else None, None, None)
            weather_text.value = "\n\n".join(weather_messages)
        else:
            weather_text.value = "天気情報が取得できませんでした。"
    else:
        weather_text.value = "天気情報が取得できませんでした。"
    page.update()

# データベース内容を表示するUI用関数
def display_database_contents():
    rows = fetch_weather_reports()
    db_text.value = "\n".join([str(row) for row in rows])
    page.update()

# 地域選択後の処理（非同期関数）
async def on_dropdown_change_async(selected_region_name):
    region_codes = regions[selected_region_name]
    area_buttons.controls.clear()

    for region_code in region_codes:
        weather_data = await load_forecast(region_code)
        if weather_data:
            for area in weather_data[0]['timeSeries'][0]['areas']:
                if "weathers" in area:
                    area_name = area['area']['name']
                    # 都道府県名を追加
                    area_full_name = f"{area_names.get(region_code, '未知の地域')} - {area_name}"
                    print(f"ボタンが追加される予定の地域: {area_full_name}")
                    location = area_full_name  # 位置情報を設定
                    area_button = ElevatedButton(
                        text=area_full_name, 
                        on_click=lambda e, area=area, location=location, temp_data=weather_data[1]['timeSeries'][1] if len(weather_data[1]['timeSeries']) > 1 else None: show_area_weather(location, area, temp_data)
                    )
                    area_buttons.controls.append(area_button)
                # 時間定義を保存しておく
                area["timeDefines"] = weather_data[0]['timeSeries'][0]['timeDefines']

    page.update()

# 地域選択後の同期ラッパー関数
def on_dropdown_change(e):
    selected_region_name = e.control.value
    asyncio.run_coroutine_threadsafe(on_dropdown_change_async(selected_region_name), loop)

# 地域ごとの天気情報をロードする非同期関数
async def load_forecast(region_code):
    try:
        weather_data = await get_weather_forecast(region_code)
        print(f"地域コード {region_code} の天気情報: {weather_data[0]['timeSeries'][0]['areas']}")
        return weather_data
    except requests.exceptions.HTTPError as ex:
        print(f"HTTPエラーが発生しました: {ex}")
        return None

# メイン関数
def main(pg):
    global area_buttons, weather_text, regions, page, area_names, db_text
    page = pg
    page.title = "天気予報アプリケーション - 地域ごとの天気"

    # データベースのセットアップとテーブル作成（存在しない場合に実行）
    setup_database()

    area_data = get_area_list()

    # 都道府県名のマッピング
    area_names = {code: info["name"] for code, info in area_data["offices"].items()}

    regions = {
        "北海道地方": ["011000", "012000", "013000", "014030", "014100", "015000", "016000", "017000"],
        "東北地方": ["020000", "030000", "040000", "050000", "060000", "070000"],
        "関東甲信地方": ["080000", "090000", "100000", "110000", "120000", "130000", "140000", "190000", "200000"],
        "東海地方": ["210000", "220000", "230000", "240000"],
        "北陸地方": ["150000", "160000", "170000", "180000"],
        "近畿地方": ["250000", "260000", "270000", "280000", "290000", "300000"],
        "中国地方（山口県を除く）": ["310000", "320000", "330000", "340000"],
        "四国地方": ["360000", "370000", "380000", "390000"],
        "九州北部地方（山口県を含む）": ["400000", "410000", "420000", "430000", "440000", "350000"],
        "九州南部・奄美地方": ["450000", "460100", "460040"],
        "沖縄地方": ["471000", "472000", "473000", "474000"]
    }

    dropdown_items = [dropdown.Option(region) for region in regions.keys()]

    dropdown_list = Dropdown(options=dropdown_items, on_change=on_dropdown_change, width=400)
    area_buttons = Column()
    weather_text = Text(value="天気予報がここに表示されます", expand=True)

    # スクロール可能なListViewにラップ
    scrollable_area = ListView(
        controls=[area_buttons],
        expand=True,
        height=400,
        width=400
    )

    db_text = Text(value="", expand=True)
    db_display_button = ElevatedButton(text="データベース内容を表示", on_click=lambda e: display_database_contents())

    page.add(dropdown_list)
    page.add(scrollable_area)
    page.add(weather_text)
    page.add(db_display_button)
    page.add(db_text)
    page.update()

    global loop
    if not loop.is_running():
        loop.run_forever()

# アプリケーション実行
ft.app(target=main)