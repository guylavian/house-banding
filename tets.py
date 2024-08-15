import requests
import json
import random
import string

# Jira Cloud instance details
JIRA_BASE_URL = 'https://guylavian4-1721247188862.atlassian.net'
AUTH_TOKEN = ''
USER_ACCOUNT_ID = '5e4c33c4052b790c9750a08b'  # Your Jira account ID


# Helper functions
def random_string(length):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def create_project(name, key):
    url = f"{JIRA_BASE_URL}/rest/api/3/project"
    headers = {
        "Authorization": f"Basic {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "key": key,
        "name": name,
        "projectTypeKey": "software",
        "projectTemplateKey": "com.pyxis.greenhopper.jira:gh-scrum-template",
        "leadAccountId": USER_ACCOUNT_ID,
        "permissionScheme": 10000,
        "notificationScheme": 10000,
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
        "Authorization": f"Basic {AUTH_TOKEN}",
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
    if parent_key:
        payload["fields"]["parent"] = {"key": parent_key}
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Check for errors in the response
    if response.status_code != 201:
        print(f"Failed to create issue {summary}. Status code: {response.status_code}, Response: {response.text}")
        return None
    return response.json()


# Create two projects
project1 = create_project("Project One", "PROJ1")
project2 = create_project("Project Two", "PROJ2")

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
        parent_epic = random.choice(portfolio_epics)
        epic = create_issue(project_key, f"Epic {random_string(5)}", "Epic", parent_epic["key"])
        if epic:
            epics.append(epic)

    # Create 30 stories related to epics
    for _ in range(30):
        parent_epic = random.choice(epics)
        create_issue(project_key, f"Story {random_string(5)}", "Story", parent_epic["key"])

print("Projects, portfolio epics, epics, and stories created successfully!")