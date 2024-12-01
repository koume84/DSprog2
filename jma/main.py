import asyncio
import requests
import flet as ft
from flet import Dropdown, dropdown, ElevatedButton, Column

# グローバルイベントループの設定
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

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

# 地域ごとの天気情報をロードする非同期関数
async def load_forecast(region_code):
    try:
        weather_data = await get_weather_forecast(region_code)
        print(f"地域コード {region_code} の天気情報: {weather_data[0]['timeSeries'][0]['areas']}")
        return weather_data
    except requests.exceptions.HTTPError as ex:
        print(f"HTTPエラーが発生しました: {ex}")
        return None

# 特定のエリアの天気情報を表示
def show_area_weather(e, area_data):
    if area_data:
        weathers = area_data.get("weathers", [])
        weather_text.value = "\n\n".join(weathers) if weathers else "天気情報が取得できませんでした。"
    else:
        weather_text.value = "天気情報が取得できませんでした。"
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
                    area_button = ElevatedButton(text=area_full_name, on_click=lambda e, area=area: show_area_weather(e, area))
                    area_buttons.controls.append(area_button)

    page.update()

# 地域選択後の同期ラッパー関数
def on_dropdown_change(e):
    selected_region_name = e.control.value
    asyncio.run_coroutine_threadsafe(on_dropdown_change_async(selected_region_name), loop)

# メイン関数
def main(pg):
    global area_buttons, weather_text, regions, page, area_names
    page = pg
    page.title = "天気予報アプリケーション - 地域ごとの天気"

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
    weather_text = ft.Text(value="天気予報がここに表示されます", expand=True)

    page.add(dropdown_list)
    page.add(area_buttons)
    page.add(weather_text)
    page.update()

    global loop
    if not loop.is_running():
        loop.run_forever()

# アプリケーション実行
ft.app(target=main)