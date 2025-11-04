import mysql.connector
from mysql.connector import Error
from datetime import datetime

class HealthAssessmentSystem:
    def __init__(self, host="localhost", user="root", password="", database="health_assessment"):
        """Initialize MySQL database connection and create tables"""
        try:
            self.conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password
            )
            self.cursor = self.conn.cursor()
            # Create database if it doesn't exist
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
            self.cursor.execute(f"USE {database}")
            self.create_tables()
            print("✓ Successfully connected to MySQL database")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            raise

    def create_tables(self):
        """Create necessary database tables"""
        try:
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS individuals (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                age INT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_metrics (
                id INT AUTO_INCREMENT PRIMARY KEY,
                individual_id INT,
                weight DECIMAL(5,2) NOT NULL,
                height DECIMAL(4,2) NOT NULL,
                systolic_bp INT NOT NULL,
                diastolic_bp INT NOT NULL,
                heart_rate INT NOT NULL,
                bmi DECIMAL(5,2),
                bmi_risk VARCHAR(20),
                bp_risk VARCHAR(20),
                hr_risk VARCHAR(20),
                overall_risk VARCHAR(20),
                FOREIGN KEY (individual_id) REFERENCES individuals(id)
                ON DELETE CASCADE
            )
            ''')
            self.conn.commit()
            print("✓ Database tables created/verified")
        except Error as e:
            print(f"Error creating tables: {e}")
            raise

    def calculate_bmi(self, weight, height):
        """Calculate BMI using weight (kg) and height (m)"""
        if height == 0:
            return 0
        return weight / (height ** 2)

    # --- UPDATED RISK LOGIC (from health_risk_analyzer.py) ---

    def classify_bmi(self, bmi):
        """Classifies BMI into risk categories."""
        if bmi < 18.5:
            return "Underweight", "Low"
        elif 18.5 <= bmi <= 24.9:
            return "Normal weight", "Low"
        else:
            return "Overweight", "High"

    def classify_bp(self, systolic, diastolic):
        """Classifies blood pressure into risk categories."""
        if systolic < 90 or diastolic < 60:
            return "Low", "Low"
        elif (90 <= systolic <= 120) and (60 <= diastolic <= 80):
            return "Normal", "Low" # Changed 'Medium' to 'Normal' to match your first file
        else:
            return "High", "High"

    def classify_hr(self, hr):
        """Classifies heart rate into risk categories."""
        if hr < 60:
            return "Low", "Low"
        elif 60 <= hr <= 100:
            return "Normal", "Low"
        else:
            return "High", "High"

    def determine_overall_risk(self, bmi_risk, bp_risk, hr_risk):
        """Determines the overall health risk based on individual metrics."""
        risks = [bmi_risk, bp_risk, hr_risk]
        high_risk_count = risks.count("High")

        if high_risk_count >= 2:
            return "High"
        elif high_risk_count == 1:
            return "Medium"
        else:
            return "Low"

    # --- END OF UPDATED LOGIC ---

    def collect_health_data(self, person_num):
        """Collect health data for a single individual"""
        print(f"\n{'='*60}")
        print(f"PERSON {person_num} - Data Collection")
        print(f"{'='*60}")
        try:
            name = input("Enter name: ").strip()
            if not name:
                name = f"Person_{person_num}"
            age = int(input("Enter age: "))
            weight = float(input("Enter weight (kg): "))
            height = float(input("Enter height (m): "))
            systolic = int(input("Enter systolic blood pressure (mmHg): "))
            diastolic = int(input("Enter diastolic blood pressure (mmHg): "))
            heart_rate = int(input("Enter heart rate (bpm): "))

            if weight <= 0 or height <= 0 or systolic <= 0 or diastolic <= 0 or heart_rate <= 0:
                print("All inputs must be positive numbers. Skipping this person.")
                return None

            return {
                'name': name,
                'age': age,
                'weight': weight,
                'height': height,
                'systolic': systolic,
                'diastolic': diastolic,
                'heart_rate': heart_rate
            }
        except ValueError as e:
            print(f"Error: Invalid input. Please enter numeric values.")
            return None

    def process_individual(self, data):
        """Process and store individual health data (UPDATED)"""
        try:
            # Calculate metrics
            bmi = self.calculate_bmi(data['weight'], data['height'])
            
            # Use new functions and get the risk (index [1])
            bmi_category, bmi_risk = self.classify_bmi(bmi) 
            bp_category, bp_risk = self.classify_bp(data['systolic'], data['diastolic'])
            hr_category, hr_risk = self.classify_hr(data['heart_rate'])
            
            overall_risk = self.determine_overall_risk(bmi_risk, bp_risk, hr_risk)

            # Insert individual data
            insert_individual = '''
            INSERT INTO individuals (name, age)
            VALUES (%s, %s)
            '''
            self.cursor.execute(insert_individual, (data['name'], data['age']))
            individual_id = self.cursor.lastrowid

            # Insert health metrics
            insert_metrics = '''
            INSERT INTO health_metrics (
                individual_id, weight, height, systolic_bp,
                diastolic_bp,
                heart_rate, bmi, bmi_risk, bp_risk, hr_risk,
                overall_risk
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            self.cursor.execute(insert_metrics, (
                individual_id, data['weight'], data['height'],
                data['systolic'],
                data['diastolic'], data['heart_rate'], bmi, bmi_risk,
                bp_risk,
                hr_risk, overall_risk
            ))
            self.conn.commit()

            # We also update the report to show the category name
            return {
                'name': data['name'],
                'bmi': bmi,
                'bmi_category': bmi_category, 
                'bp_category': bp_category,
                'hr_category': hr_category,
                'overall_risk': overall_risk
            }
        except Error as e:
            print(f"Error processing individual: {e}")
            self.conn.rollback()
            return None

    def print_individual_report(self, result, person_num):
        """Print detailed report for an individual (UPDATED)"""
        print(f"\n{'='*60}")
        print(f"HEALTH RISK ASSESSMENT REPORT - {result['name']}")
        print(f"{'='*60}")
        print(f"BMI: {result['bmi']:.2f}")
        print(f"BMI Category: {result['bmi_category']}")
        print(f"Blood Pressure Category: {result['bp_category']}")
        print(f"Heart Rate Category: {result['hr_category']}")
        print(f"\n>>> OVERALL HEALTH RISK: {result['overall_risk']} <<<")
        print(f"{'='*60}")

    def generate_summary_report(self):
        """Generate and display final summary report from database (Completed)"""
        print(f"\n\n{'='*60}")
        print("FINAL SUMMARY REPORT")
        print(f"{'='*60}")
        try:
            # Query summary statistics
            query_summary = '''
            SELECT overall_risk, COUNT(*) as count
            FROM health_metrics
            GROUP BY overall_risk
            ORDER BY
                CASE overall_risk
                    WHEN 'High' THEN 1
                    WHEN 'Medium' THEN 2
                    WHEN 'Low' THEN 3
                    ELSE 4
                END
            '''
            self.cursor.execute(query_summary)
            results = self.cursor.fetchall()

            if not results:
                print("No data in the database yet.")
                return

            print("Total entries grouped by risk level:")
            summary_counts = {"High": 0, "Medium": 0, "Low": 0}
            for risk, count in results:
                if risk in summary_counts:
                    summary_counts[risk] = count

            print(f"High risk level:   {summary_counts['High']}")
            print(f"Medium risk level: {summary_counts['Medium']}")
            print(f"Low risk level:    {summary_counts['Low']}")
            print(f"{'='*60}")

        except Error as e:
            print(f"Error generating summary report: {e}")


# --- This is the part that makes the script run ---

if __name__ == "__main__":
    try:
        # 1. Initialize the system (connects to DB, creates tables)
        #    IMPORTANT: Change the password if yours is not empty!
        system = HealthAssessmentSystem(
            host="localhost",
            user="root",
            password=""  # <--- Change this if you have a MySQL password
        )

        # 2. Ask how many people
        try:
            n = int(input("Enter the number of people: "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            exit()  # Exit if input is bad

        # 3. Loop and collect data for each person
        for i in range(1, n + 1):
            data = system.collect_health_data(i)
            
            if data:
                # Process data and save to database
                result = system.process_individual(data)
                if result:
                    # Print the individual report
                    system.print_individual_report(result, i)
            else:
                print(f"Skipping Person {i} due to input error.")
        
        # 4. Generate the final summary report from the database
        system.generate_summary_report()

    except mysql.connector.Error as e:
        print(f"\n--- DATABASE CONNECTION FAILED ---")
        print(f"Error: {e}")
        print("\nPlease ensure your MySQL server (like XAMPP) is running.")
        print("Also, check your 'host', 'user', and 'password' in the code.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")