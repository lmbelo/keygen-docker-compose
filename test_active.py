import requests

KEYGEN_BASE_URL = "https://api.keygen.localhost/v1"
LICENSE_KEY = "E158E7-938C59-173218-2B3646-466F0A-V3"
FINGERPRINT = "MY-TEST-DEVICE-001"
CA_BUNDLE_PATH = "./certificates/authorities/local/my_local_ca_bundle.pem"

def validate_license(license_key):
    data = {"meta": {"key": license_key}}
    headers = {
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json",
    }
    resp = requests.post(
        f"{KEYGEN_BASE_URL}/licenses/actions/validate-key",
        json=data,
        headers=headers,
        verify=CA_BUNDLE_PATH
    )
    response = resp.json()
    print("[License] Status:", resp.status_code)
    print("[License] Response:", response)
    if resp.status_code == 200 and "data" in response:
        lic = response["data"]
        # Check status for more control
        # The license's status, for filtering purposes and to ascertain overall status at-a-glance. 
        # An active license is a license that has been created, validated, checked out, or checked in within the last 90 days. 
        # An expiring license is a license that is expiring within the next 3 days. 
        # One of: ACTIVE, INACTIVE, EXPIRING, EXPIRED, SUSPENDED, or BANNED
        if lic and lic["attributes"]["status"] == "ACTIVE":
            return lic["id"]
        else:
            print(f"License is not active: {lic['attributes']['status'] if lic else 'Unknown'}")
            return None
    else:
        print("License key invalid or API error.")
        return None

def check_seat_active(license_id, fingerprint, license_key):
    headers = {
        "Authorization": f"License {license_key}",
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json",
    }
    resp = requests.get(
        f"{KEYGEN_BASE_URL}/licenses/{license_id}/machines?fingerprint={fingerprint}",
        headers=headers,
        verify=CA_BUNDLE_PATH
    )
    response = resp.json()
    print("[Machine] Status:", resp.status_code)
    print("[Machine] Response:", response)
    if resp.status_code == 200 and response.get("data"):
        print("Seat is valid and registered for this device.")
        return True
    else:
        print("Seat not found for this license/fingerprint.")
        return False

if __name__ == "__main__":
    license_id = validate_license(LICENSE_KEY)
    if not license_id:
        print("License INVALID or not active. Exiting.")
        exit(1)
    seat_active = check_seat_active(license_id, FINGERPRINT, LICENSE_KEY)
    if not seat_active:
        print("Seat for this device is not ACTIVE. Exiting.")
        exit(1)
    print("License and seat are valid and active. Continue to login/app!")
