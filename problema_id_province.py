
def create_database():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Creazione tabella Province
    c.execute('''CREATE TABLE Province (
                    id INTEGER PRIMARY KEY,
                    nome TEXT,
                    codice TEXT UNIQUE)''')

    # Creazione tabella Comuni con chiave esterna verso la tabella Province
    c.execute('''CREATE TABLE Comuni (
                    id INTEGER PRIMARY KEY,
                    nome TEXT,
                    codice_provincia TEXT,
                    id_provincia INTEGER,
                    FOREIGN KEY (id_provincia) REFERENCES Province (id))''')

    conn.commit()
    conn.close()

# Importazione dei dati delle Province
def import_province():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    with open('province.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Salta l'intestazione
        provinces = [(row[0], row[1], row[2]) for row in reader]  # Aggiunto codice provincia

        c.executemany("INSERT INTO Province (id, nome, codice) VALUES (?, ?, ?)", provinces)

    conn.commit()
    conn.close()

# Importazione dei dati dei Comuni
def import_comuni():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Creazione del dizionario di mapping codice provincia -> ID provincia
    province_mapping = {}
    c.execute("SELECT id, codice FROM Province")
    for row in c.fetchall():
        province_mapping[row[1]] = row[0]

    with open('comuni.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Salta l'intestazione
        comuni = [(row[0], row[1], row[2]) for row in reader]

        # Associa ogni comune alla provincia corrispondente utilizzando il dizionario di mapping
        for comune in comuni:
            id_provincia = province_mapping.get(comune[2])
            if id_provincia is not None:
                c.execute("INSERT INTO Comuni (nome, codice_provincia, id_provincia) VALUES (?, ?, ?)", (comune[0], comune[2], id_provincia))

    conn.commit()
    conn.close()

# Creazione del database e delle tabelle
create_database()

# Importazione dei dati delle Province
import_province()

# Importazione dei dati dei Comuni
import_comuni()
