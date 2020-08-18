from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

def get_authenticated_google_analytics_service(api_name, api_version, scope, service_account_name):
    """
    Returns a list service account JSON API key from a preset name
    
    TODO: add some error checking when getting the service account from the JSON.
    """
    
    # Retrieve plugin settings
    client = dataiku.api_client()
    plugin = client.get_plugin("google-analytics")
    settings = plugin.get_settings()
    
    # Retrieve service account encrypted preset
    for parameter_set in settings.settings["presets"]:
        
        if (parameter_set["type"] == "parameter-set-google-analytics-google-service-accounts") and (parameter_set["name"] == service_account_name):
            service_account_credentials_encrypted = parameter_set["config"]["service_account_credentials"]
    
    # Decrypt service account key    
    service_account_credentials_str = subprocess.Popen("$DIP_HOME/bin/dku decrypt-password " + str(service_account_credentials_encrypted), 
                                                       shell=True, stdout=subprocess.PIPE, universal_newlines=True).stdout.read()
    
    service_account_credentials = ast.literal_eval(service_account_credentials_str)
    
    # Retrieve an authenticated Google Analytics API service
    service = get_service(api_name, api_version, scope, service_account_credentials) 
    
    return service

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