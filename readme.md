# Hospital Management System

## Project Description

This **Hospital Management System** is a relational database project designed to efficiently manage hospital data such as patients, doctors, appointments, diagnoses, medications, and billing. The system uses **database normalization principles** (1NF, 2NF, 3NF) to organize data into multiple related tables, minimizing redundancy and ensuring data integrity.

---

## Key Features

- **Patient Management:** Stores patient demographics and medical history.  
- **Doctor Management:** Maintains doctor profiles, including specialization and department.  
- **Appointment Scheduling:** Tracks patient appointments with doctors.  
- **Diagnosis and Treatment:** Records diagnoses linked to appointments and prescribed medications.  
- **Billing Information:** Manages billing details per appointment.  
- **Normalized Database Design:** Implements normalization for efficient data organization.

---

## Technologies Used

- Relational Database (MySQL, PostgreSQL, SQLite, or similar)  
- SQL for database design and queries

---

## Dataset Structure

- **Patients:** PatientID, Name, Age, Contact Info  
- **Doctors:** DoctorID, Name, Specialization, Department  
- **Appointments:** AppointmentID, PatientID, DoctorID, Date, DiagnosisID, BillAmount  
- **Diagnoses:** DiagnosisID, DiagnosisName, ICDCode  
- **Medications:** AppointmentID, MedicationName

---

## How to Use

1. Clone the repository.  
2. Set up the database using provided SQL scripts.  
3. Run queries or integrate with your hospital management application.

---

## Purpose

This project is designed to help understand and demonstrate practical database design and normalization techniques in a healthcare context.
