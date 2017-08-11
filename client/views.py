from django.conf.global_settings import MEDIA_ROOT
from django.http import HttpResponse
from django.shortcuts import render
from client.excelData import excelData
from client.SecUtil import EnsafeDes,EnsafeRsa
import logging
import requests
import redis
import os

# Create your views here.
logger = logging.getLogger('django')
dir = os.path.join(MEDIA_ROOT, 'files')
truedir = os.path.abspath(dir)
pool = redis.ConnectionPool(host="localhost", port=6379)
red = redis.Redis(connection_pool=pool)
sca = 'http://'


def index(request):
    logger.info("navigate to index page")
    return render(request, 'index.html')


def get(request):
    logger.info("navigate to get page")
    return render(request, 'get.html')


def post(request):
    logger.info("navigate to post page")
    return render(request, 'post.html')


def excel(request):
    logger.info("navigate to excel page")
    return render(request, 'excel.html')


def upload(request):
    if request.method == "POST":
        logger.info("find files to upload")
        file = request.FILES.get("file", '')
        if not file:
            logger.error("file not find")
            return HttpResponse("No file found")
        logger.info("upload file")
        destination = open(os.path.join(truedir, file.name), 'wb+')
        for i in file.chunks():
            destination.write(i)
        destination.close()
        logger.info("Uploading is over")
        return HttpResponse("upload over!")


def get_re(request):
    logger.info("get get-request parameters")
    url = request.POST.get('url', '')
    keys = request.POST.getlist('key', [])
    values = request.POST.getlist('value', [])
    logger.info("build dict")
    param = dict(zip(keys, values))
    logger.info("perform request")
    re = requests.get(url=sca + url, params=param)
    logger.info("exchange request response")
    result = re.json()
    for a, b in result.items():
        red.set(a, b)
    logger.info("show response content")
    return render(request, 'get.html', {'message': u"{0}".format(re.text)})


def post_re(request):
    logger.info("get post-request data")
    url = request.POST.get('url', '')
    keys = request.POST.getlist('key', [])
    values = request.POST.getlist('value', [])
    logger.info("build dict")
    data = dict(zip(keys, values))
    logger.info("get encrypt method")
    sec1 = request.POST.get('dessec','')
    sec2 = request.POST.get('rsasec','')
    logger.info("message encrypt")
    if sec1 == "des":
        des = EnsafeDes()
        data = des.ensec(data)
    elif sec2 =="rsa":
        rsa = EnsafeRsa
        data = rsa.ensec(data)
    logger.info("send request")
    re = requests.post(url=sca + url, data=data)
    logger.info("exchange response")
    result = re.json()
    for a, b in result.items():
        red.set(a, b)
    logger.info("show response content")
    return render(request, 'post.html', {'message': u"{0}".format(re.text)})


def excel_request(request):
    logger.info("read request content from excel")
    l = os.listdir(truedir)
    li = [a for a in l if a.endswith("xlsx")]
    result = []
    count = 1
    fai = 0
    for k in li:
        book = excelData(k)
        row_num = book.sheet.max_row
        for i in range(2, row_num + 1):
            method = book.get_method(i)
            if method == 'post':
                url = book.get_url(i)
                payload = book.get_json(i)
                res = requests.post(url, data=payload)
                t = res.json()
            elif method == 'get':
                url = book.get_url(i)
                param = book.get_json(i)
                res = requests.get(url, params=param)
                t = res.json()
            if t['status'] == 200:
                book.set_result(i, "ok")
                book.set_return(i, u"{0}".format(res.text))
                ms = u"测试" + str(count) + u"通过"
                count += 1
                result.append(ms)
            else:
                book.set_result(i, "ng")
                book.set_return(i, u"{0}".format(res.text))
                fai += 1
                ms = u"测试" + str(count) + u"失败"
                count += 1
                result.append(ms)
    message = ";".join(result)
    logger.info("show response content")
    return render(request, 'excel.html', {'message': u"{0}".format(message)})
