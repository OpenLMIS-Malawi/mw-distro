#!/usr/bin/python

import os
import argparse
import csv
import sys
import uuid

try:
    import psycopg2
except:
    print "ERROR: Missing psycopg2 library. (pip install psycopg2)"
    sys.exit(1)

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True, help="Database host address", type=str)
    parser.add_argument("--port", required=False, help="Database port (default: 5432)", default=5432, type=int)
    parser.add_argument("--name", required=True, help="Database name", type=str)
    parser.add_argument("--user", required=True, help="Database username", type=str)
    parser.add_argument("--password", required=True, help="Database username password", type=str)

    parser.add_argument("--ftaps", required=True, help="Path to FacilityTypeApprovedProducts.csv", type=str)

    args = parser.parse_args()

    can_connect(parser, args)
    is_valid_file(parser, args.ftaps)

    return args

def can_connect(parser, args):
    try:
        psycopg2.connect(host = args.host, port = args.port, dbname = args.name, user = args.user, password = args.password)
    except:
        parser.error("I am unable to connect to the database")
        sys.exit(1)

def is_valid_file(parser, file_name):
    if not os.path.exists(file_name):
        parser.error("The file '{}' does not exist!".format(file_name))
        sys.exit(1)

def drop_ftaps(connection, cursor):
    SQL = """
        DELETE FROM
            referencedata.facility_type_approved_products;
    """

    cursor.execute(SQL)
    print cursor.statusmessage
    connection.commit()

def create_ftaps(connection, cursor, file_name):

    INSERT_SQL = """
        INSERT INTO
            referencedata.facility_type_approved_products(id, emergencyorderpoint, maxperiodsofstock, minperiodsofstock, facilitytypeid,
            orderableid, programid)
        SELECT
            %s, %s, %s, %s, ft.id, o.id, p.id
        FROM
            referencedata.orderables o,
            referencedata.programs p,
            referencedata.facility_types ft
        WHERE
            o.code = %s
            AND p.code ilike %s
            AND ft.code ilike %s;
    """

    with open(file_name, 'r') as file:
        reader = csv.reader(file, delimiter = ',', quotechar = '"')
        header = reader.next()

        for row in reader:
            list = map(str.strip, row)
            try:
                cursor.execute(INSERT_SQL, (str(uuid.uuid4()), list[5], list[3], list[4], list[1], list[2], list[0]))
            except psycopg2.IntegrityError, e:
                print e

            print cursor.statusmessage
            connection.commit()

if __name__ == "__main__":
    arguments = get_arguments()

    with psycopg2.connect(host = arguments.host, port = arguments.port, dbname = arguments.name, user = arguments.user, password = arguments.password) as connection:
        with connection.cursor() as cursor:
            print "DROP FTAPS"
            drop_ftaps(connection, cursor)

            print "CREATE FTAPS"
            create_ftaps(connection, cursor, arguments.ftaps)
