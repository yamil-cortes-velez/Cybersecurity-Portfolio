from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    wireguard_ip = db.Column(db.String(50), nullable=False)
    telegram_id = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f"<Device {self.name}>"