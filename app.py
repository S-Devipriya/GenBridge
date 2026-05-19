import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'hackathon_secret_key'

# 1. Configure SQLite Database File Location
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'platform.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==========================================
# 2. Database Models (Your Schema)
# ==========================================

class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    sessions_hosted = db.Column(db.Integer, default=0) # Tracks milestones for manual review
    
    # Relationship to link sessions to volunteers
    sessions = db.relationship('Session', backref='host', lazy=True)

class Learner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(200), nullable=False)  # e.g., "Digital Banking Basics"
    date = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='Upcoming') # 'Upcoming' or 'Completed'
    volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteer.id'), nullable=True)

# ==========================================
# 3. Core App Routes
# ==========================================

from flask import Flask, render_template, request

# 1. HOME LAYOUT (Knowledge Hub View)
@app.route('/')
def home():
    """Renders the central knowledge hub showing your 4 learning cards side-by-side."""
    return render_template('knowledge_hub.html')

# 2. HELPLINE LAYOUT
@app.route('/helpline')
def helpline():
    """Renders the centralized, borderless direct helpline view."""
    return render_template('helpline.html')

# 3. INTERACTIVE SEARCH CONTROLLER
@app.route('/search')
def search():
    """Handles query collection from the centralized hub search panel."""
    # Captures what the user typed into the 'q' input box
    query = request.args.get('q', '').strip()
    
    # For now, it simply re-renders the hub. 
    # Later, you can filter your lesson database using the 'query' variable.
    return render_template('knowledge_hub.html', search_query=query)

# ==========================================================================
# PLACEHOLDER ROUTES FOR TOP NAVIGATION LINKS
# ==========================================================================

@app.route('/community-meetings')
def community_meetings():
    """Placeholder route for the Green Live Online Classes tab."""
    return "Community Meetings Screen Placeholder"

@app.route('/learning-paths')
def learning_paths():
    """Placeholder route for the Start Learning Path tab."""
    return "Learning Paths Screen Placeholder"

@app.route('/login')
def login():
    """Placeholder route for the Log In button."""
    return render_template('auth.html')

@app.route('/register-volunteer')
def register_volunteer():
    """Placeholder route for the Register as Volunteer button."""
    return "Volunteer Registration Screen Placeholder"

# Admin Route to complete a session and increment the counter
@app.route('/admin/complete-session/<int:session_id>')
def complete_session(session_id):
    session = Session.query.get_or_404(session_id)
    
    if session.status != 'Completed' and session.volunteer_id:
        session.status = 'Completed'
        
        # Increment the assigned volunteer's milestone counter in the database
        volunteer = Volunteer.query.get(session.volunteer_id)
        volunteer.sessions_hosted += 1
        db.session.commit()
        
        flash(f"Session marked completed! {volunteer.name}'s session count is now {volunteer.sessions_hosted}.", "success")
    
    return redirect(url_for('home'))

# ==========================================
# 4. Initialize Database on Startup
# ==========================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Creates platform.db with Volunteer and Session tables
    app.run(debug=True)