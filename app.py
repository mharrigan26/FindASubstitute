
from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify, Response)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import cs304dbi as dbi
import database
import random
import helper
import os
import bcrypt

# for thread safety
from threading import Lock

grablock = Lock()

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
            conn = dbi.connect()
            isAdmin = database.isAdmin(conn,username)
            return render_template('greet.html',
                                   page_title='Find A Substitute: Welcome {}'.format(username),
                                   name=username, isAdmin = isAdmin)
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
        if 'username' in session:
            username = session['username']
            session['visits'] = 1+int(session['visits'])
            conn = dbi.connect()
            isAdmin = database.isAdmin(conn,username)
            return render_template('greet.html',
                                   page_title='My App: Welcome {}'.format(username),
                                   name=username, isAdmin = isAdmin)
        else:
            flash('you are not logged in. Please login or join')
            return redirect( url_for('index') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('index') )


#page for employee's to view and update their worker profile
@app.route('/profile/', methods=["GET", "POST"])
def profile():
    try:
        if 'username' in session:
            employee_ID = session['username']
        else:
            flash('you are not logged in. Please login or join to view your profile')
            return redirect( url_for('index') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('index') )
    conn = dbi.connect()
    if request.method == 'GET':
        username1 = session['username']
        isAdmin = database.isAdmin(conn,username1)
        info = database.lookupEmployee(conn, username1)
        name = info['name']
        pronouns = info['pronouns']
        curs.execute('''select username,name,filename
                    from picfile1 inner join employee1 using (username) where username = %s''', [username1])
        pics = curs.fetchall()
        return render_template('profile.html', name=name, 
        username=username1, pronouns=pronouns, title='User Profile',isAdmin = isAdmin, pics=pics)
    
    if request.method == 'POST':
        username1 = session['username']
        pronouns = request.form.get("pronouns")
        if(pronouns == "other"):
            pronouns = request.form.get("other_pronouns")
        database.updateEmployeeProfile(conn, pronouns, username1)
        flash('profile updated')
        return redirect(url_for('profile'))

@app.route('/pic/<username>')
def pic(username):
    username1 = session['username']
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    numrows = curs.execute(
        '''select filename from picfile1 where username = %s''',
        [username1])
    if numrows == 0:
        flash('No picture for {}'.format(nm))
        return redirect(url_for('index'))
    row = curs.fetchone()
    return send_from_directory(app.config['UPLOADS'],row['filename'])

@app.route('/upload/', methods=["POST"])
def upload():
    if request.method == 'POST': #if they are uploading a new picture
        try:
            
            username2 = session['username']
            f = request.files['pic']
            user_filename = f.filename
            ext = user_filename.split('.')[-1]
            filename = secure_filename('{}.{}'.format(username2,ext))
            pathname = os.path.join(app.config['UPLOADS'],filename)
            f.save(pathname)
            curs = dbi.dict_cursor(conn)
            curs.execute(
                '''insert into picfile1(username,filename) values (%s,%s)
                on duplicate key update filename = %s''',
                [username2, filename, filename])
            conn.commit()
            flash('Upload successful')
            return redirect(url_for('profile'))
        except Exception as err:
            flash('Upload failed {why}'.format(why=err))
            return render_template('profile.html',src='',nm='')


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

#route for seeing all currently available shifts
@app.route('/shifts/', methods=['GET'])
def shifts():
    if request.method == 'GET':
        try:
            if 'username' in session:
                employee = session['username']
                conn = dbi.connect()
                info = database.available(conn)
                covered = database.shiftEmployeeisCovering(conn,employee)
                return render_template('available_shifts.html', title='Available Shifts', shifts=info, conn=conn,covered = covered)
            else:
                flash('you are not logged in. Please login or join to grab shifts')
                return redirect( url_for('index') )
        except Exception as err:
            flash('some kind of error '+str(err))
            return redirect( url_for('index') )
