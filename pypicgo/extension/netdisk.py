from pprint import pprint

import requests


class BaiduNetdiskUtil:

    def download(self):
        url = "http://pan.baidu.com/rest/2.0/xpan/multimedia"
        params = dict()
        params["method"] = "filemetas"
        params["access_token"] = "121.136033ab14f36ced10ecbbaf82377aa4.YCHpal4XM1yYn844RiVVS4cCwCGcGnm9-oFPPmO.-fkI-g"
        params["fsids"] = '[273103362807712]'
        params["dlink"] = 1
        params["extra"] = 1
        resp = requests.get(url, params=params, headers={'User-Agent': 'pan.baidu.com'})
        dlink = resp.json()['list'][0]["dlink"]
        pprint(dlink)

        dlink += "&access_token=121.136033ab14f36ced10ecbbaf82377aa4.YCHpal4XM1yYn844RiVVS4cCwCGcGnm9-oFPPmO.-fkI-g"
        with open("a.png", 'wb') as f:
            response = requests.get(dlink, headers={'User-Agent': 'pan.baidu.com'})
            f.write(response.content)
