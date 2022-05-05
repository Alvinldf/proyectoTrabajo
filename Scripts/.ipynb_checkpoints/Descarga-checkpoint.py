import numpy as np
import pandas as pd
import os
from datetime import datetime
from serpapi import GoogleSearch

positions = ['diseño','audiovisual']

cantidad_búsquedas = int(input('Por favor, ingrese la cantidad de búsquedas que desea realizar:'))

def jobs_download(job_name = '',number_of_pages=1):
    df = pd.DataFrame()
    for i in np.arange(0,number_of_pages,10):
        params = {
        "engine": "google_jobs",
        "q": job_name,
        'location':'Peru',
        "gl":"pe",
        "hl": "es",
        "start":i,
        "api_key": "b13b6f7e123626508ad68e6f6810079157899c9c42dfcc877b96724f02881a25"
        #'b06c29d3b0a82343f831ba49939a14d81166aefb2d851c43b9ead7387fd3132e'
        #'0c02f0006c0a3ce6830aecc5825c7dbb35b3e9452b22d9ec51d9b599ad4d913e' 
        #'812bf33ac59dd10e11fc50e303fa219cfe47203a798067460e91ff9f26967e59'
        }

        search = GoogleSearch(params).get_dict()
        jobs_results = {}
        try:
            jobs_results = search['jobs_results']

        except:
            pass 
        df = pd.concat([df, pd.DataFrame(jobs_results)])
        df['date'] = datetime.today().strftime('%d-%m-%Y')

    print("Done")
    return (job_name, df)


results = [jobs_download(job, cantidad_búsquedas) for job in positions]
for search in results:
    df_final = search[1]
    df_final.to_excel(f'../Datos/{search[0]}.xlsx')
    if(os.path.isfile(f'../Datos/base-{search[0]}.xlsx')):
        df_last = pd.read_excel(f"../Datos/{search[0]}.xlsx")
        with pd.ExcelWriter(f"../Datos/base-{search[0]}.xlsx", mode="a", engine="openpyxl", if_sheet_exists="overlay")  as writer:
            df_last.to_excel(writer, sheet_name="Sheet1", header=None, startrow=writer.sheets["Sheet1"].max_row, index=False)
    else:
        df_final.to_excel(f"../Datos/base-{search[0]}.xlsx")