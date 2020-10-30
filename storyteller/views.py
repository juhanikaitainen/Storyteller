from django.shortcuts import render

def home_view(request):
    return render(request, 'homepage.html', { 'name': request.GET.get('name') })