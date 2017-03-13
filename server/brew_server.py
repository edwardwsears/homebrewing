##TO RUN:
## %> . venv/bin/activate
## %>  python brew_server.py
##

#imports
from flask import Flask, url_for, render_template, request, session, g, redirect, abort, flash, jsonify
import sqlite3
import flask_sijax
import os
from datetime import datetime
from decimal import *
from pytz import timezone

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

@flask_sijax.route(app, '/brewing/on_tap.html')
def serve_page_brewing_on_tap():
    def update_beers_left_handler(obj_response):
        beerOnTap = db_execute("select name,style from brews where on_tap=1")
        kegData = db_execute("SELECT * FROM keg where name=\"" + beerOnTap[0]['name'] + "\"")
        beersLeft = int(kegData[0]['current_volume'] / 16)
        beersLeftString = "Beers Left: " + str(beersLeft)
        obj_response.html("#beers_left",beersLeftString)

    def update_oz_left_handler(obj_response):
        beerOnTap = db_execute("select name,style from brews where on_tap=1")
        kegData = db_execute("SELECT * FROM keg where name=\"" + beerOnTap[0]['name'] + "\"")
        beersLeft = int(kegData[0]['current_volume'] / 16)
        ozLeftString =  str(kegData[0]['current_volume']) + "/" + str(kegData[0]['total_volume']) + " fl oz"
        obj_response.html("#oz_left",ozLeftString)

    def update_beers_left_pic_handler(obj_response):
        beerOnTap = db_execute("select name,style from brews where on_tap=1")
        kegData = db_execute("SELECT * FROM keg where name=\"" + beerOnTap[0]['name'] + "\"")
        beersLeft = float(kegData[0]['current_volume'])
        totalBeers = float(kegData[0]['total_volume'])
        beersLeftPercent = (beersLeft/totalBeers)*100;
        if (beersLeftPercent == 0):
            img_name = "images/keg/0.png";
        elif (beersLeftPercent <= 10):
            img_name = "images/keg/10.png";
        elif (beersLeftPercent <= 25):
            img_name = "images/keg/25.png";
        elif (beersLeftPercent <= 50):
            img_name = "images/keg/50.png";
        elif (beersLeftPercent <= 75):
            img_name = "images/keg/75.png";
        elif (beersLeftPercent <= 100):
            img_name = "images/keg/100.png";
        img_src = url_for('static', filename=img_name)
        obj_response.attr("#keg_pic","src",img_src);

    def update_bottles_left_handler(obj_response,bottleId,size,value):
        #update value
        bottleSizeName = "num_bottles_" + str(size) + "oz"
        currentBottles = db_execute("SELECT "+bottleSizeName+" FROM bottles where id=\"" + str(bottleId) + "\"")
        nextBottles = currentBottles[0][bottleSizeName] + value
        if (nextBottles<0):
            nextBottles = 0
        print("current: "+str(currentBottles[0][bottleSizeName])+" next: "+str(nextBottles))
        db_execute("update bottles set "+bottleSizeName+"="+str(nextBottles)+" where id=\"" + str(bottleId) + "\"")
        #display new value
        idName = "#brew_" + str(bottleId) + "_bottles_left_" +str(size)+"oz"
        nextBottlesStr = str(size)+"oz: "+str(nextBottles);
        obj_response.html(idName,nextBottlesStr)

    def update_keg_stats_handler(obj_response):
        beerOnTap = db_execute("select name,style from brews where on_tap=1")
        kegData = db_execute("SELECT * FROM keg where name=\"" + beerOnTap[0]['name'] + "\"")
        kegStatsString = ""

        #days since tap
        daysSinceTap = (datetime.now() - datetime.strptime(kegData[0]['tap_date'],"%Y-%m-%d")).days
        daysSinceTapString = "Days Since Tap: "+str(daysSinceTap)
        kegStatsString +=  daysSinceTapString + "<br>"

        #Average consumption
        totalOzConsumed = kegData[0]['total_volume'] - kegData[0]['current_volume']
        ozPerDayConsumed = Decimal(totalOzConsumed)/Decimal(daysSinceTap)
        beersPerDayConsumed = ozPerDayConsumed/16
        beersPerDayString = "Average beers/day: "
        beersPerDayString += str(round(beersPerDayConsumed,2))
        beersPerDayString += " ("+str(round(ozPerDayConsumed,2))+"oz)"
        kegStatsString +=  beersPerDayString + "<br>"

        # Est empty date
        daysUntilEmpty = int(kegData[0]['current_volume']/ozPerDayConsumed)
        daysUntilEmptyString = "Est Days Until Empty: "+str(daysUntilEmpty)
        kegStatsString +=  daysUntilEmptyString + "<br>"
        daysUntilBrewString = "Need to Brew in: "+str(daysUntilEmpty-14)+" days"
        kegStatsString +=  daysUntilBrewString + "<br>"

        obj_response.html("#keg_stats",kegStatsString)

    def update_last_pour_stats_handler(obj_response):
        beerOnTap = db_execute("select name,style from brews where on_tap=1")
        kegData = db_execute("SELECT * FROM keg where name=\"" + beerOnTap[0]['name'] + "\"")
        lastPourString = ""

        lastPourString += "Last pour: <br>"
        lastPourString += str(kegData[0]['last_pour_volume']) + " oz <br>"
        lastPourString += "at " + datetime_to_string(datetime_pst(datetime_from_sqlite(kegData[0]['last_pour_time'])))

        obj_response.html("#last_pour_stats",lastPourString)

    if g.sijax.is_sijax_request:
        # Sijax request detected - let Sijax handle it
        g.sijax.set_request_uri('/brewing/on_tap.html')
        g.sijax.register_callback('update_beers_left', update_beers_left_handler)
        g.sijax.register_callback('update_oz_left', update_oz_left_handler)
        g.sijax.register_callback('update_beers_left_pic', update_beers_left_pic_handler)
        g.sijax.register_callback('update_bottles_left', update_bottles_left_handler)
        g.sijax.register_callback('update_keg_stats', update_keg_stats_handler)
        g.sijax.register_callback('update_last_pour_stats', update_last_pour_stats_handler)
        return g.sijax.process_request()

    beerOnTap = db_execute("select name,style,brew_date,description,og,abv,ibu from brews where on_tap=1")
    kegData = db_execute("SELECT * FROM keg where name=\"" + beerOnTap[0]['name'] + "\"")
    bottleData = db_execute("SELECT * FROM bottles")
    brewData = db_execute("SELECT * FROM brews")

    return render_template('brewing/on_tap.html', beerOnTap=beerOnTap[0], kegData=kegData[0],bottleData=bottleData,brewData=brewData)

