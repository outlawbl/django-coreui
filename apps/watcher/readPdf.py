import PyPDF2
import pprint
import re
import regex
import json
from datetime import datetime, timedelta
from srbai.Alati.Transliterator import transliterate_cir2lat, transliterate_lat2cir
from pdfminer.high_level import extract_text
import logging
from .main import config

logging.basicConfig(filename=config['PATHS']['logPath'], format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

 
def readPdf(file_location):
    text = ''
    podaci = {}

    document = extract_text(file_location)
    print(text)

    for i in document:
        text += i

    niz_redova = text.split('\n')

    niz_redova = [i.strip() for i in niz_redova]
    niz_redova = [i for i in niz_redova if i.strip()]
    niz_redova = [i for i in niz_redova if not re.match(r'\d\s/\s\d', i)]
    niz_redova = [transliterate_cir2lat(i) for i in niz_redova]

    osnovni_podaci = {}
    uo = {}

    ind = 0
    for j in niz_redova:
        if regex.search(r'(?<=^((\d*-){4}))\d+', j) != None and 'tip_dokumenta' not in podaci:
            podaci['tip_dokumenta'] = (regex.search(r'(?<=^((\d*-){4}))\d+', j)[0])
            break
        else:
            ind += 1
    ind = 0
    if podaci['tip_dokumenta'] == '3':
        logging.info('Tip dokumenta: Obavjestenje o nabavci')
        osnovni_podaci['assignedUserId'] = 1
        osnovni_podaci['procjenjenaVrijednostPostupka'] = 1
        for j in niz_redova:
            if j.startswith('II 4.a.'):
                osnovni_podaci['name'] = niz_redova[ind+1]
                ind += 1
            elif j.startswith('II 3.c.') or j.startswith('II 6.a.'):
                osnovni_podaci['procjenjenaVrijednostPostupka'] = niz_redova[ind+1]
                ind += 1
            elif j.startswith('II 2. '):
                osnovni_podaci['podjelaNaLotove'] = niz_redova[ind+1]
                ind += 1
            elif j.upper().startswith('OBAVJEŠTENJE O NABAVCI') or j.startswith('OBAVIJEST O NABAVI'):
                osnovni_podaci['brojPostupka'] = niz_redova[ind+1]
                ind += 1
            elif j.startswith('IV 7.'):
                rok_predaje = datetime.strptime(niz_redova[ind+2], '%d.%m.%Y. %H:%M') - timedelta(hours=2)
                rok_predaje = json.dumps(rok_predaje, indent=4, sort_keys=True, default=str).strip('"')
                osnovni_podaci['rokZaPredajuSaVremenom'] = rok_predaje
                ind += 1
            elif j.startswith('IV 8.'):
                if niz_redova[ind+4][0].isdigit():
                    otvaranje = datetime.strptime(niz_redova[ind+4], '%d.%m.%Y. %H:%M') - timedelta(hours=2)
                elif niz_redova[ind+5][0].isdigit():
                    otvaranje = datetime.strptime(niz_redova[ind+5], '%d.%m.%Y. %H:%M') - timedelta(hours=2)
                elif niz_redova[ind+6][0].isdigit():
                    otvaranje = datetime.strptime(niz_redova[ind+6], '%d.%m.%Y. %H:%M') - timedelta(hours=2)
                otvaranje = json.dumps(otvaranje, indent=4, sort_keys=True, default=str).strip('"')
                osnovni_podaci['datumVrijemeOtvaranja'] = otvaranje
                ind += 1
            elif j.startswith('IV 5.'):
                    osnovni_podaci['isEaukcija'] = niz_redova[ind+1]
                    ind += 1
            elif j.startswith('IDB/JIB'):
                if regex.search(r'\d{13}', niz_redova[ind+2]) != None:
                    uo['jib'] = niz_redova[ind+2]
                    ind += 1
                elif regex.search(r'\d{13}', niz_redova[ind+3]) != None:
                    uo['jib'] = niz_redova[ind+3]
                    ind += 1
                elif regex.search(r'\d{13}', niz_redova[ind+4]) != None:
                    uo['jib'] = niz_redova[ind+4]
                    ind += 1
                elif regex.search(r'\d{13}', niz_redova[ind+5]) != None:
                    uo['jib'] = niz_redova[ind+5]
                    ind += 1
                elif regex.search(r'\d{13}', niz_redova[ind+6]) != None:
                    uo['jib'] = niz_redova[ind+6]
                    ind += 1
                else:
                    ind += 1
            elif j.startswith('I 1. Podaci o ugovornom'):
                uo_name = niz_redova[ind+3]
                if not niz_redova[ind+4].isdigit():
                    uo_name += ' ' + niz_redova[ind+4]
                uo['name'] = uo_name
                ind += 1
            else:
                ind += 1
    elif podaci['tip_dokumenta'] == '5':
        for j in niz_redova:
            if j.startswith('Broj obavještenja o nabavci'):
                osnovni_podaci['brojObavjestenjaONabavci'] = niz_redova[ind+1]
                ind += 1
            elif j.startswith('OBAVJEŠTENJE O DODJELI UGOVORA'):
                osnovni_podaci['brojObavjestenjaODodjeliUgovora'] = niz_redova[ind+1]
                ind += 1    
            else:
                ind += 1

    podaci['osnovni_podaci'] = osnovni_podaci
    podaci['uo'] = uo

    # pprint.pprint(podaci)
    logging.info('PDF procitan')
    return podaci

# readPdf(file_location)