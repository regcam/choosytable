"""
Application constants and static data
Consolidates repeated data structures from across the application
"""

# Ethnicity options
ETHNICITY_OPTIONS = [
    'White', 'Asian', 'Latino', 'Black', 'Afro-Latino',
    'African', 'Indigenous People', 'Pacific Islander', 'Unspecified'
]

# Gender options
GENDER_OPTIONS = [
    'Female', 'Male', 'Transgender', 'Agender', 'Unspecified'
]

# Position options
POSITION_OPTIONS = [
    ('software_engineer', 'Software Engineer'),
    ('staff_engineer', 'Staff Engineer'),
    ('lead_engineering', 'Lead Engineer'),
    ('architect', 'Architect'),
    ('software_engineer_mngr', 'Software Engineer Manager'),
    ('technical_mngr', 'Technical Manager'),
    ('technical_drtr', 'Technical Director'),
    ('vp', 'VP'),
    ('cto', 'CTO'),
    ('network_engineer', 'Network Engineer'),
    ('principal_architect', 'Principal Architect'),
    ('qa_engineer', 'QA Engineer'),
    ('sre', 'SRE'),
    ('sdet', 'SDET'),
    ('project_mngr', 'Project Manager'),
    ('program_mngr', 'Program Manager'),
    ('devops_engineer', 'DevOps Engineer'),
    ('systems_admin', 'Systems Admin'),
    ('dba', 'DBA'),
    ('operations_engineer', 'Operations Engineer')
]

# Age ranges
AGE_OPTIONS = [
    '18-24', '25-34', '35-44', '45-54', '55-64', '65-74', '75+'
]

# US states and territories
LOCATION_OPTIONS = [
    'AK', 'AL', 'AR', 'AS', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE',
    'FL', 'GA', 'GU', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY',
    'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MP', 'MS', 'MT',
    'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK',
    'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA',
    'VI', 'VT', 'WA', 'WI', 'WV', 'WY'
]

# Highlighted ethnicity groups (for special displays)
HIGHLIGHTED_ETHNICITIES = [
    'Black', 'Afro-Latino', 'Bahamian', 'Jamaican', 'African'
]

# Cache key prefixes for better organization
CACHE_KEYS = {
    'USER_REVIEWS': '_reviews',
    'COMPANY_INTERVIEWS': '_pd_interviews', 
    'ALL_REVIEWS': 'find_reviews',
    'USER_BY_EMAIL': 'user_email_'
}

# Default values
DEFAULTS = {
    'AGE': '18-24',
    'ETHNICITY': 'Unspecified', 
    'GENDER': 'Unspecified',
    'LOCATION': 'GA'
}

# Interview outcome options
INTERVIEW_OUTCOMES = [
    ('y', 'Yes'),
    ('n', 'No'), 
    ('o', 'Offered a Different Position')
]

# Employee status options
EMPLOYEE_STATUS = [
    ('y', 'Yes'),
    ('n', 'No')
]

# Rating options (1-5 stars)
RATING_OPTIONS = list(range(1, 6))