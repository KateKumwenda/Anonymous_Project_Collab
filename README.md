# Anonymous_Project_Collab
This application allows users to anonymously report suspected cases of corruption in their communities. Users can submit details such as the type of corruption, location, people involved and any evidence. The system stores and organises these reports for review by anti-corruption teams, helping promote transparency.
---
# Project Structure
Anonymous_Project_Collab/
├── Anonymous_app/
│ ├── app.py
│ ├── extensions.py
│ ├── models/
│ │ ├── init.py
│ │ └── tip.py
│ ├── templates/
│ │ ├── tips_form.html
│ │ └── admin_dashboard.html
| | |__admin_login.html
| | |__base.html
| | |__ index.html
| | 
│ └── static/
│ └── uploads/
├── migrations/
├── requirements.txt
├── README.md
|--env

## 🚀 Features

-  Anonymous tip submission form
-  Location tagging via browser geolocation
-  Category dropdown (e.g. bribery, fraud, etc.)
-  File upload support (images, documents)
-  AES encryption for sensitive data
- Admin dashboard with tips overview & analytics (Chart.js)
-  REST API for submitting/viewing tips
-  No IP address tracking
## Create Virtual environment
      python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
## Installation
### 1. Clone the repo
`bash'
  git clone https://github.com/KateKumwenda/Anonymous_Project_Collab.git
  cd Anonymous_Project_Collab
### 2.Create Virtual Environment
python -m venv venv
venv\Scripts\activate  # Windows
or
source venv/bin/activate  # macOS/Linux
### 3. Install Dependencies
pip install -r requirements.txt
### 4. Initialise the database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
### 5. Run the app
flask run --port=5001
# Future Features
-🧾 Export tips as CSV

-📬 SMS/WhatsApp integration

-🔔 Email alerts for new tips

-🗺️ Map dashboard of report hotspots

-🔍 Search & filtering options in admin view

# Authors
- Kate Kumwenda
- Perpetual Judith Chawanje
- Hanifa Makunganya
- Mandinda Phiri



