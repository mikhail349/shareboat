from django.shortcuts import render

import logging
logger = logging.getLogger(__name__)

def index(request):
    logger.error("test file console")
    return render(request, 'home.html')

def not_found(request):
    return render(request, 'not_found.html')
