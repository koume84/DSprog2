import asyncio
import requests
import flet as ft
import sqlite3
from flet import Dropdown, dropdown, ElevatedButton, Column, ListView, Image, Text, Container, Row, ScrollMode, MainAxisAlignment
from datetime import datetime

# グローバルイベントループの設定
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# データベースのパスと名前
db_name = 'weather.db'
db_path = './'

# 天気コードからアイコンURLを取得する関数
def get_weather_icon(weather_code):
    weather_category = int(weather_code) // 100  # 百の位を取得
    if weather_category == 1:
        return "https://illalet.com/wp-content/uploads/2017/05/16_2_19.png"  # 晴れ
    elif weather_category == 2:
        return "https://illalet.com/wp-content/uploads/2017/05/16_2_21.png"  # 曇り
    elif weather_category == 3:
        return "https://illalet.com/wp-content/uploads/2017/05/16_2_23.png"  # 雨
    elif weather_category == 4:
        return "https://illalet.com/wp-content/uploads/illust/16_2_925.png"  # 雪
    else:
        return "unknown.png"  # 不明な場合

# SQLiteデータベースのセットアップとテーブル作成
def setup_database():
    conn = sqlite3.connect(db_path + db_name)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS weather_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location TEXT NOT NULL,
        datetime TEXT NOT NULL,
        weather TEXT
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

# 天気データを保存する関数
def save_weather_to_db(location, datetime, weather):
    try:
        conn = sqlite3.connect(db_path + db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO weather_reports (location, datetime, weather)
        VALUES (?, ?, ?)
        ''', (location, datetime, weather))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving to database: {e}")

# 日付フォーマットを変換する関数
def format_date(date_str):
    try:
        date = datetime.fromisoformat(date_str)
        return date.strftime("%Y-%m-%d")
    except Exception as e:
        print(f"Error formatting date: {e}")
        return date_str

# 特定のエリアの天気情報を表示
def show_area_weather(location, area_data):
    try:
        if area_data:
            weathers = area_data.get("weathers", [])
            weatherCodes = area_data.get("weatherCodes", [])  # weatherCodesを取得
            timeDefines = area_data.get("timeDefines", [])

            if weathers and timeDefines and weatherCodes:
                rows = []
                for i, (date, weather, weather_code) in enumerate(zip(timeDefines[:3], weathers[:3], weatherCodes[:3])):
                    formatted_date = format_date(date)
                    weather = weather.replace('　', '')  # 全角スペースを削除する
                    weather_icon = get_weather_icon(weather_code)  # 天気アイコンの取得
                    weather_messages = f"{formatted_date} の天気: {weather}"
                    # 天気データをデータベースに保存
                    save_weather_to_db(location, formatted_date, weather)
                    
                    # 一日の天気情報を表示するコンテナ
                    weather_container = Container(
                        content=Column([
                            Text(formatted_date, size=16),
                            Image(src=weather_icon, width=48, height=48),
                            Text(weather, size=14)
                        ]),
                        width=150,
                        padding=10
                    )
                    
                    rows.append(weather_container)
                
                weather_text.controls = rows
            else:
                weather_text.controls = [Text("天気情報が取得できませんでした。")]
        else:
            weather_text.controls = [Text("天気情報が取得できませんでした。")]
    except Exception as e:
        weather_text.controls = [Text(f"Error displaying weather: {e}")]
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
                    location = area_full_name  # 位置情報を設定
                    area_button = ElevatedButton(
                        text=area_full_name, 
                        on_click=lambda e, area=area, location=location: show_area_weather(location, area),
                        width=400
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
        return weather_data
    except requests.exceptions.HTTPError as ex:
        print(f"HTTPエラーが発生しました: {ex}")
        return None

# メイン関数
def main(pg):
    global area_buttons, weather_text, regions, page, area_names
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
    area_buttons = Column(scroll=ScrollMode.ALWAYS)
    weather_text = Column(scroll=ScrollMode.ALWAYS)

    # スクロール可能なListViewにラップ
    scrollable_area = ListView(
        height=400,
        controls=[area_buttons],
        expand=True
    )

    scrollable_weather = ListView(
        height=400,
        controls=[weather_text],
        expand=True
    )

    # UIのレイアウト
    page.add(
        Column(
            [
                Container(
                    content=Text("天気予報アプリケーション", size=30, weight="bold"),
                    alignment=ft.alignment.center
                ),
                Row(
                    [Text("地域を選択してください:", size=20)],
                    alignment=MainAxisAlignment.CENTER
                ),
                Row(
                    [dropdown_list],
                    alignment=MainAxisAlignment.CENTER
                ),
                Row(
                    [
                        Column(
                            [
                                Text("地域ごとの天気情報:", size=20),
                                scrollable_area,
                            ],
                            width=400
                        ),
                        Container(width=20),  # 適切なスペースを確保するための空のコンテナ
                        Column(
                            [
                                Text("天気予報:", size=20),
                                scrollable_weather,
                            ],
                            width=400,
                            height=400
                        ),
                    ],
                    alignment=MainAxisAlignment.CENTER
                ),
            ],
            expand=True,
            alignment=MainAxisAlignment.START
        )
    )

    page.update()

    global loop
    if not loop.is_running():
        loop.run_forever()

# アプリケーションの起動
ft.app(target=main)