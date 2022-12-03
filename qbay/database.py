import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.sql import func
from sqlalchemy import Column, ForeignKey, Integer, Table
import sqlalchemy.types
from sqlalchemy.orm import relationship

import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
db_string = os.getenv('db_string')
if db_string:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_string
else:
    app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'qbay_database.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '69cae04b04756f65eabcd2c5a11c8c24'

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(320), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    postal_code = db.Column(db.String(7), nullable=True)
    billing_address = db.Column(db.String(46), nullable=True)
    balance = db.Column(db.Integer, nullable=False)  # in cents

    wallet = relationship('Wallet', back_populates='user', uselist=False)
    listings = relationship('Listing', back_populates='owner')
    reviews = relationship('Review', back_populates='user')
    bookings = relationship('Booking', back_populates='buyer')

    def __repr__(self) -> str:
        return f'<User {self.username} : {self.id}>'


class Listing(db.Model):
    __tablename__ = 'listings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(5000), nullable=False)
    price = db.Column(db.Integer, nullable=False)  # in cents to avoid errors
    address = db.Column(db.String(5000), nullable=False)
    date_created = db.Column(db.String(10), nullable=False)
    last_modified_date = db.Column(db.String(10), nullable=False)
    booked_dates = relationship('Dates', back_populates='listing')

    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    owner = relationship('User', back_populates='listings')
    bookings = relationship('Booking', back_populates='listing')
    reviews = relationship('Review', back_populates='listing')

    def __repr__(self) -> str:
        return f'<Listing {self.title}>'


class Dates(db.Model):
    __tablename__ = "dates"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'))
    listing = relationship("Listing", back_populates='booked_dates')
    date = db.Column(db.String(10), nullable=False)


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    owner_id = db.Column(db.Integer, nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    buyer = relationship("User", back_populates='bookings')

    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'))
    listing = relationship("Listing", back_populates='bookings')

    start_date = db.Column(db.String(10), nullable=False)
    end_date = db.Column(db.String(10), nullable=False)

    def __repr__(self) -> str:
        return f'<Booking {self.id}>'


class Wallet(db.Model):
    __tablename__ = 'wallets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    balance = db.Column(db.Float(precision=2, asdecimal=True), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = relationship('User', back_populates='wallet')

    transactions = relationship(
        'Transaction', primaryjoin="Wallet.id==Transaction.payer_id")

    banking_account_id = db.Column(
        db.Integer, db.ForeignKey('banking_accounts.id'))
    banking_account = relationship('BankingAccount')

    def __repr__(self) -> str:
        return f'<Wallet {self.id}>'


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    review_text = db.Column(db.String(5000), nullable=True)
    date = db.Column(db.Integer, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = relationship('User', back_populates='reviews')
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'))
    listing = relationship('Listing', back_populates='reviews')

    def __repr__(self) -> str:
        return f'<Review {self.id}>'


class BankingAccount(db.Model):
    __tablename__ = 'banking_accounts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    balance = db.Column(db.Float(precision=2, asdecimal=True), nullable=False)

    def __repr__(self) -> str:
        return f'<BankingAccount {self.id}>'


class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    amount = db.Column(db.Float(precision=2, asdecimal=True), nullable=False)
    status = db.Column(db.String(30), nullable=False)

    payer_id = db.Column(db.Integer, db.ForeignKey(Wallet.id))
    payer = relationship(
        'Wallet', foreign_keys=[payer_id], back_populates='transactions')

    payee_id = db.Column(db.Integer, db.ForeignKey(Wallet.id))
    payee = relationship('Wallet', foreign_keys=[payee_id])

    booking_id = db.Column(db.Integer, db.ForeignKey(Booking.id))
    booking = relationship('Booking')

    def __repr__(self) -> str:
        return f'<Transaction {self.id}>'
