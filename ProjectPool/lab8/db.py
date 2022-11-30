from flask import g
import psycopg2
import psycopg2.extras


data_source_name = "dbname=canthony user=canthony host=faraday.cse.taylor.edu password=reason-parrot-DAILY"


def open_db_connection():
    g.connection = psycopg2.connect(data_source_name)
    g.cursor = g.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)


def close_db_connection():
    g.cursor.close()
    g.connection.close()


def find_member(memberEmail):

    query = """
    SELECT m.email, m.first_name, m.last_name, p.file_path
    FROM member AS m
       LEFT OUTER JOIN photo AS p ON m.email = p.member_email 
    WHERE email = %(emailParam)s
    """
    g.cursor.execute(query, {'emailParam': memberEmail})
    return g.cursor.fetchone()


def create_member(email, first_name, last_name, password):

    query = '''
    INSERT INTO member (email, first_name, last_name, password)
    VALUES (%(email)s, %(first)s, %(last)s, %(pass)s)
    '''

    g.cursor.execute(query, {'email': email, 'first': first_name, 'last': last_name, 'pass': password})
    g.connection.commit()
    return g.cursor.rowcount


def update_member(email,first_name,last_name,password):
    query = '''
        Update member set first_name = %(first)s,
                       last_name = %(last)s,
                       password = %(pass)s
        where email = %(email)s
        '''
    g.cursor.execute(query, {'first':first_name,'last':last_name,'email':email,'pass':password})
    g.connection.commit()
    return g.cursor.rowcount


def all_comments(email=False):

    query = """
            SELECT  first_name, last_name, email, body
            FROM member JOIN comment ON member.email = comment.member
            """
    if email:
        query += " WHERE member.email = %(email)s"

    g.cursor.execute(query,{'email': email})
    return g.cursor.fetchall()


def all_members():
    g.cursor.execute("SELECT * FROM member ORDER BY email")
    return g.cursor.fetchall()


def all_accounts():
    query = """
    SELECT * from account
    ORDER BY name
    """
    g.cursor.execute(query)
    return g.cursor.fetchall()

def update_balance(account_id, balance_change):
    query = """
    Update account set balance = balance + %(balance)s
    where id = %(id)s
    """
    g.cursor.execute(query, {'id': account_id, 'balance': balance_change})
    return g.cursor.rowcount

def transfer_funds(from_account_id, to_account_id, transfer_amount):
    updated_rows_from = update_balance(from_account_id, -transfer_amount)
    updated_rows_to = update_balance(to_account_id, transfer_amount)
    if updated_rows_from == 1 and updated_rows_to == 1:
        g.connection.commit()
        return "You done did it!"
    else:
        g.connection.rollback()
        return "You done GOOFED"
