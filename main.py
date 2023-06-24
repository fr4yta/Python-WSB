from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__, static_folder='templates')
app.secret_key = "325bc16f39b68a45778bf14bd85e84a1"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)


def getAverageGoldPrice():
    url = 'https://api.nbp.pl/api/cenyzlota/last/255?format=json'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        monthlyPrices = {}

        for item in data:
            date = item['data']
            month = date[0:7]
            value = item['cena']

            if month in monthlyPrices:
                monthlyPrices[month].append(value)
            else:
                monthlyPrices[month] = [value]

        averagePriceGold = {}

        for month, values in monthlyPrices.items():
            average = sum(values) / len(values)
            averagePriceGold[month] = average

        return averagePriceGold
    else:
        return None


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Nazwa użytkownika jest już zajęta!', 'danger')

            return redirect('/register')

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Pomyślnie zarejestrowano użytkownika!', 'success')

        return redirect('/register')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = username

            return redirect('/dashboard')
        else:
            flash('Nieprawidłowe dane logowania!', 'danger')

            return redirect('/login')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', goldData=getAverageGoldPrice())
    else:
        flash('Najpierw się zaloguj!', 'danger')

        return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)