@app.route('/brewing/update_tap.html',methods=['POST'])
def serve_page_brewing_update_tap():
    ozPoured = request.form['oz_poured']
    beerOnTap = db_execute("select name,style from brews where on_tap=1")
    kegData = db_execute("SELECT * FROM keg where name=\"" + beerOnTap[0]['name'] + "\"")

    newVolume = kegData[0]['current_volume'] - int(ozPoured)
    if (newVolume < 0):
        newVolume = 0

    db_execute("update keg set current_volume="+str(newVolume)+" where name=\"" + beerOnTap[0]['name'] + "\"")
    db_execute("update keg set last_pour_volume="+str(ozPoured)+" where name=\"" + beerOnTap[0]['name'] + "\"")
    db_execute("update keg set last_pour_time=DateTime('now') where name=\"" + beerOnTap[0]['name'] + "\"")
    return jsonify(result=True)

@app.route('/brewing/fermenting.html')
def serve_page_brewing_fermenting():
    brewName = db_execute("SELECT name FROM brews WHERE fermenting=1")
    if (len(brewName)==1):
        return render_template('brewing/fermenting.html', name=brewName[0])
    else:
        return render_template('brewing/fermenting.html', name="Nothing")

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
    queryData = cur.fetchall()
    g.db.commit()
    return queryData

def datetime_pst(dt):
    # convert nieve to pacific
    dt_utc = dt.replace(tzinfo=timezone('UTC'))
    return dt_utc.astimezone(timezone('US/Pacific'))

def date_from_sqlite(dt):
    return datetime.strptime(dt,"%Y-%m-%d")

def datetime_from_sqlite(dt):
    return datetime.strptime(dt,"%Y-%m-%d %H:%M:%S")

def datetime_to_string(dt):
    return dt.strftime("%Y-%m-%d %I:%M:%S %p")

#to run the application
if __name__ == '__main__':
    app.run(debug=DEBUG,host='0.0.0.0')
