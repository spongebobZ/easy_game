from bs4 import BeautifulSoup
import urllib.parse
import requests
import json

search_addr = 'https://hanyu.baidu.com/s'


class Cy(object):
    def __init__(self, word, times):
        self.word = word
        self.times = times


# 从本地文件反序列化成语表函数
def read_local_cy():
    with open('src/cy', 'rb') as fr:
        content = fr.read()
        if len(content) > 0:
            return json.loads(content)
        else:
            return {}


# 从本地文件反序列化成语表至内存，dict类型
print('本地成语表加载中...')
local_cy = read_local_cy()
print('本地成语表加载完成')


# 把内存的成语表序列化至本地文件函数，先读取合并本地与内存的差异，再把合并后的结果序列化
def write_local_cy(d):
    with open('src/cy', 'w', encoding='utf-8') as fw:
        latest_cy = read_local_cy()
        for k, v in d.items():
            if k in latest_cy:
                local_words = list(map(lambda x: x[0], latest_cy[k]))
                for i in v:
                    if i[0] in local_words:
                        continue
                    else:
                        latest_cy[k].append((i[0], 0), )
            else:
                latest_cy[k] = list(map(lambda x: (x[0], 0), v))
        s = json.dumps(latest_cy)
        fw.write(s)


# 查找指定文字开头的成语
def search_cy(first_word):
    # 先查找本地库是否有匹配的成语，有则取返回次数最小的
    if first_word in local_cy:
        min_times = 10000000
        result_word = ''
        aim_key = local_cy[first_word]
        for i in aim_key:
            result_word = (result_word, i[0])[min_times > i[1]]
            min_times = (min_times, i[1])[min_times > i[1]]
        return result_word

    # 本地没有匹配则在网络查找成语，返回网络结果第一个，并把网络结果存入本地库
    value = {'wd': first_word + ' 成语'}
    keyword_urlencoded = urllib.parse.urlencode(value)
    urlparams = [('from', 'poem')]
    web_content = requests.get(search_addr + '?' + keyword_urlencoded, params=urlparams).content
    result = find_cy(first_word, web_content)
    if len(result)>0:
        local_cy[first_word] = list((i, 0) for i in result)
        local_cy[first_word][0] = (local_cy[first_word][0][0], 1)
        write_local_cy(local_cy)
        return local_cy[first_word][0][0]
    else:
        return ''


# 网络查找成语函数
def find_cy(first_word, web_content):
    soup = BeautifulSoup(web_content, 'html.parser')
    poem_list = soup.find_all('div', attrs={'class': 'poem-list-item'})
    result = []
    for poem in poem_list:
        r = str(poem.a.string).strip()
        if r[:1] == first_word: result.append(r)
    return result


# 检查对象是否为成语函数，0表示是成语，-1表示非成语，-2表示格式非法
def check_cy(word):
    if len(word) != 4:
        return -2
    # first_in_local标记第一个汉字是否存在于成语表中
    global first_in_local
    first_in_local = 0
    first_word = word[0]
    if first_word in local_cy:
        local_words = list(map(lambda x: x[0], local_cy[first_word]))
        if word in local_words:
            return 0
        else:
            first_in_local = 1

    value = {'wd': word + ' 成语'}
    keyword_urlencoded = urllib.parse.urlencode(value)
    urlparams = [('from', 'poem')]
    web_content = requests.get(search_addr + '?' + keyword_urlencoded, params=urlparams).content
    r = BeautifulSoup(web_content, 'html.parser')
    # 通过页面元素判断是否为成语，是则保存至成语表，并返回0
    if r.find('div', attrs={'id': 'term-header'}):
        if first_in_local == 0:
            local_cy[word[0]] = [(word, 1)]
            write_local_cy(local_cy)
        else:
            local_cy[word[0]].append((word, 1), )
            write_local_cy(local_cy)
        return 0
    else:
        return -1