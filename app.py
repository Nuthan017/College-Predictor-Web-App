from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
# Configure the SQLite database connection
# --- Configuration using Absolute Path to fix the OperationalError ---
# Determine the absolute path to the directory where app.py is located
basedir = os.path.abspath(os.path.dirname(__file__))

# Construct the absolute path to the database file
DB_PATH = os.path.join(basedir, 'college_cutoffs.db')

# Configure the SQLite database connection using the absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_PATH 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# ------------------------------------------------------------------

# --- Define the Database Model ---
# This mirrors the structure created by data_loader.py
class Cutoff(db.Model):
    __tablename__ = 'cutoffs'
    id = db.Column(db.Integer, primary_key=True)
    college_name = db.Column(db.String(100), nullable=False)
    program = db.Column(db.String(100), nullable=False)
    exam = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    quota = db.Column(db.String(50), nullable=False)
    closing_rank = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'college': self.college_name,
            'program': self.program,
            'quota': self.quota,
            'closing_rank': self.closing_rank
        }

# --- Flask Routes ---

@app.route('/')
def index():
    # Pass unique options to the frontend dropdowns
    categories = db.session.query(Cutoff.category).distinct().all()
    exams = db.session.query(Cutoff.exam).distinct().all()
    
    # [('General',), ('OBC',), ...] -> ['General', 'OBC', ...]
    categories = [c[0] for c in categories]
    exams = [e[0] for e in exams]
    
    return render_template('index.html', categories=categories, exams=exams)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # 1. Get user input from the AJAX request
        data = request.get_json()
        user_rank = int(data.get('rank'))
        user_category = data.get('category')
        user_exam = data.get('exam')

        # 2. CORE PREDICTION LOGIC (SQLAlchemy Query)
        # Find all cutoffs where:
        # a) The category and exam match the user's input.
        # b) The user's rank is LESS THAN OR EQUAL TO the closing rank. 
        #    (Lower rank is better, so a rank of 500 is eligible for a cutoff of 800)
        
        eligible_colleges = Cutoff.query.filter(
            Cutoff.exam == user_exam,
            Cutoff.category == user_category,
            Cutoff.closing_rank >= user_rank # The prediction criteria
        ).order_by(Cutoff.closing_rank).all() # Order by rank for better viewing

        # 3. Format results for JSON
        results = [college.to_dict() for college in eligible_colleges]

        return jsonify({'success': True, 'results': results})

    except Exception as e:
        # Good practice for debugging
        print(f"Prediction Error: {e}")
        return jsonify({'success': False, 'message': 'An error occurred during prediction.'}), 500

if __name__ == '__main__':
    # You only need to run this command once to ensure the DB and tables are ready
    # if you didn't run data_loader.py separately. 
    # db.create_all() # Not strictly needed if using data_loader.py, but safe.
    app.run(debug=True)