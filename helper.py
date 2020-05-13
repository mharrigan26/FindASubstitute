#FindASubstitute
#Bianca Pio, Alexandra Bullen-Smith, Margaret Harrigan
#CS 304 Final Project
#Submitted May 13, 2020
#helper.py is the python file that contains helper funtions to navigate the database, an extension of database.py


import cs304dbi as dbi 


def getAllEmployees(conn):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from employee1''')
    data = curs.fetchall()
    return data

def shiftExists(conn,permanent,day,time,endtime,employee):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from shift1 where day = %s and time = %s and endtime = %s and employee = %s''', (day,time,endtime,employee))
    data = curs.fetchall()
    return data

def insertShift(conn,permanent,day,time,endtime,employee):
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into shift1(permanent,day,time,endtime,employee) values(%s,%s,%s,%s,%s)''',
        (permanent,day,time,endtime,employee))
    conn.commit()
    
    