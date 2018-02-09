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
import time
from decimal import *
from pytz import timezone

#config
localTest = False;
if (localTest):
    DATABASE='db_brew_server.sql'
else:
    DATABASE='/home/ubuntu/homebrewing/server/db_brew_server.sql'

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

#facial recogntion state defines
FACE_STATE_PENDING          = 0
FACE_STATE_RECOGNIZED       = 1
FACE_STATE_NOT_REGISTERED   = 2
FACE_STATE_NO_FACE          = 3


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
    bottleData = db_execute("SELECT * FROM bottles")
    brewData = db_execute("SELECT * FROM brews")
    guestBottles = db_execute("SELECT * FROM guest_bottles")
    tempList = db_execute("SELECT * FROM temperatures ORDER BY datetime(timestamp) desc limit 1")

    return render_template('/index.html', bottleData=bottleData,brewData=brewData, tempList=tempList, guestBottles=guestBottles)

@flask_sijax.route(app, '/on_tap.html')
def serve_page_brewing_on_tap():
    def update_beers_left_handler(obj_response):
        beerOnTap = db_execute("select name, style from brews where on_tap=1")
        if (len(beerOnTap)==0):
            beersLeftString = "Beers Left: 0"
            obj_response.html("#beers_left",beersLeftString)
            return
        kegData = db_execute("SELECT * FROM keg ORDER BY datetime(tap_date) desc")
        beersLeft = int(kegData[0]['current_volume'] / 16)
        beersLeftString = "Beers Left: " + str(beersLeft)
        obj_response.html("#beers_left",beersLeftString)

    def update_oz_left_handler(obj_response):
        kegData = db_execute("SELECT * FROM keg ORDER BY datetime(tap_date) desc")
        beersLeft = int(kegData[0]['current_volume'] / 16)
        ozLeftString =  str(kegData[0]['current_volume']) + "/" + str(kegData[0]['total_volume']) + " fl oz"
        obj_response.html("#oz_left",ozLeftString)

    def update_beers_left_pic_handler(obj_response):
        beerOnTap = db_execute("select name,style from brews where on_tap=1")
        if (len(beerOnTap)==0):
            img_name = "images/keg/0.png";
            img_src = url_for('static', filename=img_name)
            obj_response.attr("#keg_pic","src",img_src);
            return
        kegData = db_execute("SELECT * FROM keg ORDER BY datetime(tap_date) desc")
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

    def add_guest_bottle_handler(obj_response,formData, numBottles):
        #edit db
        dbStr = "insert into guest_bottles values("
        dbStr += " NULL,"
        dbStr += " \""+str(formData['brew-name'])+"\","
        dbStr += " \""+str(formData['brew-style'])+"\","
        dbStr += " \""+str(numBottles)+"\""
        dbStr += " );"
        db_execute(dbStr)
        edit_guest_bottle_table_handler(obj_response)

    def delete_guest_bottle_handler(obj_response, id):
        #edit db
        dbStr = "delete from guest_bottles where "
        dbStr += " id="+str(id)+";"
        db_execute(dbStr)
        edit_guest_bottle_table_handler(obj_response)

    def update_guest_bottles_left_handler(obj_response,bottleId,value):
        #update value
        guestBottles = db_execute("SELECT * FROM guest_bottles where id=\"" + str(bottleId) + "\"")
        nextBottleNum = guestBottles[0]['num_bottles'] + value
        if (nextBottleNum<0):
            nextBottleNum = 0
        db_execute("update guest_bottles set num_bottles="+str(nextBottleNum)+" where id=\"" + str(bottleId) + "\"")
        display_guest_bottles_left_handler(obj_response)

    def edit_guest_bottle_table_handler(obj_response):
        guestBottles = db_execute("SELECT * FROM guest_bottles")
        scriptStr = """
            $('#guest_bottle_table').html("\
                <h1>Guest Bottles</h1>\
                <table class='pure-table pure-table-horizontal'>\
                    <thead>\
                        <tr>\
                            <th>Name</th>\
                            <th>Style</th>\
                            <th>Action</th>\
                        </tr>\
                    </thead>\
                    <tbody>\
                    """
        for bottle in guestBottles:
            scriptStr += """\
                        <tr>\
                            <td>"""+str(bottle['name'])+"""</td>\
                            <td>"""+str(bottle['style'])+"""</td>\
                            <td>\
                                <a class='pure-menu-link' href='javascript://' onclick=\\"Sijax.request('delete_guest_bottle',["""+str(bottle['id'])+"""])\\" >Delete</a>\
                            </td>\
                        </tr>\
                        """
        scriptStr += """\
                    </table>\
                    <form id='guest-bottle-form' class='pure-form pure-form-stacked' method='post' >\
                    <fieldset>\
                        <label for='brew-name'>Brew Name</label>\
                        <input name='brew-name' type='text' required>\
                        <label for='brew-style'>Brew Style</label>\
                        <input name='brew-style' type='text' required>\
                            <h4>\
                                <a class='pure-menu-link' style='white-space: normal' href='javascript://' onclick=\\"var values = Sijax.getFormValues('#guest-bottle-form');Sijax.request('add_guest_bottle',[values,1])\\">Add 1</a>\
                                <a class='pure-menu-link' style='white-space: normal' href='javascript://' onclick=\\"var values = Sijax.getFormValues('#guest-bottle-form');Sijax.request('add_guest_bottle',[values,6])\\">Add 6 </a>\
                            </td>\
                    </fieldset>\
                      </form>\
                    </tbody>\
            <a class='pure-menu-link' style='white-space: normal' href='javascript://' onclick=\\"Sijax.request('display_guest_bottles_left',[])\\">done </a>\
                </tbody>\
            ");
            """
        obj_response.script(scriptStr)
    def display_guest_bottles_left_handler(obj_response):
        guestBottles = db_execute("SELECT * FROM guest_bottles")
        scriptStr = """
            $('#guest_bottle_table').html("\
                <h1>Guest Bottles</h1>\
                <table class='pure-table pure-table-horizontal'>\
                    <thead>\
                        <tr>\
                            <th>Name</th>\
                            <th>Style</th>\
                            <th>Number of Bottles</th>\
                        </tr>\
                    </thead>\
                    <tbody>\
                    """
        for bottle in guestBottles:
            scriptStr += """\
                        <tr>\
                            <td>"""+str(bottle['name'])+"""</td>\
                            <td>"""+str(bottle['style'])+"""</td>\
                            <td>\
                                """+str(bottle['num_bottles'])+"""\
                                """
            if session.get('logged_in'):
                scriptStr += """\
                                <a class='button-choose pure-button' onclick=\\"Sijax.request('update_guest_bottles_left',["""+str(bottle['id'])+""",-1])\\" >-</a>\
                                <a class='button-choose pure-button' onclick=\\"Sijax.request('update_guest_bottles_left',["""+str(bottle['id'])+""",1])\\" >+</a>\
                            """
            scriptStr += """\
                            </td>\
                        </tr>\
                        """
        scriptStr += """\
                    </tbody>\
                </table>\
                """
        if session.get('logged_in'):
            scriptStr += """<a class='pure-menu-link' style='white-space: normal' href='javascript://' onclick=\\"Sijax.request('edit_guest_bottle_table',[])\\">edit </a>\\"""
        scriptStr += """\
                </tbody>\
            ");
            """
        obj_response.script(scriptStr)

    def update_keg_stats_handler(obj_response):
        kegData = db_execute("SELECT * FROM keg ORDER BY datetime(tap_date) desc")
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

        scriptStr = """
        $("#keg_stats").html("\
            <h3 style='white-space:nowrap'>"""+kegStatsString+""" </h3>\
        ");
        """
        obj_response.script(scriptStr)

    def update_edit_keg_stat_table_handler(obj_response, show):
        if (show == 1):
            kegData = db_execute("SELECT * FROM keg ORDER BY datetime(tap_date) desc")
            scriptStr = """
            $("#keg_edit").html("\
                <form id='keg-stat-form' class='pure-form pure-form-stacked' method='post' >\
                <fieldset>\
                    <label for='current-volume'>Current Volume</label>\
                    <input name='current-volume' type='text' value='"""+str(kegData[0]['current_volume'])+"""' required>\
                    <label for='total-volume'>Total Volume</label>\
                    <input name='total-volume' type='text' value='"""+str(kegData[0]['total_volume'])+"""' required>\
                    <label for='tap-date'>Tap Date</label>\
                    <input name='tap-date' type='date' value='"""+str(kegData[0]['tap_date'])+"""' required>\
                    <input name='kick-date' type='date' value='"""+str(kegData[0]['kick_date'])+"""'>\
                    <h4>\
                        <a class='pure-menu-link' style='white-space: normal' href='javascript://' onclick=\\"var values = Sijax.getFormValues('#keg-stat-form');Sijax.request('edit_keg_stats',[values])\\">Submit</a>\
                        <a class='pure-menu-link' style='white-space: normal' href='javascript://' onclick=\\"Sijax.request('update_edit_keg_stat_table',[0])\\">Done</a>\
                    </td>\
                </fieldset>\
                </form>\
            ");
            """
        else:
            scriptStr = """
            $("#keg_edit").html("\
                <a class='pure-menu-link' style='white-space: normal' href='javascript://' onclick=\\"Sijax.request('update_edit_keg_stat_table',[1])\\">edit</a>\
            ");
            """
        obj_response.script(scriptStr)

    def edit_keg_stats_handler(obj_response,formData):
        #edit db
        beerOnTap = db_execute("select id from brews where on_tap=1")
        dbStr = "update keg set "
        dbStr += " current_volume = "+str(formData['current-volume'])+","
        dbStr += " total_volume = "+str(formData['total-volume'])+","
        dbStr += " tap_date = date(\""+str(formData['tap-date'])+"\"),"
        dbStr += " kick_date = date(\""+str(formData['kick-date'])+"\")"
        dbStr += " where brew_id = "+str(beerOnTap[0]['id'])
        dbStr += ";"
        db_execute(dbStr)
        update_edit_keg_stat_table_handler(obj_response,0)

    def update_last_pour_stats_handler(obj_response):
        kegData = db_execute("SELECT * FROM keg ORDER BY datetime(tap_date) desc")
        pourHistory = db_execute("SELECT * FROM pour_history ORDER BY datetime(pour_time) desc")
        #usernameData = db_execute("SELECT * FROM usernames where username=")
        lastPourString = ""

        #FACE_STATE_PENDING=0
        #FACE_STATE_RECOGNIZED=1
        #FACE_STATE_NOT_REGISTERED=2
        #FACE_STATE_NO_FACE=3
        if (pourHistory[0]['recognition_state'] == FACE_STATE_PENDING or pourHistory[0]['recognition_state'] == FACE_STATE_NO_FACE):
            lastPourString += "Last pour: <br>"
            lastPourString += str(pourHistory[0]['pour_volume']) + " oz <br>"
            lastPourString += "at " + datetime_to_string(datetime_pst(datetime_from_sqlite(pourHistory[0]['pour_time'])))
        elif (pourHistory[0]['recognition_state'] == FACE_STATE_RECOGNIZED):
            lastPourString += "Last pour: <br>"
            lastPourString += str(pourHistory[0]['pour_volume']) + " oz "
            lastPourString += "by " + str(pourHistory[0]['poured_username']) + " <br>"
            lastPourString += "at " + datetime_to_string(datetime_pst(datetime_from_sqlite(pourHistory[0]['pour_time'])))
        elif (pourHistory[0]['recognition_state'] == FACE_STATE_NOT_REGISTERED):
            lastPourString += "Last pour: <br>"
            lastPourString += str(pourHistory[0]['pour_volume']) + " oz "
            lastPourString += "by a " + str(pourHistory[0]['poured_age']) + " yr old " + str(pourHistory[0]['poured_gender']) + " <br>"
            lastPourString += "at " + datetime_to_string(datetime_pst(datetime_from_sqlite(pourHistory[0]['pour_time'])))

        obj_response.html("#last_pour_stats",lastPourString)

    if g.sijax.is_sijax_request:
        # Sijax request detected - let Sijax handle it
        g.sijax.set_request_uri('/on_tap.html')
        g.sijax.register_callback('update_beers_left', update_beers_left_handler)
        g.sijax.register_callback('update_oz_left', update_oz_left_handler)
        g.sijax.register_callback('update_beers_left_pic', update_beers_left_pic_handler)
        g.sijax.register_callback('update_bottles_left', update_bottles_left_handler)
        g.sijax.register_callback('update_guest_bottles_left', update_guest_bottles_left_handler)
        g.sijax.register_callback('display_guest_bottles_left', display_guest_bottles_left_handler)
        g.sijax.register_callback('edit_guest_bottle_table', edit_guest_bottle_table_handler)
        g.sijax.register_callback('delete_guest_bottle', delete_guest_bottle_handler)
        g.sijax.register_callback('add_guest_bottle', add_guest_bottle_handler)
        g.sijax.register_callback('update_keg_stats', update_keg_stats_handler)
        g.sijax.register_callback('edit_keg_stats', edit_keg_stats_handler)
        g.sijax.register_callback('update_edit_keg_stat_table', update_edit_keg_stat_table_handler)
        g.sijax.register_callback('update_last_pour_stats', update_last_pour_stats_handler)
        return g.sijax.process_request()

    bottleData = db_execute("SELECT * FROM bottles")
    brewData = db_execute("SELECT * FROM brews")
    guestBottles = db_execute("SELECT * FROM guest_bottles")
    beerOnTap = db_execute("select * from brews where on_tap=1")
    if (len(beerOnTap)==0):
        return render_template('/on_tap.html', bottleData=bottleData, brewData=brewData, guestBottles=guestBottles)

    return render_template('/on_tap.html', beerOnTap=beerOnTap[0], bottleData=bottleData,brewData=brewData,guestBottles=guestBottles)

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
        db_execute_args('update chamber set set_temp = ?',[request.form['set_temp']])
        db_execute_args('update chamber set set_range = ?',[request.form['set_range']])
        if (request.form['temp_control_on'] == "On"):
            temp_control_num = 1
        else:
            temp_control_num = 0
        if (request.form['temp_history_reset'] == "True"):
            db_execute("delete from temperatures;")
        db_execute_args('update chamber set temp_control_on = ?',[temp_control_num])
        flash('Temp Changed')

    fermBrew = db_execute("SELECT name,id FROM brews WHERE fermenting=1")
    tempList = db_execute("SELECT * FROM temperatures ORDER BY datetime(timestamp) desc limit 96")
    fermStats = db_execute("SELECT * FROM chamber")
    formattedTempList = []
    for temp in tempList:
        dt_temp = datetime_from_sqlite(temp['timestamp'])
        formattedTempList.append({'year':int(dt_temp.year),'month':int(dt_temp.month),'day':int(dt_temp.day),'hour':int(dt_temp.hour) ,'minute':int(dt_temp.minute) ,'temp':temp['temperature']})
    if (len(fermBrew)==1):
        return render_template('fermenting.html', fermBrew=fermBrew[0], tempList=formattedTempList, fermStats=fermStats)
    else:
        return render_template('fermenting.html', tempList=formattedTempList, fermStats=fermStats)

