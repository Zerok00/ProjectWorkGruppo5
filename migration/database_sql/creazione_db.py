import db_connection

try:
    db_connection.connect.create_db(drop=False)
except:
    print("\nOperazioni fermate, è già presente un database! \nPer eliminarlo e caricarlo nuovamente utilizzare il parametro 'drop=True'\n")

