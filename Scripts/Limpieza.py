import pandas as pd
from ast import literal_eval
import numpy as np
import string, re, math

# Función para quitar la puntuación
def cleanPunctuation(text):
    return ' '.join(word.strip(string.punctuation+'•–“”»').lower() for word in text.split())

# Para encontrar los años de experiencia
def year_mean(data):
    if data == 'No disponible':
        return data
    else:
        if len(data) > 0:
            return math.ceil(sum(list(map(int,data))) / len(data))
        else:
            return sum(data)

# Lectura de stopwords
f = open('../stop_words_spanish.txt')
stopwords = f.readlines()
stop = []
english_words = ['and','the','to','of','in','with','for','our','your','you','is','·','jefa']

for i in english_words:
    stop.append(i)
for i in stopwords:
    stops = re.sub('\n','',i)
    stop.append(stops)

df = pd.read_excel('../Datos/data-25-04-2022.xlsx')#('../Datos/...') # Este código debe apuntar al excel donde se almacenan los datos
df = df.reset_index()
# Primero borramos los duplicados
df['dup'] = df.duplicated(subset=['title', 'company_name', 'location', 
                                        'via', 'description'], keep='first')
df = df[df.dup == False]

# Limpieza columna title
df['title'] = df['title'].replace('Oferta de trabajo.\s?','',regex=True)
df['title'] = df['title'].replace('Oferta de empleo.\s','',regex=True)
df['title'] = df['title'].replace('Empleo.\s','',regex=True)
df['title'] = df['title'].replace('se recluta.\s','',regex=True)
df['title'] = df['title'].replace('Urgente.\s','',regex=True)

# Limpieza columna title 2 
df['title_clean'] = df.title.apply(lambda x: cleanPunctuation(x))
rx = re.compile(r"\w+", re.I)
df['title_clean'] = df.title_clean.apply(lambda x: rx.findall(x))
df['title_clean'] = df['title_clean'].str.join(' ')
df['title_clean'] = df['title_clean'].apply(lambda x: cleanPunctuation(x))
df['title_clean'] = df['title_clean'].replace('á','a',regex=True)
df['title_clean'] = df['title_clean'].replace('é','e',regex=True)
df['title_clean'] = df['title_clean'].replace('í','i',regex=True)
df['title_clean'] = df['title_clean'].replace('ó','o',regex=True)
df['title_clean'] = df['title_clean'].replace('ú','u',regex=True)
df['title_clean'] = df['title_clean'].replace('ó','o',regex=True)
df['title_clean'] = df['title_clean'].replace('í','i',regex=True)
df['title_clean'] = df['title_clean'].replace('é','e',regex=True)
df['title_clean'] = df['title_clean'].apply(lambda x: [item for item in str(x).split() if item not in stop])
df['title_clean'] = df['title_clean'].str.join(' ')
rx = re.compile(r'[a-z]+')
df['title_clean'] = df.title_clean.apply(lambda x: rx.findall(x))
df['title_clean'] = df['title_clean'].str.join(' ')
rx = re.compile(r'^\w+\s?\w+')
df['title_clean'] = df.title_clean.apply(lambda x: rx.findall(x))
df['title_clean'] = df['title_clean'].str.join(' ')
df['title_clean'] = df['title_clean'].replace(r'^\s*$', 'No disponible', regex=True)
df['title'] = df.title_clean.str.title()

# Limpieza columna vía
df['via'] = df['via'].replace('a trav.s de\s?','',regex=True)

# Limpieza comulna location
df['location'] = df['location'].replace(' \(y 1 ubicaci.n m.s\)','',regex=True)
df['location'] = df['location'].replace(r'^\s*$', 'No disponible', regex=True)

# Extraer la información de detectec extensión en más columnas (posted_at, salary, schedule_type)
df.detected_extensions = df.detected_extensions.apply(literal_eval)
df = df.join(pd.json_normalize(df.detected_extensions))

# Limpieza de la columna posted_at
df['posted_at'] = df['posted_at'].replace('Hace más de.\s?','',regex=True)
df['posted_at'] = df['posted_at'].replace('hace.\s?','',regex=True)
df['posted_at'] = df['posted_at'].str.strip()

