from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship('Profile', back_populates='user', uselist=False)
    photos = relationship('Photo', back_populates='user')
    analyses = relationship('Analysis', back_populates='user')
    recommendations = relationship('Recommendation', back_populates='user')
    feedback = relationship('Feedback', back_populates='user')


class Profile(Base):
    __tablename__ = 'profiles'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    location = Column(String(120), nullable=True)
    allergies = Column(Text, nullable=True)
    lifestyle = Column(Text, nullable=True)
    skin_type = Column(String(50), nullable=True)
    hair_type = Column(String(50), nullable=True)

    user = relationship('User', back_populates='profile')


class Photo(Base):
    __tablename__ = 'photos'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    filename = Column(String(255), nullable=False)
    s3_key = Column(String(512), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='photos')


class Analysis(Base):
    __tablename__ = 'analyses'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    photo_id = Column(Integer, ForeignKey('photos.id'), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    skin_type = Column(String(50), nullable=True)
    hair_type = Column(String(50), nullable=True)
    # store detected conditions and confidence scores as JSON
    conditions = Column(JSON, nullable=True)
    confidence_scores = Column(JSON, nullable=True)

    user = relationship('User', back_populates='analyses')


class Recommendation(Base):
    __tablename__ = 'recommendations'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    content = Column(Text, nullable=False)
    source = Column(String(120), nullable=True)

    user = relationship('User', back_populates='recommendations')


class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    analysis_id = Column(Integer, ForeignKey('analyses.id'), nullable=True)
    rating = Column(Integer, nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='feedback')

