import mysql.connector
import config

db_config = {
    'host': config.DB_HOST,
    'user': config.DB_USER,
    'password': config.DB_PASSWORD,
    'database': config.DB_NAME
}


def create_db(drop=True):
    localhost_connect = {
        'host': config.DB_HOST,
        'user': config.DB_USER,
        'password': config.DB_PASSWORD,
    }

    connection = mysql.connector.connect(**localhost_connect)
    cursor = connection.cursor()

    if drop:
        query_drop = f"DROP DATABASE {db_config['database']};"
        cursor.execute(query_drop)
        connection.commit()
    
    query_db = f"CREATE DATABASE {db_config['database']};"

    cursor.execute(query_db)
    connection.commit()

    cursor.close()
    connection.close()


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


def execute_one(query, params=None):
    connection = create_db_connection()
    cursor = connection.cursor()

    if params:
        try:
            cursor.execute(query, params)
        except mysql.connector.Error as err:
            print(f"Error: '{err}'")

    else:
        try:
            cursor.execute(query)
        except mysql.connector.Error as err:
            print(f"Error: '{err}'")

    connection.commit()

    cursor.close()
    connection.close()


def execute_many(query, data):
    connection = create_db_connection()
    cursor = connection.cursor()

    try:
        cursor.executemany(query, data)
        connection.commit()
       
    except mysql.connector.Error as err:
        print(f"Error: '{err}'")

    cursor.close()
    connection.close()
