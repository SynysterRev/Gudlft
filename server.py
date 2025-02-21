import json
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    club = next((club for club in clubs if club['email'] == request.form['email']), None)
    if club is None:
        flash("This email is not registered")
        return render_template('index.html')
    else:
        return render_template('welcome.html',club=club,competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchase_places():
    competition = next((c for c in competitions if c['name'] == request.form[
        'competition']), None)
    club = next((c for c in clubs if c['name'] == request.form['club']), None)

    if not club:
        flash("This club is not registered")
        return render_template('index.html')

    if not competition:
        flash("This competition is not registered")
        return render_template('index.html')

    left_places = int(competition['numberOfPlaces'])
    places_required = int(request.form['places'])

    if places_required < 0 or places_required > 12:
        flash(f"Place must be between 0 and 12")
        return render_template('booking.html', club=club, competition=competition)

    if left_places < places_required:
        flash("There is only {} places available".format(left_places))
        return render_template('booking.html', club=club, competition=competition)

    competition['numberOfPlaces'] = left_places - places_required
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))