from django.shortcuts import render, redirect
from .api_utils import get_vehicle_data

def index(request):
    return render(request, 'index.html')

def login(request):
        if request.method == 'POST':
            return redirect('index')
        return render(request, 'login.html')

def data(request):
    pesel = "0111169100"
    rejestracja_auta = "AV831OF"
    vin_auta = "PX8E8WPSUSTE84HRR"

    vehicle_data = get_vehicle_data(pesel, rejestracja_auta, vin_auta)
    return render(request, 'data.html', {'vehicle_data': vehicle_data})