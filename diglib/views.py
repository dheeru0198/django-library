#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from diglib.models import Books, Author, Publisher, Transaction, \
    BookRequestForm, BookRequest

import datetime

model_dict = {'book': Books, 'author': Author, 'publisher': Publisher}


def detail(request, var_name=None, var_id=None):

# displays the details of the book/author/publisher

    model = model_dict.get(var_name, '')
    obj = get_object_or_404(model, pk=var_id)
    tr = None

    if var_name == 'book':
        try:
            tr = \
                Transaction.objects.filter(book__id=var_id).order_by(
                '-date_issued')[0]
        except IndexError, e:
            pass
    return render(request, 'detail.html', {'detail': var_name,
                  var_name: obj, 'trans': tr})


def about(request):

# The about page

    return render(request, 'about.html', {})


@login_required
def edit_request(request, req_id):

# Edit a request you/team made

    req_data = BookRequest.objects.get(id=req_id)
    form = BookRequestForm(data=request.POST or None, instance=req_data)
    if form.is_valid():
        form.save()
        return redirect('/request/detail/')
    return render(request, 'request.html', {'form': form})


@login_required
def book_request(request, var):

# make a book request

    if var == 'detail':
        bookreqs = BookRequest.objects.all().order_by('-date_requested')
        return render(request, 'request.html', {'reqs': bookreqs})

    if var == 'create':
        form = BookRequestForm(data=request.POST or None)
        if form.is_valid():
            form.save()
            return redirect('/request/detail/')
        return render(request, 'request.html', {'form': form})


def aclogout(request):
    logout(request)
    return redirect('/')


@login_required
@csrf_exempt
def funct(request, book_id, var):

# handles issue, return, upvote and downvote

    book = Books.objects.get(id=book_id)
    if var == 'issue' and book.status == False:
        return HttpResponse('0')
    elif var == 'return' and book.status == True:
        return HttpResponse('0')
    else:
        if var == 'upvote':
            book.number_of_upvotes += 1
        if var == 'downvote':
            book.number_of_downvotes += 1

        usr = request.user

        if var == 'issue':
            tr = Transaction.objects.create(usr=usr, book=book,
                    date_issued=datetime.date.today())
            book.status = False
            tr.save()
        if var == 'return':
            tr = Transaction.objects.filter(usr=usr,
                    book=book).order_by('-date_issued')[0]
            tr.date_returned = datetime.date.today()
            book.read_by.add(usr)
            book.status = True
            tr.save()
        book.save()
        return HttpResponse(var)


@csrf_exempt
def aclogin(request):
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/')
            else:
                return HttpResponse('disabled account')
        else:
            return HttpResponse('invalid login')
    else:
        return render(request, 'login.html', {})


def filter(request, var_name=None, var_id=None):

# filters book by the author or publisher

    if var_name == 'author':
        obj = Books.objects.filter(author__id=var_id)
    else:
        obj = Books.objects.filter(publisher__id=var_id)
    return render(request, 'filter.html', {'books': obj})


def libdetails(request):

# displays the library transaction details

    tr = Transaction.objects.all().order_by('-date_issued')[:20]
    return render(request, 'trans.html', {'trans': tr})


def index(request):

# displays the list of available books

    books = Books.objects.all()
    return render(request, 'index.html', {'books': books})
