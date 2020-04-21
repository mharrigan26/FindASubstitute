from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite
import cs304dbi as dbi
#import cs304dbi_sqlite3 as dbi
import database
import random

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
    return render_template('main.html',title='Find A Substitute')

@app.route('/profile/', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        conn = dbi.connect()
        if (request.form.get('name') == ""):
            flash("missing input: Name is missing")
        if (request.form.get('username') == ""):
            flash("missing input: Username is missing")
        if (request.form.get('password') == ""):
            flash("missing input: Password is missing")
        if (request.form.get('email') == ""):
            flash("missing input: Email is missing")
        else:
            name = request.form.get('name')
            username = request.form.get('username')
            password = request.form.get('password')
            email = request.form.get('email')
            username_exists = database.usernameAvailability(conn, username)
            email_exists = database.emailAvailability(conn, email)
            if username_exists:
                flash('Username already exists')
            if email_exists:
                flash('Email already has an account set up')
            else:
                database.insertEmployee(conn, name, username, email, password)
                return redirect(url_for('person_temp', username = username))
        return(render_template('profile.html'))
    else: #if GET
        return render_template('profile.html', title='Create a profile')

@app.route('/person_temp/<username>', methods=['GET'])
def person_temp(username):
    conn = dbi.connect()
    info = database.lookup(conn, username)
    name = info['name']
    password = info['password']
    email = info['email']
    return render_template('person.html', title='Person', name = name, password = password, username =username, email = email )

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
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
    print('connected to FindASubstitute at {}'.format(ct))
    app.debug = True
    app.run('0.0.0.0',port)
