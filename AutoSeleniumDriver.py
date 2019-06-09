# -*- conding:utf-8 -*-
__author__ = "snake"

import os
import re
import sys
import winreg


def _get_chrome_version():
    """
        获取chrome版本号
    """
    print("查找已安装的Chrome浏览器版本")

    # 打开Chrome注册表位置
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,"Software\Google\Chrome\BLBeacon")
    except FileNotFoundError as e:
        print("本机上未找到Chrome浏览器版本,退出.")
        exit(0)

    # 遍历注册表
    for i in range(0, 4):
        try:
            name, value, type1 = winreg.EnumValue(key, i)
        except OSError as e:
            print("本机上未找到Chrome浏览器版本,退出.")
            exit(0)

        if name.lower() == "version":
            print("找到Chrome浏览器，版本号为:{}".format(value))
            return value


def _get_new_chrome_driver_url(chrome_version):
    """
        获取chrome70以上的chrome driver下载链接
    """
    url = "https://npm.taobao.org/mirrors/chromedriver"

    res = requests.get(url+"/"+chrome_version)
    # 运气不好，进一步匹配小版本
    if res.status_code > 400:
        urls = []
        res = requests.get(url)

        # 倒数第二级小版本(还可以优化)
        chrome_version = ".".join(chrome_version.split(".")[0:-1])
        for u in BeautifulSoup(res.text, "lxml").find_all("a"):
            if chrome_version in u.text:
                urls.append(url.split("/mirrors/chromedriver")[0]+u["href"])

        return urls

    # 刚好碰巧遇到这个版本 666
    else:
        return url


def _get_old_chrome_driver_url(chrome_version):
    """
        获取chrome70以下的chrome driver下载链接
    """
    version_list = "http://npm.taobao.org/mirrors/chromedriver/2.46/notes.txt"
    res = requests.get(version_list)
    if res.status_code > 400:
        print("获取版本号列表失败!")
        return 0

    # 匹配ChromeDriver和ChromeBrowser版本号
    chrome_driver_lists = re.findall("----------ChromeDriver v(.*?) \(", res.text)
    chrome_browse_lists = re.findall("Supports Chrome v(.*?)\nResolved issue", res.text)

    """
        根据Chrome浏览器大版本匹配
    """
    for r in range(len(chrome_driver_lists)):
        minv, maxv = int(chrome_browse_lists[r].split("-")[0]), int(chrome_browse_lists[r].split("-")[1])
        if minv==chrome_version or maxv == chrome_version or (minv<chrome_version and maxv>chrome_version):
            return "http://npm.taobao.org/mirrors/chromedriver/"+chrome_driver_lists[r]+"/"

    return 0


def _get_max_driver_version(urls=[]):
    """
        获取最大的driver版本
    """
    # step1. 然后最最后一位大版本对比
    version = []
    for url in urls:
        # 返回最后一个版本，一定是兼容的
        if "LATEST_RELEASE" in url:
            continue
        
        # 否则就找匹配最后一个小版本
        temp = url.split("/mirrors/chromedriver/")[1].replace("/","")
        version.append(int(temp.split(".")[-1]))
    
    # step2:寻找最大版本
    last_max_version = str(max(version))
    for url in urls:
        if ".{}/".format(str(max(version))) in url:
            return url

    return 0


def _download_file(url):
    """
        下载文件
    """
    print("开始下载ChromeDriver")
    try:
        r = requests.get(url=url) 
        with open("./chromedriver_win32.zip", "wb") as file:
            file.write(r.content)
            print("下载成功,ChromeDriver保存在:{}".format(os.getcwd()+"\\chromedriver_win32.zip"))
    except:
        print("下载失败!")


def _init_libs():
    """
        安装所需要的库
    """
    print("开始初始化环境")
    
    libs = ["requests", "beautifulsoup4", "lxml"]
    for lib in libs:
        print("开始安装依赖库:{}".format(lib))
        os.system("pip3 install {}".format(lib))
        print("=="*10)

    print("初始化环境结束")


if __name__ == "__main__":
    # 判断系统版本
    if "win32" != sys.platform:
        print("当前只支持Windows版本哦~")
        exit(0)

    # 初始化环境
    print("****"*10)
    _init_libs()
    print("****"*10)

    # 导入依赖库
    print("导入各项依赖库")
    import requests
    from bs4 import BeautifulSoup

    # 获取chrome安装版本
    print("****"*10)
    chrome_version = _get_chrome_version()
    print("****"*10)

    """
        chrome版本大于69，则使用新方法
        chrome版本小于70，则使用老方法
    """
    big_version = int(chrome_version.split(".")[0])
    if big_version > 69:
        # 获取chromedriver的url
        urls = _get_new_chrome_driver_url(chrome_version)

        # 获取chromedriver最后版本的url
        if isinstance(urls, list):
            max_chromedriver_url = _get_max_driver_version(urls) 
        else:
            max_chromedriver_url = urls
    else:
        max_chromedriver_url = _get_old_chrome_driver_url(big_version)
    
    # 下载ChromeDriver
    if max_chromedriver_url == 0:
        print("未找到ChromeDriver!")
    else:
        max_chromedriver_url = max_chromedriver_url + "chromedriver_win32.zip"
        print("找到ChromeDriver地址:{}".format(max_chromedriver_url))
        print("****"*10)
        _download_file(max_chromedriver_url)

    print("****"*10)