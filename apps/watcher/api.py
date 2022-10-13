from apps.watcher.espo_api_client import EspoAPI
from datetime import date
import base64
import pprint
from datetime import date, datetime
import json
import logging
from configparser import ConfigParser
import re
import os
from core.settings import BASE_DIR


data_file = os.path.join(BASE_DIR, 'config.ini')
config = ConfigParser()
config.read(data_file)

espo_api_host = config['espo_api']['espo_api_host']
espo_api_key = config['espo_api']['espo_api_key']

client = EspoAPI(espo_api_host, espo_api_key)

logging.basicConfig(filename=config['PATHS']['logPath'], format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

# Get accounts
def get_accounts():
    params = {
        "select": "",
        "where": [
            {
                "type": "like",
                "attribute": "id",
                "value": '%%',
            },
        ],
    }

    client.request('GET', 'Tenderi', params)

def get_tender(broj_postupka):
    params = {
        "select": "",
        "where": [
            {
                "type": "like",
                "attribute": "brojPostupka",
                "value": broj_postupka
            },
            {
                "type": "equals",
                "attribute": "deleted",
                "value": 0
            }
        ],
    }

    return client.request('GET', 'Tenderi', params)

def get_account(pdf_data):
    # provjeri postoji li Pravno lice u CRM
    logging.info('Checking if account already exists...')
    jib = pdf_data['uo']['jib']
    params = {
        "select": "name",
        "where": [
            {
                "type": "equals",
                "attribute": "sicCode",
                "value": f'{jib}'
            },
        ],
    }
    response = client.request('GET', 'Account', params)
    # pprint.pprint(response)
    return response

def get_document(attribute, value):
    params = {
        "select": "id",
        "where": [
            {
                "type": "equals",
                "attribute": attribute,
                "value": value,
            },
        ],
        }
    response = client.request('GET', 'Document', params)
    pprint.pprint(response)
    return response['list'][0]['id']

def post_account(acc_info):
    logging.info('Adding new account...')
    data = {
        'name': acc_info['name'],
        'sicCode': acc_info['jib']
    }
    response = client.request('POST', 'Account', data)
    posted_account_id = response['id']
    posted_account_name = response['name']
    logging.info(f'New account has been added: {posted_account_name}')
    return posted_account_id

def post_tender(pdf_data, account_id):
    logging.info('Adding new tender...')
    data = pdf_data['osnovni_podaci']
    data['accounts1Id'] = account_id
    data['tipTendera'] = "Objavljeni"
    data['createdAt'] = json.dumps(datetime.now(), indent=4, default=str)
    response = client.request('POST', 'Tenderi', data)
    tender_id = response['id']
    logging.info(f'New tender has been successfully added! ID: {tender_id}')
    return tender_id

def post_attachment(file_path):
    logging.info('    - Adding new attachment...')
    with open(file_path, "rb") as pdf_file:
        encoded_file = base64.b64encode(pdf_file.read()).decode()
        # regex_query = re.compile('(?<=watch_folder\/).*')
        # file_name = regex_query.findall(file_path)[0]
        file_name = os.path.basename(file_path)
    data = {
    "name": f"{file_name}",
    "type": "application/pdf",
    "role": "Attachment",
    "relatedType": "Document",
    "field": "file",
    "file": f"data:application/pdf;base64, {encoded_file}"
    }
    try:
        attachment_id = (client.request('POST', 'Attachment', data))['id']
        logging.info('    - New attachment added...')
        return attachment_id
    except:
        return None

def post_document(file_id, tender_id):
    logging.info('Adding new document...')

    today = date.today()
    publish_date = today.strftime("%Y-%m-%d")

    logging.info('    - Adding new document...')
    data = {
        "name": "Obavjestenje o nabavci",
        "fileId": file_id,
        "publishDate": publish_date,
        "status": "Active",
        "tenderisIds": [f"{tender_id}"],
        "folderId": "62552a7b40dcbca04",
        "assignedUserId": "1"
        }
    response = client.request('POST', 'Document', data)
    logging.info('New document has been successfully added!')
    return response
# post_document()

def update_tender_documents(tender_id, documents_ids):
    client.request('PUT', f'Tenderi/{tender_id}', {'documentsIds': documents_ids})

def update_document_name(document_id, new_name):
    client.request('PUT', f'Document/{document_id}',{'name': new_name})

def get_document_fileId(entity, id):
    response = client.request('GET', f'{entity}/{id}')
    return response['fileId']

def get_documents(entity, id):
    response = client.request('GET', f'{entity}/{id}')
    if response['documentsIds'] == 0:
        return response['documentsIds']
    else:
        return []