import mysql.connector

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

def data(id_stazione, tipologia):
    #'Biossido di Azoto'
    #'Biossido di Zolfo'
    #'Ozono'
    #'Monossido di Carbonio'
    #'PM10 (SM2005)'
    #'Particelle sospese PM2.5'

    query = """
    SELECT data_rilevazione.data
    FROM rilevazione
    JOIN data_rilevazione ON rilevazione.id_data_rilevazione = data_rilevazione.id_data_rilevazione
    JOIN sensore ON rilevazione.id_sensore = sensore.id_sensore
    JOIN tipologia ON sensore.id_tipologia = tipologia.id_tipologia
    WHERE sensore.id_stazione = %s AND tipologia.nome = %s;
    """

    data = execute_fetchall(query, (id_stazione, tipologia,), dict=False)
    return data
def valore(id_stazione, tipologia):

    query = """
    SELECT rilevazione.valore
    FROM rilevazione
    JOIN data_rilevazione ON rilevazione.id_data_rilevazione = data_rilevazione.id_data_rilevazione
    JOIN sensore ON rilevazione.id_sensore = sensore.id_sensore
    JOIN tipologia ON sensore.id_tipologia = tipologia.id_tipologia
    WHERE sensore.id_stazione = %s AND tipologia.nome = %s;
    """

    valore = execute_fetchall(query, (id_stazione, tipologia,), dict=False)
    return valore


id_stazione = 560

lista_finale = []
sostanze = ['Particelle sospese PM2.5', 'PM10 (SM2005)', 'Biossido di Azoto', 'Monossido di Carbonio' ]
for elem in sostanze:
    lista_dato = [data(id_stazione, elem), valore(id_stazione, elem)]
    lista_finale.append(lista_dato)

print(lista_finale)
#lista_dati = []
#for elem in lista_sostanze:
#lista_dati = lista_dati_grafico(560, 'Biossido di Azoto')
#print(lista_dati)





