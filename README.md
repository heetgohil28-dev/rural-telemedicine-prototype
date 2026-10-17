
\# Rural Telemedicine Prototype



Prototype for the SEP micro project "Comparative SDLC Analysis for Developing a Rural Telemedicine Application" (SDG 3).



Features: appointment booking, doctor panel with prescriptions, status check by phone number, English/Hindi interface, Jitsi video-consult link.



\## Run

pip install -r requirements.txt

streamlit run app.py



Doctor panel password: set the DOCTOR_PASSWORD environment variable (a Jenkins secret in the pipeline).



Note: demo with fictional data only, not for real clinical use.

