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

    parser.add_argument("--orderables", required=True, help="Path to Orderables.csv", type=str)
    parser.add_argument("--program-orderables", required=True, help="Path to ProgramOrderables.csv", type=str)

    args = parser.parse_args()

    can_connect(parser, args)
    is_valid_file(parser, args.orderables)
    is_valid_file(parser, args.program_orderables)

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

def update_orderables(connection, cursor, file_name):
    SQL = """
        UPDATE
            referencedata.orderables
        SET
            fullproductname = %s,
            description = %s,
            packroundingthreshold = %s,
            netcontent = %s,
            roundtozero = %s,
            dispensingunit = %s
        WHERE
            code = %s;
    """

    with open(file_name, 'r') as file:
        reader = csv.reader(file, delimiter = ',', quotechar = '"')
        header = reader.next()

        for row in reader:
            row[6] = row[6].split(':')[1]
            list = [x.strip().replace("'", "''") for x in row]

            try:
            	cursor.execute(SQL, (list[1], list[2], list[3], list[4], list[5], list[6], list[0]))
            except:
            	print list
            	raise
            print cursor.statusmessage
            connection.commit()

def update_program_orderables(connection, cursor, file_name):
    SELECT_SQL = """
        SELECT
            1
        FROM
            referencedata.program_orderables po
            CROSS JOIN referencedata.orderables o,
                       referencedata.programs p,
                       referencedata.orderable_display_categories c
        WHERE
            po.orderableid = o.id
            AND po.programid = p.id
            AND po.orderabledisplaycategoryid = c.id
            AND o.code = %s
            AND p.code = %s
            AND c.code = %s;
    """

    INSERT_SQL = """
        INSERT INTO
            referencedata.program_orderables(id, active, displayorder, dosesperpatient, fullsupply, priceperpack, orderabledisplaycategoryid, orderableid, programid)
        SELECT
            %s, %s, %s, %s, %s, %s, c.id, o.id, p.id
        FROM
            referencedata.orderables o,
            referencedata.programs p,
            referencedata.orderable_display_categories c
        WHERE
            o.code = %s
            AND p.code = %s
            AND c.code = %s;
    """

    UPDATE_SQL = """
        UPDATE
            referencedata.program_orderables po
        SET
            dosesperpatient = %s,
            active = %s,
            fullsupply = %s,
            displayorder = %s,
            priceperpack = %s
        FROM
            referencedata.orderables o,
            referencedata.programs p,
            referencedata.orderable_display_categories c
        WHERE
            po.orderableid = o.id
            AND po.programid = p.id
            AND po.orderabledisplaycategoryid = c.id
            AND o.code = %s
            AND p.code = %s
            AND c.code = %s;
    """

    with open(file_name, 'r') as file:
        reader = csv.reader(file, delimiter = ',', quotechar = '"')
        header = reader.next()

        for row in reader:
            list = map(str.strip, row)

            cursor.execute(SELECT_SQL, (list[0], list[1], list[2]))
            result = cursor.fetchone()

            if result is None:
                cursor.execute(INSERT_SQL, (str(uuid.uuid4()), list[4], list[6], list[3], list[5], list[7], list[0], list[1], list[2]))
            else:
                cursor.execute(UPDATE_SQL, (list[3], list[4], list[5], list[6], list[7], list[0], list[1], list[2]))

            print cursor.statusmessage
            connection.commit()

if __name__ == "__main__":
    arguments = get_arguments()

    with psycopg2.connect(host = arguments.host, port = arguments.port, dbname = arguments.name, user = arguments.user, password = arguments.password) as connection:
        with connection.cursor() as cursor:
            print "UPDATE ORDERABLES"
            update_orderables(connection, cursor, arguments.orderables)

            print "UPDATE PROGRAM ORDERABLES"
            update_program_orderables(connection, cursor, arguments.program_orderables)
