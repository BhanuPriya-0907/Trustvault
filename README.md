\# TrustVault — Secure Document Sharing



TrustVault is a secure document-sharing application designed to prevent unauthorized access to sensitive files and maintain an audit trail of sharing activities.



\## Features



\- User registration and login

\- Token-based authentication

\- Secure document upload and download

\- Permission-controlled document sharing

\- Read and edit permission checks

\- Audit logging for sharing activities

\- File type and file size validation

\- REST API built with FastAPI



\## Technology Stack



\- Python

\- FastAPI

\- SQLAlchemy

\- Uvicorn

\- Pytest



\## Project Structure



```text

TrustVault/

├── backend/

│   └── app/

├── tests/

├── requirements.txt

├── .gitignore

└── README.md

```



\## Installation



Open PowerShell in the project folder and run:



```powershell

python -m venv .venv

.\\.venv\\Scripts\\Activate.ps1

pip install -r requirements.txt

```



\## Configure and Run



Set the application path:



```powershell

$env:PYTHONPATH = "$PWD\\backend"

```



Set a unique development secret:



```powershell

$env:TRUSTVAULT\_SECRET\_KEY = "replace-with-a-long-random-secret"

```



Start the server:



```powershell

python -m uvicorn app

