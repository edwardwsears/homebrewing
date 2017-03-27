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
localTest = False;
if (localTest):
    DATABASE='brew_server.sql'
else:
    DATABASE='/home/ubuntu/homebrewing/server/brew_server.sql'

DEBUG=True
SECRET_KEY='key'
USERNAME='sears'
PASSWORD='beers'

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
    beerOnTap = db_execute("select name,style,brew_date,description,og,abv,ibu from brews where on_tap=1")
    kegData = db_execute("SELECT * FROM keg where name=\"" + beerOnTap[0]['name'] + "\"")
    bottleData = db_execute("SELECT * FROM bottles")
    brewData = db_execute("SELECT * FROM brews")
    tempList = db_execute("SELECT * FROM temperatures ORDER BY datetime(timestamp) desc limit 1")

    return render_template('/index.html', beerOnTap=beerOnTap[0], kegData=kegData[0],bottleData=bottleData,brewData=brewData, tempList=tempList)

@flask_sijax.route(app, '/on_tap.html')
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
        daysSinceTap = (datetime.now() - datetime.strptime(kegData[0]['tap_date'],"%Y-%m-%d")).days + 1
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
        if (ozPerDayConsumed>0):
            daysUntilEmpty = int(kegData[0]['current_volume']/ozPerDayConsumed)
            daysUntilEmptyString = "Est Days Until Empty: "+str(daysUntilEmpty)
            kegStatsString +=  daysUntilEmptyString + "<br>"
            daysUntilBrewString = "Need to Brew in: "+str(daysUntilEmpty-14)+" days"
            kegStatsString +=  daysUntilBrewString + "<br>"
        else:
            daysUntilEmptyString = "Est Days Until Empty: &#x221e;"
            kegStatsString +=  daysUntilEmptyString + "<br>"
            daysUntilBrewString = "Need to Brew in: &#x221e; days"
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
        g.sijax.set_request_uri('/on_tap.html')
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

    return render_template('/on_tap.html', beerOnTap=beerOnTap[0], kegData=kegData[0],bottleData=bottleData,brewData=brewData)

@app.route('/update_tap.html',methods=['POST'])
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

@flask_sijax.route(app, '/fermenting.html')
def serve_page_brewing_fermenting():
    def update_ferm_temp_handler(obj_response):
        tempList = db_execute("SELECT * FROM temperatures ORDER BY datetime(timestamp) desc")
        tempDatetimeStr = datetime_to_string(datetime_pst(datetime_from_sqlite(tempList[0]['timestamp'])))
        tempString = "Latest Fermentation Temperature: <br>"+str(tempList[0]['temperature'])+"&degF at "+tempDatetimeStr
        obj_response.html("#latest_temp",tempString)

    if g.sijax.is_sijax_request:
        # Sijax request detected - let Sijax handle it
        g.sijax.set_request_uri('/fermenting.html')
        g.sijax.register_callback('update_ferm_temp', update_ferm_temp_handler)
        return g.sijax.process_request()

    if request.method == 'POST':
        g.db.execute('update chamber set set_temp = ?',[request.form['set_temp']])
        g.db.execute('update chamber set set_range = ?',[request.form['set_range']])
        if (request.form['temp_control_on'] == "On"):
            temp_control_num = 1
        else:
            temp_control_num = 0
        g.db.execute('update chamber set temp_control_on = ?',[temp_control_num])
        flash('Temp Changed')

    brewName = db_execute("SELECT name FROM brews WHERE fermenting=1")
    tempList = db_execute("SELECT * FROM temperatures ORDER BY datetime(timestamp) desc limit 96")
    fermStats = db_execute("SELECT * FROM chamber")
    formattedTempList = []
    for temp in tempList:
        dt_temp = datetime_from_sqlite(temp['timestamp'])
        formattedTempList.append({'year':int(dt_temp.year),'month':int(dt_temp.month),'day':int(dt_temp.day),'hour':int(dt_temp.hour) ,'minute':int(dt_temp.minute) ,'temp':temp['temperature']})
    if (len(brewName)==1):
        return render_template('fermenting.html', name=brewName[0], tempList=formattedTempList, fermStats=fermStats)
    else:
        return render_template('fermenting.html', name="Nothing", tempList=formattedTempList, fermStats=fermStats)

