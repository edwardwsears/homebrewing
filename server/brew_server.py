##TO RUN:
## %> . venv/bin/activate
## %>  python brew_server.py
##

#imports
from flask import Flask, url_for, render_template, request, session, g, redirect, abort, flash
import sqlite3
import flask_sijax
import os

#config
DATABASE='brew_server.sql'
DEBUG=True
SECRET_KEY='key'
USERNAME='esears'
PASSWORD='esears'

path = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')

app = Flask(__name__)
# can put the config into a file
#BREW_SERVER_SETTINGS= <filename>
#app.config.from_envvar('BREW_SERVER_SETTINGS', silent=True)
app.config.from_object(__name__)
app.config['SIJAX_STATIC_PATH'] = path
app.config['SIJAX_JSON_URI'] = '/static/js/sijax/json2.js'
flask_sijax.Sijax(app)


def connect_db():
    con = sqlite3.connect(DATABASE)
    con.row_factory = sqlite3.Row
    return con

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
      db.close()

@app.route('/')
@app.route('/index.html')
def serve_page_index():
    return render_template('index.html',)

##@app.route('/brewing/on_tap.html')
@flask_sijax.route(app, '/brewing/on_tap.html')
def serve_page_brewing_on_tap():
    def update_beers_left_handler(obj_response):
        beerOnTap = db_execute("select name,style from brews where on_tap=1")
        kegData = db_execute("SELECT * FROM keg where name=\"" + beerOnTap[0]['name'] + "\"")
        beersLeft = int(kegData[0]['current_volume'] / 16)
        beersLeftString = "Beers Left: " + str(beersLeft)
        obj_response.html("#beersLeft",beersLeftString)

    def update_beers_left_percent_handler(obj_response):
        beerOnTap = db_execute("select name,style from brews where on_tap=1")
        kegData = db_execute("SELECT * FROM keg where name=\"" + beerOnTap[0]['name'] + "\"")
        beersLeft = float(kegData[0]['current_volume'])
        totalBeers = float(kegData[0]['total_volume'])
        beersLeftPercent = (beersLeft/totalBeers)*100;
        print("beersLeftPercent: "+str(totalBeers)+"\n")
        scriptStr = " var skillBar = $('#level'); $(skillBar).animate({ height: "+str(beersLeftPercent)+" }, 1500); "
        obj_response.script(scriptStr);

    if g.sijax.is_sijax_request:
        # Sijax request detected - let Sijax handle it
        g.sijax.set_request_uri('/brewing/on_tap.html')
        g.sijax.register_callback('update_beers_left', update_beers_left_handler)
        g.sijax.register_callback('update_beers_left_percent', update_beers_left_percent_handler)
        return g.sijax.process_request()

    beerOnTap = db_execute("select name,style from brews where on_tap=1")
    kegData = db_execute("SELECT * FROM keg where name=\"" + beerOnTap[0]['name'] + "\"")
    bottleData = db_execute("SELECT * FROM bottles")
    brewData = db_execute("SELECT * FROM brews")

    return render_template('brewing/on_tap.html', kegData=kegData[0],bottleData=bottleData,brewData=brewData)

@app.route('/brewing/fermenting.html')
def serve_page_brewing_fermenting():
    brewName = db_execute("SELECT name FROM brews WHERE fermenting=1")
    return render_template('brewing/fermenting.html', name=brewName[0])

@app.route('/brewing/brews.html')
def serve_page_brewing_brews():
    return render_template('brewing/brews.html',)

@app.route('/brewing/brew_tech.html')
def serve_page_brewing_brew_tech():
    return render_template('brewing/brew_tech.html',)

@app.route('/brewing/add_brew.html',methods=['GET', 'POST'])
def serve_page_brewing_add_brew():
    if not session.get('logged_in'):
      return render_template('brewing/login.html',)
    else:
      print "BEFORE POST\n";
      print "request.method: " + request.method
      if request.method == 'GET':
        null=1; ##do nothing
      elif request.method == 'POST':
        print "IN POST\n";
        ##g.db.execute('insert into brews (name, style, brew_date, in_bottles, on_tap, fermenting) values (?, ?, ?, ?, ?, ?)',["IPA 3", "IPA","2012-1-1",0,0,1])
        g.db.execute('insert into brews (name, style, brew_date, in_bottles, on_tap, fermenting) values (?, ?, ?, ?, ?, ?)',[request.form['brew-name'], request.form['brew-type'],request.form['brew-date'],0,0,1])
        print "IN POST 2\n";
        g.db.commit()
        print "IN POST 3\n";
        flash('New entry was successfully posted')
        print "IN POST 4\n";
      return render_template('brewing/add_brew.html',)

@app.route('/brewing/login.html', methods=['GET', 'POST'])
def serve_page_brewing_login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
            flash('Invalid username')
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
            flash('Invalid password')
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('serve_page_brewing_add_brew'))
    return render_template('brewing/login.html', error=error)

@app.route('/brewing/logout')
def brewing_logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('serve_page_brewing_login'))

### Helper fns #######################
def db_execute(query):
    cur = g.db.execute(query)
    #for row in cur.fetchall():
    #  queryData=row
    queryData = cur.fetchall()
    return queryData


#to run the application
if __name__ == '__main__':
    app.run(debug=DEBUG)
