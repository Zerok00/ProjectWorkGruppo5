import csv
import mysql.connector
#from migration.database_sql.modules import connect as conn

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
    query = "SELECT * FROM rilevazione ORDER BY id_rilevazione DESC;"
    result = execute_fetchall(query)
    diz_id = {}
    for elem in result:
        if elem[1] not in diz_id:
            diz_id[elem[1]] = elem[3]

    query2 = """SELECT stazione.id_stazione, stazione.latitudine, stazione.longitudine, sensore.id_sensore, tipologia.nome
    FROM stazione INNER JOIN sensore INNER JOIN tipologia
    ON stazione.id_stazione = sensore.id_stazione AND sensore.id_tipologia = tipologia.id_tipologia
    ORDER BY id_stazione;"""
    sensori_per_stazione = execute_fetchall(query2)

    lista_finale = []

    for cristo in sensori_per_stazione:
        if cristo[3] in diz_id:
            x = (cristo[0], cristo[1], cristo[2], cristo[3], cristo[4], diz_id[cristo[3]])
            lista_finale.append(x)

    dizionario_stazione_posizione_sensori = {}

    for elem in lista_finale:
        dizionario_stazione_posizione_sensori[f"stazione{elem[0]}"] = {"coord": [], "lista_sensori": []}

    for elem in lista_finale:
        dizionario_stazione_posizione_sensori[f"stazione{elem[0]}"]["coord"] = [elem[1], elem[2]]
        tupla = (elem[3], elem[4], elem[5])
        dizionario_stazione_posizione_sensori[f"stazione{elem[0]}"]["lista_sensori"].append(tupla)

    return dizionario_stazione_posizione_sensori