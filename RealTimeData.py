import random
import time
from datetime import datetime

class RealTimeServices:
    def __init__(self):
        # 🟢 REFACTORED: Hierarchical State/District Structure
        self.state_districts = {
            "Bihar": [
                "Patna", "Gaya", "Muzaffarpur", "Bhagalpur", "Darbhanga", "Purnia", "Begusarai", "Ara", "Munger", "Chapra",
                "Araria", "Arwal", "Aurangabad", "Banka", "Bhojpur", "Buxar", "East Champaran (Motihari)", "Gopalganj", 
                "Jamui", "Jehanabad", "Kaimur (Bhabua)", "Katihar", "Khagaria", "Kishanganj", "Lakhisarai", "Madhepura", 
                "Madhubani", "Nalanda", "Nawada", "Rohtas", "Saharsa", "Samastipur", "Sheikhpura", "Sheohar", 
                "Sitamarhi", "Siwan", "Supaul", "Vaishali", "West Champaran"
            ],
            "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Thane", "Aurangabad", "Solapur", "Amravati"],
            "Delhi": ["New Delhi", "North Delhi", "South Delhi", "West Delhi", "East Delhi"],
            "Karnataka": ["Bangalore", "Mysore", "Hubli", "Mangalore", "Belgaum"],
            "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Trichy", "Salem"],
            "West Bengal": ["Kolkata", "Howrah", "Durgapur", "Siliguri", "Asansol"],
            "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar"],
            "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Agra", "Noida", "Ghaziabad", "Prayagraj", "Meerut"],
            "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar"],
            "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Bikaner"],
            "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Hazaribagh"]
        }

        # GEOSPATIAL DATA FOR MAP VIUSALIZATION (Lat, Lon)
        self.city_coords = {
            "Patna": [25.5941, 85.1376], "Gaya": [24.7914, 85.0002], "Muzaffarpur": [26.1197, 85.3910],
            "Delhi": [28.7041, 77.1025], "New Delhi": [28.6139, 77.2090], "Mumbai": [19.0760, 72.8777],
            "Bangalore": [12.9716, 77.5946], "Chennai": [13.0827, 80.2707], "Kolkata": [22.5726, 88.3639],
            "Hyderabad": [17.3850, 78.4867], "Lucknow": [26.8467, 80.9462], "Ahmedabad": [23.0225, 72.5714],
            "Jaipur": [26.9124, 75.7873], "Ranchi": [23.3441, 85.3096], 
            # Default fallback for others will be generated near Patna/Delhi based on region
        }
        
        # Simulated hospital data structure with expanded Bihar coverage
        # Note: For locations not in this explicit list, we now generate dynamic names
        self.hospitals = {
            # --- METROS ---
            "Delhi": ["AIIMS Delhi", "Apollo Hospital", "Sir Ganga Ram Hospital", "Max Super Speciality", "Fortis Escorts", "BLK Super Speciality"],
            "South Delhi": ["Max Smart Super Speciality", "Apollo Spectra", "Batra Hospital"],
            "West Delhi": ["Maharaja Agrasen Hospital", "Mata Chanan Devi Hospital"],
            "East Delhi": ["Max Super Speciality Patparganj", "Dharamshila Narayana", "Guru Teg Bahadur Hospital"],
            "New Delhi": ["AIIMS Delhi", "Safdarjung Hospital", "RML Hospital", "Lady Hardinge"],
            "Mumbai": ["Lilavati Hospital", "Nanavati Hospital", "Breach Candy Hospital", "Kokilaben Dhirubhai Ambani Hospital", "Tata Memorial Hospital", "Jaslok Hospital"],
            "Pune": ["Ruby Hall Clinic", "Jehangir Hospital", "Aditya Birla Memorial", "Deenanath Mangeshkar Hospital"],
            "Nagpur": ["Kingsway Hospitals", "Orange City Hospital", "Care Hospital Nagpur"],
            "Nashik": ["Wockhardt Hospital", "Sahyadri Hospital", "Six Sigma Hospital"],
            "Thane": ["Jupiter Hospital", "Bethany Hospital", "Kaushalya Medical Foundation"],
            "Aurangabad": ["MGM Medical College", "Seth Nandlal Dhoot Hospital", "Kamalnayan Bajaj Hospital"],
            "Solapur": ["Ashwini Rural Medical College", "Markaz Hospital"],
            "Amravati": ["PDMC Hospital", "Suyash Hospital"],
            "Bangalore": ["Narayana Health", "Manipal Hospital", "Fortis Hospital", "Aster CMI", "Apollo Bnaghankota"],
            "Mysore": ["Apollo BGS Hospitals", "Columbia Asia Hospital", "JSS Hospital"],
            "Hubli": ["SDM College of Medical Sciences", "KIMS Hubli"],
            "Mangalore": ["KMC Hospital", "AJ Hospital", "Father Muller Hospital"],
            "Belgaum": ["KLE Dr. Prabhakar Kore Hospital", "Lakeview Hospital"],
            "Chennai": ["Apollo Main Greams Road", "MIOT International", "Fortis Malar", "Gleneagles Global", "CMC Vellore (Nearby)"],
            "Coimbatore": ["G. Kuppuswamy Naidu Memorial Hospital", "PSG Hospitals", "Kovai Medical Center"],
            "Madurai": ["Apollo Speciality Hospitals", "Meenakshi Mission", "Velammal Medical College"],
            "Trichy": ["Kavery Medical Centre", "Apollo Speciality Hospitals Trichy"],
            "Salem": ["Manipal Hospital Salem", "Salem Polyclinic"],
            "Kolkata": ["Apollo Gleneagles", "Fortis Kolkata", "AMRI Hospital", "Medica Super Specialty", "SSKM Hospital"],
            "Howrah": ["Narayana Superspeciality", "Howrah District Hospital"],
            "Durgapur": ["Mission Hospital", "Healthworld Hospitals"],
            "Siliguri": ["Neotia Getwel", "North Bengal Medical College"],
            "Asansol": ["H L G Memorial Hospital", "Asansol District Hospital"],
            "Hyderabad": ["Apollo Health City", "Yashoda Hospitals", "KIMS Hospitals", "Care Hospitals", "Osmania General Hospital"],
            "Warangal": ["MGM Hospital Warangal", "Rohini Super Speciality"],
            "Nizamabad": ["Government General Hospital", "Pragati Hospital"],
            "Karimnagar": ["Prathima Institute of Medical Sciences", "Rene Hospital"],
            "Lucknow": ["SGPGI Lucknow", "Medanta Lucknow", "King George's Medical University"],
            "Kanpur": ["Regency Hospital", "Rama Hospital", "LPS Institute of Cardiology"],
            "Varanasi": ["Apex Hospital", "Popular Hospital", "Trauma Centre BHU"],
            "Agra": ["Pushpanjali Hospital", "SN Medical College"],
            "Noida": ["Jaypee Hospital", "Kailash Hospital", "Fortis Noida"],
            "Ghaziabad": ["Yashoda Hospital", "Max Hospital Vaishali"],
            "Prayagraj": ["Nazareth Hospital", "Swaroop Rani Nehru Hospital"],
            "Meerut": ["Nutema Hospital", "Anand Hospital"],
            "Ahmedabad": ["Apollo Hospitals", "Zydus Hospital", "Sterling Hospital", "Civil Hospital Ahmedabad"],
            "Surat": ["Sunshine Global Hospital", "Kiran Super Multispeciality"],
            "Vadodara": ["Sterling Hospital Vadodara", "Bhailal Amin General Hospital"],
            "Rajkot": ["Wockhardt Hospital", "Sterling Hospital Rajkot"],
            "Bhavnagar": ["HCG Hospital", "Sir T Hospital"],
            "Jaipur": ["SMS Hospital", "Fortis Jaipur", "Narayana Hrudayalaya"],
            "Jodhpur": ["AIIMS Jodhpur", "MDM Hospital"],
            "Udaipur": ["Geetanjali Hospital", "Paras JK Hospital"],
            "Kota": ["Sudha Hospital", "Maitri Hospital"],
            "Bikaner": ["PBM Hospital", "Kothari MEdical"],
            "Ranchi": ["RIMS Ranchi", "Medica Ranchi", "Hill View Hospital"],
            "Jamshedpur": ["Tata Main Hospital", "Brahmananda Narayana"],
            "Dhanbad": ["Central Hospital", "PMCH Dhanbad"],
            "Bokaro": ["Bokaro General Hospital", "Muskan Hospital"],
            "Hazaribagh": ["Hazaribagh Sadar Hospital", " आरोग्यam Hospital"],

            # --- BIHAR SPECIFIC DATA - LARGE SCALE COVERAGE (ALL DISTRICTS) ---
            "Patna": ["AIIMS Patna", "PMCH (Patna Medical College)", "IGIMS Sheikhpura", "Paras HMRI Hospital", "Ruban Memorial Hospital", "Ford Hospital", "Mahavir Cancer Sansthan", "Mediversal Hospital", "Sahyog Hospital", "Tripolia Hospital"],
            "Gaya": ["ANMMCH (Magadh Medical College)", "Pilgrim Hospital", "Jai Prakash Narayan Hospital", "Archana Hospital", "Kumar Hospital", "Life Line Hospital", "Prabhavati Hospital"],
            "Muzaffarpur": ["SKMCH (Sri Krishna Medical College)", "Prashant Memorial Charitable Hospital", "Kejriwal Hospital", "Muzaffarpur Eye Hospital", "IT Memorial Hospital", "Sadar Hospital Muzaffarpur"],
            "Bhagalpur": ["JLNMCH (Mayaganj Hospital)", "Glover Memorial", "Sadar Hospital", "Hope Hospital", "Arc Hospital", "Sundarwati Mahila Hospital"],
            "Darbhanga": ["DMCH (Darbhanga Medical College)", "Paras Global Hospital", "R.B. Memorial", "Health Line Hospital", "Sadar Hospital Darbhanga"],
            "Purnia": ["Max 7 Hospital", "Sadar Hospital Purnia", "Mata Gujri Memorial Medical College", "Line Bazar Hospital Hub", "Mount Zion Hospital"],
            "Begusarai": ["Sadar Hospital", "Alexia Hospital", "Refinery Township Hospital", "Jivan Sewa Sadan", "Amrit Jeevan Hospital"],
            "Ara": ["Sadar Hospital Ara", "Sun Hospital", "Mahavir Arogya Sansthan", "Bhojpur District Hospital"],
            "Munger": ["Sadar Hospital Munger", "Sevayan Hospital", "National Hospital", "Railway Hospital Jamalpur"],
            "Chapra": ["Sadar Hospital Chapra", "Ganga Hospital", "Sanjeevani Nursing Home", "Saran General Hospital"],
            "Araria": ["Sadar Hospital Araria", "Narpatganj PHC", "Forbesganj Sub-Divisional Hospital"],
            "Arwal": ["Sadar Hospital Arwal", "Community Health Center Arwal"],
            "Aurangabad": ["Sadar Hospital Aurangabad", "Magadh Hospital", "Surya Clinic"],
            "Banka": ["Sadar Hospital Banka", "Referral Hospital Amarpur", "Banka District Hospital"],
            "Bhojpur": ["Sadar Hospital Ara", "Jagdishpur Referral Hospital", "Piro PHC"],
            "Buxar": ["Sadar Hospital Buxar", "Vishwamitra Hospital", "Dumraon Sub-divisional Hospital"],
            "East Champaran (Motihari)": ["Sadar Hospital Motihari", "Rahman Hospital", "Chirayu Hospital", "Champaran Nursing Home"],
            "Gopalganj": ["Sadar Hospital Gopalganj", "Hathua Hospital", "Life Care Gopalganj"],
            "Jamui": ["Sadar Hospital Jamui", "Sono Hospital", "Jhajha Referral Hospital"],
            "Jehanabad": ["Sadar Hospital Jehanabad", "Referral Hospital Makhdumpur", "Jehanabad Central Clinic"],
            "Kaimur (Bhabua)": ["Sadar Hospital Bhabua", "Mohania Sub-Divisional Hospital"],
            "Katihar": ["Katihar Medical College", "Sadar Hospital Katihar", "Seemanchal Hospital"],
            "Khagaria": ["Sadar Hospital Khagaria", "Mansi PHC", "Gogri Referral Hospital"],
            "Kishanganj": ["MGM Medical College", "Sadar Hospital Kishanganj", "Lions Seva Kendra"],
            "Lakhisarai": ["Sadar Hospital Lakhisarai", "Barahiya Referral Hospital"],
            "Madhepura": ["JNKTM Medical College", "Sadar Hospital Madhepura", "Amrit Hospital"],
            "Madhubani": ["Sadar Hospital Madhubani", "Jhanjharpur Sub-Divisional Hospital", "Madhubani Medical College"],
            "Nalanda": ["VIMS Pawapuri (Nalanda Medical College)", "Sadar Hospital Bihar Sharif", "Kalyan Hospital"],
            "Nawada": ["Sadar Hospital Nawada", "Rajauli Sub-Divisional Hospital", "Nawada City Hospital"],
            "Rohtas": ["Sadar Hospital Sasaram", "Narayan Medical College Jamuhar", "Dehri-on-Sone Railway Hospital"],
            "Saharsa": ["Sadar Hospital Saharsa", "Lord Buddha Medical College", "Kosi Anchal Hospital"],
            "Samastipur": ["Sadar Hospital Samastipur", "Anukampa Hospital", "Dalsinghsarai Hospital"],
            "Sheikhpura": ["Sadar Hospital Sheikhpura", "Barbigha Referral Hospital"],
            "Sheohar": ["Sadar Hospital Sheohar", "Piprhi PHC"],
            "Sitamarhi": ["Sadar Hospital Sitamarhi", "Dumra Hospital", "Pupri Referral Hospital"],
            "Siwan": ["Sadar Hospital Siwan", "Siwan Medical College", "Hussainganj PHC"],
            "Supaul": ["Sadar Hospital Supaul", "Birpur Sub-Divisional Hospital", "Triveniganj Hospital"],
            "Vaishali": ["Sadar Hospital Hajipur", "Maitri Hospital", "Vaishali District Hospital"],
            "West Champaran": ["GMCH Bettiah (Govt Medical College)", "Sadar Hospital Bettiah", "Narkatiaganj Sub-Divisional Hospital"]
        }
    
    def get_emergency_bed_status(self, city):
        """Simulates real-time hospital bed availability"""
        # 1. Check if we have explicit data for this city
        hospital_list = self.hospitals.get(city)
        
        # 2. If not, try partial match or GENERATE plausible hospital names
        if not hospital_list:
             city_lower = city.lower()
             # Try Partial match
             for key in self.hospitals.keys():
                 if key.lower() in city_lower or city_lower in key.lower():
                     hospital_list = self.hospitals[key]
                     break
        
        # 3. If still nothing (e.g., highly obscure village or fallback needed)
        if not hospital_list:
            city_name = city.split('(')[0].strip() # Clean name
            hospital_list = [
                f"Sadar Hospital {city_name}",
                f"District Hospital {city_name}",
                f"{city_name} Medical College & Hospital",
                f"Life Care Nursing Home {city_name}",
                f"City Multi-Specialty Center {city_name}"
            ]
            
        # Get Base Coordinates for the City
        city_clean = city.split('(')[0].strip()
        base_lat, base_lon = self.city_coords.get(city_clean, [25.5941, 85.1376]) # Default to Patna if unknown
        
        status = []
        for hosp in hospital_list:
            # Dynamic randomization for demo purposes
            total_beds = random.randint(50, 600) # Varied scale
            occupied = random.randint(int(total_beds*0.4), int(total_beds*0.95))
            
            # Fewer ICU beds in smaller districts logic
            icu_base = 5 if "Sadar" in hosp else 20
            icu_beds = random.randint(icu_base, icu_base + 40)
            
            icu_occupied = random.randint(int(icu_beds*0.2), int(icu_beds*0.9))
            
            # Make some hospitals full to simulate realism
            if random.random() < 0.15:
                occupied = total_beds
                icu_occupied = icu_beds

            # Generate Geo-Coordinates (Jitter around city center)
            hosp_lat = base_lat + random.uniform(-0.03, 0.03)
            hosp_lon = base_lon + random.uniform(-0.03, 0.03)

            status.append({
                "hospital": hosp,
                "regular_beds_available": max(0, total_beds - occupied),
                "icu_beds_available": max(0, icu_beds - icu_occupied),
                "oxygen_cylinders": random.randint(0, 100),
                "last_updated": datetime.now().strftime("%H:%M:%S"),
                "contact": f"+91-{random.randint(6000000000, 9999999999)}",
                "distance_km": round(random.uniform(0.5, 15.0), 1),
                "specialties": random.choice(["General, Trauma", "Cardiology, Neuro", "General, Ortho", "Multi-Specialty, Pediatrics"]),
                "latitude": hosp_lat,
                "longitude": hosp_lon
            })
        
        # Sort by distance for "Nearest First" interaction
        status.sort(key=lambda x: x['distance_km'])
        return status
    
    def get_opd_status(self, hospital_name):
        """Simulates Live OPD (Outpatient Department) Queue Status"""
        # Logic: Usage is higher in 'Sadar' or 'AIIMS' hospitals
        is_gov = "Sadar" in hospital_name or "AIIMS" in hospital_name or "PMCH" in hospital_name
        
        current_token = random.randint(15, 150) if is_gov else random.randint(5, 40)
        avg_handling_time = random.randint(3, 8) # minutes per patient
        your_est_token = current_token + random.randint(5, 20)
        est_wait = (your_est_token - current_token) * avg_handling_time
        
        doctors_active = random.randint(2, 12) if is_gov else random.randint(1, 5)
        
        return {
            "is_open": True,
            "current_token": current_token,
            "your_token": your_est_token,
            "wait_time_mins": est_wait,
            "doctors_on_duty": doctors_active,
            "next_slot": f"{random.randint(10,12)}:30 AM"
        }

    def get_blood_bank_status(self, city, blood_group=None):
        """Simulates real-time blood bank inventory"""
        blood_groups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
        inventory = []
        
        # Smart Name Generation for Blood Banks based on location
        # Check standard lists first
        banks = []
        # Fallback Name Generator
        city_name = city.split('(')[0].strip()
        banks = [
             f"Jeevan Deep Blood Center ({city_name})", 
             f"Red Cross Society {city_name}", 
             f"Maa Vaishno Blood Bank {city_name}", 
             f"Sadar Hospital Blood Bank {city_name}",
             f"Prathama Blood Centre {city_name}"
         ]
        
        # Randomly select 3-5 banks
        selected_banks = random.sample(banks, k=min(len(banks), random.randint(3, 5)))

        for bank in selected_banks:
            stock = {}
            for bg in blood_groups:
                stock[bg] = random.randint(0, 50) # Increased inventory for scale
            
            inventory.append({
                "bank_name": bank,
                "stock": stock,
                "contact": f"+91-{random.randint(7000000000, 9999999999)}"
            })
            
        return inventory

    def get_ambulance_tracking(self, city):
        """Simulates nearby ambulances with ETA"""
        ambulances = []
        # Increased density of ambulances for "Large Scale" feel
        count = random.randint(5, 12) 
        
        for i in range(count):
            ambulances.append({
                "id": f"AMB-{random.randint(1000, 9999)}", # 4 digit IDs
                "type": random.choice(["ALS (Ventilator)", "BLS (Oxygen)", "Patient Transport", "Neonatal Ambulance"]),
                "distance": f"{random.uniform(0.2, 8.0):.1f} km",
                "eta": f"{random.randint(1, 25)} mins",
                "driver_contact": f"+91-{random.randint(7000000000, 9999999999)}",
                "status": random.choice(["Idle", "On Mission", "Returning"]) 
            })
        
        # Filter to show only 'Idle' or relevant ones mostly, but for dash show all
        return ambulances
    
    def get_epidemic_alerts(self, city):
        """Simulates local health alerts based on geospatial data"""
        
        city_name = city.split('(')[0].strip()
        
        # Custom alerts for Bihar region
        if city in self.state_districts.get("Bihar", []) or "Bihar" in city:
             alerts = [
                {"level": "High", "msg": f"AES (Chamki Bukhar) Surveillance Active in {city_name} region"},
                {"level": "Medium", "msg": f"Flood Warning Level 2 in {city_name} - Water disease risk"},
                {"level": "Low", "msg": "Heatwave Advisory: Stay hydrated"},
                {"level": "Medium", "msg": "Dengue cases reported in urban blocks"}
            ]
        elif city in self.state_districts.get("Maharashtra", []):
             alerts = [{"level": "High", "msg": "Monsoon Malaria Surge"}]
        else:
            alerts = [
                {"level": "High", "msg": f"Viral Flu rapid spread detected in {city_name} Sector 4"},
                {"level": "Medium", "msg": "Dengue cases rising - Mosquito control active"},
                {"level": "Low", "msg": "Air Quality Index (AQI) is growing poor"}
            ]
            
        # Randomly return 0-3 alerts
        return random.sample(alerts, random.randint(0, 3)) if random.random() > 0.2 else []

# Singleton instance
emergency_services = RealTimeServices()
