import math
import re

import requests
import os
from bs4 import BeautifulSoup
from tqdm import tqdm
from requests.exceptions import RequestException

"""
e-hen 抓取学习
"""
# 定义请求的头部信息
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Upgrade-Insecure-Requests': '1'}

# 创建一个会话，这样我们就可以在多个请求间复用同一个TCP连接
session = requests.Session()
session.headers.update(headers)


def save_file(url, path):
    """
    下载并保存文件
    :param url:
    :param path:
    :return:
    """
    try:
        response = session.get(url)
        with open(path, 'wb') as f:
            f.write(response.content)
            f.flush()
        return True
    except RequestException as e:
        print(f"Error downloading {url}: {e}")
        return False


def get_website(url, title, output_dir):
    """
    获取网页，并保存所有图片
    :param url:
    :param title:
    :param output_dir:
    :return:
    """
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    divs = soup.find_all(class_='gdtm')
    successful_downloads = 0
    for i, div in enumerate(tqdm(divs, desc=f"Downloading {title}", unit="page")):
        pic_url = div.a.get('href')
        pic_src = get_pic_url(pic_url)
        page_num = div.img.get("alt")
        output_path = os.path.join(output_dir, f"{title}_{page_num}.jpg")
        if save_file(pic_src, output_path):
            successful_downloads += 1
    print(f'Finished downloading {len(divs)} files, {successful_downloads} of them are successful')


def get_pic_url(url):
    """
    从网页中解析出图片的URL
    :param url:
    :return:
    """
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    img = soup.find(id="img")
    return img['src']


def sanitize_filename(filename: str) -> str:
    """
    对输入的文件名进行清洗，将不符合Windows文件命名规则的字符替换为下划线。

    参数:
        filename (str): 需要清洗的原始文件名字符串。

    返回:
        str: 清洗后的文件名字符串。

    """

    # Windows系统不允许在文件名中使用的字符
    illegal_chars = '<>:"/\\|?*'
    for char in illegal_chars:
        filename = filename.replace(char, '_')

    # 去除文件名前后的空格
    filename = filename.strip()

    # 如果文件名以点结尾，则用下划线替换
    if filename.endswith('.'):
        filename = filename[:-1] + '_'

    return filename


# 菜单函数，负责处理用户输入的URL，然后开始下载
def start(url, root_dir):
    """
    开始
    :param url: ehentai漫画详情页面
    :param root_dir: 本地保存目录地址
    :return:
    """
    if not url.startswith('https://e-hentai.org/g/'):
        print('Oh,it is not an e-hentai comic url,please enter again\n')
        return

    print('--OK,getting information--')
    try:
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = sanitize_filename(str(soup.h1.get_text()))
        divs = soup.find_all(class_='gdtm')
        pages_tags = soup.find_all('td', string=re.compile('pages', re.IGNORECASE))
        pages = pages_tags[0].text.split(" ")[0].strip()
        print(f'The comic name is {title}, it has {pages} pages, start downloading!!!')
        output_dir = os.path.join(root_dir, title)  # 用用户提供的根目录和标题合并，得到输出目录
        os.makedirs(output_dir, exist_ok=True)
        # todo 保存封面
        output_dir = output_dir+f'/_Chapter/'
        os.makedirs(output_dir, exist_ok=True)
        # 网页每页40张图片 计算网页数量
        pages = int(pages)
        web_num = math.ceil(pages / 40)
        print(f"The comic has {web_num} web_pages")
        if web_num > 1:
            for i in range(web_num):
                # download
                print(f"Download web_page {i + 1} ")
                get_website(url, title, output_dir)
                if i >= 1:
                    # 拼接下一页地址
                    url_next = url + f'?p={i}'
                    get_website(url_next, title, output_dir)
        else:
            get_website(url, title, output_dir)
    except Exception as e:
        print(f'Error downloading comic: {e}')


root_dir = "F:/comics/"
# 用户输入的URL
url = ""
start(url, root_dir)  # 调用menu函数开始处理用户输入的URL
