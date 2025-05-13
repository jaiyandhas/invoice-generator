import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or '055f4a21525f0bf02bf58f59062a5c197e3aa1a7846eea19a768b39c219c4b12'
    
    # Change this to MySQL configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
        'mysql+pymysql://root:donbilla@localhost/invoice_app?charset=utf8mb4'
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False