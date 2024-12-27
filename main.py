import time
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import argparse

urllib3.disable_warnings(category=InsecureRequestWarning)

def upgrade_task(url, headers):
    requests.post(url, headers=headers, verify=False)

def get_collection_hosts(console, headers, collection_name):
    url = f"https://{console}/api/v1/collections"
    params = {"excludePrisma": False, "prisma": False, "system": False}
    response_plain = requests.get(url, headers=headers, params=params, verify=False)
    response = response_plain.json()
    for collection in response:
        if collection["name"] == collection_name:
            name = collection["name"]
            print(f"found collection! {name}")
            return collection["hosts"]
    return []

def get_defenders(console, headers):
    url = f"https://{console}/api/v32.07/defenders"
    headers["Content-Type"] = "application/json"

    params = {"offset": 0}
    defenders = []
    while True:
        response = requests.get(
            url, headers=headers, params=params, verify=False
        ).json()
        if not response:
            break
        defenders.extend(response)
        params["offset"] += 50
        print(f"getting defenders with offset {params}")
    return defenders

def upgrade_defenders(collection_name):
    console = "us-west1.cloud.twistlock.com/us-3-159241910"
    headers = {
        "Authorization": "Bearer <your token goes here>",
        "Content-Type": "text/plain",
    }
    hosts = get_collection_hosts(console, headers, collection_name)

    if not hosts:
        print(f"No hosts found for collection {collection_name}")
        return

    upgraded_hosts_count = 1
    for host in hosts:
        if upgraded_hosts_count % 100 == 0:
            time.sleep(120)  # sleep 2 minutes after upgrade of 100 defenders
        print(f"Will run upgrade for host {host}")
        upgrade_url = f"https://{console}/api/v1/defenders/{host}/upgrade"
        try:
            print("Upgrading")
            upgrade_task(upgrade_url, headers)
        except Exception as e:
            print(e)
        upgraded_hosts_count += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upgrade defenders in a specified collection.')
    parser.add_argument('-c', '--collection', type=str, required=True, help='The name of the collection.')
    args = parser.parse_args()

    upgrade_defenders(args.collection)
