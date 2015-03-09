from leapi import db
from sqlalchemy import UniqueConstraint, PrimaryKeyConstraint

class Instrument(db.Model):
    __tablename__ = 'instruments'
    __table_args__ = (PrimaryKeyConstraint('site_id', 'name',name='instrument_site_name_pk'),)

    id = db.Column(db.Integer)
    name = db.Column(db.Unicode)
    model = db.Column(db.Unicode)
    manufacturer = db.Column(db.Unicode)
    site_id = db.Column(db.Unicode, db.ForeignKey('sites.id'))

    sensors = db.relationship('Sensor', backref='instruments')
    observations = db.relationship('Observation', backref='instruments')
    
    def __init__(self,name):
        self.name = name

    def __repr__(self):
        return '<instrument id {}>'.format(self.id)
