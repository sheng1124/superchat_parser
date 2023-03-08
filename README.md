# Youtuber 頻道爬蟲 Super Chat

## demo

[![sc parser](https://res.cloudinary.com/marcomontalbano/image/upload/v1678309578/video_to_markdown/images/youtube--6vBbLm3sNgU-c05b58ac6eb4c4700831b2b3070cd403.jpg)](https://youtu.be/6vBbLm3sNgU "sc parser")

## 安裝&環境要求
* 環境要求
    * Python 3.7 up
* 安裝
    * `pip install selenium`
    * 安裝 chromedriver
        * 要根據 chrome 版本安裝所需的 chromedriver
        * 載點: https://chromedriver.chromium.org/downloads
        * [教學](https://medium.com/@bob800530/selenium-1-%E9%96%8B%E5%95%9Fchrome%E7%80%8F%E8%A6%BD%E5%99%A8-21448980dff9)

## 使用教學
* 設定yt影片
    1. 打開並編輯 chat_parser.py
    2. 195 行 id = '你要得網址的'
        * ex: https://www.youtube.com/watch?v=6vBbLm3sNgU id = 6vBbLm3sNgU

* 啟動
    * 執行 chat_parser.py
