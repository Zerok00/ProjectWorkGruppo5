import modules.connect

def lista_dati_grafico(id_stazione, tipologia):
    #'Biossido di Azoto'
    #'Biossido di Zolfo' 
    #'Ozono' 
    #'Monossido di Carbonio'
    #'PM10 (SM2005)'
    #'Particelle sospese PM2.5'

    query = """
    SELECT rilevazione.valore, data_rilevazione.data, tipologia.nome
    FROM rilevazione
	JOIN data_rilevazione ON rilevazione.id_data_rilevazione = data_rilevazione.id_data_rilevazione
    JOIN sensore ON rilevazione.id_sensore = sensore.id_sensore
    JOIN tipologia ON sensore.id_tipologia = tipologia.id_tipologia
    WHERE sensore.id_stazione = %s AND tipologia.nome = %s;
    """

    lista_dati = modules.connect.execute_fetchall(query, (id_stazione, tipologia,), dict=False)

    return lista_dati



lista_dati = lista_dati_grafico(560, 'Biossido di Azoto')
print(lista_dati)


