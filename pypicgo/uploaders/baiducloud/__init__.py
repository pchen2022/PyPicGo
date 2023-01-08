"""
 新增的uploader
 调用百度网盘api接口上传图片
"""
from pprint import pprint

import requests


def pre():
    url = "http://pan.baidu.com/rest/2.0/xpan/file?method=precreate&access_token=121.136033ab14f36ced10ecbbaf82377aa4.YCHpal4XM1yYn844RiVVS4cCwCGcGnm9-oFPPmO.-fkI-g"
    payload = {'path': '/app/wiki/wiki-486d05a6714031b2ee7e698843970967-pchen-20230108212441-2.jpg',
               'size': 1547,
               'rtype': 1,
               'isdir': 0,
               'autoinit': 1,
               'block_list': '["00ef24928bfd3d9188b47cfead918849"]'}
    response = requests.request("POST", url, data=payload)
    # response = requests.post(url, data=payload)
    pprint(response.json())
    print(response.status_code)
    """
    {'block_list': [0],
     'errno': 0,
     'path': '/apps/wiki/test.jpg',
     'request_id': 181432904890039227,
     'return_type': 1,
     'uploadid': 'N1-MTEyLjEuMzQuMTAzOjE2NzMxNzgyOTA6MTgxNDMyOTA0ODkwMDM5MjI3'}
    """


def upload():
    url = "https://d.pcs.baidu.com/rest/2.0/pcs/superfile2?method=upload&access_token=121.136033ab14f36ced10ecbbaf82377aa4.YCHpal4XM1yYn844RiVVS4cCwCGcGnm9-oFPPmO.-fkI-g&path=/apps/wiki/test.jpg&type=tmpfile&uploadid=N1-MTEyLjEuMzQuMTAzOjE2NzMxNzgyOTA6MTgxNDMyOTA0ODkwMDM5MjI3&partseq=0"
    files = [
        ('file', open('/home/cp/Pictures/2.jpg', 'rb'))
    ]
    response = requests.request("POST", url, files=files)
    pprint(response.json())
    print(response.status_code)
    """
    {'md5': '486d05a6714031b2ee7e698843970967', 'request_id': 181448555206778182}
    """


def create():
    url = "https://pan.baidu.com/rest/2.0/xpan/file?method=create&access_token=121.136033ab14f36ced10ecbbaf82377aa4.YCHpal4XM1yYn844RiVVS4cCwCGcGnm9-oFPPmO.-fkI-g"
    payload = {'path': '/apps/wiki/test.jpg',
               'size': 1547,
               'rtype': 1,
               'isdir': 0,
               'uploadid': 'N1-MTEyLjEuMzQuMTAzOjE2NzMxNzgyOTA6MTgxNDMyOTA0ODkwMDM5MjI3',
               'block_list': '["486d05a6714031b2ee7e698843970967"]'}
    response = requests.request("POST", url, data=payload)
    pprint(response.json())


pre()
# upload()
# create()
