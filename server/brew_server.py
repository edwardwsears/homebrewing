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
    bottleData = db_execute("SELECT * FROM bottles")
    brewData = db_execute("SELECT * FROM brews")
    guestBottles = db_execute("SELECT * FROM guest_bottles")
    tempList = db_execute("SELECT * FROM temperatures ORDER BY datetime(timestamp) desc limit 1")

    return render_template('/index.html', bottleData=bottleData,brewData=brewData, tempList=tempList, guestBottles=guestBottles)


@flask_sijax.route(app, '/on_tap.html')
def serve_page_brewing_on_tap():
    def update_beers_left_handler(obj_response):
        beerOnTap = db_execute("select name,style from brews where on_tap=1")
        if (len(beerOnTap)==0):
            beersLeftString = "Beers Left: 0"
            obj_response.html("#beers_left",beersLeftString)
            return
        kegData = db_execute("SELECT * FROM keg")
        beersLeft = int(kegData[0]['current_volume'] / 16)
        beersLeftString = "Beers Left: " + str(beersLeft)
        obj_response.html("#beers_left",beersLeftString)

    def update_oz_left_handler(obj_response):
        kegData = db_execute("SELECT * FROM keg")
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
        kegData = db_execute("SELECT * FROM keg")
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
        kegData = db_execute("SELECT * FROM keg ORDER BY datetime(last_pour_time)")
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
            kegData = db_execute("SELECT * FROM keg")
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
        dbStr = "update keg set "
        dbStr += " current_volume = "+str(formData['current-volume'])+","
        dbStr += " total_volume = "+str(formData['total-volume'])+","
        dbStr += " tap_date = date(\""+str(formData['tap-date'])+"\")"
        dbStr += ";"
        db_execute(dbStr)
        update_edit_keg_stat_table_handler(obj_response,0)

    def update_last_pour_stats_handler(obj_response):
        kegData = db_execute("SELECT * FROM keg ORDER BY datetime(last_pour_time)")
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
    kegData = db_execute("SELECT * FROM keg")

    return render_template('/on_tap.html', beerOnTap=beerOnTap[0], kegData=kegData[0],bottleData=bottleData,brewData=brewData,guestBottles=guestBottles)

@app.route('/update_tap.html',methods=['POST'])
def serve_page_brewing_update_tap():
    ozPoured = request.form['oz_poured']
    beerOnTap = db_execute("select name,style from brews where on_tap=1")
    kegData = db_execute("SELECT * FROM keg")

    newVolume = kegData[0]['current_volume'] - int(ozPoured)
    if (newVolume < 0):
        newVolume = 0

    db_execute("update keg set current_volume="+str(newVolume))
    db_execute("update keg set last_pour_volume="+str(ozPoured))
    db_execute("update keg set last_pour_time=DateTime('now')")
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

@app.route('/update_temp.html',methods=['POST'])
def serve_page_brewing_update_temp():
    temp = request.form['temp']
    avg = request.form['average']

    # add temp
    db_execute("insert into temperatures values(CURRENT_TIMESTAMP,"+str(temp)+");")
    db_execute("update chamber set avg = "+avg)
    return jsonify(result=True)

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
    db_execute("update tap_flow_data set sec_per_oz=,"+str(sec_per_oz)+";")
    return jsonify(result=True)

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
        ########################### END YEAST ###################################
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

def db_execute_args(query,args):
    cur = g.db.execute(query,args)
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
