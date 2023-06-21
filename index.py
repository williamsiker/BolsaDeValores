from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_wtf.csrf import CSRFProtect,generate_csrf, validate_csrf
from config import config
from api import get_stock_data, calculate_technical_indicators, simulate_trading, plot_stock_data

from models.ModelUser import ModelUser
from models.entities.User import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'B!1w8NAt1T^%kvhUI*S^'
csrf = CSRFProtect(app)
db = MySQL(app)
login_manager_app = LoginManager(app)

@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db, id)

@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/simulate",methods=['GET', 'POST'])
def simulate():
    if request.method == 'POST':
        ticker = request.form['ticker']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        capital = float(request.form['capital'])

        stock_data = get_stock_data(ticker, start_date, end_date)
        stock_data = calculate_technical_indicators(stock_data)
        simulate_trading(stock_data, capital)
        plot_stock_data(stock_data)
        buy_messages = stock_data[stock_data['Signal'] == 'BUY'].apply(lambda row: f"FECHA DE COMPRA: {row['Date']} - Precio: {row['Close']} - Intercambios: {row['Shares']} - Valor de Compra: {row['Portfolio Value']}", axis=1).tolist()
        sell_messages = stock_data[stock_data['Signal'] == 'SELL'].apply(lambda row: f"FECHA DE VENTA: {row['Date']} - Precio: {row['Close']} - Intercambios: {row['Shares']} - Valor de Venta : {row['Portfolio Value']}", axis=1).tolist()
        return render_template('home.html', buy_messages=buy_messages, sell_messages=sell_messages)
    else:
        return render_template('home.htlm')

@app.route("/")
def index():
    return redirect(url_for('login'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        # print(request.form['username'])
        user = User(0, request.form['username'], request.form['password'])
        logged_user = ModelUser.login(db, user)
        if logged_user != None:
            if logged_user.password:
                login_user(logged_user)
                return redirect(url_for('home'))
            else:
                flash("Contraseña Invalida!")
                return render_template('auth/login.html')
        else:
            flash("Usuario Invalido")
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html') 


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/protected")
@login_required
def protected():
    return "<h1>Hola<h1/>"

def status_401(error):
    return redirect(url_for('login'))

def status_404(error):
    return "<h1>No encontrada<h1/>"

if __name__ == "__main__":
    app.config.from_object(config['development'])
    #csrf.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run(debug=False,host='0.0.0.0') #debug=False,host='0.0.0.0'
