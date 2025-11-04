import mysql.connector
from datetime import date

# --- 1. Database Configuration ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",          # your MySQL username
    "password": "Ritanu",     # your MySQL password
    "database": "HealthRiskSystem"
}



def get_db_connection():
    """Establishes and returns a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("[v0] Successfully connected to database")
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None


# --- 2. Classification Functions ---

def classify_bmi(bmi):
    """Classifies BMI into risk categories."""
    if bmi < 18.5:
        return "Underweight", "Low"
    elif 18.5 <= bmi <= 24.9:
        return "Normal weight", "Low"
    else:
        return "Overweight", "High"


def classify_bp(systolic, diastolic):
    """Classifies blood pressure into risk categories."""
    if systolic < 90 or diastolic < 60:
        return "Low", "Low"
    elif (90 <= systolic <= 120) and (60 <= diastolic <= 80):
        return "Medium", "Low"
    else:
        return "High", "High"


def classify_hr(hr):
    """Classifies heart rate into risk categories."""
    if hr < 60:
        return "Low", "Low"
    elif 60 <= hr <= 100:
        return "Normal", "Low"
    else:
        return "High", "High"


def determine_overall_risk(bmi_risk, bp_risk, hr_risk):
    """Determines overall health risk based on individual metrics."""
    risks = [bmi_risk, bp_risk, hr_risk]
    high_risk_count = risks.count("High")
    if high_risk_count >= 2:
        return "High"
    elif high_risk_count == 1:
        return "Medium"
    else:
        return "Low"


# --- 3. Main Function with Database Operations ---

def main():
    """Main function to collect data, classify, save to DB, and generate reports."""

    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database. Exiting.")
        return

    cursor = conn.cursor()

    try:
        n = int(input("Enter the number of people to assess: "))
        if n <= 0:
            print("Number must be positive. Exiting.")
            conn.close()
            return
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        conn.close()
        return

    for i in range(1, n + 1):
        print(f"\n--- Entering data for Person {i} ---")
        try:
            # Collect name for Individuals table
            name = input(f"Enter name for Person {i}: ").strip()
            if not name:
                print("Name cannot be empty. Skipping this person.")
                continue

            weight = float(input(f"Enter weight (kg): "))
            height = float(input(f"Enter height (m): "))

            bp_input = input(f"Enter Blood Pressure (Systolic/Diastolic, e.g., 120/80): ")
            systolic, diastolic = map(int, bp_input.split('/'))

            heart_rate = int(input(f"Enter heart rate (bpm): "))

            # Validate all inputs are positive
            if weight <= 0 or height <= 0 or systolic <= 0 or diastolic <= 0 or heart_rate <= 0:
                print("All inputs must be positive numbers. Skipping this person.")
                continue

        except (ValueError, IndexError):
            print("Invalid input format. Skipping this person.")
            continue

        # Calculate metrics and classify
        bmi = weight / (height ** 2)
        bmi_category, bmi_risk = classify_bmi(bmi)
        bp_category, bp_risk = classify_bp(systolic, diastolic)
        hr_category, hr_risk = classify_hr(heart_rate)
        overall_risk = determine_overall_risk(bmi_risk, bp_risk, hr_risk)

        # Insert into Individuals table
        try:
            insert_individual_query = "INSERT INTO Individuals (name) VALUES (%s)"
            cursor.execute(insert_individual_query, (name,))
            person_id = cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Database error during Individual insertion: {err}")
            conn.rollback()
            continue

        # Insert into HealthAssessments table
        try:
            insert_assessment_query = """
                INSERT INTO HealthAssessments (
                    person_id, assessment_date, weight_kg, height_m, 
                    systolic_bp, diastolic_bp, heart_rate_bpm, bmi, 
                    bmi_category, bp_category, hr_category, bmi_risk, 
                    bp_risk, hr_risk, overall_risk
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            assessment_data = (
                person_id, date.today(), weight, height, systolic, diastolic,
                heart_rate, bmi, bmi_category, bp_category, hr_category,
                bmi_risk, bp_risk, hr_risk, overall_risk
            )
            cursor.execute(insert_assessment_query, assessment_data)
            conn.commit()

            # Print Individual Report
            print(f"\n--- Health Report for {name} (ID: {person_id}) ---")
            print(f"BMI: {bmi:.2f} kg/m² ({bmi_category}, {bmi_risk} Risk)")
            print(f"Blood Pressure: {systolic}/{diastolic} mm/hg ({bp_category}, {bp_risk} Risk)")
            print(f"Heart Rate: {heart_rate} bpm ({hr_category}, {hr_risk} Risk)")
            print(f"Overall Health Risk: {overall_risk} risk level")

        except mysql.connector.Error as err:
            print(f"Database error during Assessment insertion: {err}")
            conn.rollback()
            continue

    # Generate Summary Report from Database
    print("\n--- Summary Health Risk Report (Today's Assessments) ---")
    try:
        summary_query = """
            SELECT overall_risk, COUNT(overall_risk)
            FROM HealthAssessments
            WHERE assessment_date = CURDATE()
            GROUP BY overall_risk;
        """
        cursor.execute(summary_query)
        summary_results = dict(cursor.fetchall())

        print(f"High risk level: {summary_results.get('High', 0)}")
        print(f"Medium risk level: {summary_results.get('Medium', 0)}")
        print(f"Low risk level: {summary_results.get('Low', 0)}")

    except mysql.connector.Error as err:
        print(f"Error querying summary report: {err}")

    finally:
        # Clean up database resources
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
