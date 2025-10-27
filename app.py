import os
import time
import psycopg2
import logging
from flask import Flask, render_template, request, redirect

# --- 1. Set up the App's Diary (Logging) ---
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

app = Flask(__name__)
logging.info("Chef is in the kitchen! The app is starting.")

# --- 2. How to connect to the database ---
def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    tries = 5
    while tries > 0:
        try:
            conn = psycopg2.connect(database_url)
            logging.info("Successfully connected to the database.")
            return conn
        except:
            tries -= 1
            logging.warning("Database isn't ready. Waiting and trying again...")
            time.sleep(5)
    logging.error("Could not connect to the database. Is it running?")
    raise Exception("Could not connect to the database.")

# --- 3. How to write in our activity book ---
def log_activity(conn, action, details=""):
    with conn.cursor() as cur:
        cur.execute(
            'INSERT INTO activity_log (action_type, details) VALUES (%s, %s)',
            (action, details)
        )
    conn.commit()

# --- 4. Get the kitchen ready for the first time ---
def init_db():
    conn = get_db_connection()
    with conn.cursor() as cur:
        # Create a table for expenses if it's not there
        cur.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id SERIAL PRIMARY KEY, description TEXT, amount REAL,
                created_at DATE DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        # Create a table for our activity book if it's not there
        cur.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id SERIAL PRIMARY KEY, action_type TEXT, details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
    conn.commit()
    log_activity(conn, "APP_START", "Tables are ready.")
    conn.close()

# --- 5. What to do when someone visits our website ---
@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    with conn.cursor() as cur:
        # If the user submitted the "Add Expense" form
        if request.method == 'POST':
            desc = request.form['description']
            amount = float(request.form['amount'])
            cur.execute('INSERT INTO expenses (description, amount) VALUES (%s, %s)', (desc, amount))
            conn.commit()
            log_activity(conn, "NEW_EXPENSE", f"Added '{desc}' for ${amount}")
            logging.info(f"User added a new expense: {desc}")
            return redirect('/')

        # If the user is just looking at the page
        cur.execute('SELECT * FROM expenses ORDER BY created_at DESC;')
        all_expenses = cur.fetchall()
    conn.close()
    
    # Use the index.html drawing and show the user the list of expenses
    return render_template('index.html', expenses=all_expenses)

# --- 6. Edit an expense ---
@app.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    conn = get_db_connection()
    
    if request.method == 'POST':
        # Update the expense
        new_desc = request.form['description']
        new_amount = float(request.form['amount'])
        
        with conn.cursor() as cur:
            # Get old values for logging
            cur.execute('SELECT description, amount FROM expenses WHERE id = %s', (expense_id,))
            old_expense = cur.fetchone()
            
            # Update the expense
            cur.execute(
                'UPDATE expenses SET description = %s, amount = %s WHERE id = %s',
                (new_desc, new_amount, expense_id)
            )
            conn.commit()
            
            # Log the change
            log_activity(conn, "EDIT_EXPENSE", 
                        f"Changed '{old_expense[0]}' (${old_expense[1]}) to '{new_desc}' (${new_amount})")
        
        conn.close()
        return redirect('/')
    
    # Show edit form
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM expenses WHERE id = %s', (expense_id,))
        expense = cur.fetchone()
    conn.close()
    
    if not expense:
        return "Expense not found", 404
    
    return render_template('edit.html', expense=expense)

# --- 7. Delete an expense ---
@app.route('/delete/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    conn = get_db_connection()
    
    with conn.cursor() as cur:
        # Get expense details for logging
        cur.execute('SELECT description, amount FROM expenses WHERE id = %s', (expense_id,))
        expense = cur.fetchone()
        
        if expense:
            # Delete the expense
            cur.execute('DELETE FROM expenses WHERE id = %s', (expense_id,))
            conn.commit()
            
            # Log the deletion
            log_activity(conn, "DELETE_EXPENSE", 
                        f"Deleted '{expense[0]}' (${expense[1]})")
    
    conn.close()
    return redirect('/')

# --- 8. The page for our activity book ---
@app.route('/activity')
def activity_log_page():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM activity_log ORDER BY timestamp DESC;')
        activities = cur.fetchall()
    conn.close()
    return render_template('activity.html', activities=activities)

# --- 9. Start everything! ---
init_db()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
