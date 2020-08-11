from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

def get_service(api_name, api_version, scope, service_account_keyfile_dict):
    
    """
    Initializes a Google API using a Service Account json key

    Returns:
    An authorized Google API service object.
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(service_account_keyfile_dict, scope)

    # Build the service object.
    analytics = build(api_name, api_version, credentials=credentials)

    return analytics