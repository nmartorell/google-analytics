import dataiku
import googleanalytics

# Parameters for Google Analytics V3 API (Metadata and Managements APIs)
API_NAME = 'analytics'
API_VERSION = 'v3'
SCOPE = ['https://www.googleapis.com/auth/analytics.readonly']

def do(payload, config, plugin_config, inputs):
    
    # Unpack config
    user_secret = config.get("user_secret", "")
    service_account_credentials = config.get("service_account_credentials", "")
    
    account_id = config.get("account", dict()).get("id", "")
    web_property_id = config.get("web_property", dict()).get("id", "")
    view_id = config.get("view", dict()).get("id", "")
    
    # Select appropriate method based on payload    
    if payload["method"] == "get_user_secrets":
        user_secrets = get_user_secrets_list()
        return {"user_secrets" : user_secrets}
    
    elif payload["method"] == "get_service_account_credentials":
        service_account_credentials = get_service_account_credentials(user_secret)
        return {"service_account_credentials" : service_account_credentials}
    
    elif payload["method"] == "get_account_summaries":        
        account_summaries = get_account_summaries(service_account_credentials)
        return {"account_summaries" : account_summaries}
    
    elif payload["method"] == "get_view_properties":        
        metrics, dimensions = get_metrics_and_dimensions(service_account_credentials, account_id, web_property_id, view_id)
        segments = get_segments(service_account_credentials)
        return {"metrics" : metrics, "dimensions" : dimensions, "segments" : segments}

    else:
        raise ValueError("I forgot to define a python helper function... whoops! This is a bug.") 

        
def get_user_secrets():
    """
    Retrieve a list of the available User Secret names of the logged in user. 
    """
    client = dataiku.api_client()
    auth_info = client.get_auth_info()
    user_name = auth_info["authIdentifier"]
    
    user = client.get_user(user_name)
    secrets = user.get_definition()["secrets"]
    
    return secrets


def get_service_account_credentials(user_secret):
    """
    Retrieve Service Account Credentials for selected Service Account. 
    """
    
    return googleanalytics.api.get_service_account_credentials(user_secret)

    
def get_account_summaries(service_account_credentials):
    """
    Retrieve Account, Web Property and View information accessible to the authenticated Google Service account. 
    """
    
    # Get authenticated Google Analytics API service using selected service account
    service = googleanalytics.api.get_authenticated_service(API_NAME, 
                                                            API_VERSION, 
                                                            SCOPE, 
                                                            service_account_credentials)
    
    # Retrieve AccountSummaries from Management API
    response = googleanalytics.api.get_account_summaries(service)
    
    # Parse response
    account_summaries = googleanalytics.json.parse_account_summaries(response)
    
    return account_summaries
 

def get_metrics_and_dimensions(service_account_credentials, account_id, web_property_id, view_id):   
    """
    Retrieve all Metrics and Dimensions associated to the selected Web Property and View.
    """
    
    # Get authenticated Google Analytics API service using selected service account
    service = googleanalytics.api.get_authenticated_service(API_NAME, 
                                                            API_VERSION, 
                                                            SCOPE, 
                                                            service_account_credentials)
    
    # Default Metrics and Dimensions from Metadata API
    response = googleanalytics.api.get_default_metrics_and_dimensions(service)
    default_metrics, default_dimensions = googleanalytics.json.parse_columns_metadata(response)
    
    # Retrieve Custom Metrics from Management API
    response = googleanalytics.api.get_custom_metrics(service, account_id, web_property_id)
    custom_metrics = googleanalytics.json.parse_custom_metrics(response)
    
    # Retrieve Custom Dimensions from Management API
    response = googleanalytics.api.get_custom_dimensions(service, account_id, web_property_id)
    custom_dimensions = googleanalytics.json.parse_custom_dimensions(response)
    
    # Retrieve Goals from Management API (Goals are a type of Metric)
    response = googleanalytics.api.get_goals(service, account_id, web_property_id, view_id)
    goals = googleanalytics.json.parse_goals(response)

    # Construct return lists
    metrics = default_metrics + custom_metrics + goals
    dimensions = default_dimensions + custom_dimensions
    
    # Sort by metric and dimension name (this leads to better dropdowns in the UI)
    metrics = sorted(metrics, key=lambda metric: metric['name']) 
    dimensions = sorted(dimensions, key=lambda dimension: dimension['name']) 
    
    return metrics, dimensions


def get_segments(service_account_credentials):
    """
    Retrieve the Segments accessible to the authenticated Google Service account.
    """
    
    # Get authenticated Google Analytics API service using selected service account
    service = googleanalytics.api.get_authenticated_service(API_NAME, 
                                                            API_VERSION, 
                                                            SCOPE, 
                                                            service_account_credentials)
    
    # Retrieve all available Segments from the Management API
    response = googleanalytics.api.get_segments(service)
    segments = googleanalytics.json.parse_segments(response)
    
    # Sort by segmments by name (this leads to better dropdowns in the UI)
    segments = sorted(segments, key=lambda segment: segment['name'])
    
    return segments