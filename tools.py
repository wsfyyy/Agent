import os

import requests
from bs4 import BeautifulSoup
from mcp_meta_tools import tool

@tool()
async def get_weather(area:str):
    """
    获取天气信息
    :param area: 地点的拼音，如：zhaoqing
    :return:
    """

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Referer': 'https://www.tianqi.com/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'Priority': 'u=0, i',
    }

    response = requests.get(f"https://www.tianqi.com/{area}", headers=headers)
    html = response.text

    soup = BeautifulSoup(html, 'html.parser')
    dl = soup.find('dl', class_='weather_info')

    #提取各字段
    city = dl.find('dd', class_='name').find('h1').get_text(strip=True)
    week = dl.find('dd', class_='week').get_text(strip=True)

    #温度
    now_temp = dl.find('p', class_='now').get_text(strip=True)

    #天气状况和温度范围
    weather_span = dl.find('dd', class_='weather').find('span')
    weather_condition = weather_span.find('b').get_text(strip=True)
    temp_range = weather_span.get_text(strip=True).replace(weather_condition, '').strip()

    #湿度、风向、紫外线
    shidu = dl.find('dd', class_='shidu')
    humidity = shidu.find_all('b')[0].get_text(strip=True)
    wind = shidu.find_all('b')[1].get_text(strip=True)
    uv = shidu.find_all('b')[2].get_text(strip=True)

    #空气质量
    kongqi = dl.find('dd', class_='kongqi')
    aqi = kongqi.find('h5').get_text(strip=True)
    pm = kongqi.find('h6').get_text(strip=True)

    #日出日落
    sun_info = kongqi.find('span').get_text(strip=True)


    return f"""{city},日期：{week},当前温度：{now_temp},天气：{weather_condition},温度范围：{temp_range},{humidity} | {wind} | {uv},{aqi} | {pm},{sun_info}"""



@tool()
async def save_file(path:str, text:str, file_name:str):
    """
    存储文件
    :param path: 路径
    :param text: 存储的内容
    :param file_name: 文件名字 如：文本.txt
    :return:
    """
    try:

        with open(os.path. join(path,file_name), 'w',encoding="utf-8")as f:
            f.write(text)
        return f"已经存储到{os.path. join(path,file_name)}"
    except Exception as e:
        return f"存储失败"



@tool()
async def get_subdir_list(path:str):
    """
    获取path路径下的目录和文件
    :param path: 路径
    :return:
    """
    return os.listdir(path)

@tool()
async def read_txt(file_path:str):
    """
    读txt文件
    :param file_path: txt文件的路径
    :return:
    """
    with open(file_path,'r',encoding="utf-8") as f:
        return f.read()









