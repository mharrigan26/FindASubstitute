from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
app = Flask(__name__)

import cs304dbi as dbi
import database
import random
import helper
import os
import bcrypt

# for file upload
app.config['UPLOADS'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1*1024*1024 # 1 MB


app.secret_key = 'raaaaandom'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def index():
    try:
        if 'username' in session:
            username = session['username']
            #session['visits'] = 1+int(session['visits'])
            return render_template('greet.html',
                                   page_title='Find A Substitute: Welcome {}'.format(username),
                                   name=username)
        else:
            flash('you are not logged in. Please login or join')
            return render_template('main.html',title='Find A Substitute')
    except Exception as err:
        flash('some kind of error '+str(err))
        return render_template('main.html',title='Find A Substitute')
    

#route for current welcome / home page
@app.route('/user/<username>')
def user(username):
    try:
        # don't trust the URL; it's only there for decoration
        if 'username' in session:
            username = session['username']
            session['visits'] = 1+int(session['visits'])
            return render_template('greet.html',
                                   page_title='My App: Welcome {}'.format(username),
                                   name=username)
        else:
            flash('you are not logged in. Please login or join')
            return redirect( url_for('index') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('index') )

#page for employee's to view and update their worker profile
@app.route('/profile/', methods=["GET", "POST"])
def profile():
    conn = dbi.connect()
    if request.method == 'GET':
        username1 = session['username']
        info = database.lookupEmployee(conn, username1)
        name = info['name']
        return render_template('profile.html', name=name, username=username1, title='User Profile')
    if request.method == 'POST':
        username1 = session['username']
        new_username = request.form['new_username']
        new_name = request.form['name']
        database.updateEmployeeProfile(conn, username1, new_username, new_name)
        flash('profile updated')
        return redirect(url_for('profile'))

#reference code for file upload
""" if request.method == 'GET':
        return render_template('form.html',src='',nm='')
    else:
        try:
            nm = int(request.form['nm']) # may throw error
            f = request.files['pic']
            user_filename = f.filename
            ext = user_filename.split('.')[-1]
            filename = secure_filename('{}.{}'.format(nm,ext))
            pathname = os.path.join(app.config['UPLOADS'],filename)
            f.save(pathname)
            conn = dbi.connect()
            curs = dbi.dict_cursor(conn)
            curs.execute(
                '''insert into picfile(nm,filename) values (%s,%s)
                   on duplicate key update filename = %s''',
                [nm, filename, filename])
            conn.commit()
            flash('Upload successful')
            return render_template('form.html',
                                   src=url_for('pic',nm=nm),
                                   nm=nm) """

    
#route for joining find a substitute
@app.route('/join/', methods=["POST"])
def join():
    try:
        username = request.form['username']
        passwd1 = request.form['password1']
        passwd2 = request.form['password2']
        name = request.form['name']
        email = request.form['email']
        if passwd1 != passwd2:
            flash('passwords do not match')
            return redirect( url_for('index'))
        hashed = bcrypt.hashpw(passwd1.encode('utf-8'), bcrypt.gensalt())
        hashed_str = hashed.decode('utf-8')
        conn = dbi.connect()
        curs = dbi.cursor(conn)
        try:
            curs.execute('''INSERT INTO employee1(username,password,name,email)
                            VALUES(%s,%s,%s,%s)''',
                         [username, hashed_str, name, email])
            conn.commit()
        except Exception as err:
            flash('That username is taken: {}'.format(repr(err)))
            return redirect(url_for('index'))
        session['username'] = username
        session['logged_in'] = True
        session['visits'] = 1
        return redirect( url_for('user', username=username) )
    except Exception as err:
        flash('form submission error '+str(err))
        return redirect( url_for('index') )

#route for employee log in        
@app.route('/loginE/', methods=["POST"])
def loginE():
    try:
        username = request.form['username']
        passwd = request.form['password']
        conn = dbi.connect()
        curs = dbi.dict_cursor(conn)
        curs.execute('''SELECT username,password
                      FROM employee1
                      WHERE username = %s''',
                     [username])
        row = curs.fetchone()
        if row is None:
            # Same response as wrong password,
            # so no information about what went wrong
            flash('login incorrect. Try again or join')
            return redirect( url_for('index'))
        hashed = row['password']
        hashed2 = bcrypt.hashpw(passwd.encode('utf-8'),hashed.encode('utf-8'))
        hashed2_str = hashed2.decode('utf-8')
        if hashed2_str == hashed:
            flash('successfully logged in as '+username)
            session['username'] = username
            session['logged_in'] = True
            session['visits'] = 1
            return redirect( url_for('user', username=username) )
        else:
            flash('login incorrect. Try again or join')
            return redirect( url_for('index'))
    except Exception as err:
        flash('form submission error '+str(err))
        return redirect( url_for('index') )

#route for administrator log in
@app.route('/loginA/', methods=["POST"])
def loginA():
    try:
        username = request.form['username']
        passwd = request.form['password']
        conn = dbi.connect()
        curs = dbi.dict_cursor(conn)
        curs.execute('''SELECT username,password
                      FROM admin
                      WHERE username = %s''',
                     [username])
        row = curs.fetchone()
        if row is None:
            # Same response as wrong password,
            # so no information about what went wrong
            flash('login incorrect. Try again or join')
            return redirect( url_for('index'))
        hashed = row['password']
        hashed2 = bcrypt.hashpw(passwd.encode('utf-8'),hashed.encode('utf-8'))
        hashed2_str = hashed2.decode('utf-8')
        if hashed2_str == hashed:
            flash('successfully logged in as '+username)
            session['username'] = username
            session['logged_in'] = True
            session['visits'] = 1
            return redirect( url_for('user', username=username) )
        else:
            flash('login incorrect. Try again or join')
            return redirect( url_for('index'))
    except Exception as err:
        flash('form submission error '+str(err))
        return redirect( url_for('index') )



#log out route
@app.route('/logout/')
def logout():
    try:
        if 'username' in session:
            username = session['username']
            session.pop('username')
            session.pop('logged_in')
            flash('You are logged out')
            return redirect(url_for('index'))
        else:
            flash('you are not logged in. Please login or join')
            return redirect( url_for('index') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('index') )

@app.route('/shifts/', methods=['GET'])
def shifts():
    if request.method == 'GET':
        conn = dbi.connect()
        info = database.available(conn)
        return render_template('available_shifts.html', title='Available Shifts', shifts=info, conn=conn)

@app.route('/grabShift/', methods=["GET",'POST'])
def grabShift():
    conn = dbi.connect()
    shift = request.form.get('shiftid')
    try:
        if 'username' in session:
            username = session['username']
            data = database.changeOwnershipCovered(conn,shift,username)
            flash(str("Shift Grabbed by " + username))
            return redirect( url_for('shifts') )
        else:
            flash('you are not logged in. Please login or join to grab shifts')
            return redirect( url_for('index') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('index') )
    
    
@app.route('/inputSchedule/', methods=["GET","POST"])
def inputSchedule():
    employee_ID = request.form.get('employee')
    submit = request.form.get('submit')
    day = request.form.get('day')
    time = str(request.form.get('time'))
    permanent = 1
    if submit == "process form":
        conn = dbi.connect()
        #print(employee_ID)
        exists = helper.shiftExists(conn,permanent,day,time,employee_ID)
        if exists == True:
            flash('This shift already exists!')
        else:
            conn = dbi.connect()
            data = helper.insertShift(conn,permanent,day,time,employee_ID)

    conn = dbi.connect()
    data = helper.getAllEmployees(conn)
    return render_template('inputSchedule.html', list = data)

@app.route('/input_availability/', methods=["GET","POST"])
def input_availability():
    employee_ID = request.form.get('employee')
    submit = request.form.get('submit')
    day = request.form.get('day')
    time = str(request.form.get('time'))
    #need to add in code to insert data into a table, see Alexandra's code as example
    conn = dbi.connect()
    data = helper.getAllEmployees(conn)

    return render_template('input_availability.html', list=data)

@app.route('/request_coverage/', methods=["GET","POST"])
def request_coverage():
    employee_ID = request.form.get('employee')
    submit = request.form.get('submit')
    day = request.form.get('day')
    time = str(request.form.get('time'))
    #need to add in code to insert data into a table, see Alexandra's code as example
    conn = dbi.connect()
    data = helper.getAllEmployees(conn)
    return render_template('request_coverage.html', list=data)

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        #port = 7907 #Bianca's port
        port = os.getuid()
    # the following database code works for both PyMySQL and SQLite3
    dbi.cache_cnf()
    dbi.use('findasubstitute_db')
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    # the following query works for both MySQL and SQLite
    curs.execute('select current_timestamp as ct')
    row = curs.fetchone()
    ct = row['ct']
    print('connected to findasubstitute_db at {}'.format(ct))
    print('connected to FindASubstitute at {}'.format(ct))
    app.debug = True
    app.run('0.0.0.0',port)
