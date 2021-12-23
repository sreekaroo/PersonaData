from flask import Flask, render_template, request, redirect, url_for, flash, g, session

import get_credentials
from conection import Connection

app = Flask(__name__)
app.secret_key = "super secret key"

# need to change these based on local credentials
dbUsername = 'root'
dbPassword = 'root'
dbHost = 'localhost'


def get_db():
    """establishes the database connection and returns db after storing in global context"""
    if 'db' not in g:
        conn, error = Connection(username=dbUsername, password=dbPassword,
                                 host=dbHost).connect()
        if conn is None:
            return None
        g.db = conn
    return g.db


@app.teardown_appcontext
def closeDB(exception):
    """disconnects from database at end of request life"""
    db = g.pop('db', None)

    if db is not None:
        db.close()

    if exception is not None:
        print(exception)


@app.route('/')
def index():
    """index page """
    return render_template('index.html')


@app.route("/login", methods=['POST'])
def login():
    """validates and logs in a user """

    username = request.form.get('username')
    password = request.form.get('password')

    db = get_db()
    cur = db.cursor()
    cur.callproc('is_valid_user', [username, password])
    isValid = cur.fetchone().get('True')
    if not isValid or len(username) == 0 or len(password) == 0:
        flash("Invalid log in, please try again")
        return redirect(url_for('index'))

    print(username)
    print(password)
    session['username'] = username
    return render_template('landingPage.html')


@app.route("/deleteUser", methods=['GET'])
def deleteUser():
    db = get_db()
    cur = db.cursor()
    cur.callproc('delete_user', [session.get('username')])

    return redirect(url_for('index'))


@app.route("/resetPassword", methods=['GET', 'POST'])
def resetPassword():
    """resetting the password of a user"""

    if request.method == 'GET':
        return render_template('forgotPassword.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')

        # need to fill out
        db = get_db()
        cur = db.cursor()
        cur.callproc('reset_password', [username, password])

        print(username)
        print(password)
        isValid = cur.fetchone().get('True')
        if not isValid or len(username) == 0 or len(password) == 0:
            flash("Invalid username or password, please try again")
            return redirect(url_for('index'))

        return redirect(url_for('index'))


@app.route("/register", methods=['POST'])
def register():
    """registering a new user in the database"""

    username = request.form.get('registerUsername')
    password = request.form.get('registerPassword')
    country = request.form.get('country')
    continent = request.form.get('continent')
    city = request.form.get('city')

    db = get_db()
    cur = db.cursor()
    cur.callproc("register", (username, password, country, city, continent, ''))

    # need to fill out
    isValid = cur.fetchone().get('True')
    if not isValid or len(username) == 0 or len(password) == 0 or len(country) == 0 or len(city) == 0 or len(
            continent) == 0:
        flash("Invalid Registration please try again")
        return redirect(url_for('index'))

    print(username)
    print(password)
    print(country)

    session['username'] = username

    return render_template('landingPage.html')


@app.route("/big5Quiz", methods=['GET'])
def takeQuiz():
    """displays the quiz to be taken"""

    return render_template('quiz.html')


@app.route("/submitResponse", methods=['POST'])
def submitResponses():
    """stores the responses of most recent quiz taken"""

    responses = []
    for i in range(1, 51):
        inputTag = "q" + str(i)
        response = request.form.get(inputTag)
        responses.append(int(response))

    db = get_db()
    cur = db.cursor()

    username = session.get('username')
    if username is None:
        flash("I dont know how u got here!")
        return redirect(url_for('index'))

    for qId, answer in enumerate(responses):
        cur.callproc("store_answer", [answer, username, qId + 1])

    return redirect(url_for('results'))


def getEvaluation(traitScore, trait):
    """Returns the message associated with trait score and
    trait according to BIg 5 personality theory"""

    if traitScore < 15:
        return "You have low " + trait

    elif traitScore <= 30:
        return "You have average " + trait

    else:
        return "You have high " + trait


@app.route("/results", methods=['GET'])
def results():
    """displays the results of the most recent quiz for the logged in user
    and computes/stores the personality scores for logged in user"""

    db = get_db()
    cur = db.cursor()

    cur.callproc('get_specific_scores', [session.get('username'), 1, 10])
    rows = cur.fetchall()
    ExtraversionScores = [q.get('resp') for q in rows]

    print(len(ExtraversionScores))

    cur.callproc('get_specific_scores', [session.get('username'), 11, 20])
    rows = cur.fetchall()
    NeuroticismScores = [q.get('resp') for q in rows]

    cur.callproc('get_specific_scores', [session.get('username'), 21, 30])
    rows = cur.fetchall()
    AgreeablenessScores = [q.get('resp') for q in rows]

    cur.callproc('get_specific_scores', [session.get('username'), 31, 40])
    rows = cur.fetchall()
    ConscientiousnessScores = [q.get('resp') for q in rows]

    cur.callproc('get_specific_scores', [session.get('username'), 41, 50])
    rows = cur.fetchall()
    OpennessScores = [q.get('resp') for q in rows]

    Extraversion = sum(ExtraversionScores)
    Neuroticism = sum(NeuroticismScores)
    Agreeableness = sum(AgreeablenessScores)
    Conscientiousness = sum(ConscientiousnessScores)
    Openness = sum(OpennessScores)

    session['ext'] = Extraversion
    session['neuro'] = Neuroticism
    session['agr'] = Agreeableness
    session['csn'] = Conscientiousness
    session['opn'] = Openness

    cur2 = db.cursor()
    cur2.callproc('store_personality',
                  [Agreeableness, Extraversion, Neuroticism, Openness, Conscientiousness, session.get('username')])

    ExtraversionString = getEvaluation(Extraversion, 'Extraversion')
    NeuroticismString = getEvaluation(Neuroticism, 'Neuroticism')
    AgreeablenessString = getEvaluation(Agreeableness, 'Agreeableness')
    ConscientiousnessString = getEvaluation(Conscientiousness, 'Conscientiousness')
    OpennessString = getEvaluation(Openness, 'Openness')

    cur = db.cursor()
    cur.callproc('get_all_scores')
    avgAllUsers = cur.fetchone()

    cur.close()

    cur = db.cursor()
    cur.callproc('get_user_loc', [session.get('username')])
    locations = cur.fetchone()
    print(locations)
    continent = locations.get('continent')
    country = locations.get('countryOrigin')

    print(continent)

    cur = db.cursor()
    cur.callproc('get_avg_continent_scores', [continent])
    avgContinent = cur.fetchone()
    cur.close()

    cur = db.cursor()
    cur.callproc('get_avg_country_scores', [country])
    avgCountry = cur.fetchone()
    cur.close()

    print(avgAllUsers)

    return render_template('results.html', ext=ExtraversionString, neuro=NeuroticismString,
                           agr=AgreeablenessString, cns=ConscientiousnessString, opn=OpennessString,
                           extNum=Extraversion, neuroNum=Neuroticism, agrNum=Agreeableness, cnsNum=Conscientiousness,
                           opnNum=Openness, avgAllUsers=avgAllUsers, avgContinent=avgContinent, avgCountry=avgCountry,
                           continent=locations.get('continent'), country=locations.get('countryOrigin'))


if __name__ == "__main__":
    app.run(debug=True)
