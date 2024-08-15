import requests
import json
import random
import string
import base64

# Jira Cloud instance details
JIRA_BASE_URL = 'https://guylavian4-1721247188862.atlassian.net'
EMAIL = 'guylavian4@gmail.com'  # Replace with your actual email
API_TOKEN = 'ATATT3xFfGF0EWO021hWEWwnDb959--u00IUTj03948c3XBuzFJ7JIHaf24LrHpwuu27Oqm2Q8kYE3dHD2XcF5QF-7MmEGPNLyJmPlAscnNNaYu9-v3D1PSfDmejMoomtDd7SrZ_sn3oyhkHhS-z7QssU3GLB8gHmVQq9NvdE0LOgl6Lf7VkalI=0C6DBD39'  # Replace with your actual API token
USER_ACCOUNT_ID = '5e4c33c4052b790c9750a08b'  # Replace with your actual account ID

# Encode the credentials
credentials = f"{EMAIL}:{API_TOKEN}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

AUTH_TOKEN = f"Basic {encoded_credentials}"

# Helper functions
def random_string(length):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def create_project(name, key):
    url = f"{JIRA_BASE_URL}/rest/api/3/project"
    headers = {
        "Authorization": AUTH_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "key": key,
        "name": name,
        "projectTypeKey": "software",
        "projectTemplateKey": "com.pyxis.greenhopper.jira:gh-scrum-template",
        "leadAccountId": USER_ACCOUNT_ID,
        "assigneeType": "PROJECT_LEAD"
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Check for errors in the response
    if response.status_code != 201:
        print(f"Failed to create project {name}. Status code: {response.status_code}, Response: {response.text}")
        return None
    return response.json()

def create_issue(project_key, summary, issue_type, parent_key=None):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue"
    headers = {
        "Authorization": AUTH_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "fields": {
            "project": {
                "key": project_key
            },
            "summary": summary,
            "issuetype": {
                "name": issue_type
            }
        }
    }
    if parent_key and issue_type != "Epic":  # Epics cannot have a parent
        payload["fields"]["parent"] = {"key": parent_key}
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Check for errors in the response
    if response.status_code != 201:
        print(f"Failed to create issue {summary}. Status code: {response.status_code}, Response: {response.text}")
        return None
    return response.json()

# Generate unique project names and keys
project_name_1 = f"Project One {random_string(5)}"
project_key_1 = f"PROJ1{random_string(3)}"
project_name_2 = f"Project Two {random_string(5)}"
project_key_2 = f"PROJ2{random_string(3)}"

# Create two projects
project1 = create_project(project_name_1, project_key_1)
project2 = create_project(project_name_2, project_key_2)

if not project1 or not project2:
    print("Project creation failed. Exiting script.")
    exit(1)

projects = [project1, project2]

# Create portfolio epics, epics, and stories
for project in projects:
    project_key = project["key"]
    portfolio_epics = []

    # Create 5 portfolio epics
    for _ in range(5):
        portfolio_epic = create_issue(project_key, f"Portfolio Epic {random_string(5)}", "Epic")
        if portfolio_epic:
            portfolio_epics.append(portfolio_epic)

    # Create 15 epics related to portfolio epics
    epics = []
    for _ in range(15):
        epic = create_issue(project_key, f"Epic {random_string(5)}", "Epic")
        if epic:
            epics.append(epic)

    if not epics:
        print(f"Failed to create any epics in project {project_key}. Exiting script.")
        exit(1)

    # Create 30 stories related to epics
    for _ in range(30):
        parent_epic = random.choice(epics)
        create_issue(project_key, f"Story {random_string(5)}", "Story", parent_epic["key"])

print("Projects, portfolio epics, epics, and stories created successfully!")