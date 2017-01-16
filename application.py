import pyowm
import random

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import gettempdir

# API Key to access OpenWeatherMap API
owm = pyowm.OWM('647613b0420866b915de469efc8b2732')

# configure application
app = Flask(__name__)


# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

def apology(top=""):
    """Renders message as an apology to user.

    If you wish to use this function with Pagedraw, make sure you create
    a Pagedraw page with file path `templates/apology.html` that displays
    the variables `top` and `bottom`.
    """
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), ("_", "__"), ("?", "~q"),
            ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=escape(top))
    
@app.route("/", methods = ["GET", "POST"])
def index():
    # if user reached route via POST
    if request.method == "POST":
        
        # ensures user actually inputs valid zipcode.
        if not request.form.get("place"):
            return apology("please enter a valid zip code")
        
        if not request.form.get("place").isdigit():
            return apology("please enter a valid zip code")
        
        if len(request.form.get("place")) != 5:
            return apology("please enter a valid zip code")
        
        # ensures exactly one gender box is checked
        Male = request.form.get("male")
        Female = request.form.get("female")
        if not Male and not Female:
            return apology("please check gender box")
        if Male and Female:
            return apology("please check only one gender box")
        
        
        else: 
            # store zipcode that user inputted
            zipcode = request.form.get("place")
            
            rows = db.execute("SELECT latitude, longitude FROM places WHERE postal_code=:postal_code", postal_code=zipcode)
            # check if zipcode entered exists
            if len(rows) != 1:
                return apology("please enter a valid zip code")
            
            # get weather information through pyowm wrapper 
            observation = owm.weather_at_coords(rows[0]["latitude"], rows[0]["longitude"])
            w = observation.get_weather()
            l = observation.get_location()
            
            # storing information about location's temperature, weather, etc. in a location dict object
            location = {}
            location["name"] = l.get_name()
            location["temperature"] = w.get_temperature('fahrenheit')['temp']
            location["status"] = w.get_detailed_status() 

            # defining variable for "hot" temperature cutoff
            hottemp = 80
            coldtemp = 60
            
            # if male
            if Male:
                # generate random male outfit for hot temperatures
                if w.get_temperature('fahrenheit')['temp'] > hottemp:
                    id = random.randint(1, 5)
                    outfit = db.execute("SELECT top, bottom, shoes, accessory, toppicture, bottompicture, shoespicture, accessorypicture, toppiclink, bottompiclink, shoepiclink, accessorypiclink FROM MaleOutfits WHERE id=:id", id=id)
                # generate random male outfit for cold temperatures
                elif w.get_temperature('fahrenheit')['temp'] < coldtemp:
                    id = random.randint(6, 10)
                    outfit = db.execute("SELECT top, bottom, shoes, accessory, toppicture, bottompicture, shoespicture, accessorypicture, toppiclink, bottompiclink, shoepiclink, accessorypiclink FROM MaleOutfits WHERE id=:id", id=id)
                # generate random male outfit for medium temperatures
                else:
                    id = random.randint(11, 15)
                    outfit = db.execute("SELECT top, bottom, shoes, accessory, toppicture, bottompicture, shoespicture, accessorypicture, toppiclink, bottompiclink, shoepiclink, accessorypiclink FROM MaleOutfits WHERE id=:id", id=id)
                
                # adding links to purchase items of outfit at Amazon in men's section 
                outfit[0]["toplink"] = "https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=" + outfit[0]["top"] +"+men"
                outfit[0]["bottomlink"] = "https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=" + outfit[0]["bottom"] + "+men"
                outfit[0]["shoeslink"] = "https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=" + outfit[0]["shoes"] +"+men"
                outfit[0]["accessorylink"] = "https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=" + outfit[0]["accessory"] +"+men"
                
            # if female
            elif Female:
                # generate random female outfit for hot temperatures
                if w.get_temperature('fahrenheit')['temp'] > hottemp:
                    id = random.randint(1, 5)
                    outfit = db.execute("SELECT top, bottom, shoes, accessory, toppicture, bottompicture, shoespicture, accessorypicture, toppiclink, bottompiclink, shoepiclink, accessorypiclink FROM FemaleOutfits WHERE id=:id", id=id)
                # generate random female outfit for cold temperatures
                elif w.get_temperature('fahrenheit')['temp'] < coldtemp:
                    id = random.randint(6, 10)
                    outfit = db.execute("SELECT top, bottom, shoes, accessory, toppicture, bottompicture, shoespicture, accessorypicture, toppiclink, bottompiclink, shoepiclink, accessorypiclink FROM FemaleOutfits WHERE id=:id", id=id)
                # generate random female outfit for medium temperatures
                else:
                    id = random.randint(11, 15)
                    outfit = db.execute("SELECT top, bottom, shoes, accessory, toppicture, bottompicture, shoespicture, accessorypicture, toppiclink, bottompiclink, shoepiclink, accessorypiclink FROM FemaleOutfits WHERE id=:id", id=id)
                
                # adding links to purchase items of outfit at Amazon in women's section 
                outfit[0]["toplink"] = "https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=" + outfit[0]["top"] + "+women"
                outfit[0]["bottomlink"] = "https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=" + outfit[0]["bottom"] + "+women"
                outfit[0]["shoeslink"] = "https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=" + outfit[0]["shoes"] + "+women"
                outfit[0]["accessorylink"] = "https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=" + outfit[0]["accessory"] + "+women"
           

            # replace "+" in outfit items with spaces for html table
            outfit[0]["top"] = outfit[0]["top"].replace("+", " ")
            outfit[0]["bottom"] = outfit[0]["bottom"].replace("+", " ")
            outfit[0]["shoes"] = outfit[0]["shoes"].replace("+", " ")
            outfit[0]["accessory"] = outfit[0]["accessory"].replace("+", " ")
            
            return render_template("results.html", outfit=outfit, location=location)
            
# if user reached route via GET
    else:
        return render_template("index.html")
