import csv
import mysql.connector
#from migration.database_sql.modules import connect as conn
import time
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'projectwork5'
db_config = {
    'host': DB_HOST,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'database': DB_NAME
}
def create_db_connection():
    return mysql.connector.connect(**db_config)

def execute_fetchall(query, params=None, dict=False):
    connection = create_db_connection()

    if dict:
        cursor = connection.cursor(dictionary=True)
    else:
        cursor = connection.cursor()

    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)

    result = cursor.fetchall()

    cursor.close()
    connection.close()

    return result

def calcolo_stazioni():
    start = time.process_time()
    print(start)
    query = "SELECT * FROM rilevazione_desc;"
    result = execute_fetchall(query)
    print("PRIMA QUERY", time.process_time() - start)
    diz_id = {}
    for elem in result:
        if elem[1] not in diz_id:
            diz_id[elem[1]] = elem[3]

    query2 = """SELECT * FROM data_stazioni;"""
    sensori_per_stazione = execute_fetchall(query2)
    print("SECONDA QUERY", time.process_time() - start)

    lista_finale = []

    for elementoo in sensori_per_stazione:
        if elementoo[3] in diz_id:
            x = (elementoo[0], elementoo[1], elementoo[2], elementoo[3], elementoo[4], diz_id[elementoo[3]])
            lista_finale.append(x)

    dizionario_stazione_posizione_sensori = {}

    for elem in lista_finale:
        dizionario_stazione_posizione_sensori[f"stazione{elem[0]}"] = {"coord": [], "lista_sensori": []}

    for elem in lista_finale:
        dizionario_stazione_posizione_sensori[f"stazione{elem[0]}"]["coord"] = [elem[1], elem[2]]
        tupla = (elem[3], elem[4], elem[5])
        dizionario_stazione_posizione_sensori[f"stazione{elem[0]}"]["lista_sensori"].append(tupla)

    print("TERZA QUERY", time.process_time() - start)


    return dizionario_stazione_posizione_sensori