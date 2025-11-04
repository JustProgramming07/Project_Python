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
    """Determines the overall health risk based on individual metrics."""
    risks = [bmi_risk, bp_risk, hr_risk]
    high_risk_count = risks.count("High")

    if high_risk_count >= 2:
        return "High"
    elif high_risk_count == 1:
        return "Medium"
    else:
        return "Low"

def main():
    """Main function to collect data and generate reports."""
    risk_summary = {"High": 0, "Medium": 0, "Low": 0}

    try:
        n = int(input("Enter the number of people: "))
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    for i in range(1, n + 1):
        print(f"\n--- Entering data for Person {i} ---")
        try:
            weight = float(input(f"Enter weight for Person {i} (kg): "))
            height = float(input(f"Enter height for Person {i} (m): "))
            
            bp_input = input(f"Enter Blood Pressure for Person {i} (Systolic/Diastolic, e.g., 120/80): ")
            systolic, diastolic = map(int, bp_input.split('/'))
            
            heart_rate = int(input(f"Enter heart rate for Person {i} (bpm): "))

            if weight <= 0 or height <= 0 or systolic <= 0 or diastolic <= 0 or heart_rate <= 0:
                print("All inputs must be positive numbers. Skipping this person.")
                continue

        except (ValueError, IndexError):
            print("Invalid input format. Skipping this person.")
            continue

        # Calculate BMI and classify
        bmi = weight / (height ** 2)
        bmi_category, bmi_risk = classify_bmi(bmi)

        # Classify BP
        bp_category, bp_risk = classify_bp(systolic, diastolic)

        # Classify Heart Rate
        hr_category, hr_risk = classify_hr(heart_rate)

        # Determine overall risk
        overall_risk = determine_overall_risk(bmi_risk, bp_risk, hr_risk)
        risk_summary[overall_risk] += 1

        # Print individual report
        print(f"\n--- Health Report for Person {i} ---")
        print(f"BMI: {bmi:.2f} kg/m²")
        print(f"BMI Category: {bmi_category}")
        print(f"Blood Pressure: {systolic}/{diastolic} mm/hg")
        print(f"Blood Pressure Category: {bp_category}")
        print(f"Heart Rate: {heart_rate} bpm")
        print(f"Heart Rate Category: {hr_category}")
        print(f"Overall Health Risk: {overall_risk} risk level")

    # Print summary report
    print("\n--- Summary Health Risk Report ---")
    print(f"High risk level: {risk_summary['High']}")
    print(f"Medium risk level: {risk_summary['Medium']}")
    print(f"Low risk level: {risk_summary['Low']}")

if __name__ == "__main__":
    main()
