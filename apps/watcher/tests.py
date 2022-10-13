from django.test import TestCase
import re
import regex
from apps.watcher.espo_api_client import EspoAPI
from .api import client

documents_ids = []
documents_ids.append('6345719d086ac3650')
tender_id = '634571f49a5c650dc'

print(client.request('PUT', f'Tenderi/{tender_id}', {'documentsIds': documents_ids}))