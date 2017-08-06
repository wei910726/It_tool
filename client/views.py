from django.conf.global_settings import MEDIA_ROOT
from django.http import HttpResponse
from django.shortcuts import render
from client.excelData import excelData
from client.SecUtil import EnsafeDes,EnsafeRsa
import requests
import redis
import os

# Create your views here.

dir = os.path.join(MEDIA_ROOT, 'files')
truedir = os.path.abspath(dir)
pool = redis.ConnectionPool(host="localhost", port=6379)
red = redis.Redis(connection_pool=pool)
sca = 'http://'


def index(request):
    return render(request, 'index.html')


def get(request):
    return render(request, 'get.html')


def post(request):
    return render(request, 'post.html')


def excel(request):
    return render(request, 'excel.html')


def upload(request):
    if request.method == "POST":
        file = request.FILES.get("file", '')
        if not file:
            return HttpResponse("No file found")
        destination = open(os.path.join(truedir, file.name), 'wb+')
        for i in file.chunks():
            destination.write(i)
        destination.close()
        return HttpResponse("upload over!")


def get_re(request):
    url = request.POST.get('url', '')
    keys = request.POST.getlist('key', [])
    values = request.POST.getlist('value', [])
    param = dict(zip(keys, values))
    re = requests.get(url=sca + url, params=param)
    result = re.json()
    for a, b in result.items():
        red.set(a, b)
    return render(request, 'get.html', {'message': u"{0}".format(re.text)})


def post_re(request):
    url = request.POST.get('url', '')
    keys = request.POST.getlist('key', [])
    values = request.POST.getlist('value', [])
    data = dict(zip(keys, values))
    sec1 = request.POST.get('dessec','')
    sec2 = request.POST.get('rsasec','')
    if sec1 == "des":
        des = EnsafeDes()
        data = des.ensec(data)
    elif sec2 =="rsa":
        rsa = EnsafeRsa
        data = rsa.ensec(data)
    re = requests.post(url=sca + url, data=data)
    result = re.json()
    for a, b in result.items():
        red.set(a, b)
    return render(request, 'post.html', {'message': u"{0}".format(re.text)})


def excel_request(request):
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
    return render(request, 'excel.html', {'message': u"{0}".format(message)})
