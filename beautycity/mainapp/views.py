from django.shortcuts import render
from django.http import HttpResponse
from . models import Registration
from django.shortcuts import render


def index(request):
    date_from = Registration.get_datatime_from_date_dict('28.05 Вс', '12:30')
    return HttpResponse(f'<h1>Сервис BeautyCity</h1></br>{Registration.free_time()}</br></br></br>{date_from}')
