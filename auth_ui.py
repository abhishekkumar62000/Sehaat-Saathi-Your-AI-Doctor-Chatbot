"""
📱 SEHAAT SAATHI - Interactive Authentication UI
Beautiful, realistic phone-based login system
"""

import streamlit as st
from auth_database import patient_db
from datetime import datetime
import re
import time

def validate_phone_number(phone):
    """Validate Indian phone number format"""
    pattern = r'^[6-9]\d{9}$'
    return re.match(pattern, phone) is not None

def show_login_page():
    """Display interactive login page"""
    
    # Custom CSS for beautiful login page
    st.markdown("""
    <style>
        .login-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
        
        .stButton>button {
            border-radius: 10px;
            height: 3rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 243, 255, 0.4);
        }
        
        .auth-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .neon-text {
            color: #00f3ff;
            text-shadow: 0 0 10px rgba(0, 243, 255, 0.5);
        }

        /* Login Container Styles */
        .login-container {
            background: linear-gradient(135deg, #1a1c2c 0%, #4a192c 100%);
            padding: 40px;
            border-radius: 20px;
            color: white;
            text-align: center;
            border: 1px solid #FF8C00;
            margin-bottom: 20px;
        }
        
        .otp-container {
            background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
            padding: 30px;
            border-radius: 15px;
            border: 1px solid #00f3ff;
        }

        .auth-footer {
            text-align: center;
            font-size: 0.8rem;
            color: #888;
            margin-top: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        st.markdown("<h1 style='color: #FF8C00;'>🏥 SEHAAT <span style='color: #22C55E;'>SAATHI</span></h1>", unsafe_allow_html=True)
        st.markdown("<p class='neon-text'>Your Advanced AI-Powered Health Guardian</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Tabs for better UI
        login_tab, signup_tab = st.tabs(["🔐 Secure Login", "📝 Create Account"])
        
        # Initialize session state for persistent auth
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'auth_step' not in st.session_state:
            st.session_state.auth_step = 'phone'
        if 'user_type' not in st.session_state:
            st.session_state.user_type = 'returning' # returning or new
        
        # Check if already authenticated (prevents redirect back to login on reload)
        if st.session_state.authenticated:
            st.rerun()

        with login_tab:
            if st.session_state.auth_step == 'phone':
                st.markdown("### Welcome Back")
                phone = st.text_input("📱 Mobile Number", placeholder="99xxxxxxxx", key="login_phone")
                password = st.text_input("🔑 Password", type="password", placeholder="••••••••", key="login_pw")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("🚀 Sign In", use_container_width=True, type="primary"):
                        if not phone or not password:
                            st.error("Please fill all fields")
                        else:
                            pw_res = patient_db.verify_password(phone, password)
                            if pw_res['status'] == 'success':
                                # Now trigger OTP for 2FA (Double security)
                                otp_res = patient_db.send_otp(phone)
                                if otp_res['status'] == 'success':
                                    st.session_state.phone_number = phone
                                    st.session_state.auth_step = 'otp'
                                    st.session_state.user_type = 'returning'
                                    st.toast("Verification code sent!", icon="📲")
                                    st.rerun()
                                else:
                                    st.error(otp_res['message'])
                            else:
                                st.error(pw_res['message'])
                
                with col_b:
                    if st.button("❓ Forgot Password", use_container_width=True):
                        st.info("Please use 'Create Account' to reset or contact support.")

            elif st.session_state.auth_step == 'otp':
                st.markdown(f"### 🛡️ 2FA Verification")
                st.info("🔐 **Demo OTP: 123456** (Development Mode)")
                st.write(f"Verification code sent to +91 {st.session_state.phone_number}")
                
                otp_code = st.text_input("Enter 6-Digit OTP", max_chars=6, key="otp_verify_input")
                
                if st.button("🔗 Verify & Access Health Vault", use_container_width=True, type="primary"):
                    res = patient_db.verify_otp(st.session_state.phone_number, otp_code)
                    if res['status'] == 'success':
                        # Fetch full patient data to keep in session
                        patient_data = patient_db.get_patient_by_phone(st.session_state.phone_number)
                        st.session_state.authenticated = True
                        st.session_state.patient_id = res['patient_id']
                        st.session_state.patient_name = patient_data.get('full_name') if patient_data else "User"
                        st.session_state.auth_step = 'phone'
                        st.success("Access Granted!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(res['message'])
                
                if st.button("🔙 Back to Login", use_container_width=True):
                    st.session_state.auth_step = 'phone'
                    st.rerun()

        with signup_tab:
            st.markdown("### 🆕 Join Sehaat Saathi")
            new_phone = st.text_input("📱 Mobile Number", placeholder="99xxxxxxxx", key="signup_phone")
            new_pw = st.text_input("🔑 Choose Password", type="password", key="signup_pw")
            confirm_pw = st.text_input("🔁 Confirm Password", type="password", key="signup_confirm")
            
            if st.button("✨ Register Account", use_container_width=True, type="primary"):
                if not new_phone or not new_pw:
                    st.error("Please fill all fields")
                elif new_pw != confirm_pw:
                    st.error("Passwords do not match!")
                elif not validate_phone_number(new_phone):
                    st.error("Invalid phone number")
                else:
                    # Check if exists
                    existing = patient_db.get_patient_by_phone(new_phone)
                    if existing:
                        st.warning("Account already exists! Please login.")
                    else:
                        # Register & Send OTP
                        otp_res = patient_db.send_otp(new_phone)
                        if otp_res['status'] == 'success':
                            # We'll set password after OTP verification for security
                            st.session_state.temp_pw = new_pw
                            st.session_state.phone_number = new_phone
                            st.session_state.auth_step = 'otp_signup'
                            st.rerun()

        if st.session_state.get('auth_step') == 'otp_signup':
             st.markdown(f"### 🛡️ Verify New Account")
             st.info("🔐 **Demo OTP: 123456** (Development Mode)")
             otp_signup = st.text_input("Enter OTP", max_chars=6, key="otp_signup_input")
             if st.button("✔️ Verify & Complete Registration", use_container_width=True, type="primary"):
                 res = patient_db.verify_otp(st.session_state.phone_number, otp_signup)
                 if res['status'] == 'success':
                     # Set the password now
                     patient_db.set_password(st.session_state.phone_number, st.session_state.temp_pw)
                     st.session_state.authenticated = True
                     st.session_state.patient_id = res['patient_id']
                     st.session_state.patient_name = "New Patient"
                     st.session_state.is_new_patient = True
                     st.session_state.auth_step = 'phone'
                     st.success("Account created successfully!")
                     st.balloons()
                     st.rerun()
                 else:
                     st.error(res['message'])

        st.markdown("""
        <div class='auth-footer'>
            By continuing, you agree to our <b>Terms of Service</b> and <b>Privacy Policy</b>.<br>
            All health data is encrypted and secure.
        </div>
        """, unsafe_allow_html=True)


def show_patient_dashboard(patient_id, phone_number):
    """Display patient dashboard after login"""
    
    # Fetch patient data
    patient = patient_db.get_patient_by_phone(phone_number)
    
    if not patient or patient['full_name'] is None:
        show_complete_profile(patient_id, phone_number)
    else:
        show_main_dashboard(patient_id, phone_number, patient)


def show_complete_profile(patient_id, phone_number):
    """Show profile completion form for new patients"""
    
    st.markdown("### 👤 Complete Your Profile")
    st.info("👋 Welcome! Let's complete your health profile for personalized care.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        full_name = st.text_input("Full Name *", placeholder="e.g., Rajesh Kumar")
        email = st.text_input("Email", placeholder="e.g., rajesh@email.com")
        age = st.number_input("Age *", min_value=1, max_value=120, value=25)
        gender = st.selectbox("Gender *", ["Select", "Male", "Female", "Other"])
    
    with col2:
        weight = st.number_input("Weight (kg) *", min_value=20.0, max_value=200.0, value=70.0)
        blood_group = st.selectbox("Blood Group", ["Select", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
        conditions = st.text_area("Medical Conditions", placeholder="e.g., Diabetes, Hypertension")
        allergies = st.text_area("Known Allergies", placeholder="e.g., Penicillin, Peanuts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        emergency_contact = st.text_input("Emergency Contact Name", placeholder="e.g., Wife/Brother")
        emergency_phone = st.text_input("Emergency Contact Number", placeholder="10-digit number")
    
    with col2:
        insurance_id = st.text_input("Insurance ID (Optional)", placeholder="Your policy number")
        insurance_provider = st.selectbox("Insurance Provider", ["None", "HDFC Health", "Aetna", "Star Health", "Other"])
    
    if st.button("💾 Save & Encrypt Profile", type="primary", use_container_width=True):
        if not full_name or gender == "Select" or not email:
            st.error("❌ Please fill in all required fields (marked with *)")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            st.error("❌ Please enter a valid email address")
        else:
            with st.spinner("🔒 Securing your health profile..."):
                time.sleep(1.5) # Realistic processing delay
                profile_data = {
                    'full_name': full_name,
                    'email': email,
                    'age': age,
                    'gender': gender,
                    'weight': weight,
                    'blood_group': blood_group if blood_group != "Select" else None,
                    'medical_conditions': conditions,
                    'allergies': allergies,
                    'emergency_contact': emergency_contact,
                    'emergency_phone': emergency_phone,
                    'insurance_id': insurance_id,
                    'insurance_provider': insurance_provider if insurance_provider != "None" else None
                }
                
                res = patient_db.update_patient_profile(phone_number, profile_data)
                if res['status'] == 'success':
                    st.success("🎉 Profile completed! Your health vault is now ready.")
                    st.toast("Profile data encrypted successfully", icon="🔐")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ Error: {res['message']}")


def show_main_dashboard(patient_id, phone_number, patient):
    """Display main patient dashboard"""
    
    st.markdown(f"### 👋 Welcome back, {patient['full_name']}!")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        consultations = patient_db.get_consultation_history(patient_id, limit=1)
        st.metric("💬 Total Consultations", len(consultations))
    
    with col2:
        medicines = patient_db.get_active_medicines(patient_id)
        st.metric("💊 Active Medicines", len(medicines))
    
    with col3:
        vitals = patient_db.get_health_vitals(patient_id, days=1)
        st.metric("💓 Recent Vitals", len(vitals))
    
    with col4:
        reminders = patient_db.get_pending_reminders(patient_id)
        st.metric("⏰ Pending Reminders", len(reminders))
    
    st.markdown("---")
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Dashboard", "📜 History", "💊 Medicines", "💓 Vitals", "👤 Profile"])
    
    with tab1:
        show_dashboard_section(patient_id)
    
    with tab2:
        show_consultation_history(patient_id)
    
    with tab3:
        show_medicines_section(patient_id)
    
    with tab4:
        show_vitals_section(patient_id)
    
    with tab5:
        show_profile_section(patient_id, phone_number, patient)


def show_dashboard_section(patient_id):
    """Main dashboard overview"""
    
    consultations = patient_db.get_consultation_history(patient_id, limit=3)
    reminders = patient_db.get_pending_reminders(patient_id)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📰 Recent Consultations")
        if consultations:
            for c in consultations:
                with st.expander(f"🏥 {c['doctor_type']} - {c['consultation_date'][:10]}"):
                    st.write(f"**Symptoms:** {c['symptoms']}")
                    st.write(f"**Diagnosis:** {c['diagnosis']}")
                    st.write(f"**Recommendations:** {c['recommendations']}")
                    if c['follow_up_date']:
                        st.info(f"⏰ Follow-up: {c['follow_up_date']}")
        else:
            st.info("No consultations yet. Start your first consultation!")
    
    with col2:
        st.markdown("### ⏰ Pending Reminders")
        if reminders:
            for r in reminders:
                st.warning(f"⚠️ {r['title']}")
                st.write(f"📅 {r['reminder_date']}")
        else:
            st.success("✅ All reminders completed!")


def show_consultation_history(patient_id):
    """Display consultation history"""
    
    consultations = patient_db.get_consultation_history(patient_id)
    
    if not consultations:
        st.info("📋 No consultations yet. Book your first appointment!")
        return
    
    st.markdown("### 📜 Your Consultation History")
    
    for consultation in consultations:
        with st.expander(
            f"🏥 {consultation['doctor_type']} - {consultation['consultation_date'][:10]}",
            expanded=False
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Symptoms:**")
                st.write(consultation['symptoms'])
                st.write("\n**Diagnosis:**")
                st.write(consultation['diagnosis'])
            
            with col2:
                st.write("**Recommendations:**")
                st.write(consultation['recommendations'])
                if consultation['follow_up_date']:
                    st.info(f"📅 **Follow-up Date:** {consultation['follow_up_date']}")


def show_medicines_section(patient_id):
    """Display active medicines"""
    
    medicines = patient_db.get_active_medicines(patient_id)
    
    st.markdown("### 💊 Your Medicines")
    
    if not medicines:
        st.info("No active medicines. Get a consultation to receive prescriptions!")
        return
    
    for med in medicines:
        with st.expander(
            f"💊 {med['medicine_name']} - {med['dosage']}",
            expanded=True
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Frequency:** {med['frequency']}")
                st.write(f"**Duration:** {med['duration']}")
                st.write(f"**Started:** {med['start_date'][:10]}")
            
            with col2:
                if med['side_effects']:
                    st.write(f"**Side Effects:** {med['side_effects']}")
                else:
                    st.write("**Side Effects:** None reported")
                
                if st.checkbox(f"Mark as taken today - {med['id']}", value=False):
                    st.success("✅ Marked as taken!")


def show_vitals_section(patient_id):
    """Display health vitals"""
    
    st.markdown("### 💓 Your Health Vitals")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📝 Record New Vitals")
        bp = st.text_input("Blood Pressure (e.g., 120/80)", placeholder="120/80")
        hr = st.number_input("Heart Rate (bpm)", min_value=40, max_value=180, value=72)
        temp = st.number_input("Temperature (°C)", min_value=35.0, max_value=42.0, value=37.0, step=0.1)
        o2 = st.number_input("Oxygen Saturation (%)", min_value=70, max_value=100, value=98)
        bs = st.number_input("Blood Sugar (mg/dL)", min_value=50, max_value=500, value=100)
        notes = st.text_area("Additional Notes")
        
        if st.button("💾 Save Vitals", use_container_width=True, type="primary"):
            vitals_data = {
                'blood_pressure': bp,
                'heart_rate': hr,
                'temperature': temp,
                'oxygen_saturation': o2,
                'blood_sugar': bs,
                'notes': notes
            }
            result = patient_db.save_health_vitals(patient_id, vitals_data)
            if result['status'] == 'success':
                st.success("✅ " + result['message'])
            else:
                st.error(result['message'])
    
    with col2:
        st.markdown("#### 📊 Recent Vitals")
        vitals = patient_db.get_health_vitals(patient_id, days=30)
        
        if vitals:
            vitals_df = [[
                v['recorded_date'][:10],
                v['blood_pressure'] or '-',
                v['heart_rate'] or '-',
                f"{v['temperature'] or '-'}°C"
            ] for v in vitals[:10]]
            
            st.dataframe(
                vitals_df,
                column_config={
                    0: st.column_config.TextColumn("Date"),
                    1: st.column_config.TextColumn("BP"),
                    2: st.column_config.TextColumn("HR"),
                    3: st.column_config.TextColumn("Temp")
                },
                hide_index=True
            )
        else:
            st.info("No vitals recorded yet")


def show_profile_section(patient_id, phone_number, patient):
    """Display and edit patient profile"""
    
    st.markdown("### 👤 Your Profile")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Phone:** +91{phone_number}")
        st.markdown(f"**Name:** {patient['full_name']}")
        st.markdown(f"**Age:** {patient['age']} years")
        st.markdown(f"**Gender:** {patient['gender']}")
        st.markdown(f"**Weight:** {patient['weight']} kg")
    
    with col2:
        st.markdown(f"**Blood Group:** {patient['blood_group'] or 'Not set'}")
        st.markdown(f"**Email:** {patient['email']}")
        st.markdown(f"**Conditions:** {patient['medical_conditions'] or 'None'}")
        st.markdown(f"**Allergies:** {patient['allergies'] or 'None'}")
    
    st.markdown("---")
    
    if st.button("✏️ Edit Profile", use_container_width=True):
        show_complete_profile(patient_id, phone_number)


def logout_user():
    """Logout current user"""
    st.session_state.authenticated = False
    st.session_state.patient_id = None
    st.session_state.phone_number = None
    st.success("✅ Logged out successfully!")
    st.rerun()
