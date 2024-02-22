import modules.connect

# tabelle senza auto increment: stazione e sensore
def create_tables():

    # provincia -> comune -> stazione
    query = """
    CREATE TABLE IF NOT EXISTS provincia(
    id_provincia INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(255)
    );
    """
    modules.connect.execute_one(query)

    query = """
    CREATE TABLE IF NOT EXISTS comune(
    id_comune INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(255),
    id_provincia INT,
    CONSTRAINT fk_provincia FOREIGN KEY (id_provincia) 
        REFERENCES provincia(id_provincia)
        ON DELETE CASCADE ON UPDATE CASCADE
    );
    """
    modules.connect.execute_one(query)

    query = """
    CREATE TABLE IF NOT EXISTS stazione(
    id_stazione INT PRIMARY KEY,
    quota INT,
    id_comune INT,
    latitudine FLOAT,
    longitudine FLOAT,
    CONSTRAINT fk_comune FOREIGN KEY (id_comune) 
        REFERENCES comune(id_comune)
        ON DELETE CASCADE ON UPDATE CASCADE 
    );
    """
    modules.connect.execute_one(query)

    # tipologia -> sensore
    query = """
    CREATE TABLE IF NOT EXISTS tipologia(
    id_tipologia INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(255),
    unita_misura VARCHAR(255)
    );
    """
    modules.connect.execute_one(query)

    query = """
    CREATE TABLE IF NOT EXISTS sensore(
    id_sensore INT PRIMARY KEY AUTO_INCREMENT,
    id_stazione INT,
    id_tipologia INT,
    frequenza INT,
    CONSTRAINT fk_stazione FOREIGN KEY (id_stazione)
        REFERENCES stazione(id_stazione)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_tipologia FOREIGN KEY (id_tipologia)
        REFERENCES tipologia(id_tipologia)
        ON DELETE CASCADE ON UPDATE CASCADE
    );
    """
    modules.connect.execute_one(query)


    # data rilevazione -> rilevazione <- sensore
    query = """
    CREATE TABLE IF NOT EXISTS data_rilevazione(
    id_data_rilevazione INT PRIMARY KEY AUTO_INCREMENT,
    data DATETIME
    );
    """
    modules.connect.execute_one(query)

    query = """
    CREATE TABLE IF NOT EXISTS rilevazione(
    id_rilevazione INT PRIMARY KEY AUTO_INCREMENT,
    id_sensore INT,
    id_data_rilevazione INT,
    valore FLOAT,
    CONSTRAINT fk_sensore FOREIGN KEY (id_sensore)
        REFERENCES sensore(id_sensore)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_data_rilevazione FOREIGN KEY (id_data_rilevazione)
        REFERENCES data_rilevazione(id_data_rilevazione)
        ON DELETE CASCADE ON UPDATE CASCADE
    );
    """
    modules.connect.execute_one(query)



   
