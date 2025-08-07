# Healthcare Support Portal Authorization Policies

# Users can read their own information
allow(user, "read", resource: User) if
    user.id = resource.id;

# Admins can read any user
allow(user, "read", resource: User) if
    user.role = "admin";

# Patient access rules
allow(user, "read", patient: Patient) if
    user.role = "doctor" and patient.assigned_doctor_id = user.id;

allow(user, "read", patient: Patient) if
    user.role = "nurse" and patient.department = user.department;

allow(user, "read", patient: Patient) if
    user.role = "admin";

# Document access rules
allow(user, "read", document: Document) if
    user.role = "admin";

# Doctors can read documents for their patients
allow(user, "read", document: Document) if
    user.role = "doctor" and 
    document.patient.assigned_doctor_id = user.id;

# Nurses can read non-sensitive documents in their department
allow(user, "read", document: Document) if
    user.role = "nurse" and 
    document.department = user.department and 
    not document.is_sensitive;

# Users can read general documents (not patient-specific)
allow(user, "read", document: Document) if
    document.patient_id = null and 
    not document.is_sensitive;

# Write permissions (more restrictive)
allow(user, "write", patient: Patient) if
    user.role = "doctor" and patient.assigned_doctor_id = user.id;

allow(user, "write", document: Document) if
    user.role = "doctor" and 
    document.patient.assigned_doctor_id = user.id;

allow(user, "write", resource) if
    user.role = "admin";
