# Health Risk Assessment System

This project is a command-line application written in Python that assesses a person's health risk based on their Body Mass Index (BMI), Blood Pressure (BP), and Heart Rate (HR).

It collects data for multiple individuals, classifies their risk levels (Low, Medium, High) for each metric, determines an overall health risk, and stores all assessment data in a MySQL database. At the end of the session, it generates a summary report of the day's assessments by querying the database.

## 📋 Features

* **Data Collection:** Gathers name, weight (kg), height (m), blood pressure (systolic/diastolic), and heart rate (bpm) from the command line.
* **Risk Classification:**
    * Calculates BMI and classifies it (Underweight, Normal weight, Overweight).
    * Classifies Blood Pressure (Low, Medium, High).
    * Classifies Heart Rate (Low, Normal, High).
* **Overall Risk Assessment:** Determines a final "Overall Health Risk" (Low, Medium, High) based on the combination of individual metric risks.
* **Database Integration:** Securely saves all personal data and assessment results into a MySQL database.
* **Reporting:**
    * Displays an immediate, detailed report for each person after their data is entered.
    * Provides a summary report at the end, showing the total count of individuals in each risk category for the current day.
* **Input Validation:** Includes basic validation to handle invalid formats or non-positive numbers.

## 🛠️ Technologies Used

* **Python 3**
* **MySQL**
* **`mysql-connector-python`**: The Python library used to interface with the MySQL database.

## 🚀 How to Get Started

Follow these steps to set up and run the project on your local machine.

### 1. Prerequisites

* **Python 3:** Ensure you have Python 3 installed.
* **MySQL Server:** You must have a MySQL server installed and running (e.g., MySQL Community Server, XAMPP, MAMP).

### 2. Installation

1.  **Clone the repository (or download the script):**
    ```bash
    # If you're using Git
    git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
    cd your-repository-name
    ```

2.  **Install the required Python library:**
    ```bash
    pip install mysql-connector-python
    ```

### 3. Database Setup

The script **does not** create the database or tables. You must run the following SQL commands in your MySQL client (like MySQL Workbench, DBeaver, or the `mysql` command line) *before* running the script.

```sql
-- 1. Create the database
CREATE DATABASE IF NOT EXISTS HealthRiskSystem;

-- 2. Use the new database
USE HealthRiskSystem;

-- 3. Create the Individuals table
CREATE TABLE Individuals (
    person_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- 4. Create the HealthAssessments table
CREATE TABLE HealthAssessments (
    assessment_id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT,
    assessment_date DATE NOT NULL,
    weight_kg DECIMAL(5, 2),
    height_m DECIMAL(4, 2),
    systolic_bp INT,
    diastolic_bp INT,
    heart_rate_bpm INT,
    bmi DECIMAL(5, 2),
    bmi_category VARCHAR(50),
    bp_category VARCHAR(50),
    hr_category VARCHAR(50),
    bmi_risk VARCHAR(50),
    bp_risk VARCHAR(50),
    hr_risk VARCHAR(50),
    overall_risk VARCHAR(50),
    FOREIGN KEY (person_id) REFERENCES Individuals(person_id)
);
```

### 4. Configuration

Open the Python script (e.g., `health_system.py`) and update the `DB_CONFIG` dictionary with your personal MySQL credentials.

```python
# --- 1. Database Configuration ---
DB_CONFIG = {
    "host": "localhost",
    "user": "your_mysql_username",      # E.g., "root"
    "password": "your_mysql_password",  # Your password
    "database": "HealthRiskSystem"
}
```

### 5. Run the Application

You are now ready to run the script. Execute the following command in your terminal:

```bash
python health_system.py
```

The application will start and prompt you to enter the number of people you want to assess. Follow the on-screen prompts to input the data.

**Example Output:**
```
[v0] Successfully connected to database
Enter the number of people to assess: 1

--- Entering data for Person 1 ---
Enter name for Person 1: John Doe
Enter weight (kg): 80
Enter height (m): 1.75
Enter Blood Pressure (Systolic/Diastolic, e.g., 120/80): 130/85
Enter heart rate (bpm): 95

--- Health Report for John Doe (ID: 1) ---
BMI: 26.12 kg/m² (Overweight, High Risk)
Blood Pressure: 130/85 mm/hg (High, High Risk)
Heart Rate: 95 bpm (Normal, Low Risk)
Overall Health Risk: High risk level

--- Summary Health Risk Report (Today's Assessments) ---
High risk level: 1
Medium risk level: 0
Low risk level: 0
```
