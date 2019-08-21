import requests
from lxml import etree
import json
from queue import Queue
import threading


class QiushibaikeSpider:
    """糗事百科文字热门页爬虫"""

    def __init__(self):
        """初始化地址和headers"""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"}
        self.url = "https://www.qiushibaike.com/text/page/{}/"
        self.url_queue = Queue()
        self.html_queue = Queue()
        self.content_queue = Queue()

    def get_url_list(self):
        """获取url地址"""
        # return [self.url.format(i) for i in range(1, 14)]
        for i in range(1, 14):
            self.url_queue.put(self.url.format(i))

    def parse_url(self):
        """发送请求获取响应"""
        while True:
            url = self.url_queue.get()
            res = requests.get(url, headers=self.headers)
            # return res.content.decode()
            self.html_queue.put(res.content.decode())
            self.url_queue.task_done()

    def get_content_list(self):
        """提取数据"""
        while True:
            html_str = self.html_queue.get()
            html = etree.HTML(html_str)
            div_list = html.xpath("//div[@id='content-left']/div")
            content_list = list()
            for div in div_list:
                item = dict()
                item['content'] = div.xpath("./a//span/text()")
                item['content'] = [i.replace("\n", "") for i in item['content']]
                item['img_src'] = div.xpath(".//div[@class='author clearfix']/a/img/@src") if len(
                    div.xpath("./div[@class='author clearfix']/a/img/@src")) > 0 else None
                item['author'] = div.xpath(".//img/@alt")[0] if len(div.xpath(".//img/@alt")) > 0 else None
                item['gender'] = div.xpath(".//div[contains(@class,'articleGender')]/@class")
                item['gender'] = item['gender'][0].split(" ")[-1].replace("Icon", "") if len(
                    div.xpath(".//div[contains(@class,'articleGender')]/@class")) > 0 else None
                item['age'] = div.xpath(".//div[contains(@class,'articleGender')]/text()")[0] if len(
                    div.xpath(".//div[contains(@class,'articleGender')]/text()")) > 0 else None
                item['good_con'] = div.xpath(".//div[@class='main-text']/text()")
                item['good_con'] = [i.replace("\n", "") for i in item['good_con']] if len(
                    div.xpath(".//div[@class='main-text']/text()")) > 0 else None
                content_list.append(item)
            self.content_queue.put(content_list)
            self.html_queue.task_done()

    def save_content(self):
        """保存数据"""
        while True:
            content_list = self.content_queue.get()
            with open("糗事百科.txt", "a", encoding="utf-8") as f:
                for content in content_list:
                    f.write(json.dumps(content, ensure_ascii=False, indent=4))
                    f.write("\n")
            self.content_queue.task_done()

    def run(self):
        thread_list = list()
        # 1.获取url地址
        t_url = threading.Thread(target=self.get_url_list)
        thread_list.append(t_url)
        # 2.发送请求 获取响应
        for i in range(3):  # 放置3个线程一起执行
            t_parse = threading.Thread(target=self.parse_url)
            thread_list.append(t_parse)
        # 3.提取数据
        for i in range(3):
            t_html = threading.Thread(target=self.get_content_list)
            thread_list.append(t_html)
        # 4.保存数据
        t_save = threading.Thread(target=self.save_content)
        thread_list.append(t_save)
        for t in thread_list:
            t.setDaemon(True)  # 把子线程设置为守护线程，主线程结束，子线程结束。
            t.start()

        for q in [self.html_queue, self.url_queue, self.content_queue]:
            q.join()
        print("主线程结束")


if __name__ == '__main__':
    a = QiushibaikeSpider()
    a.run()
