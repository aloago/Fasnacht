import requests

# Base URL for the request
base_url = "http://krimidinner.party/download/"

# Function to attempt a connection to the subdomain
def try_connect(number):
    # Generate the full URL
    url = f"{base_url}{str(number).zfill(10)}"
    
    try:
        # Attempt to connect to the URL
        response = requests.get(url, timeout=5)  # Timeout after 5 seconds

        # Check the response status code
        if response.status_code == 200:
            print(f"Success: {url} is accessible!")
        else:
            print(f"Failed: {url} returned status code {response.status_code}")
    except requests.RequestException as e:
        # Handle any connection errors (e.g., timeouts or invalid URLs)
        print(f"Error: Could not connect to {url}. Exception: {e}")

# Loop through the range of numbers from 0 to 9999999999
for i in range(10000000000):  # 10-digit numbers
    try_connect(i)

print("Finished attempting connections.")
