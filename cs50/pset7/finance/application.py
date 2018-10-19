import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    portfolio = db.execute("SELECT * FROM portfolio WHERE user_id = :user_id", user_id=session['user_id'])
    cash = db.execute("SELECT cash FROM users WHERE id = :id", id = session["user_id"])

    print(portfolio)
    print(cash)

    if len(portfolio) < 1:
        return render_template("index_new.html")

    user_cash = usd(cash[0]['cash'])
    total = cash[0]['cash']

    for stock in portfolio:
        stock['value'] = stock['shares'] * stock['price']
        value = stock['shares'] * stock['price']
        total += value
        stock['value'] = usd(value)
        stock['price'] = usd(stock['price'])

    return render_template("index.html", stocks=portfolio, cash=user_cash, total=usd(total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("symbol"):
            return apology("must enter symbol", 403)

        # Ensure password was submitted
        elif not request.form.get("shares"):
            return apology("must enter shares amount", 403)

        # Store and format info
        stock = lookup(request.form.get("symbol"))
        shares = request.form.get("shares")
        shares = int(shares)

        # Ensure stock is found
        if not stock:
            return apology("stock symbol does not exist")

        # Ensure share is a postive num
        if not shares or shares <= 0:
            return apology("select one or more shares")

        # Get users cash
        row = db.execute("SELECT cash FROM users WHERE id = :id", id = session["user_id"])
        available_cash = row[0]['cash']

        # Ensure user has enough money to buy x number of shares
        spending = shares * stock['price']
        if spending > available_cash:
            return apology("not enough money available")
        else:
            existing_shares = db.execute("SELECT shares FROM portfolio WHERE user_id = :user_id AND symbol = :symbol",
                          user_id=session["user_id"], symbol=stock["symbol"])

            if not existing_shares:
                db.execute("INSERT INTO portfolio (user_id, symbol, shares, price, name) VALUES (:user_id, :symbol, :shares, :price, :name)",
                            user_id=session["user_id"], symbol=stock['symbol'], shares=shares, price=stock['price'], name=stock['name'])
            else:
                shares_total = existing_shares[0]["shares"] + shares
                db.execute("UPDATE portfolio SET shares=:shares WHERE user_id=:id AND symbol=:symbol",
                            shares=shares_total, id=session["user_id"], symbol=stock['symbol'])
            db.execute("UPDATE users SET cash=cash - :spending WHERE id=:id", spending=spending, id=session["user_id"])

        return redirect("/")

    # Return template for GET request
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        stock = lookup(request.form.get("symbol"))
        if not stock:
            return apology("invaild stock symbol", 403)
        stock['price'] = usd(stock['price'])
        return render_template("stockInfo.html", stock=stock)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        #Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must enter in password again", 403)

        # Ensure passwords are a match
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords must be a match", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Check if user already exists
        if len(rows) == 1:
            return apology("username already exists", 403)

        # Insert that user and password into the table
        db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",
                    username=request.form.get("username"), hash=generate_password_hash(request.form.get("password")))

         # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