@app.route('/update_temp.html',methods=['POST'])
def serve_page_brewing_update_temp():
    first = request.form['first']
    temp = request.form['temp']

    if (first==True):
        #clear table
        db_execute("delete from temperatures;")

    # add temp
    db_execute("insert into temperatures values(CURRENT_TIMESTAMP,"+str(temp)+");")
    return jsonify(result=True)

@flask_sijax.route(app, '/brews.html')
def serve_page_brewing_brews():
    def update_display_recipe_handler(obj_response,id):
        displayBrew = db_execute("SELECT * FROM brews where id="+str(id))
        scriptStr = """
            $("#statTable").html("\
            <table class='pure-table pure-table-bordered'>\
                <thead>\
                    <tr>\
                        <th>Beer Stats </th>\
                    </tr>\
                </thead>\
                <tbody>\
                    <tr>\
                        <td >\
                            <h1> """+displayBrew[0]['name']+""" </h1>\
                            <h4>\
                                """+displayBrew[0]['description']+"""\
                            </h4>\
                            <h4>\
                                Style: """+displayBrew[0]['style']+""" <br>\
                                OG: """+displayBrew[0]['og']+""" <br>\
                                ABV: """+displayBrew[0]['abv']+""" <br>\
                                IBU: """+displayBrew[0]['ibu']+""" <br>\
                                Brew Date: """+displayBrew[0]['brew_date']+"""\
                            </h4>\
                        </td>\
                    </tr>\
                </tbody>\
            </table>\
            ");
            // scroll
            $('html, body').animate({
                scrollTop: $('#statTable').offset().top
            }, 'slow');
            """
        ########################### BEGIN Grain ###################################
        displayGrain = db_execute("SELECT * FROM grain where id="+str(id)+" order by amount_lbs desc")
        scriptStr += """
            $("#grainTable").html("\
            <br><h3>Grain:</h3>\
            <table class='pure-table pure-table-bordered'>\
                <thead>\
                    <tr>\
                        <th>Grain Type </th>\
                        <th>Amount in Lbs </th>\
                    </tr>\
                </thead>\
                <tbody>\
                """
        for grain in displayGrain:
            scriptStr += """\
                        <tr>\
                            <td> """+grain['type']+"""</td>\
                            <td> """+str(grain['amount_lbs'])+"""</td>\
                        </tr>\
                    """
        scriptStr += """\
                </tbody>\
            </table>\
            ");
            """
        ########################### END HOPS ###################################
        ########################### BEGIN HOPS ###################################
        displayHops = db_execute("SELECT * FROM hops where id="+str(id)+" order by boil_minutes desc")
        scriptStr += """
            $("#hopsTable").html("\
            <br><h3>Hops:</h3>\
            <table class='pure-table pure-table-bordered'>\
                <thead>\
                    <tr>\
                        <th>Hop Type </th>\
                        <th>Amount in oz </th>\
                        <th>Boil Minutes </th>\
                    </tr>\
                </thead>\
                <tbody>\
                """
        for hop in displayHops:
            scriptStr += """\
                        <tr>\
                            <td> """+hop['hop_name']+"""</td>\
                            <td> """+hop['oz_amount']+"""</td>\
                            <td> """+hop['boil_minutes']+"""</td>\
                        </tr>\
                    """
        scriptStr += """\
                </tbody>\
            </table>\
            ");
            """
        ########################### END HOPS ###################################
        ########################### BEGIN yeast ###################################
        displayYeast = db_execute("SELECT * FROM yeast where id="+str(id))
        scriptStr += """
            $("#yeastTable").html("\
            <br><h3>Yeast:</h3>\
            <table class='pure-table pure-table-bordered'>\
                <thead>\
                    <tr>\
                        <th>Yeast Type </th>\
                        <th>Fermentation Temperature </th>\
                    </tr>\
                </thead>\
                <tbody>\
                    <tr>\
            """
        if (len(displayYeast)>0):
            scriptStr += """\
                        <td> """+displayYeast[0]['yeast_type']+"""</td>\
                        <td> """+str(displayYeast[0]['temp'])+"""</td>\
                """
        scriptStr += """\
                </tr>\
            </tbody>\
        </table>\
        ");
        """
        ########################### END YEAST ###################################
        ########################### BEGIN water ###################################
        displayWater = db_execute_arg("SELECT * FROM water where profile_name=?",displayBrew[0]['water_profile'])
        scriptStr += """
            $("#waterTable").html("\
            """
        if (len(displayWater)>0):
            scriptStr += """\
            <br><h3>Water Additions:</h3>\
            <table class='pure-table pure-table-bordered'>\
                <thead>\
                    <tr>\
                    <th></td>\
                    <th></td>\
                    </tr>\
                </thead>\
                <tbody>\
                <tr>\
                    <td>Profile Name</td>\
                    <td> """+displayWater[0]['profile_name']+"""</td>\
                </tr>\
                <tr>\
                    <td>Base Water</td>\
                    <td> """+displayWater[0]['base_water']+"""</td>\
                </tr>\
                <tr>\
                    <td>Baking Soda Addition</td>\
                    <td> """+displayWater[0]['baking_soda']+"""</td>\
                </tr>\
                <tr>\
                    <td>Gypsum Addition</td>\
                    <td> """+displayWater[0]['gypsum']+"""</td>\
                </tr>\
                <tr>\
                    <td>CaCl Addition</td>\
                    <td> """+displayWater[0]['CaCl']+"""</td>\
                </tr>\
                <tr>\
                    <td>Campden Addition</td>\
                    <td> """+displayWater[0]['campden']+"""</td>\
                </tr>\
            </tbody>\
        </table>\
                """
        scriptStr += """\
        ");
        """
        ########################### END YEAST ###################################
        obj_response.script(scriptStr)
    if g.sijax.is_sijax_request:
        # Sijax request detected - let Sijax handle it
        g.sijax.set_request_uri('/brews.html')
        g.sijax.register_callback('update_display_recipe', update_display_recipe_handler)
        return g.sijax.process_request()
    brews = db_execute("SELECT * FROM brews")
    return render_template('brews.html',brews=brews)

