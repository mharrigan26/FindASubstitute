'''This example implements file upload to the filesystem'''

from flask import (Flask, render_template, make_response, request, redirect,
                   url_for, session, flash, send_from_directory, Response)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import sys, os, random
import imghdr
import cs304dbi as dbi

app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

# new for file upload
app.config['UPLOADS'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1*1024*1024 # 1 MB

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/pic/<nm>')
def pic(nm):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    numrows = curs.execute(
        '''select filename from picfile where nm = %s''',
        [nm])
    if numrows == 0:
        flash('No picture for {}'.format(nm))
        return redirect(url_for('index'))
    row = curs.fetchone()
    return send_from_directory(app.config['UPLOADS'],row['filename'])

    
@app.route('/pics/')
def pics():
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute('''select nm,name,filename
                    from picfile inner join person using (nm)''')
    pics = curs.fetchall()
    return render_template('all_pics.html',n=len(pics),pics=pics)

@app.route('/upload/', methods=["GET", "POST"])
def file_upload():
    if request.method == 'GET':
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
                                   nm=nm)
        except Exception as err:
            flash('Upload failed {why}'.format(why=err))
            return render_template('form.html',src='',nm='')
            

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    dbi.cache_cnf()
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute('select database() as db')
    row = curs.fetchone()
    db = row['db']
    print('connected to database {}'.format(db))
    app.debug = True
    app.run('0.0.0.0',port)