# Rellenar NA values
df.fillna('No disponible', inplace=True)

# Limpieza de la columna description

df['description'] = df['description'].replace('Oferta de trabajo.\s?','',regex=True)
df['description'] = df['description'].replace('Oferta de empleo.\s?','',regex=True)
df['description'] = df['description'].replace('Empleo.\s?','',regex=True)

#Encontrar años de experiencia
rx = re.compile(r"\s?\s0?[1-9]\s?añ?os?|experie.{0,4}\s?0?[1-9]", re.I)
df['expReq'] = df.description.apply(lambda x: rx.findall(x)).apply(set)
# unir la lista 
df['expReq'] = df['expReq'].str.join(', ')
df['expReq'] = df['expReq'].replace('ao','año',regex=True)
df['expReq'] = df['expReq'].replace(r'^\s*$', 'No disponible', regex=True)

rx = re.compile(r"[1-9]+", re.I)
df['expReq_limpio'] = df.expReq.apply(lambda x: rx.findall(x))
df['expY'] = df['expReq_limpio'].apply(lambda x: year_mean(x))

df['limpio'] = df.description.apply(lambda x: cleanPunctuation(x))

rx = re.compile(r"\D+", re.I)
df['limpio'] = df.limpio.apply(lambda x: rx.findall(x))
df['limpio'] = df['limpio'].str.join('')
df['limpio'] = df['limpio'].apply(lambda x: cleanPunctuation(x))
df['limpio'] = df['limpio'].replace('á','a',regex=True)
df['limpio'] = df['limpio'].replace('é','e',regex=True)
df['limpio'] = df['limpio'].replace('í','i',regex=True)
df['limpio'] = df['limpio'].replace('ó','o',regex=True)
df['limpio'] = df['limpio'].replace('ú','u',regex=True)
df['limpio'] = df['limpio'].replace('ó','o',regex=True)
df['limpio'] = df['limpio'].replace('í','i',regex=True)
df['limpio'] = df['limpio'].replace('é','e',regex=True)
df['limpio'] = df['limpio'].replace(r'^\s*$', 'No disponible', regex=True)


# Encontrar requerimiento de inglés
english = ['ingles','inglés','english']
df['english'] = df['limpio'].apply(lambda x: any([k in x for k in english]))
 
# Encontrar requerimiento de Educación Secundaria
rx = re.compile(r"educaci.n se.undaria", re.I)
df['edu2'] = df.limpio.apply(lambda x: rx.findall(x))
# unir la lista 
df['edu2'] = df['edu2'].str.join(', ')
df['edu2'] = df['edu2'].replace(r'^\s*$', 'No disponible', regex=True)

