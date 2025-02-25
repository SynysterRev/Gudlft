import json
from datetime import datetime

from flask import Flask, render_template, request, redirect, flash, url_for


def loadClubs():
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions


def update_clubs():
    with open('clubs.json', 'w') as c:
        final = {"clubs": clubs}
        json.dump(final, c, indent=4)


def find_competition_by_name(name):
    return next((c for c in competitions if c['name'] == name), None)


def find_club_by_name(name):
    return next((c for c in clubs if c['name'] == name), None)


def find_club_by_email(email):
    return next((c for c in clubs if c['email'] == email), None)


def validate_places(places_required):
    return 0 <= places_required <= 12


def enough_places(competition, places_required):
    return int(competition['numberOfPlaces']) >= places_required


def enough_points(club, places_required):
    return int(club['points']) >= places_required


def book_places(club, competition, places_required):
    competition['numberOfPlaces'] = str(int(competition['numberOfPlaces']) - places_required)
    club['points'] = str(int(club['points']) -places_required)
    update_clubs()


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()


@app.route('/')
def index():
    return render_template('index.html')


@app.template_filter('is_past')
def is_past(date):
    converted_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    return converted_date < datetime.today()

@app.route('/showSummary', methods=['POST'])
def show_summary():
    club = find_club_by_email(request.form['email'])
    if club is None:
        flash("This email is not registered")
        return render_template('index.html')
    else:
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition, club):
    found_club = find_club_by_name(club)
    found_competition = find_competition_by_name(competition)
    if found_club and found_competition:
        if is_past(found_competition['date']):
            return render_template('welcome.html', club=found_club, competitions=competitions)

        return render_template('booking.html', club=found_club,
                               competition=found_competition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces', methods=['POST'])
def purchase_places():
    competition = find_competition_by_name(request.form['competition'])
    club = find_club_by_name(request.form['club'])

    if not club:
        flash("This club is not registered")
        return render_template('index.html')

    if not competition:
        flash("This competition is not registered")
        return render_template('index.html')

    left_places = int(competition['numberOfPlaces'])
    places_required = int(request.form['places'])
    points = int(club['points'])

    if not validate_places(places_required):
        flash(f"Place must be between 0 and 12")
        return render_template('booking.html', club=club, competition=competition)

    if not enough_places(competition, places_required):
        flash("There is only {} places available".format(left_places))
        return render_template('booking.html', club=club, competition=competition)

    if not enough_points(club, places_required):
        flash("You have only {} points available".format(points))
        return render_template('booking.html', club=club, competition=competition)

    book_places(club, competition, places_required)
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
