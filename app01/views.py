"""
视图部分
login函数是登录视图；
view函数是登录成功后的视图 ；
book函数是Ajax返回的页面；
"""

from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import HttpResponse
from django.contrib import auth
from .models import *
import datetime
import json
from django.db.models import Q


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        pwd = request.POST.get("password")
        user = auth.authenticate(username=username, password=pwd)
        if user:
            auth.login(request, user)  # request.user
            request.session['user'] = username
            return redirect("/index/")    # 登陆成功返回index页面
    return render(request, "login.html")


def index(request):
    # 验证是否登录，没有登录不能访问此页面
    if not request.session['user']:
        return redirect('/login/')
    # 获取当前日期
    date = datetime.datetime.now().date()
    # 获取前端选择的日期
    book_date = request.GET.get("book_date", date)
    time_choices = Book.time_choices
    room_list = Room.objects.all()
    # 在选择日期内的预定情况
    book_list = Book.objects.filter(date=book_date)
    # 自定义html
    htmls = ""
    for room in room_list:
        htmls += "<tr><td>{}({})</td>".format(room.caption, room.num)
        for time_choice in time_choices:
            book = None
            flag = False
            for book in book_list:
                if book.room.pk == room.pk and book.time_id == time_choice[0]:
                    # 意味这个单元格已被预定
                    flag = True
                    break
            if flag:
                if request.user.pk == book.user.pk:
                    # 预定该房间
                     htmls += "<td class='active item'  room_id={} time_id={}>{}</td>".format(room.pk, time_choice[0], book.user.username)
                else:
                    # 取消预定
                     htmls += "<td class='another_active item'  room_id={} time_id={}>{}</td>".format(room.pk, time_choice[0], book.user.username)
            else:
                # 还没人预定该房间
                 htmls += "<td room_id={} time_id={} class='item'></td>".format(room.pk, time_choice[0])
        htmls += "</tr>"
    return render(request, "index.html", locals())


def book(request):
    post_data = json.loads(request.POST.get("post_data"))   # {"ADD":{"1":["5"],"2":["5","6"]},"DEL":{"3":["9","10"]}}
    choose_date = request.POST.get("choose_date")
    res = {"state": True, "msg": None}
    try:
        # 添加预定
        book_list = []
        for room_id, time_id_list in post_data["ADD"].items():
            for time_id in time_id_list:
                book_obj = Book(user=request.user, room_id=room_id, time_id=time_id, date=choose_date)
                book_list.append(book_obj)
        Book.objects.bulk_create(book_list)
        # 删除预定
        remove_book = Q()
        for room_id, time_id_list in post_data["DEL"].items():
            temp = Q()
            for time_id in time_id_list:
                temp.children.append(("room_id", room_id))
                temp.children.append(("time_id", time_id))
                temp.children.append(("user_id", request.user.pk))
                temp.children.append(("date", choose_date))
                remove_book.add(temp, "OR")
        if remove_book:
             Book.objects.filter(remove_book).delete()
    except Exception as e:
        res["state"] = False
        res["msg"] = str(e)
    return HttpResponse(json.dumps(res))
