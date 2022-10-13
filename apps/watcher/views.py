from fileinput import filename
from django.http import HttpResponse
from django.shortcuts import redirect, render
from flask import render_template
from httplib2 import Http
from apps.watcher.main import main_function
from apps.watcher.readPdf import readPdf
from core.settings import BASE_DIR
from configparser import ConfigParser
import os
import logging

data_file = os.path.join(BASE_DIR, 'config.ini')
config = ConfigParser()
config.read(data_file)

logging.basicConfig(filename=config['PATHS']['logPath'], format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

# Create your views here.
def test(request):
    print('test radi')
    try:
        headers = request.headers
        print(headers)
        fileName = headers['Filename']
        fileId = headers['File-Id']
        upload_path = config['PATHS']['uploadFoderPath']
        file_path = os.path.join(upload_path, fileId)
        # print(f"{event.src_path} je kreiran!")
        logging.info(f"{file_path} je kreiran!")
        # file_path = event.src_path
        # dir_path = os.path.dirname(os.path.realpath(file_path))
        # file_extention = pathlib.Path(file_path).suffix
        # print(file_extention)
        pdf_data = readPdf(file_path)
        main_function(pdf_data, file_path)
        
    except Exception as e:
        print('Greska:' ,e)
        logging.error(e)
        pass
    return redirect(home)

def home(request):
    return render(request ,'watcher/home.html')

def callAction(request):
    print('action called')
    return redirect(home)