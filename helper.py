import cs304dbi as dbi 


def getAllEmployees(conn):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from employee1''')
    data = curs.fetchall()
    return data

def shiftExists(conn,permanent,day,time,employee):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from shift1 where day = %s and time = %s and employee = %s''', (day,time,employee))
    data = curs.fetchall()
    return data

def insertShift(conn,permanent,day,time,employee):
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into shift1(permanent,day,time,employee) values(%s,%s,%s,%s)''',
        (permanent,day,time,employee))
    conn.commit()
    
    