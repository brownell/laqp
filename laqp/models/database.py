"""
Database models for Louisiana QSO Party
Uses SQLAlchemy ORM for database abstraction
"""
from datetime import datetime
# from sqlalchemy import (
#     create_engine, Column, Integer, String, Float, 
#     DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
# )
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import relationship, sessionmaker
import enum

Base = declarative_base()

# Enums for categorical data
class LocationType(enum.Enum):
    DX = 0
    NON_LA = 1
    LA_FIXED = 2
    LA_ROVER = 3

class ModeCategory(enum.Enum):
    PHONE_ONLY = 0
    CW_DIGITAL_ONLY = 1
    MIXED = 2

class PowerLevel(enum.Enum):
    QRP = 0
    LOW = 1
    HIGH = 2

class OverlayCategory(enum.Enum):
    NONE = 0
    WIRES = 1
    TB_WIRES = 2
    POTA = 3


class Contestant(Base):
    """
    Represents a contest participant
    """
    __tablename__ = 'contestants'
    
    id = Column(Integer, primary_key=True)
    callsign = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(100))
    name = Column(String(100))
    
    # Location and category
    location_type = Column(SQLEnum(LocationType), nullable=False)
    is_rover = Column(Boolean, default=False)
    mode_category = Column(SQLEnum(ModeCategory), nullable=False)
    power_level = Column(SQLEnum(PowerLevel))
    overlay_category = Column(SQLEnum(OverlayCategory), default=OverlayCategory.NONE)
    
    # Cabrillo header info
    club = Column(String(100))
    operators = Column(Text)  # Comma-separated list
    soapbox = Column(Text)
    
    # Log processing metadata
    log_filename = Column(String(255))
    submission_date = Column(DateTime, default=datetime.utcnow)
    validation_status = Column(String(20))  # 'valid', 'invalid', 'pending'
    validation_notes = Column(Text)
    
    # Scoring
    claimed_score = Column(Integer, default=0)
    calculated_score = Column(Integer, default=0)
    final_score = Column(Integer, default=0)  # After bonuses
    
    # Certificate request
    wants_certificate = Column(Boolean, default=False)
    
    # Relationships
    qsos = relationship('QSO', back_populates='contestant', cascade='all, delete-orphan')
    score_detail = relationship('ScoreDetail', back_populates='contestant', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Contestant(callsign='{self.callsign}', category='{self.get_category_name()}')>"
    
    def get_category_name(self):
        """Generate human-readable category name"""
        from config.config import get_category_name
        return get_category_name(
            self.location_type.value,
            self.mode_category.value,
            self.is_rover,
            self.power_level.value if self.power_level else None,
            self.overlay_category.value if self.overlay_category else None
        )


class QSO(Base):
    """
    Represents a single QSO (contact)
    """
    __tablename__ = 'qsos'
    
    id = Column(Integer, primary_key=True)
    contestant_id = Column(Integer, ForeignKey('contestants.id'), nullable=False, index=True)
    
    # QSO details
    band = Column(Integer, nullable=False)  # 160, 80, 40, 20, 15, 10, 6, 2
    frequency_khz = Column(Integer)
    mode = Column(String(5), nullable=False)  # CW, PH, DG, RY, FM
    datetime_utc = Column(DateTime, nullable=False, index=True)
    
    # Exchange sent
    sent_call = Column(String(20), nullable=False)
    sent_rst = Column(String(10))
    sent_qth = Column(String(10), nullable=False)  # Parish or State/Province/Country
    
    # Exchange received
    rcvd_call = Column(String(20), nullable=False, index=True)
    rcvd_rst = Column(String(10))
    rcvd_qth = Column(String(10), nullable=False)  # Parish or State/Province/Country
    
    # Validation and scoring
    is_valid = Column(Boolean, default=True)
    is_dupe = Column(Boolean, default=False)
    is_multiplier = Column(Boolean, default=False)
    error_notes = Column(Text)
    
    # Points earned
    qso_points = Column(Integer, default=0)
    
    # Relationships
    contestant = relationship('Contestant', back_populates='qsos')
    
    def __repr__(self):
        return f"<QSO({self.sent_call} -> {self.rcvd_call} {self.band}m {self.mode})>"


class ScoreDetail(Base):
    """
    Detailed scoring breakdown for a contestant
    """
    __tablename__ = 'score_details'
    
    id = Column(Integer, primary_key=True)
    contestant_id = Column(Integer, ForeignKey('contestants.id'), nullable=False, unique=True)
    
    # QSO counts
    total_qsos = Column(Integer, default=0)
    valid_qsos = Column(Integer, default=0)
    dupe_qsos = Column(Integer, default=0)
    invalid_qsos = Column(Integer, default=0)
    
    # QSO counts by mode
    cw_qsos = Column(Integer, default=0)
    phone_qsos = Column(Integer, default=0)
    digital_qsos = Column(Integer, default=0)
    
    # QSO counts by band
    qsos_160m = Column(Integer, default=0)
    qsos_80m = Column(Integer, default=0)
    qsos_40m = Column(Integer, default=0)
    qsos_20m = Column(Integer, default=0)
    qsos_15m = Column(Integer, default=0)
    qsos_10m = Column(Integer, default=0)
    qsos_6m = Column(Integer, default=0)
    qsos_2m = Column(Integer, default=0)
    
    # Points
    raw_qso_points = Column(Integer, default=0)
    
    # Multipliers
    # For Non-LA: parishes worked per band/mode
    # For LA: parishes + states + provinces + DXCC per band/mode
    total_multipliers = Column(Integer, default=0)
    parish_multipliers = Column(Integer, default=0)
    state_multipliers = Column(Integer, default=0)
    province_multipliers = Column(Integer, default=0)
    dxcc_multipliers = Column(Integer, default=0)
    
    # Multiplier detail (JSON-serialized)
    multiplier_detail = Column(Text)  # band:mode:qth counts
    
    # Score calculation
    score_before_bonus = Column(Integer, default=0)  # raw_qso_points × multipliers
    
    # Bonuses
    n5lcc_bonus = Column(Integer, default=0)  # 100 if worked
    rover_activation_bonus = Column(Integer, default=0)  # 50 × parishes activated (rovers only)
    
    # Final
    final_score = Column(Integer, default=0)
    
    # Score reduction from claimed
    score_reduction = Column(Integer, default=0)
    
    # Parishes activated (for rovers)
    parishes_activated = Column(String(255))  # Comma-separated list
    num_parishes_activated = Column(Integer, default=0)
    
    # Relationships
    contestant = relationship('Contestant', back_populates='score_detail')
    
    def __repr__(self):
        return f"<ScoreDetail(contestant_id={self.contestant_id}, score={self.final_score})>"


class Parish(Base):
    """
    Louisiana Parish reference data
    """
    __tablename__ = 'parishes'
    
    id = Column(Integer, primary_key=True)
    abbrev = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    
    # Statistics
    qsos_sent = Column(Integer, default=0)
    qsos_rcvd = Column(Integer, default=0)
    stations_active = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<Parish({self.abbrev}, {self.name})>"


class Multiplier(Base):
    """
    Track multipliers worked by each contestant
    """
    __tablename__ = 'multipliers'
    
    id = Column(Integer, primary_key=True)
    contestant_id = Column(Integer, ForeignKey('contestants.id'), nullable=False, index=True)
    
    band = Column(Integer, nullable=False)
    mode_type = Column(String(10), nullable=False)  # 'CW/Digital' or 'Phone'
    qth_abbrev = Column(String(10), nullable=False)  # Parish, State, Province, or DXCC
    mult_type = Column(String(10), nullable=False)  # 'Parish', 'State', 'Province', 'DXCC'
    
    # Composite index for efficient lookups
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )
    
    def __repr__(self):
        return f"<Multiplier({self.qth_abbrev} {self.band}m {self.mode_type})>"


class ContestStatistics(Base):
    """
    Overall contest statistics
    """
    __tablename__ = 'contest_statistics'
    
    id = Column(Integer, primary_key=True)
    stat_name = Column(String(100), unique=True, nullable=False)
    stat_value = Column(String(255))
    stat_notes = Column(Text)
    
    def __repr__(self):
        return f"<Stat({self.stat_name}={self.stat_value})>"


# Database initialization and session management
class Database:
    """Database manager"""
    
    def __init__(self, database_url):
        self.engine = create_engine(database_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(self.engine)
        
    def drop_tables(self):
        """Drop all tables"""
        Base.metadata.drop_all(self.engine)
        
    def get_session(self):
        """Get a new database session"""
        return self.Session()


if __name__ == "__main__":
    # Test database creation
    from config.config import DATABASE_URL
    
    db = Database(DATABASE_URL)
    print("Creating database tables...")
    db.create_tables()
    print("Tables created successfully!")
    
    # Test session
    session = db.get_session()
    print(f"Database session created: {session}")
    session.close()
