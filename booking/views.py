from django.shortcuts import render

def create(request):
    if request.method == 'POST':
        data = request.POST
        
        start_date  = data.get('start_date')
        end_date    = data.get('end_date')
        price       = data.get('price')

        