#route to pick up a shift
@app.route('/grabShift/', methods=["GET",'POST'])
def grabShift():
    conn = dbi.connect()
    shift = request.form.get('shiftid')
    try:
        if 'username' in session:
            grablock.acquire()
            username = session['username']
            isCovered = database.isCovered(conn,shift)
            if isCovered:
                flash("This shift is already covered")
                grablock.release()
                return redirect( url_for('shifts') )
            else:
                data = database.changeOwnershipCovered(conn,shift,username)
                flash(str("Shift Grabbed by " + username))
                grablock.release()
                return redirect( url_for('shifts') )
        else:
            flash('you are not logged in. Please login or join to grab shifts')
            return redirect( url_for('index') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('index') )

#route for all admin functions page
@app.route('/adminfunctions/', methods=["GET","POST"])
def adminfunctions():
    try:
        if 'username' in session:
            if request.method == "GET":
                conn = dbi.connect()
                data = helper.getAllEmployees(conn)
                info = database.available(conn)
                availablities = database.findAllAvailabilities(conn)
                master = database.getAllShifts(conn)
                return render_template('adminFunctions.html', list = data, shifts = info, 
                available= availablities,master = master )
            if request.method == "POST":
                employee_ID = request.form.get('employee')
                submit = request.form.get('submit')
                if submit == 'delete':
                    grablock.acquire()
                    conn = dbi.connect()
                    database.deleteEmployee(conn,employee_ID)
                    grablock.release()
                    flash("Employee " + employee_ID + " deleted")
                    return redirect(url_for('adminfunctions'))
        else:
            flash('you are not logged in. Please login or join to use admin functions')
            return redirect( url_for('index') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('index') )
    
       
    
#input schedule route
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

#route to input shifts you are available for
@app.route('/input_availability/', methods=["GET","POST"])
def input_availability():
    try:
        if 'username' in session:
            username = session['username']
        else:
            flash('you are not logged in. Please login or join to input availability')
            return redirect( url_for('index') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('index') )
    if request.method == "POST":
        submit = request.form.get('submit')
        day = request.form.get('day')
        start_time = str(request.form.get('start_time'))
        end_time = str(request.form.get('end_time'))
        conn = dbi.connect()
        database.insertAvailability(conn,username, start_time, end_time, day)
        flash("availability updated")
        return render_template('input_availability.html')
    else:
        return render_template('input_availability.html')

#route to request coverage of a shift
@app.route('/request_coverage/', methods=["GET","POST"])
def request_coverage():
    conn = dbi.connect()

    try:
        if 'username' in session:
            employee_ID = session['username']
        else:
            flash('you are not logged in. Please login or join to grab shifts')
            return redirect( url_for('index') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('index') )


    if request.method == 'GET':
        data = helper.getAllEmployees(conn)
        info = database.getSpecEmployeeShifts(conn, employee_ID)
        length = len(info)
        return render_template('request_coverage.html', shifts = info, length = length)
    else:
        shift = request.form.get('shiftid')
        print (shift)
        print(employee_ID)
        database.requestCoverage(conn, employee_ID, shift)
        flash('You have successfully requested coverage')
        return render_template('request_coverage.html')

#route to search for the shifts of a specific person        
@app.route('/search/', methods=["GET", "POST"])
def search():
    try:
        if 'username' in session:
            employee_ID = session['username']
        else:
            flash('you are not logged in. Please login or join to grab shifts')
            return redirect( url_for('index') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('index') )

    if request.method == "GET":
        return render_template('search.html', title="Search by Employee")
    else:
        conn = dbi.connect()
        if (request.form.get('employee-username') == ""):
            flash('Please submit a non-empty form.')
            return render_template('search.html', title="Search by Employee")
        else:
            username = request.form.get('employee-username')
            existence = database.usernameAvailability(conn, username)
            if existence:
                return redirect(url_for('usershifts', username=username))
            else:
                flash("Employee does not exist.")
                return render_template('search.html')

@app.route('/usershifts/<username>', methods=["GET"])
def usershifts(username):
    try:
        if 'username' in session:
            employee_ID = session['username']
        else:
            flash('you are not logged in')
            return redirect( url_for('index') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('index') )

    conn = dbi.connect()
    info = database.getSpecEmployeeShifts(conn, username)
    return render_template('user_shifts.html', shifts=info, username=username)

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

