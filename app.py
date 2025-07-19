from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['ADMIN_USERNAME'] = 'admin'
app.config['ADMIN_PASSWORD'] = 'admin123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200))
    project_url = db.Column(db.String(200))

class HomeContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hero_title = db.Column(db.String(200), nullable=False)
    hero_description = db.Column(db.Text, nullable=False)

class SiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(100), nullable=False)
    footer_text = db.Column(db.String(200), nullable=False)

class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_range = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    institution = db.Column(db.String(200))
    details = db.Column(db.Text)
    position = db.Column(db.String(10))  # 'left' or 'right'

# Create tables
with app.app_context():
    db.create_all()
    # Initialize default content if tables are empty
    if not HomeContent.query.first():
        default_home = HomeContent(
            hero_title="Hi, I'm <span>Abdeldjalil HANI</span>",
            hero_description="A Ph.D. student in Quantum Computing, a senior in AI and Machine Learning (NLP, Computer Vision, Deep Learning), and a skilled backend developer creating smart, scalable web applications"
        )
        db.session.add(default_home)
    
    if not SiteSettings.query.first():
        default_settings = SiteSettings(
            site_name="My Portfolio",
            footer_text="© 2025 My Portfolio. All rights reserved."
        )
        db.session.add(default_settings)
    
    if not Project.query.first():
        default_projects = [
            Project(
                title='Quantum Algorithm Implementation',
                description='Developed quantum algorithms for optimization problems using Qiskit.',
                image_url='https://via.placeholder.com/400x300?text=Quantum+Project',
                project_url='#'
            ),
            # Add other default projects...
        ]
        db.session.add_all(default_projects)

    if not Education.query.first():
        default_education = [
            Education(
                date_range="2024 - Present",
                title="Ph.D. in Quantum Computing",
                institution="Setif 1 University",
                details="Ranked 1st place in doctoral competition among 872 candidates\nResearch focus: Quantum metaheuristics for complex health problems optimization",
                position="left"
            ),
            Education(
                date_range="2022 - 2024",
                title="Master's Degree in Artificial Intelligence",
                institution="Specialization: Data Science, Computer Vision, NLP",
                position="right"
            ),
            # Add other default education entries...
        ]
        db.session.add_all(default_education)
        db.session.commit()
    
    db.session.commit()

# Contact Form
class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')

def is_admin():
    return session.get('is_admin', False)

@app.route('/')
def home():
    home_content = HomeContent.query.first()
    projects = Project.query.limit(4).all()
    return render_template('index.html', projects=projects, home_content=home_content)

@app.route('/projects')
def projects():
    projects = Project.query.all()
    return render_template('projects.html', projects=projects)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if is_admin():
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
            session['is_admin'] = True
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/admin')
def admin_dashboard():
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    home_content = HomeContent.query.first()
    projects = Project.query.all()
    settings = SiteSettings.query.first()
    education_entries = Education.query.all()
    
    return render_template('admin.html', 
                         projects=projects,
                         home_content=home_content,
                         settings=settings,
                         education_entries=education_entries)

@app.route('/admin/update-home', methods=['POST'])
def admin_update_home():
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    home_content = HomeContent.query.first()
    home_content.hero_title = request.form.get('hero_title')
    home_content.hero_description = request.form.get('hero_description')
    db.session.commit()
    
    flash('Home content updated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update-settings', methods=['POST'])
def admin_update_settings():
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    settings = SiteSettings.query.first()
    settings.site_name = request.form.get('site_name')
    settings.footer_text = request.form.get('footer_text')
    db.session.commit()
    
    flash('Settings updated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add-project', methods=['GET', 'POST'])
def admin_add_project():
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        new_project = Project(
            title=request.form.get('title'),
            description=request.form.get('description'),
            image_url=request.form.get('image_url') or url_for('static', filename='images/project-placeholder.png'),
            project_url=request.form.get('project_url') or '#'
        )
        db.session.add(new_project)
        db.session.commit()
        
        flash('Project added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('add_project.html')

@app.route('/admin/edit-project/<int:project_id>', methods=['GET', 'POST'])
def admin_edit_project(project_id):
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        project.title = request.form.get('title')
        project.description = request.form.get('description')
        project.image_url = request.form.get('image_url') or url_for('static', filename='images/project-placeholder.png')
        project.project_url = request.form.get('project_url') or '#'
        db.session.commit()
        
        flash('Project updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_project.html', project=project, project_id=project.id)

@app.route('/admin/delete-project/<int:project_id>', methods=['POST'])
def admin_delete_project(project_id):
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Add these routes to app.py

@app.route('/admin/add-education', methods=['GET', 'POST'])
def admin_add_education():
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        new_education = Education(
            date_range=request.form.get('date_range'),
            title=request.form.get('title'),
            institution=request.form.get('institution'),
            details=request.form.get('details'),
            position=request.form.get('position', 'left')
        )
        db.session.add(new_education)
        db.session.commit()
        
        flash('Education entry added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    # Pass all required variables to the template
    home_content = HomeContent.query.first()
    settings = SiteSettings.query.first()
    projects = Project.query.all()
    education_entries = Education.query.all()
    
    return render_template('admin.html', 
                        home_content=home_content,
                        settings=settings,
                        projects=projects,
                        education_entries=education_entries)

@app.route('/admin/edit-education/<int:edu_id>', methods=['GET', 'POST'])
def admin_edit_education(edu_id):
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    education = Education.query.get_or_404(edu_id)
    
    if request.method == 'POST':
        education.date_range = request.form.get('date_range')
        education.title = request.form.get('title')
        education.institution = request.form.get('institution')
        education.details = request.form.get('details')
        education.position = request.form.get('position', 'left')
        db.session.commit()
        
        flash('Education entry updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin.html', education=education, edu_id=edu_id)

@app.route('/admin/delete-education/<int:edu_id>', methods=['POST'])
def admin_delete_education(edu_id):
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    education = Education.query.get_or_404(edu_id)
    db.session.delete(education)
    db.session.commit()
    
    flash('Education entry deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)