@flask_sijax.route(app, '/brews.html')
def serve_page_brewing_brews():
    def submit_edit_stat_table_handler(obj_response,id,formData):
        if formData.has_key('is_in_bottles'):
            is_in_bottles = 1
            dbStr = "insert into bottles values("
            dbStr += "\"" + formData['brew-name'] + "\","
            dbStr += "0 , 0,"
            dbStr += str(id) + ");"
            db_execute(dbStr)
        else:
            is_in_bottles = 0
            dbStr = "delete from bottles where id="
            dbStr += str(id)
            db_execute(dbStr)
        if formData.has_key('is_on_tap'):
            is_on_tap = 1
            dbStr = "insert into keg values(560,560,"
            dbStr += "Date('now'), NULL"
            dbStr += str(id)
            dbStr += ")"
            db_execute(dbStr)
        else:
            is_on_tap = 0
        if formData.has_key('is_fermenting'):
            is_fermenting = 1
        else:
            is_fermenting = 0
        #edit db
        dbStr = "update brews set"
        dbStr += " name=\""+str(formData['brew-name'])+"\","
        dbStr += " description=\""+str(formData['brew-description'])+"\","
        dbStr += " style=\""+str(formData['brew-style'])+"\","
        dbStr += " og=\""+str(formData['brew-og'])+"\","
        dbStr += " abv=\""+str(formData['brew-abv'])+"\","
        dbStr += " ibu=\""+str(formData['brew-ibu'])+"\","
        dbStr += " brew_date=date(\""+str(formData['brew-date'])+"\"),"
        dbStr += " in_bottles=\""+str(is_in_bottles)+"\","
        dbStr += " on_tap=\""+str(is_on_tap)+"\","
        dbStr += " fermenting=\""+str(is_fermenting)+"\""
        dbStr += " where id="+str(id)
        db_execute(dbStr)
        update_display_recipe_handler(obj_response,id);
    def update_edit_stat_table_handler(obj_response,id):
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
                          <form id='brew-data-form' class='pure-form pure-form-aligned' method='post' >\
                            <fieldset>\
                                <label for='brew-name'>Brew Name</label>\
                                    <input name='brew-name' class='pure-u-1' type='text' value='"""+displayBrew[0]['name']+"""'>\
                                <label for='brew-description'>Description</label>\
                                    <textarea name='brew-description' class='pure-u-1' required>"""+displayBrew[0]['description']+"""</textarea>\
                                <label for='brew-style'>Style</label>\
                                    <input name='brew-style' class='pure-u-1' type='text' value='"""+displayBrew[0]['style']+"""'>\
                                <label for='brew-og'>OG</label>\
                                    <input name='brew-og' class='pure-u-1' type='text' value='"""+displayBrew[0]['og']+"""'>\
                                <label for='brew-abv'>ABV</label>\
                                    <input name='brew-abv' class='pure-u-1' type='text' value='"""+displayBrew[0]['abv']+"""'>\
                                <label for='brew-ibu'>IBU</label>\
                                    <input name='brew-ibu' class='pure-u-1' type='text' value='"""+displayBrew[0]['ibu']+"""'>\
                                <label for='brew-date'>Brew Date</label>\
                                    <input name='brew-date' class='pure-u-1' type='date' value='"""+displayBrew[0]['brew_date']+"""'>\
                                <label for='bottles' class='pure-checkbox'>\
                                    <input name='is_in_bottles' type='checkbox' \
                                    """
        if (displayBrew[0]['in_bottles']):
            scriptStr += "checked"
        scriptStr += """\
                                > This beer is in bottles\
                                </label>\
                                <label for='tap' class='pure-checkbox'>\
                                    <input name='is_on_tap' type='checkbox' \
                                    """
        if (displayBrew[0]['on_tap']):
            scriptStr += "checked"
        scriptStr += """\
                                    > This beer is on tap\
                                </label>\
                                <label for='fermenting' class='pure-checkbox'>\
                                    <input name='is_fermenting' type='checkbox' \
                                    """
        if (displayBrew[0]['fermenting']):
            scriptStr += "checked"
        scriptStr += """\
                                    > This beer is currently fermenting\
                                </label>\
                            </fieldset>\
                          </form>\
                            <h4>\
                                <a class='pure-menu-link' style='white-space: normal' href='javascript://' onclick=\\"var values = Sijax.getFormValues('#brew-data-form');Sijax.request('submit_edit_stat_table',["""+str(displayBrew[0]['id'])+""",values])\\">Submit </a>\
                                <a class='pure-menu-link' style='white-space: normal' href='javascript://' onclick=\\"Sijax.request('update_display_recipe',["""+str(displayBrew[0]['id'])+"""])\\">Cancel </a>\
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
        obj_response.script(scriptStr)
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
                                Brew Date: """+displayBrew[0]['brew_date']+""" <br>\
                                """
        if (displayBrew[0]['on_tap']):
            scriptStr += "<br>Currently On Tap"
        if (displayBrew[0]['in_bottles']):
            scriptStr += "<br>Currently In Bottles"
        if (displayBrew[0]['fermenting']):
            scriptStr += "<br>Currently Fermenting"
        if session.get('logged_in'):
            scriptStr += """<a class='pure-menu-link' style='white-space: normal' href='javascript://' onclick=\\"Sijax.request('update_edit_stat_table',["""+str(displayBrew[0]['id'])+"""])\\">edit </a>\\"""

        scriptStr +="""\
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
        ########################### END GRAIN ##################################
        ########################### BEGIN HOPS #################################
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
        ########################### BEGIN yeast ################################
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
        ########################### END YEAST ##################################
        ########################### BEGIN WATER ################################
        displayWater = db_execute_args("SELECT * FROM water where profile_name=?",[displayBrew[0]['water_profile']])
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
        ########################### END WATER ##################################
        obj_response.script(scriptStr)

    if g.sijax.is_sijax_request:
        # Sijax request detected - let Sijax handle it
        g.sijax.set_request_uri('/brews.html')
        g.sijax.register_callback('update_display_recipe', update_display_recipe_handler)
        g.sijax.register_callback('update_edit_stat_table', update_edit_stat_table_handler)
        g.sijax.register_callback('submit_edit_stat_table', submit_edit_stat_table_handler)
        return g.sijax.process_request()

    brews = db_execute("SELECT * FROM brews")
    if request.method == 'GET':
        selectBrewId = request.args.get("selectBrewId")
        return render_template('brews.html', brews=brews, selectBrewId=selectBrewId)

    return render_template('brews.html', brews=brews)

@app.route('/add_brew.html',methods=['GET', 'POST'])
def serve_page_brewing_add_brew():
    if request.method == 'POST':
        if request.form.get('is_in_bottles'):
            is_in_bottles = 1
        else:
            is_in_bottles = 0
        if request.form.get('is_on_tap'):
            is_on_tap = 1
            dbStr = "insert into keg values(560,560,"
            dbStr += "Date('now'), NULL"
            dbStr += str(request.form.get('brew-id'))
            dbStr += ")"
            db_execute(dbStr)
        else:
            is_on_tap = 0
        if request.form.get('is_fermenting'):
            is_fermenting = 1
        else:
            is_fermenting = 0

        # Brew data
        db_execute_args('insert into brews values (?, ?, date(?), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',[request.form.get('brew-name'), request.form.get('brew-style'),request.form.get('brew-date'), is_in_bottles, is_on_tap, is_fermenting, request.form.get('brew-description'), request.form.get('brew-og'), request.form.get('brew-fg'), request.form.get('brew-abv'), request.form.get('brew-ibu'), request.form.get('brew-id'), request.form.get('brew-style_type'), request.form.get('brew-water_profile')])

        index = 1
        while (1):
            #GRAINS
            grainNumStr = "grain"+str(index)
            if request.form.get(grainNumStr+'_type'):
                db_execute_args('insert into grain values (?,?,?)',[request.form.get('brew-id'), request.form.get(grainNumStr+'_type'), request.form.get(grainNumStr+'_amount')])
                index += 1
            else:
                break;

        index = 1
        while (1):
            #HOPS
            hopNumStr = "hop"+str(index)
            if request.form.get(hopNumStr+'_type'):
                db_execute_args('insert into hops values (?,?,?,?)',[request.form.get('brew-id'), request.form.get(hopNumStr+'_type'), request.form.get(hopNumStr+'_amount'), request.form.get(hopNumStr+'_mins')])
                index += 1
            else:
                break;

        #yeast
        db_execute_args('insert into yeast values (?,?,?)',[request.form.get('brew-id'), request.form.get('yeast_type'), request.form.get('yeast_temp')])

        #db_execute('insert into brews (name, style, brew_date, in_bottles, on_tap, fermenting) values (?, ?, ?, ?, ?, ?)',[request.form.get('brew-name'), request.form.get('brew-type'),request.form.get('brew-date'), is_in_bottles, is_on_tap, is_fermenting])
        flash('New entry was successfully posted')
    return render_template('add_brew.html')

@app.route('/history.html')
def serve_page_history():
    pourHistory = db_execute("SELECT * FROM pour_history ORDER BY datetime(pour_time) desc")
    keg = db_execute("SELECT * FROM keg ORDER BY date(tap_date) desc")
    brews = db_execute("select name,id from brews")

    brewid_to_name = {}
    for brew in brews:
        brewid_to_name[brew['id']] = brew['name']

    # Per beer beer/day average
    perBeerAvg = []
    for k in keg:
        if (not k['kick_date']):
            daysTapped = (datetime.now() - date_from_sqlite(k['tap_date'])).days
        else:
            daysTapped = (date_from_sqlite(k['kick_date']) - date_from_sqlite(k['tap_date'])).days

        volumeDrank = k['total_volume'] - k['current_volume']
        beersPerDay = (float(volumeDrank) / daysTapped) / 16
        perBeerAvg += [{'id':k['brew_id'], 'bpd':beersPerDay}]

    # Weekday percentage split
    total_oz = 0
    weekdayAverages = [0.0] * 7
    cumulativeVolume = []
    for history in reversed(pourHistory):
        weekdayAverages[datetime_pst(datetime_from_sqlite(history['pour_time'])).weekday()] += history['pour_volume']
        total_oz += history['pour_volume']
        date_js = int(time.mktime(datetime_from_sqlite(history['pour_time']).timetuple())) * 1000
        cumulativeVolume += [{'volume':total_oz,'pour_time':date_js}]

    for day in range(0,7):
        weekdayAverages[day] /= total_oz

    return render_template('/history.html', pourHistory=pourHistory, brewid_to_name=brewid_to_name, weekdayAverages=weekdayAverages, perBeerAvg=perBeerAvg, cumulativeVolume=cumulativeVolume)

@flask_sijax.route(app, '/brewai.html')
def serve_page_brewing_brewai():
    def submit_brew_name_handler(obj_response,formData):

        # TODO Generate beerxml recipe
        if formData['brew_name'] == "":
            obj_response.script("")
            return
        beerxml = "<RECIPES> <RECIPE> <NAME>"+formData['brew_name']+"</NAME> <VERSION>1</VERSION> <TYPE>All Grain</TYPE> <BREWER>Beerfan</BREWER> <DISPLAY_BATCH_SIZE>6.5 gal</DISPLAY_BATCH_SIZE> <DISPLAY_BOIL_SIZE>7.75 gal</DISPLAY_BOIL_SIZE> <BATCH_SIZE>24.60517657</BATCH_SIZE> <BOIL_SIZE>29.336941295</BOIL_SIZE> <BOIL_TIME>70</BOIL_TIME> <EFFICIENCY>79</EFFICIENCY> <NOTES>if your like me and love hops just add an ounce of Cascade to your keg, let it slow carbonate for a 3 or 4 days then take it out and enjoy a great beer! &#13; &#13; Adjust your caramel 60L and shoot for an SRM of 8. </NOTES> <EST_COLOR>8</EST_COLOR> <IBU>39.79</IBU> <IBU_METHOD>Tinseth</IBU_METHOD> <EST_ABV>5.58</EST_ABV> <EST_OG>1.055 sg</EST_OG> <EST_FG>1.013 sg</EST_FG> <OG>1.055</OG> <FG>1.013</FG> <PRIMING_SUGAR_NAME></PRIMING_SUGAR_NAME> <CARBONATION_USED></CARBONATION_USED> <BF_PRIMING_METHOD></BF_PRIMING_METHOD> <BF_PRIMING_AMOUNT></BF_PRIMING_AMOUNT> <BF_CO2_LEVEL></BF_CO2_LEVEL> <BF_CO2_UNIT>Volumes</BF_CO2_UNIT> <URL></URL> <BATCH_SIZE_MODE>f</BATCH_SIZE_MODE> <YEAST_STARTER>true</YEAST_STARTER> <NO_CHILL_EXTRA_MINUTES></NO_CHILL_EXTRA_MINUTES> <PITCH_RATE>1.0</PITCH_RATE> <FERMENTABLES> <FERMENTABLE> <NAME>Pale 2-Row</NAME> <VERSION>1</VERSION> <TYPE>Grain</TYPE> <AMOUNT>5.216312255</AMOUNT> <YIELD>80.43</YIELD> <COLOR>1.8</COLOR> <ADD_AFTER_BOIL>false</ADD_AFTER_BOIL> <ORIGIN>American</ORIGIN> </FERMENTABLE> <FERMENTABLE> <NAME>Caramel / Crystal 60L</NAME> <VERSION>1</VERSION> <TYPE>Grain</TYPE> <AMOUNT>0.412202065874</AMOUNT> <YIELD>73.91</YIELD> <COLOR>60</COLOR> <ADD_AFTER_BOIL>false</ADD_AFTER_BOIL> <ORIGIN>American</ORIGIN> </FERMENTABLE> </FERMENTABLES> <HOPS> <HOP> <NAME>Magnum</NAME> <VERSION>1</VERSION> <ALPHA>15</ALPHA> <AMOUNT>0.01417476155</AMOUNT> <USE>Boil</USE> <USER_HOP_USE>Boil</USER_HOP_USE> <TIME>60</TIME> <FORM>Pellet</FORM> </HOP> <HOP> <NAME>Perle</NAME> <VERSION>1</VERSION> <ALPHA>8.2</ALPHA> <AMOUNT>0.01417476155</AMOUNT> <USE>Boil</USE> <USER_HOP_USE>Boil</USER_HOP_USE> <TIME>30</TIME> <FORM>Pellet</FORM> </HOP> <HOP> <NAME>Cascade</NAME> <VERSION>1</VERSION> <ALPHA>7</ALPHA> <AMOUNT>0.0283495231</AMOUNT> <USE>Boil</USE> <USER_HOP_USE>Boil</USER_HOP_USE> <TIME>10</TIME> <FORM>Pellet</FORM> </HOP> <HOP> <NAME>Cascade</NAME> <VERSION>1</VERSION> <ALPHA>7</ALPHA> <AMOUNT>0.0566990462</AMOUNT> <TIME>0</TIME> <USE>Boil</USE> <USER_HOP_USE>Boil</USER_HOP_USE> <FORM>Pellet</FORM> </HOP> <HOP> <NAME>Cascade</NAME> <VERSION>1</VERSION> <ALPHA>7</ALPHA> <AMOUNT>0.0566990462</AMOUNT> <USE>Dry Hop</USE> <USER_HOP_USE>Dry Hop</USER_HOP_USE> <TIME>5760</TIME> <FORM>Pellet</FORM> </HOP> </HOPS> <MISCS> <MISC> <NAME>Crush whilrfoc Tablet</NAME> <VERSION>1</VERSION> <TYPE>Water Agent</TYPE> <USE>Boil</USE> <TIME>10</TIME> <AMOUNT>1</AMOUNT> <AMOUNT_IS_WEIGHT>true</AMOUNT_IS_WEIGHT> </MISC> </MISCS> <MASH> <NAME>Mash Steps</NAME>";
        beerxml += "<VERSION>1</VERSION> <GRAIN_TEMP>20</GRAIN_TEMP> <MASH_STEPS> <MASH_STEP> <NAME>Rest</NAME> <VERSION>1</VERSION> <TYPE>Temperature</TYPE> <STEP_TIME>60</STEP_TIME> <INFUSE_AMOUNT>18.9270589</INFUSE_AMOUNT> <STEP_TEMP>67.222222222222</STEP_TEMP> </MASH_STEP> <MASH_STEP> <NAME>Mash-out Rest</NAME> <VERSION>1</VERSION> <TYPE>Temperature</TYPE> <STEP_TIME>10</STEP_TIME> <INFUSE_AMOUNT></INFUSE_AMOUNT> <STEP_TEMP>75.555555555556</STEP_TEMP> </MASH_STEP> <MASH_STEP> <NAME>Sparge</NAME> <VERSION>1</VERSION> <TYPE>Infusion</TYPE> <STEP_TIME>10</STEP_TIME> <INFUSE_AMOUNT>18.9270589</INFUSE_AMOUNT> <STEP_TEMP>76.666666666667</STEP_TEMP> </MASH_STEP> </MASH_STEPS> </MASH> <YEASTS> <YEAST> <NAME>Safale - American Ale Yeast US-05</NAME> <VERSION>1</VERSION> <TYPE>Ale</TYPE> <FORM>Dry</FORM> <AMOUNT>0.11</AMOUNT> <AMOUNT_IS_WEIGHT>true</AMOUNT_IS_WEIGHT> <PRODUCT_ID>US-05</PRODUCT_ID> <LABORATORY>Fermentis / Safale</LABORATORY> <ATTENUATION>76</ATTENUATION> <FLOCCULATION>Medium</FLOCCULATION> <MIN_TEMPERATURE>12.222222222222</MIN_TEMPERATURE> <MAX_TEMPERATURE>25</MAX_TEMPERATURE> </YEAST> </YEASTS> <WATERS/> <STYLE> <NAME>American Pale Ale</NAME> <VERSION>1</VERSION> <CATEGORY>American Ale</CATEGORY> <CATEGORY_NUMBER>10</CATEGORY_NUMBER> <STYLE_LETTER>A</STYLE_LETTER> <STYLE_GUIDE>BJCP</STYLE_GUIDE> <TYPE>Ale</TYPE> <OG_MIN>1.045</OG_MIN> <OG_MAX>1.06</OG_MAX> <FG_MIN>1.01</FG_MIN> <FG_MAX>1.015</FG_MAX> <ABV_MIN>4.5</ABV_MIN> <ABV_MAX>6.2</ABV_MAX> <IBU_MIN>30</IBU_MIN> <IBU_MAX>45</IBU_MAX> <COLOR_MIN>5</COLOR_MIN> <COLOR_MAX>14</COLOR_MAX> </STYLE> </RECIPE> </RECIPES>";

        # Get a list of recipes 
        scriptStr = ""
        scriptStr += """var recipes = Brauhaus.Recipe.fromBeerXml(" """+beerxml+""" ");"""

        scriptStr += """var r = recipes[0];"""
        scriptStr += """r.scale(Brauhaus.gallonsToLiters(5),Brauhaus.gallonsToLiters(6.5));"""
        scriptStr += """r.calculate();"""

        scriptStr += """var main_html = "<table class='pure-table pure-table-bordered'>";"""
        scriptStr += """main_html += "<thead>";"""
        scriptStr += """main_html += "    <tr>";"""
        scriptStr += """main_html += "        <th>Beer Stats </th>";"""
        scriptStr += """main_html += "    </tr>";"""
        scriptStr += """main_html += "</thead>";"""
        scriptStr += """main_html += "<tbody>";"""
        scriptStr += """main_html += "           <tr>";"""
        scriptStr += """main_html += "               <td>";"""
        scriptStr += """main_html += "                  <h1> "+r.name+" </h1>";"""
        scriptStr += """main_html += "                  <h4>";"""
        scriptStr += """main_html += "                      description TODO";"""
        scriptStr += """main_html += "                  </h4>";"""
        scriptStr += """main_html += "                  <h4>";"""
        scriptStr += """main_html += "                      Style: style TODO <br>";"""
        scriptStr += """main_html += "                      OG: "+r.og.toFixed(2)+" <br>";"""
        scriptStr += """main_html += "                      ABV: "+r.abv.toFixed(2)+" <br>";"""
        scriptStr += """main_html += "                      IBU: "+r.ibu.toFixed(2)+" <br>";"""
        scriptStr += """main_html += "                  </h4>";"""
        scriptStr += """main_html += "               </td>";"""
        scriptStr += """main_html += "           </tr>";"""
        scriptStr += """main_html += "   </tbody>";"""
        scriptStr += """main_html += "</table>";"""
        scriptStr += """$("#main").html(main_html);"""

        # HOPS
        scriptStr += """var hops_html = "    <br><h3>Hops:</h3>";"""
        scriptStr += """hops_html += "<table class='pure-table pure-table-bordered'>";"""
        scriptStr += """hops_html += "<thead>";"""
        scriptStr += """hops_html += "    <tr>";"""
        scriptStr += """hops_html += "        <th>Hop Type </th>";"""
        scriptStr += """hops_html += "        <th>Amount in oz </th>";"""
        scriptStr += """hops_html += "        <th>Boil Minutes </th>";"""
        scriptStr += """hops_html += "    </tr>";"""
        scriptStr += """hops_html += "</thead>";"""
        scriptStr += """hops_html += "<tbody>";"""

        scriptStr += """var hops = r.spices;"""
        scriptStr += """for (var i=0; i<hops.length; i++)"""
        scriptStr += """{"""
        scriptStr += """    hops_html += "           <tr>";"""
        scriptStr += """    hops_html += "               <td> "+hops[i].name+"</td>";"""
        scriptStr += """    hops_html += "               <td> "+hops[i].weightLbOz().oz.toFixed(2)+"</td>";"""
        scriptStr += """    hops_html += "               <td> "+hops[i].time+"</td>";"""
        scriptStr += """    hops_html += "           </tr>";"""
        scriptStr += """}"""
        scriptStr += """hops_html += "   </tbody>";"""
        scriptStr += """hops_html += "</table>";"""
        scriptStr += """$("#hops").html(hops_html);"""

        ## GRAIN
        scriptStr += """var grain_html = "    <br><h3>Grain:</h3>";"""
        scriptStr += """grain_html += "<table class='pure-table pure-table-bordered'>";"""
        scriptStr += """grain_html += "<thead>";"""
        scriptStr += """grain_html += "    <tr>";"""
        scriptStr += """grain_html += "     <th>Grain Type </th>";"""
        scriptStr += """grain_html += "     <th>Amount in Lbs </th>";"""
        scriptStr += """grain_html += "    </tr>";"""
        scriptStr += """grain_html += "</thead>";"""
        scriptStr += """grain_html += "<tbody>";"""

        scriptStr += """var grain = r.fermentables;"""
        scriptStr += """for (var i=0; i<grain.length; i++)"""
        scriptStr += """{"""
        scriptStr += """    grain_html += "           <tr>";"""
        scriptStr += """    grain_html += "               <td> "+grain[i].name+"</td>";"""
        scriptStr += """    grain_html += "               <td> "+grain[i].weightLb().toFixed(2)+"</td>";"""
        scriptStr += """    grain_html += "           </tr>";"""
        scriptStr += """}"""
        scriptStr += """grain_html += "   </tbody>";"""
        scriptStr += """grain_html += "</table>";"""
        scriptStr += """$("#grain").html(grain_html);"""

        ## YEAST
        scriptStr += """var yeast_html = "    <br><h3>Yeast:</h3>";"""
        scriptStr += """yeast_html += "<table class='pure-table pure-table-bordered'>";"""
        scriptStr += """yeast_html += "<thead>";"""
        scriptStr += """yeast_html += "    <tr>";"""
        scriptStr += """yeast_html += "     <th>Yeast Type </th>";"""
        scriptStr += """yeast_html += "     <th>Fermentation Temperature </th>";"""
        scriptStr += """yeast_html += "    </tr>";"""
        scriptStr += """yeast_html += "</thead>";"""
        scriptStr += """yeast_html += "<tbody>";"""

        scriptStr += """var yeast = r.yeast;"""
        scriptStr += """for (var i=0; i<yeast.length; i++)"""
        scriptStr += """{"""
        scriptStr += """    yeast_html += "           <tr>";"""
        scriptStr += """    yeast_html += "               <td> "+yeast[i].name+"</td>";"""
        scriptStr += """    yeast_html += "               <td> "+Brauhaus.cToF(r.primaryTemp)+"</td>";"""
        scriptStr += """    yeast_html += "           </tr>";"""
        scriptStr += """}"""
        scriptStr += """yeast_html += "   </tbody>";"""
        scriptStr += """yeast_html += "</table>";"""
        scriptStr += """$("#yeast").html(yeast_html);"""
        obj_response.script(scriptStr)
    if g.sijax.is_sijax_request:
        # Sijax request detected - let Sijax handle it
        g.sijax.set_request_uri('/brewai.html')
        g.sijax.register_callback('submit_brew_name', submit_brew_name_handler)
        return g.sijax.process_request()
    return render_template('/brewai.html')

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

## *********************** API *************************************************************
@app.route('/get_chamber_set_data.html')
def serve_page_brewing_get_chamber_set_data():
    fermStats = db_execute("SELECT * FROM chamber")
    return jsonify(set_temp=fermStats[0]['set_temp'],set_range=fermStats[0]['set_range'],temp_control_on=fermStats[0]['temp_control_on'])

@app.route('/get_sec_per_oz_data.html')
def serve_page_brewing_get_sec_per_oz_data():
    tapFlowData = db_execute("SELECT * FROM tap_flow_data")
    return jsonify(sec_per_oz=tapFlowData[0]['sec_per_oz'])

@app.route('/update_sec_per_oz_data.html')
def serve_page_brewing_update_sec_per_oz_data():
    sec_per_oz = request.form['sec_per_oz']

    # add latest sec per oz
    dbStr = "update tap_flow_data set sec_per_oz="+str(sec_per_oz)+";"
    db_execute(dbStr)
    return jsonify(result=True)

@app.route('/update_tap.html',methods=['POST'])
def serve_page_brewing_update_tap():
    beerOnTap = db_execute("select name,style,id from brews where on_tap=1")
    kegData = db_execute("SELECT * FROM keg ORDER BY datetime(tap_date) desc")

    ozPoured = request.form['oz_poured']
    recognition_state = request.form['recognition_state']
    poured_username = request.form['poured_username']
    poured_age = request.form['poured_age']
    poured_gender = request.form['poured_gender']

    newVolume = kegData[0]['current_volume'] - int(ozPoured)
    if (newVolume < 0):
        newVolume = 0

    # add pour_history
    dbStr = "insert into pour_history values("
    dbStr += str(ozPoured)+", "
    dbStr += "DateTime('now'), "
    dbStr += str(recognition_state)+", "
    dbStr += "\""+str(poured_username)+"\", "
    dbStr += str(poured_age)+", "
    dbStr += "\""+str(poured_gender)+"\", "
    dbStr += str(beerOnTap[0]['id'])+");"
    db_execute(dbStr);

    # update keg status
    db_execute("update keg set current_volume="+str(newVolume)+" where brew_id="+str(beerOnTap[0]['id']))
    db_execute("update keg set last_pour_volume="+str(ozPoured)+" where brew_id="+str(beerOnTap[0]['id']))
    return jsonify(result=True)

@app.route('/update_temp.html',methods=['POST'])
def serve_page_brewing_update_temp():
    temp = request.form['temp']
    avg = request.form['average']

    # add temp
    db_execute("insert into temperatures values(CURRENT_TIMESTAMP,"+str(temp)+");")
    db_execute("update chamber set avg = "+avg)
    return jsonify(result=True)

### Helper fns #######################
def db_execute(query):
    cur = g.db.execute(query)
    queryData = cur.fetchall()
    g.db.commit()
    return queryData

def db_execute_args(query,args):
    cur = g.db.execute(query,args)
    queryData = cur.fetchall()
    g.db.commit()
    return queryData

@app.template_filter('datetime_pst')
def datetime_pst(dt):
    # convert nieve to pacific
    dt_utc = dt.replace(tzinfo=timezone('UTC'))
    return dt_utc.astimezone(timezone('US/Pacific'))

@app.template_filter('date_from_sqlite')
def date_from_sqlite(dt):
    return datetime.strptime(dt,"%Y-%m-%d")

@app.template_filter('datetime_from_sqlite')
def datetime_from_sqlite(dt):
    return datetime.strptime(dt,"%Y-%m-%d %H:%M:%S")

@app.template_filter('datetime_to_string')
def datetime_to_string(dt):
    return dt.strftime("%Y-%m-%d %I:%M:%S %p")

#to run the application
if __name__ == '__main__':
    app.run(debug=DEBUG,host='0.0.0.0')