@app.route('/brew_tech.html')
def serve_page_brewing_brew_tech():
    return render_template('brew_tech.html',)

@app.route('/add_brew.html',methods=['GET', 'POST'])
def serve_page_brewing_add_brew():
    if not session.get('logged_in'):
      return render_template('login.html',)
    else:
      if request.method == 'GET':
        null=1; ##do nothing
      elif request.method == 'POST':
        ##g.db.execute('insert into brews (name, style, brew_date, in_bottles, on_tap, fermenting) values (?, ?, ?, ?, ?, ?)',["IPA 3", "IPA","2012-1-1",0,0,1])
        #g.db.execute('insert into brews (name, style, brew_date, in_bottles, on_tap, fermenting) values (?, ?, ?, ?, ?, ?)',[request.form['brew-name'], request.form['brew-type'],request.form['brew-date'],0,0,1])
        flash('New entry was successfully posted')
      return render_template('add_brew.html',)

@app.route('/login.html', methods=['GET', 'POST'])
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
            return redirect(url_for('serve_page_index'))
    return render_template('login.html', error=error)

@app.route('/logout.html')
def brewing_logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('serve_page_index'))

### Helper fns #######################
def db_execute(query):
    cur = g.db.execute(query)
    queryData = cur.fetchall()
    g.db.commit()
    return queryData

def db_execute_arg(query,arg):
    cur = g.db.execute(query,[arg])
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
