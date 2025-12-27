import sqlite3
from flask import Flask, render_template, g, request, redirect, url_for, session
import os
from datetime import datetime
from functools import wraps
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---

BASEDIR = os.path.abspath(os.path.dirname(__file__))
ACCOUNT_HOLDER_NAME = os.getenv('ACCOUNT_HOLDER_NAME', 'NAME')
# Load DB filename from .env (defaults to 'toybank.db' if not set)
DB_FILENAME = os.getenv('DB_FILENAME', 'toybank.db')
DATABASE = os.path.join(BASEDIR,'data', DB_FILENAME)

# Load teller password and secret key from .env
TELLER_PASSWORD = os.getenv('TELLER_PASSWORD')
# Note: os.getenv returns None if not found; Flask handles None gracefully by failing
# if secret_key is not set, which is desired for security.
app = Flask(__name__)
app.secret_key = os.getenv('TOYBANK_SECRET_KEY')

# --- Decorator for Password Protection ---

def login_required(f):
    """Protects routes by requiring a user to be logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the 'teller_logged_in' session variable is True
        if not session.get('teller_logged_in'):
            # If not logged in, redirect them to the login page
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# --- Database Helper Functions ---

def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        # Configure sqlite3 to return rows as dictionaries (access columns by name)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Closes the database connection at the end of the request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initializes the database schema if it doesn't exist."""
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        # SQL to create the transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                withdrawal REAL DEFAULT 0.00,
                deposit REAL DEFAULT 0.00
            );
        ''')
        db.commit()
        
        # Add an initial transaction if the table is empty
        cursor.execute('SELECT COUNT(*) FROM transactions')
        if cursor.fetchone()[0] == 0:
            initial_date = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                INSERT INTO transactions (date, description, deposit, withdrawal)
                VALUES (?, ?, ?, ?);
            ''', (initial_date, 'Welcome to Toybank', 0.00, 0.00))
            db.commit()
        
    print(f"Database initialized successfully at {DATABASE}.")

# Run initialization function on startup if the database file doesn't exist
if not os.path.exists(DATABASE):
    init_db()


# --- Authentication Routes ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles the login process for the Bank Teller."""
    if request.method == 'POST':
        password = request.form['password']
        if password == TELLER_PASSWORD:
            session['teller_logged_in'] = True
            # Redirect to the 'next' URL parameter if available, otherwise to the transaction form
            next_url = request.args.get('next') or url_for('add_transaction')
            return redirect(next_url)
        else:
            return render_template('login.html', error='Incorrect password. Try again.')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logs the teller out and redirects to the main ledger."""
    session.pop('teller_logged_in', None)
    return redirect(url_for('ledger_view'))


# --- Web Routes ---

@app.route('/')
def ledger_view():
    """
    Main route for the daughter's ledger view.
    Fetches all transactions, calculates the running balance, and displays the table.
    """
    db = get_db()
    
    # Fetch all transactions, ordered by date (oldest first)
    transactions = db.execute(
        'SELECT id, date, description, withdrawal, deposit FROM transactions ORDER BY date ASC, id ASC;'
    ).fetchall()
    
    # Calculate running balance and total balance
    current_balance = 0.00
    ledger = []
    
    for t in transactions:
        current_balance += t['deposit']
        current_balance -= t['withdrawal']
        
        # Format the transaction data for display
        ledger.append({
            'id': t['id'], # Keep the ID for the edit link
            'date': t['date'],
            'description': t['description'],
            # Show a dash if the amount is zero
            'withdrawal': f"${t['withdrawal']:.2f}" if t['withdrawal'] > 0 else '--',
            'deposit': f"${t['deposit']:.2f}" if t['deposit'] > 0 else '--',
            'running_balance': f"${current_balance:.2f}"
        })
        
    # The final balance is the last calculated balance
    final_balance_display = f"${current_balance:.2f}"
    
    return render_template('index.html', 
                           transactions=ledger, 
                           current_balance=final_balance_display,
                           teller_logged_in=session.get('teller_logged_in'),
                           account_holder_name=ACCOUNT_HOLDER_NAME) # Pass login status for conditional actions

@app.route('/add_transaction', methods=['GET', 'POST'])
@login_required 
def add_transaction():
    """
    Bank Teller Portal route.
    GET: Displays the form for adding a new transaction.
    POST: Processes the form submission and inserts the record into the database.
    """
    if request.method == 'POST':
        try:
            # Extract form data
            date = request.form['date']
            description = request.form['description']
            # Convert deposits and withdrawals to float, defaulting to 0.00 if empty
            deposit = float(request.form.get('deposit') or 0.00)
            withdrawal = float(request.form.get('withdrawal') or 0.00)

            # Basic validation: ensure either deposit OR withdrawal is present
            if deposit == 0.00 and withdrawal == 0.00:
                today = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
                return render_template('add_transaction.html', error="Must enter a deposit or a withdrawal amount.", today=today)

            # Insert the new transaction into the database
            db = get_db()
            db.execute('''
                INSERT INTO transactions (date, description, deposit, withdrawal)
                VALUES (?, ?, ?, ?);
            ''', (date, description, deposit, withdrawal))
            db.commit()
            
            # Redirect to the main ledger page after successful submission
            return redirect(url_for('ledger_view'))

        except ValueError:
            return render_template('add_transaction.html', error="Amounts must be valid numbers.")
        except Exception as e:
            print(f"Database error: {e}")
            return render_template('add_transaction.html', error="An unexpected error occurred during submission.")

    # GET request: Display the form
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('add_transaction.html', today=today)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(id):
    """
    Allows editing an existing transaction.
    """
    db = get_db()
    
    if request.method == 'POST':
        try:
            date = request.form['date']
            description = request.form['description']
            deposit = float(request.form.get('deposit') or 0.00)
            withdrawal = float(request.form.get('withdrawal') or 0.00)

            if deposit == 0.00 and withdrawal == 0.00:
                # Fetch the current transaction data again to pass back to the form
                transaction = db.execute('SELECT * FROM transactions WHERE id = ?', (id,)).fetchone()
                return render_template('edit_transaction.html', error="Must enter a deposit or a withdrawal amount.", transaction=transaction)
            
            db.execute('''
                UPDATE transactions SET date = ?, description = ?, deposit = ?, withdrawal = ?
                WHERE id = ?
            ''', (date, description, deposit, withdrawal, id))
            db.commit()
            
            return redirect(url_for('ledger_view'))

        except Exception as e:
            print(f"Database update error: {e}")
            # Refetch the transaction to display the form again with the error
            transaction = db.execute('SELECT * FROM transactions WHERE id = ?', (id,)).fetchone()
            return render_template('edit_transaction.html', error="An error occurred during update.", transaction=transaction)
    
    # GET request: Fetch transaction data and display the form
    transaction = db.execute('SELECT * FROM transactions WHERE id = ?', (id,)).fetchone()
    
    if transaction is None:
        return redirect(url_for('ledger_view')) # Redirect if ID is invalid
    
    return render_template('edit_transaction.html', transaction=transaction)


# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True)