# Encontrar las carreas
"""rx = re.compile(r'acuicultura|administraci.n|aerograf.a|arton.utica|agroindustrias|\
                  agronom.a|agropecuaria|sistemas?|arqueolog.a|\sarte\s|dise.o|\
                  auditoria|biolog.a|botanica|ciencias? pol.ticas?|negocios internacionales|\
                  computaci.n|comunicaci.ne?s?|construcci.n|contabilidad|derecho|ambiental|\
                  ecolog.a|econom.a|electr.nica|estad.stica|filosof.a|alta direcci.n|\
                  psicolog.a|historia|matem.atica|markenting|publicidad|zootecnia|sociolog.a|\
                  pedagog.a|trabajo social|secretariado|petroqu.mica|mec.anic.|\sminas?|\
                  gesti.n|comercial|finanzas|qu.mica|sanitaria|comercio internacional|\
                  industrial|el.ctrica|telecomunicaci.ne?s?|mecatr.nica|literatura|\
                  mercadotecnia|inform.tica|nutrici.n|periodismo|turismo')

df['carreras'] = df.limpio.apply(lambda x: rx.findall(x)).apply(set)
df['carreras'] = df['carreras'].str.join(', ')
df['carreras'] = df['carreras'].replace(r'^\s*$', 'No disponible', regex=True)

# Carreras estandarizadas
replace_values = {'matematica':'Matemática','zootectnia':'Zootecnia',
                  'sociologia':'Servicios Sociales y Asistenciales',
                  'telecomunicaciones':'Ingeniería de Telecomunicaciones',
                  'pedagogia':'Educación Secundaria','trabajo social':'Trabajo Social',
                  'agronomia':'Agropecuaria','economia':'Economía',
                  'computacion':'Ciencias de la Computación',
                  'industrial':'Ingeniería Industrial',
                  'administracion':'Administración de Empresas',
                  'sistemas?':'Ingeniería de Sistemas y Cómputo','secretariado':'Secretariado',
                  'negocios internacionales':'Negocios Internacionales','marketing':'Marketing'
                  ,'contabilidad':'Contabilidad y Finanzas',
                  'comunicacione?s?':'Ciencias de la Comunicación',
                  'publicidad':'Ciencias de la Comunicación',
                  'comercio internacional':'Negocios Internacionales',
                  'ciencias politicas':'Ciencias Políticas',
                  'empresarial':'Administración de Empresas',
                  'quimica':'Química','sanitaria':'Ingeniería Sanitaria',
                  'ambiental':'Ecología y Medio Ambiente',
                  'petroquimica':'Ingeniería Minera, Metalurgia y Petróleo',
                  'mecanica':'Ingeniería Mecánica',
                  'dise.o':'Diseño',
                  'minas':'Ingeniería Minera, Metalurgia y Petróleo',
                  'electrica':'Ingeniería Electrica','comercial':'Administración de Empresas',
                  'finanzas':'Contabilidad y Finanzas','estadistica':'Estadística',
                  'psicologia':'Psicología','gestion':'Otras Carreras de Administración',
                  'alta direccion':'Otras Carreras de Administración',
                  'informatica':'Ciencias de la Computación'}

df['carreras_limpio'] = df['carreras'].replace(replace_values, regex=True)
# conocimientos técnicos
      
rx = re.compile(r"django|autocad|\sword\s|python|oracle|postgresql|\
                  shell|perl\s|matlab|spss|stata|eviews|power\s?bi|linux|\
                  \sscala\s|\sr\s|sql\s?server|mysql|java\s?script|jquery|\
                  css|html|poo|php|json|xml|html|sql|bootstrap|\sc\s|\sapi\s\
                  azure|java|\saws\s|\sasp\s|\snet\s|api\s?rest|typescript|\
                  angular|\sexcel\s|\sgit|github|sass|scrum|\snode\s|wordpress|\
                  \sreact\s|\ssas\s|cobol|\soffice", re.I)
df['tec'] = df.limpio.apply(lambda x: rx.findall(x)).apply(set)
df['tec'] = df['tec'].str.join(',')
df['tec'] = df['tec'].replace(r'^\s*$', 'No disponible', regex=True)
"""
# Hallando la fecha
import dateutil.relativedelta
from datetime import datetime

def col_fecha(data):
    
    if data == 'No disponible':
        return data
    elif 'mes' in data:
        rx = re.compile(r"\d+", re.I)
        number = rx.findall(data)
        number = int(''.join(number))
        return datetime.now().date() - dateutil.relativedelta.relativedelta(months=number)
    elif 'día' in data:
        rx = re.compile(r"\d+", re.I)
        number = rx.findall(data)
        number = int(''.join(number))
        return datetime.now().date() - dateutil.relativedelta.relativedelta(days=number)
    elif 'hora' or 'minutos' in data:
        rx = re.compile(r"\d+", re.I)
        number = rx.findall(data)
        number = int(''.join(number))
        return datetime.now().date()

df['date'] = df['posted_at'].apply(lambda x: col_fecha(x))



# Borrar columnas extra
df.reset_index(inplace=True)
del df['dup']
del df['index']
del df['thumbnail']
del df['detected_extensions']
del df['extensions']
del df['Unnamed: 0']
del df['title_clean']
del df['expReq']
del df['expReq_limpio']
del df['limpio']
del df['posted_at']

# Guardar la base de datos
print(df.shape)
df.to_excel('../Datos/cleanBase.xlsx')
