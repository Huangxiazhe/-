import os
import requests
from pyquery import PyQuery as pq

"""
存图
"""


class Model():
    """
    基类, 用来显示类的信息
    """

    def __repr__(self):
        name = self.__class__.__name__
        properties = ('{}=({})'.format(k, v) for k, v in self.__dict__.items())
        s = '\n<{} \n  {}>'.format(name, '\n  '.join(properties))
        return s


class Movie(Model):
    """
    存储电影信息
    """

    def __init__(self):
        self.name = ''
        self.score = 0
        self.quote = ''
        self.cover_url = ''
        self.ranking = 0


def get(url, filename):
    """
    缓存, 避免重复下载网页浪费时间
    """
    folder = 'cached_mtime'
    # 建立 cached 文件夹
    if not os.path.exists(folder):
        os.makedirs(folder)

    path = os.path.join(folder, filename)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            s = f.read()
            return s
    else:
        # 发送网络请求, 把结果写入到文件夹中
        r = requests.get(url)
        with open(path, 'wb') as f:
            f.write(r.content)
            return r.content


def movie_from_div(div):
    """
    从一个 div 里面获取到一个电影信息
    """
    e = pq(div)
    # 小作用域变量用单字符
    m = Movie()

    name = e('.px14')
    pq_name = pq(name)
    if pq_name('.c_blue'):
        m.name = pq_name('.c_blue').text()
    else:
        m.name = pq_name('.c_fff').text()

    s1 = e('.total').text()
    s2 = e('.total2').text()
    m.score = s1 + s2

    m.quote = e('.mt3').text()
    m.cover_url = e('img').attr('src')
    m.ranking = e('.number em').text()
    return m


def save_cover(movies):
    for m in movies:
        filename = '{}.jpg'.format(m.ranking)
        get(m.cover_url, filename)


def movies_from_url(url):
    """
    从 url 中下载网页并解析出页面内所有的电影
    http://www.mtime.com/top/movie/top100/index-10.html
    """
    filename = '{}'.format(url.split('-', 1)[-1])

    # 首页 url 与其他页格式不同，这里需要将首页 url 改为正确格式
    if filename == '1.html':
        url = 'http://www.mtime.com/top/movie/top100/'

    print('url', url)
    page = get(url, filename)
    e = pq(page)
    top_list = e('.top_list')
    top_list = pq(top_list)
    items = top_list('li')
    # 调用 movie_from_div
    movies = [movie_from_div(i) for i in items]
    save_cover(movies)
    return movies


def main():
    for i in range(1,11):
        url = 'http://www.mtime.com/top/movie/top100/index-{}.html'.format(i)
        movies = movies_from_url(url)
        print('mtime top100 movies', movies)


if __name__ == '__main__':
    main()

"""
1.描述爬虫的工作流程:
  拿到 url
  下载 url 对应的资源， 一般是 html 
  提取资源中有用的部分（洗数据）
  分析

2.描述写爬虫的流程:
  分析爬取页面的页面结构，确定爬取那一部分
  通过 requests.get 方法对指定 url 发送网络请求, 将得到的资源进行缓存
  通过选择器拿取资源中的目标对象，将其构造成 model 类，存储信息
"""