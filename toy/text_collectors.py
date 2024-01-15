import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

curl_command_template = """
curl 'https://news.housefun.com.tw/news/article/114325404711.html' \
  -H 'authority: news.housefun.com.tw' \
  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
  -H 'accept-language: zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'cache-control: no-cache' \
  -H 'cookie: ASP.NET_SessionId=jvpjiofkzfukzqt0sgpox4l0; yawbewkcehc=0; _gcl_au=1.1.1684013684.1702122110; __ltm_https_flag=true; _ga=GA1.4.1528627278.1702122110; _userid=69afe672-a81a-491f-afc7-06f03efb3adf; __lt__cid=5ee40a4b-ae14-4b17-945d-919fca4836e1; one_fp=%2522b04a6b30714dd72aae5ee9bfd9a00c3f%2522; oid=%257B%2522oid%2522%253A%2522f66a6492-04d5-11ee-a4b8-0242ac130002%2522%252C%2522ts%2522%253A-62135596800%252C%2522v%2522%253A%252220201117%2522%257D; FCNEC=%5B%5B%22AKsRol9m3NzA98bGWmu2avm4GgVC4dHnzJ4xogxa9S1gMeN10lLAs0NvtLFkNwJcaBb03lYAhCE_UWMXbTWaLO7aap3Iz9CfE2j0g9hYI2lmb2WA1Z2aoExXnKZXpyhqAPNr0RI7vsBu07rkbn2guUz8SLG6UXjSGQ%3D%3D%22%5D%5D; SEID_G=00aa9e8c-d241-4b46-8e8b-0aa26fd9680a; TRID_G=2fc216df-7d0e-4e6d-b8d5-7f82e8223d31; search_buy_searchMode="1"; search_buy_regArea="-"; search_buy_room="-"; search_buy_buildAge="-"; search_buy_unitPrice="-"; search_buy_caseFloor="-"; search_buy_tag=""; search_buy_district={"county":"%E6%96%B0%E5%8C%97%E5%B8%82","district":"%E6%96%B0%E8%8E%8A%E5%8D%80%2C%E8%98%86%E6%B4%B2%E5%8D%80%2C%E4%B8%89%E9%87%8D%E5%8D%80"}; search_buy_caseType="%E9%9B%BB%E6%A2%AF%E5%A4%A7%E6%A8%93"; search_buy_purpose="%E4%BD%8F%E5%AE%85"; search_buy_parkingType="%E6%9C%89%E8%BB%8A%E4%BD%8D"; search_buy_price="1200-1600"; _ga_4GCENMEV2L=GS1.1.1704346430.2.1.1704346431.59.0.0; __ltmwga=utmcsr=google|utmccn=2023CPC|utmcmd=cpc|utmcct=008; _gid=GA1.3.1409024408.1705289274; verecord=1; ez2o_UNID=1705289277112112; _gid=GA1.4.1409024408.1705289274; RRD=UhkC8*jJOekLWNvlnRKTVW7wCJiv1LBGeCum422I4xBiuZ0HrcDICT8raBbVQ9Zf; _gcl_aw=GCL.1705298462.CjwKCAiAqY6tBhAtEiwAHeRopVrzn-AF47HBg6Cuqjo8xIngmvl6ZaUY2fjBgKhHkvRl-_zB4Y21dBoCpkgQAvD_BwE; _gac_UA-34471860-1=1.1705298462.CjwKCAiAqY6tBhAtEiwAHeRopVrzn-AF47HBg6Cuqjo8xIngmvl6ZaUY2fjBgKhHkvRl-_zB4Y21dBoCpkgQAvD_BwE; _gac_UA-22823074-10=1.1705298465.CjwKCAiAqY6tBhAtEiwAHeRopVrzn-AF47HBg6Cuqjo8xIngmvl6ZaUY2fjBgKhHkvRl-_zB4Y21dBoCpkgQAvD_BwE; _ga=GA1.1.1528627278.1702122110; _gac_UA-34471860-1=1.1705298462.CjwKCAiAqY6tBhAtEiwAHeRopVrzn-AF47HBg6Cuqjo8xIngmvl6ZaUY2fjBgKhHkvRl-_zB4Y21dBoCpkgQAvD_BwE; __lt__sid=f74d8e3e-9a700972; _pk_ref.22.df11=%5B%22%22%2C%22%22%2C1705298468%2C%22https%3A%2F%2Fwww.housefun.com.tw%2F%22%5D; _pk_ses.22.df11=*; _ga_PD28GNZW3Z=GS1.1.1705298461.8.1.1705298520.0.0.0; _ga_8FX3CC1EZY=GS1.1.1705298465.6.1.1705298520.5.0.0; _pk_id.22.df11=5765d767b3b0461e.1702122110.6.1705298523.1705298466.' \
  -H 'pragma: no-cache' \
  -H 'referer: https://news.housefun.com.tw/topic/751873120' \
  -H 'sec-ch-ua: "Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: document' \
  -H 'sec-fetch-mode: navigate' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sec-fetch-user: ?1' \
  -H 'upgrade-insecure-requests: 1' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36' \
  --compressed
"""


def housefun_request(url):
    global curl_command_template
    headers = {}
    matches = re.findall(r"-H '([^']+)'", curl_command_template)
    for m in matches:
        header = re.findall(r"^([^:]+): (.+)", m)
        if header:
            header = header[0]
            k, v = header
            headers[k] = v

    response = requests.get(url, headers=headers)
    return response


def url_to_filename(url):
    parsed_url = urlparse(url)
    domain_parts = parsed_url.netloc.split(".")
    longest_domain_part = max(domain_parts, key=len)
    filename = parsed_url.path.split("/")[-1]
    return f"{longest_domain_part}_{filename}"


def download(url: str):
    response = housefun_request(url)
    soup = BeautifulSoup(response.content, "lxml")
    content = soup.select_one("#content")
    compact_content = "\n".join(
        [x.strip() for x in content.text.splitlines() if x.strip()]
    )
    return compact_content


def download_urls():
    with open("urls.txt", "r") as f:
        for url in f:
            u = url.strip()
            filename = url_to_filename(u)
            with open(filename, "w") as out:
                out.write(download(u))


if __name__ == "__main__":
    url = "https://news.housefun.com.tw/news/article/114325404711.html"
    # download(url)

    # print(url_to_filename(url))
    download_urls()
