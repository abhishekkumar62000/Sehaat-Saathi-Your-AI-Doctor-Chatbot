"""
🔐 SEHAAT SAATHI - Patient Authentication & Database System
Realistic phone-based login with persistent patient data storage
"""

import sqlite3
import hashlib
import random
import json
from datetime import datetime, timedelta
from pathlib import Path

DATABASE_PATH = "sehaat_patients.db"

class PatientDatabase:
    """Manages patient authentication and data persistence"""
    
    def __init__(self):
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with all required tables"""
        try:
            self.conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
            
            # 👤 Patients Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone_number TEXT UNIQUE NOT NULL,
                    password_hash TEXT,
                    full_name TEXT,
                    email TEXT,
                    age INTEGER,
                    gender TEXT,
                    weight REAL,
                    medical_conditions TEXT,
                    allergies TEXT,
                    blood_group TEXT,
                    emergency_contact TEXT,
                    emergency_phone TEXT,
                    insurance_id TEXT,
                    insurance_provider TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    verified BOOLEAN DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    login_attempts INTEGER DEFAULT 0,
                    locked_until TIMESTAMP
                )
            ''')
            
            # 🔐 OTP Verification Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS otp_verification (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone_number TEXT NOT NULL,
                    otp_code TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    verified BOOLEAN DEFAULT 0
                )
            ''')
            
            # 📋 Consultation History Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS consultations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    doctor_type TEXT,
                    symptoms TEXT,
                    diagnosis TEXT,
                    recommendations TEXT,
                    medicines_prescribed TEXT,
                    consultation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    follow_up_date TEXT,
                    notes TEXT,
                    FOREIGN KEY (patient_id) REFERENCES patients(id)
                )
            ''')
            
            # 💊 Medicines Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS medicines_prescribed (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    consultation_id INTEGER,
                    medicine_name TEXT,
                    dosage TEXT,
                    frequency TEXT,
                    duration TEXT,
                    start_date TIMESTAMP,
                    end_date TEXT,
                    side_effects TEXT,
                    reminder_enabled BOOLEAN DEFAULT 1,
                    FOREIGN KEY (patient_id) REFERENCES patients(id),
                    FOREIGN KEY (consultation_id) REFERENCES consultations(id)
                )
            ''')
            
            # 📊 Health Vitals Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS health_vitals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    blood_pressure TEXT,
                    heart_rate INTEGER,
                    temperature REAL,
                    oxygen_saturation INTEGER,
                    blood_sugar INTEGER,
                    recorded_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (patient_id) REFERENCES patients(id)
                )
            ''')
            
            # 📄 Medical Reports Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS medical_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    report_type TEXT,
                    report_name TEXT,
                    report_path TEXT,
                    lab_name TEXT,
                    test_date TIMESTAMP,
                    uploaded_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    normal_range TEXT,
                    result_value TEXT,
                    status TEXT,
                    doctor_notes TEXT,
                    FOREIGN KEY (patient_id) REFERENCES patients(id)
                )
            ''')
            
            # 🔔 Reminders Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    reminder_type TEXT,
                    title TEXT,
                    description TEXT,
                    reminder_date TIMESTAMP,
                    reminder_time TEXT,
                    is_completed BOOLEAN DEFAULT 0,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients(id)
                )
            ''')
            
            # 🛠️ Migration: Ensure 'password_hash' and other missing columns exist in 'patients' table
            try:
                cursor.execute('ALTER TABLE patients ADD COLUMN password_hash TEXT')
            except sqlite3.OperationalError:
                pass  # Already exists
                
            try:
                cursor.execute('ALTER TABLE patients ADD COLUMN login_attempts INTEGER DEFAULT 0')
            except sqlite3.OperationalError:
                pass
                
            try:
                cursor.execute('ALTER TABLE patients ADD COLUMN locked_until TIMESTAMP')
            except sqlite3.OperationalError:
                pass

            try:
                cursor.execute('ALTER TABLE patients ADD COLUMN status TEXT DEFAULT "active"')
            except sqlite3.OperationalError:
                pass
            
            self.conn.commit()
            print("✅ Database initialized successfully!")
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
    
    def generate_otp(self):
        """Generate a 6-digit OTP (Hardcoded for Demo)"""
        return "123456"
    
    def send_otp(self, phone_number):
        """Store OTP for phone number (in production, integrate SMS gateway)"""
        otp = self.generate_otp()
        expires_at = datetime.now() + timedelta(minutes=5)
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO otp_verification (phone_number, otp_code, expires_at)
                VALUES (?, ?, ?)
            ''', (phone_number, otp, expires_at))
            self.conn.commit()
            
            # In production: Use Twilio/AWS SNS to send SMS
            # For demo: Return OTP (in real app, SMS would be sent)
            return {
                "status": "success",
                "message": f"OTP sent to {phone_number}",
                "demo_otp": otp  # Remove in production
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def verify_otp(self, phone_number, otp_code):
        """Verify OTP and create/update patient account"""
        try:
            # FOR DEMO: Allow '123456' regardless of database record
            if otp_code == "123456":
                # Check if patient already exists
                cursor = self.conn.cursor()
                cursor.execute('SELECT * FROM patients WHERE phone_number = ?', (phone_number,))
                patient = cursor.fetchone()
                
                if not patient:
                    # Create new patient
                    cursor.execute('''
                        INSERT INTO patients (phone_number, verified, last_login)
                        VALUES (?, 1, ?)
                    ''', (phone_number, datetime.now()))
                    self.conn.commit()
                    patient_id = cursor.lastrowid
                    return {
                        "status": "success",
                        "message": "Account created successfully!",
                        "patient_id": patient_id,
                        "is_new": True
                    }
                else:
                    # Update existing patient's last login
                    cursor.execute('''
                        UPDATE patients SET last_login = ? WHERE phone_number = ?
                    ''', (datetime.now(), phone_number))
                    self.conn.commit()
                    return {
                        "status": "success",
                        "message": "Login successful! Welcome back!",
                        "patient_id": patient['id'],
                        "is_new": False
                    }

            cursor = self.conn.cursor()
            
            # Check if OTP is valid and not expired
            cursor.execute('''
                SELECT * FROM otp_verification 
                WHERE phone_number = ? AND otp_code = ? 
                AND verified = 0
                AND datetime(expires_at) > datetime('now')
                ORDER BY created_at DESC LIMIT 1
            ''', (phone_number, otp_code))
            
            otp_record = cursor.fetchone()
            if not otp_record:
                return {"status": "error", "message": "Invalid or expired OTP"}
            
            # Mark OTP as verified
            cursor.execute('''
                UPDATE otp_verification SET verified = 1 WHERE id = ?
            ''', (otp_record['id'],))
            
            # Check if patient already exists
            cursor.execute('SELECT * FROM patients WHERE phone_number = ?', (phone_number,))
            patient = cursor.fetchone()
            
            if not patient:
                # Create new patient
                cursor.execute('''
                    INSERT INTO patients (phone_number, verified, last_login)
                    VALUES (?, 1, ?)
                ''', (phone_number, datetime.now()))
                self.conn.commit()
                patient_id = cursor.lastrowid
                return {
                    "status": "success",
                    "message": "Account created successfully!",
                    "patient_id": patient_id,
                    "is_new": True
                }
            else:
                # Update existing patient's last login
                cursor.execute('''
                    UPDATE patients SET last_login = ? WHERE phone_number = ?
                ''', (datetime.now(), phone_number))
                self.conn.commit()
                return {
                    "status": "success",
                    "message": "Login successful! Welcome back!",
                    "patient_id": patient['id'],
                    "is_new": False
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_patient_by_phone(self, phone_number):
        """Fetch patient data by phone number"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM patients WHERE phone_number = ?', (phone_number,))
            patient = cursor.fetchone()
            
            if patient:
                return dict(patient)
            return None
        except Exception as e:
            print(f"Error fetching patient: {e}")
            return None
    
    def hash_password(self, password):
        """Hash a password for storing"""
        return hashlib.sha256(password.encode()).hexdigest()

    def set_password(self, phone_number, password):
        """Set or update patient password"""
        try:
            cursor = self.conn.cursor()
            pw_hash = self.hash_password(password)
            cursor.execute('UPDATE patients SET password_hash = ? WHERE phone_number = ?', (pw_hash, phone_number))
            self.conn.commit()
            return {"status": "success", "message": "Password set successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def verify_password(self, phone_number, password):
        """Verify password for a patient"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT password_hash, locked_until, login_attempts FROM patients WHERE phone_number = ?', (phone_number,))
            patient = cursor.fetchone()
            
            if not patient:
                return {"status": "error", "message": "Patient not found"}
            
            # Check if account is locked
            if patient['locked_until']:
                locked_until = datetime.strptime(patient['locked_until'], '%Y-%m-%d %H:%M:%S.%f')
                if locked_until > datetime.now():
                    return {"status": "error", "message": f"Account locked until {locked_until.strftime('%H:%M')}"}

            pw_hash = self.hash_password(password)
            if patient['password_hash'] == pw_hash:
                # Reset login attempts on success
                cursor.execute('UPDATE patients SET login_attempts = 0, locked_until = NULL WHERE phone_number = ?', (phone_number,))
                self.conn.commit()
                return {"status": "success", "message": "Password verified"}
            else:
                # Increment login attempts
                attempts = patient['login_attempts'] + 1
                if attempts >= 5:
                    locked_until = datetime.now() + timedelta(minutes=15)
                    cursor.execute('UPDATE patients SET login_attempts = ?, locked_until = ? WHERE phone_number = ?', 
                                 (attempts, locked_until, phone_number))
                    self.conn.commit()
                    return {"status": "error", "message": "Too many failed attempts. Account locked for 15 mins."}
                else:
                    cursor.execute('UPDATE patients SET login_attempts = ? WHERE phone_number = ?', (attempts, phone_number))
                    self.conn.commit()
                    remaining = 5 - attempts
                    return {"status": "error", "message": f"Invalid password. {remaining} attempts remaining."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
            return None
    
    def update_patient_profile(self, phone_number, profile_data):
        """Update patient profile information"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE patients SET
                    full_name = ?,
                    email = ?,
                    age = ?,
                    gender = ?,
                    weight = ?,
                    blood_group = ?,
                    medical_conditions = ?,
                    allergies = ?,
                    emergency_contact = ?,
                    emergency_phone = ?,
                    insurance_id = ?,
                    insurance_provider = ?
                WHERE phone_number = ?
            ''', (
                profile_data.get('full_name'),
                profile_data.get('email'),
                profile_data.get('age'),
                profile_data.get('gender'),
                profile_data.get('weight'),
                profile_data.get('blood_group'),
                profile_data.get('medical_conditions'),
                profile_data.get('allergies'),
                profile_data.get('emergency_contact'),
                profile_data.get('emergency_phone'),
                profile_data.get('insurance_id'),
                profile_data.get('insurance_provider'),
                phone_number
            ))
            self.conn.commit()
            return {"status": "success", "message": "Profile updated successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def save_consultation(self, patient_id, consultation_data):
        """Save consultation history"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO consultations 
                (patient_id, doctor_type, symptoms, diagnosis, recommendations, 
                 medicines_prescribed, follow_up_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                patient_id,
                consultation_data.get('doctor_type'),
                consultation_data.get('symptoms'),
                consultation_data.get('diagnosis'),
                consultation_data.get('recommendations'),
                json.dumps(consultation_data.get('medicines', [])),
                consultation_data.get('follow_up_date'),
                consultation_data.get('notes')
            ))
            self.conn.commit()
            consultation_id = cursor.lastrowid
            
            # Save medicines
            for medicine in consultation_data.get('medicines', []):
                cursor.execute('''
                    INSERT INTO medicines_prescribed
                    (patient_id, consultation_id, medicine_name, dosage, frequency, 
                     duration, start_date, side_effects)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    patient_id,
                    consultation_id,
                    medicine.get('name'),
                    medicine.get('dosage'),
                    medicine.get('frequency'),
                    medicine.get('duration'),
                    datetime.now(),
                    medicine.get('side_effects', '')
                ))
            
            self.conn.commit()
            return {"status": "success", "message": "Consultation saved successfully", "consultation_id": consultation_id}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_consultation_history(self, patient_id, limit=10):
        """Fetch consultation history for patient"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM consultations 
                WHERE patient_id = ? 
                ORDER BY consultation_date DESC 
                LIMIT ?
            ''', (patient_id, limit))
            
            consultations = [dict(row) for row in cursor.fetchall()]
            return consultations
        except Exception as e:
            print(f"Error fetching consultation history: {e}")
            return []
    
    def get_active_medicines(self, patient_id):
        """Get currently active medicines for patient"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM medicines_prescribed 
                WHERE patient_id = ? 
                AND (end_date IS NULL OR datetime(end_date) > datetime('now'))
                ORDER BY start_date DESC
            ''', (patient_id,))
            
            medicines = [dict(row) for row in cursor.fetchall()]
            return medicines
        except Exception as e:
            print(f"Error fetching medicines: {e}")
            return []
    
    def save_health_vitals(self, patient_id, vitals):
        """Save patient health vitals"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO health_vitals
                (patient_id, blood_pressure, heart_rate, temperature, 
                 oxygen_saturation, blood_sugar, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                patient_id,
                vitals.get('blood_pressure'),
                vitals.get('heart_rate'),
                vitals.get('temperature'),
                vitals.get('oxygen_saturation'),
                vitals.get('blood_sugar'),
                vitals.get('notes', '')
            ))
            self.conn.commit()
            return {"status": "success", "message": "Vitals saved successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_health_vitals(self, patient_id, days=30):
        """Fetch health vitals for last N days"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM health_vitals 
                WHERE patient_id = ? 
                AND datetime(recorded_date) >= datetime('now', ? || ' days')
                ORDER BY recorded_date DESC
            ''', (patient_id, -days))
            
            vitals = [dict(row) for row in cursor.fetchall()]
            return vitals
        except Exception as e:
            print(f"Error fetching vitals: {e}")
            return []
    
    def add_reminder(self, patient_id, reminder_data):
        """Add reminder for patient"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO reminders
                (patient_id, reminder_type, title, description, reminder_date, reminder_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                patient_id,
                reminder_data.get('type'),
                reminder_data.get('title'),
                reminder_data.get('description'),
                reminder_data.get('date'),
                reminder_data.get('time')
            ))
            self.conn.commit()
            return {"status": "success", "message": "Reminder added successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_pending_reminders(self, patient_id):
        """Get pending reminders for patient"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM reminders 
                WHERE patient_id = ? 
                AND is_completed = 0
                AND datetime(reminder_date) <= datetime('now')
                ORDER BY reminder_date ASC
            ''', (patient_id,))
            
            reminders = [dict(row) for row in cursor.fetchall()]
            return reminders
        except Exception as e:
            print(f"Error fetching reminders: {e}")
            return []


# Initialize database
patient_db = PatientDatabase()
