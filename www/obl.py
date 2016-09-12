#!/usr/bin/env python
# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from datetime import datetime, timedelta
import math
import alsaaudio

try:
    from configparser import SafeConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser

try:
    from IPython.core.debugger import Tracer
except:
    pass

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

# Load the config file and import settings
parser = SafeConfigParser()
parser.read('../conf/settings.conf')
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, '../db/obl.sqlite'),
    SECRET_KEY=parser.get('www', 'secret_key'),
    GOOGLE_TRACKING_ID=parser.get('www', 'google_tracking_id'),
))






def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv









def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()








@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')










def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db









@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()











@app.route('/', methods=['GET'])
def show_plots():
 
    # define how many hours the plot should cover
    if request.args.get('hours'):
        try:
            hours = int(request.args.get('hours'))
        except:
            # if there is text, 'all' in this case
            hours = get_hours_since_oldest_entry()
    else:
        hours = 24
    
    # get the sound data
    sound = get_data_points(hours, 'sound')

    # get the motion data
    motion = get_data_points(hours, 'motion')

    # Tracer()()

    return render_template('show_plots.html', sound=sound, motion=motion)









@app.route('/settings', methods=['POST', 'GET'])
def settings():

    error = []

    # get the current settings
    parser = SafeConfigParser()
    parser.read('../conf/settings.conf')

    # handle posted data
    if request.method == 'POST':
        error += validate_settings_post(request.form, parser)
        
        if not error:
            flash('Settings saved successfully!')
            return redirect(url_for('settings'))

    # get the valid sound devices
    sound_devices = get_valid_sound_devices()
    return render_template('settings.html', settings=parser._sections, sound_devices=sound_devices, error=error)









@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_plots'))










@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_plots'))
    return render_template('login.html', error=error)









@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_plots'))













def get_data_points(hours, table):

    # connect to db
    db = get_db()
    
    # get all logged sound from the last N hours
    window_start_point_dt = datetime.now()-timedelta(hours=hours)
    window_start_point_str = window_start_point_dt.strftime('%Y,%m,%d,%H,%M,%S')
    cur = db.execute('select start,end,intensity from %s where end > "%s"' % (table, window_start_point_str))
    data_points = []

    # add start point
    
    data_points.append(['new Date(%s)' % window_start_point_str, 0])

    for row in cur.fetchall():

        # convert to datetime
        start_dt = datetime.strptime(row['start'], '%Y,%m,%d,%H,%M,%S')
        end_dt = datetime.strptime(row['end'], '%Y,%m,%d,%H,%M,%S')

        # adjust start if it is before the start of the requested interval
        if row['start'] < window_start_point_str:
            start_dt = window_start_point_dt
        
        # pad interval with zeroes
        data_points.append([(start_dt-timedelta(seconds=1)).strftime('new Date(%Y,%m,%d,%H,%M,%S)'), 0])

        # add interval
        data_points.append(['new Date(%s)' % row['start'], row['intensity']])
        data_points.append(['new Date(%s)' % row['end'] , row['intensity']])

        # pad interval with zeroes
        data_points.append([(end_dt+timedelta(seconds=1)).strftime('new Date(%Y,%m,%d,%H,%M,%S)'), 0])

    # add end point
    data_points.append([datetime.now().strftime('new Date(%Y,%m,%d,%H,%M,%S)'), 0])

    return data_points
    





def get_hours_since_oldest_entry():

    # get the oldest entries
    db = get_db()
    cur = db.execute('select min(start) from sound')
    first_logged_sound = datetime.strptime(cur.fetchone()['min(start)'], '%Y,%m,%d,%H,%M,%S')
    cur = db.execute('select min(start) from motion')
    first_logged_motion = datetime.strptime(cur.fetchone()['min(start)'], '%Y,%m,%d,%H,%M,%S')

    # return the number of hours since the oldest entry
    td = datetime.now()-min(first_logged_sound, first_logged_motion)
    return math.ceil(td.days*24 + td.seconds/3600)






def get_valid_sound_devices():

    available_cards = alsaaudio.cards()
    if available_cards:
        return available_cards

    return ["No audio devices found."]





def validate_settings_post(form, parser):

    return []
