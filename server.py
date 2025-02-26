import json
import logging
from datetime import datetime

from flask import Flask, render_template, request, redirect, flash, url_for, session


def load_clubs(path='clubs.json'):
    try:
        with open(path) as c:
            list_of_clubs = json.load(c).get('clubs', [])
            return list_of_clubs
    except FileNotFoundError:
        raise FileNotFoundError(f"{path} not found for clubs")
    except json.JSONDecodeError:
        logging.error(f"Invalid json {path}")
        raise



def load_competitions(path='competitions.json'):
    try:
        with open(path) as comps:
            list_of_competitions = json.load(comps).get('competitions', [])
            return list_of_competitions
    except FileNotFoundError:
        raise FileNotFoundError(f"{path} not found for competitions")
    except json.JSONDecodeError:
        logging.error(f"Invalid json {path}")
        raise


def update_clubs(path='clubs.json'):
    with open(path, 'w') as c:
        final = {"clubs": clubs}
        json.dump(final, c, indent=4)


def update_competitions(path='competitions.json'):
    with open(path, 'w') as c:
        final = {"competitions": competitions}
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
    competition['numberOfPlaces'] = str(
        int(competition['numberOfPlaces']) - places_required)
    update_competitions()
    club['points'] = str(int(club['points']) - places_required)
    club_data = find_club_by_name(club['name'])
    if club_data:
        club_data['points'] = club['points']
        update_clubs()


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = load_competitions()
clubs = load_clubs()


@app.route('/')
def index():
    return render_template('index.html')


@app.template_filter('is_past')
def is_past(date):
    converted_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    return converted_date < datetime.today()


@app.route('/showSummary', methods=['GET', 'POST'])
def show_summary():
    if request.method == 'POST':
        club = find_club_by_email(request.form['email'])
    else:
        club = session.get('club')
    if club is None:
        flash("This email is not registered")
        return redirect(url_for('index'))
    else:
        session['club'] = club
        return render_template('welcome.html', competitions=competitions)


@app.route('/book/<competition>')
def book(competition):
    found_competition = find_competition_by_name(competition)
    if found_competition:
        if is_past(found_competition['date']):
            return redirect(url_for('show_summary'))

        return render_template('booking.html', competition=found_competition)
    else:
        flash("Something went wrong-please try again")
        return redirect(url_for('show_summary'))


@app.route('/purchasePlaces', methods=['GET', 'POST'])
def purchase_places():
    if request.method == 'GET':
        return redirect(url_for('show_summary'))

    competition = find_competition_by_name(request.form['competition'])
    club = session.get('club')

    if not club:
        flash("This club is not registered")
        return redirect(url_for('index'))

    if find_club_by_name(club['name']) is None:
        flash("This club is not registered")
        return redirect(url_for('index'))

    if not competition:
        flash("This competition is not registered")
        return redirect(url_for('show_summary'))

    left_places = int(competition['numberOfPlaces'])
    places_required = int(request.form['places'])
    points = int(club['points'])

    if not validate_places(places_required):
        flash(f"Place must be between 0 and 12")
        return render_template('booking.html', competition=competition)

    if not enough_places(competition, places_required):
        flash("There is only {} places available".format(left_places))
        return render_template('booking.html', competition=competition)

    if not enough_points(club, places_required):
        flash("You have only {} points available".format(points))
        return render_template('booking.html', competition=competition)

    book_places(club, competition, places_required)
    flash('Great-booking complete!')
    return redirect(url_for('show_summary'))


@app.route('/points', methods=['GET'])
def see_points():
    return render_template('points.html', clubs=clubs)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
