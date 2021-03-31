# this is the data access layer: only dumb read / write functions to the DB
# no business logic should be implemented here to maintain seperation of concerns

import psycopg2
from configparser import ConfigParser
import settings


# gets the db info from the database.ini config file
def GetDB(filename=settings.DB_SETTINGS.FILENAME, section=settings.DB_SETTINGS.SECTION):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to researchDB
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(
            'Section {0} not found in the {1} file'.format(section, filename))
    return db


def ExecuteQuery(query):
    conn = None
    try:
        # read connection parameters
        params = GetDB()

        # conn = psycopg2.connect(**params)
        conn = psycopg2.connect(**params)
        # create a cursor
        cur = conn.cursor()

        cur.execute(query)
        result = cur.fetchall()

        # close the communication with the PostgreSQL
        cur.close()
        return result

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
