import requests

# The URL of your running Flask API
url = 'http://127.0.0.1:5000/extract_text'

# The name of your image file, which is in the same directory
image_file_name = 'example id .png'

# Open the file in binary read mode ('rb')
# The 'files' dictionary is how you tell the requests library to send a file
try:
    with open(image_file_name, 'rb') as image_file:
        files = {'file': image_file}
        
        response = requests.post(url, files=files)
        response.raise_for_status()  # This will raise an exception for HTTP error codes
        
        print("API Response:")
        print(response.json())

except FileNotFoundError:
    print(f"Error: The file '{image_file_name}' was not found in the current directory.")
except requests.exceptions.RequestException as e:
    print(f"An error occurred while making the API request: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")