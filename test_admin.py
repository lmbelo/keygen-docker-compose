import requests
from requests.auth import HTTPBasicAuth

KEYGEN_BASE_URL = "https://api.keygen.localhost/v1"
ADMIN_EMAIL = "user@user.com"
ADMIN_PASSWORD = "123"
CA_BUNDLE_PATH = "./certificates/authorities/local/my_local_ca_bundle.pem"

def get_admin_token():
    resp = requests.post(
        f"{KEYGEN_BASE_URL}/tokens",
        headers={"Accept": "application/vnd.api+json"},
        auth=HTTPBasicAuth(ADMIN_EMAIL, ADMIN_PASSWORD),
        verify=CA_BUNDLE_PATH
    )
    resp.raise_for_status()
    token = resp.json()["data"]["attributes"]["token"]
    print(f"Admin token: {token[:8]}...")  # show only first 8 chars
    return token

def create_product(token, name, code):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json",
    }
    data = {
        "data": {
            "type": "products",
            "attributes": {
                "name": name,
            }
        }
    }
    try:
        resp = requests.post(f"{KEYGEN_BASE_URL}/products", 
                            json=data, 
                            headers=headers,
                            verify=CA_BUNDLE_PATH)
        resp.raise_for_status()
    except requests.HTTPError as e:
        print("Status:", resp.status_code)
        print("Response:", resp.text)
        raise
    prod = resp.json()["data"]
    print(f"Product created: {prod['id']} ({prod['attributes']['name']})")
    return prod["id"]

def create_policy(token, product_id, name, max_seats, heartbeat_days=7):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json"
    }
    heartbeat_interval = heartbeat_days * 24 * 3600
    data = {
        "data": {
            "type": "policies",
            "attributes": {
                "name": name,
                "strict": True,
                "floating": True,
                "duration": 31536000,
                "machineUniquenessStrategy": "UNIQUE_PER_LICENSE",
                "maxMachines": max_seats,
                #"requireHeartbeat": True,
                #"heartbeatInterval": heartbeat_interval,
                "authenticationStrategy": "LICENSE"
            },
            "relationships": {
                "product": {
                    "data": {"type": "products", "id": product_id}
                }
            }
        }
    }
    try:
        resp = requests.post(f"{KEYGEN_BASE_URL}/policies", 
                            json=data, 
                            headers=headers,
                            verify=CA_BUNDLE_PATH)
        resp.raise_for_status()
    except requests.HTTPError as e:
        print("Status:", resp.status_code)
        print("Response:", resp.text)
        raise
    policy = resp.json()["data"]
    print(f"Policy created: {policy['id']} ({policy['attributes']['name']})")
    return policy["id"]

def create_license(token, policy_id):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json",
    }
    data = {
        "data": {
            "type": "licenses",
            "relationships": {
                "policy": {"data": {"type": "policies", "id": policy_id}}
            }
        }
    }
    resp = requests.post(f"{KEYGEN_BASE_URL}/licenses", 
                         json=data, 
                         headers=headers,
                         verify=CA_BUNDLE_PATH)
    resp.raise_for_status()
    lic = resp.json()["data"]
    print(f"License created: {lic['id']} (key: {lic['attributes']['key']})")
    return lic["id"], lic["attributes"]["key"]

if __name__ == "__main__":
    # 1. Authenticate and get a token
    admin_token = get_admin_token()

    # 2. Create the product
    product_id = create_product(admin_token, "BI Designer Client Desktop", "bi-designer-client")

    # 3. Create the policy (weekly heartbeat, 3 seats)
    policy_id = create_policy(
        admin_token,
        product_id,
        "Standard License (Weekly Heartbeat, 3 Seats)",
        max_seats=3,
        heartbeat_days=7
    )

    # 4. Issue license (serial key)
    license_id, license_key = create_license(admin_token, policy_id)

    print("\nREADY TO DISTRIBUTE TO CLIENT:")
    print(f"License key: {license_key}")
