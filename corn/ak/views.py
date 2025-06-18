from pyexpat.errors import messages

from django.shortcuts import render, redirect
from rest_framework.response import Response

from .models import Ak
from .forms import AkForms




def create_ak(request):
    if request.method == 'POST':
        form = AkForms(request.POST)
        if form.is_valid():
            form.save()
            return Response(status=200)
    else:
        form = AkForms()
        return Response(status=400)

    # return  render(request, "нужно добавить путь к нему ", {'form': form})
# Create your views here.
