from flask import Flask, render_template, request, jsonify
import os
import sqlite3 as sql
import json
from dotenv import load_dotenv

# app - The flask application where all the magical things are configured.
load_dotenv()
app = Flask(__name__)

app.debug = bool(os.getenv('DEBUG'))
app.debug = os.getenv('ENV')

# Constants - Stuff that we need to know that won't ever change!
DATABASE_FILE = os.environ.get('DATABASE_FILE', 'database.db')
DEFAULT_BUGGY_ID = "1"
BUGGY_RACE_SERVER_URL = "https://rhul.buggyrace.net"

#------------------------------------------------------------
# the index page
#------------------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html', server_url=BUGGY_RACE_SERVER_URL)
#------------------------------------------------------------

@app.route('/info')
def showbuggyinfo():
        return render_template("info.html")
#------------------------------------------------------------
# creating a new buggy:
#  if it's a POST request process the submitted data
#  but if it's a GET request, just show the form
#------------------------------------------------------------



@app.route('/new', methods = ['POST', 'GET'])
def create_buggy():
    if request.method == 'GET':
        with sql.connect(DATABASE_FILE) as con:
            cur = con.cursor()
            cur.execute("SELECT qty_wheels, flag_color, flag_color_secondary, qty_tyres  FROM buggies WHERE id=?", (DEFAULT_BUGGY_ID,))
            result = cur.fetchone()
            if result:
                qty_wheels = result[0]
                flag_color = result[1]
                flag_color_secondary = result[2]
                qty_tyres = result[3]
  
                return render_template("buggy-form.html", qty_wheels=qty_wheels, flag_color=flag_color, flag_color_secondary=flag_color_secondary, qty_tyres=qty_tyres)
            else:
                return render_template("buggy-form.html")
    elif request.method == 'POST':
        msg = ""
        qty_wheels = request.form['qty_wheels']
        flag_color = request.form['flag_color']
        power_type = request.form['power_type']
        tyres = request.form['tyres']
        armour = request.form['armour']
        attack = request.form['attack']
        algo = request.form['algo']
        special = request.form['special']
        qty_tyres= request.form['qty_tyres']
        flag_color_secondary = request.form['flag_color_secondary']
        flag_pattern = request.form['flag_pattern']
        power_type_costs = {
            'bio': 5,
            'electric': 20,
            'fusion': 400,
            'hamster': 3,
            'none': 0,
            'petrol': 4,
            'rocket': 16,
            'solar': 40,
            'steam': 3,
            'thermo': 300,
            'wind': 20
        }.get(power_type, 0)
        tyres_costs = {
            'knobbly': 15,
            'maglev': 50,
            'reactive': 40,
            'slick': 10,
            'steelband': 20
        }.get(tyres, 0)
        armour_costs =  {
            'aluminium': 200,
            'none': 0,
            'thicksteel': 200,
            'thinsteel': 100,
            'titanium': 290,
            'wood': 40
        }.get(armour, 0)
        attack_costs = {
            'biohazard': 30,
            'charge': 28,
            'flame': 20,
            'none': 0,
            'spike': 5
        }.get(attack, 0)
        special_costs = {
            'antibiotic': 90,
            'banging': 42,
            'fireproof': 70,
            'hamster_booster': 5,
            'insulated': 100
        }.get(special,0)


   

        if not qty_wheels.isdigit() or not int(qty_wheels)%2 == 0 or int(qty_wheels) == 0:
            invalid_input = "Invalid input for number of wheels. Please enter a valid even integer."
            return render_template("buggy-form.html", invalid_input=invalid_input, qty_wheels=qty_wheels, flag_color=flag_color, power_type_costs=power_type_costs, tyres_costs=tyres_costs, armour_costs=armour_costs, attack_costs=attack_costs, special_costs=special_costs)
        
                
        
        wheel_cost_percentage = ((int(qty_wheels) - 4) * 0.1) + 1
        if wheel_cost_percentage > 1:
            total_cost = power_type_costs + tyres_costs + (armour_costs*wheel_cost_percentage) + attack_costs + special_costs
        elif wheel_cost_percentage <= 1:
            total_cost = power_type_costs + tyres_costs + armour_costs + attack_costs + special_costs

        
        
        if power_type == "None" or tyres == "None" or armour == "None" or attack == "None" or algo == "None" or flag_pattern == "None" or special == "None":
            Invalid_data_warning = "Must pick an option!"
            return render_template("buggy-form.html", power_type_warning=Invalid_data_warning if power_type == "None" else None,
                                                    tyres_warning=Invalid_data_warning if tyres == "None" else None,
                                                    armour_warning=Invalid_data_warning if armour == "None" else None,
                                                    attack_warning=Invalid_data_warning if attack == "None" else None,
                                                    algo_warning=Invalid_data_warning if algo == "None" else None,
                                                    flag_pattern_warning=Invalid_data_warning if flag_pattern == "None" else None,
                                                    special_warning=Invalid_data_warning if special == "None" else None,
                                                    qty_wheels=qty_wheels, flag_color=flag_color, flag_color_secondary=flag_color_secondary, qty_tyres=qty_tyres)
        
        try:
            flag_color = flag_color.upper()
            flag_color_secondary = flag_color_secondary.upper()
            qty_wheels = int(qty_wheels)
            qty_tyres = int(qty_tyres)
            with sql.connect(DATABASE_FILE) as con:
                cur = con.cursor()
                cur.execute(
                    "UPDATE buggies SET qty_wheels=?, qty_tyres=?, flag_color=?, flag_color_secondary=?, flag_pattern=?, power_type=?, tyres=?, armour=?, attack=?, algo=?, special=?, total_cost=? WHERE id=?",
                (qty_wheels, qty_tyres, flag_color, flag_color_secondary, flag_pattern, power_type, tyres, armour, attack, algo, special, total_cost, DEFAULT_BUGGY_ID)
                )
                con.commit()
                msg = "Record successfully saved"
        except:
            con.rollback()
            msg = "Error in update operation"
        finally:
            con.close()
        return render_template("updated.html", msg=msg)

#------------------------------------------------------------
# a page for displaying the buggy
#------------------------------------------------------------
@app.route('/buggy')
def show_buggies():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies")
    record = cur.fetchone(); 
    return render_template("buggy.html", buggy = record)

#------------------------------------------------------------
# a placeholder page for editing the buggy: you'll need
# to change this when you tackle task 2-EDIT
#------------------------------------------------------------
@app.route('/edit')
def edit_buggy():
    return render_template("buggy-form.html")

#------------------------------------------------------------
# You probably don't need to edit this... unless you want to ;)
#
# get JSON from current record
#  This reads the buggy record from the database, turns it
#  into JSON format (excluding any empty values), and returns
#  it. There's no .html template here because it's *only* returning
#  the data, so in effect jsonify() is rendering the data.
#------------------------------------------------------------

@app.route('/poster')
def poster():
  return render_template('poster.html')


@app.route('/json')
def summary():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies WHERE id=? LIMIT 1", (DEFAULT_BUGGY_ID))

    buggies = dict(zip([column[0] for column in cur.description], cur.fetchone())).items() 
    return jsonify({ key: val for key, val in buggies if (val != "" and val is not None) })

# You shouldn't need to add anything below this!
if __name__ == '__main__':
    alloc_port = os.environ.get('CS1999_PORT') or 5000
    app.run(debug=True, host="0.0.0.0", port=alloc_port)

