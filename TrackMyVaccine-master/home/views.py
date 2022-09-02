from django.shortcuts import render
from django.http import HttpResponse
import json
# Create your views here.
def home(request):
    return render(request, 'home/home.html')

def session_fetcher(request):
    dictionary={}
    dictionary['parent'] = request.session.has_key('parent')
    dictionary['hospital'] = request.session.has_key('hospital')
    data = json.dumps(dictionary)
    return HttpResponse(data)