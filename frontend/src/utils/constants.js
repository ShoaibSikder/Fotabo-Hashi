
export const BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];

export const DEMO_DONORS = [
  { id: 1, name: 'Karim Hossain', blood_group: 'O+', location: 'Mirpur, Dhaka', donations: 8, is_available_for_donation: true },
  { id: 2, name: 'Nusrat Jahan', blood_group: 'A+', location: 'Uttara, Dhaka', donations: 5, is_available_for_donation: true },
  { id: 3, name: 'Sabbir Ahmed', blood_group: 'B-', location: 'Dhanmondi, Dhaka', donations: 14, is_available_for_donation: true },
  { id: 4, name: 'Tania Akter', blood_group: 'AB+', location: 'Banani, Dhaka', donations: 3, is_available_for_donation: true },
  { id: 5, name: 'Imran Khan', blood_group: 'O-', location: 'Mohakhali, Dhaka', donations: 21, is_available_for_donation: true },
];

export const DEMO_REQUESTS = [
  { id: 1, requester_name: 'Farhana Islam', blood_group: 'B+', location: 'Dhaka Medical College Hospital', required_units: 2, description: 'Urgent support needed for a scheduled procedure.', status: 'ACTIVE', created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString() },
  { id: 2, requester_name: 'Rahim Uddin', blood_group: 'O+', location: 'Square Hospital, Dhaka', required_units: 1, description: 'A family member is in need of a donor.', status: 'ACTIVE', created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString() },
  { id: 3, requester_name: 'Jamal Uddin', blood_group: 'A-', location: 'United Hospital, Dhaka', required_units: 3, description: 'Please contact the family for details.', status: 'ACTIVE', created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString() },
];
