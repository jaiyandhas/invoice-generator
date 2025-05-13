import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config import Config
from datetime import datetime

db = SQLAlchemy()

def create_app(config_class=Config):
    # Get absolute path to project root (one level up from app/)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    app = Flask(__name__,
               template_folder=os.path.join(project_root, 'templates'),
               static_folder=os.path.join(project_root, 'static'))
    
    app.config.from_object(config_class)
    db.init_app(app)

    # Register blueprints
    from app.routes import main_routes, customer_routes, invoice_routes
    app.register_blueprint(main_routes)
    app.register_blueprint(customer_routes)
    app.register_blueprint(invoice_routes)

    # Create database tables
    with app.app_context():
        db.create_all()

    # Test template path (remove in production)
    @app.route('/template_test')
    def template_test():
        try:
            return render_template('index.html')
        except Exception as e:
            return f"Error: {str(e)}<br>Template folder: {app.template_folder}", 500
    
    @app.context_processor
    def inject_now():
        """Inject current datetime into all templates"""
        return {'now': datetime.utcnow()}

    return app