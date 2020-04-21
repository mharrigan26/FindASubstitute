import database
import cs304dbi as dbi

dsn = dbi.cache_cnf()
dbi.use('findasubstitute_db')

#sees if an entered username already exists
def usernameAvailability(conn, username):
    curs = dbi.dict_cursor(conn)
    sql = 'select * from employee where username = %s'
    vals = [username]
    curs.execute(sql, vals)
    available = curs.fetchall()
    if (len(available) == 1):
        return True #username already exists
    else:
        return False #unique username

def emailAvailability(conn, email):
    curs = dbi.dict_cursor(conn)
    sql = 'select * from employee where email = %s'
    vals = [email]
    curs.execute(sql, vals)
    available = curs.fetchall()
    if (len(available) == 1):
        return True #username already exists
    else:
        return False #unique username

def insertEmployee(conn, name, username, email, password):
    curs = dbi.dict_cursor(conn)
    sql = 'insert into employee(name, username, email, password) VALUES(%s, %s, %s, %s)'
    vals = [name, username, email, password]
    curs.execute(sql, vals)
    conn.commit()

def lookup(conn, username):
    curs = dbi.dict_cursor(conn)
    sql = 'select * from employee where username = %s'
    vals = [username]
    curs.execute(sql, vals)
    info = curs.fetchone()
    return info