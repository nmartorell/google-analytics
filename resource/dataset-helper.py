import dataiku
from dataikuapi.utils import DataikuException

from googleanalytics import ga_api
from googleanalytics import ga_json

# Google Analytics API definition
API_NAME = 'analytics'
API_VERSION = 'v3'
SCOPE = ['https://www.googleapis.com/auth/analytics.readonly']

def do(payload, config, plugin_config, inputs):
    
    if payload["method"] == "validate_plugin_and_preset_ids":
        
        # Unpack plugin config
        plugin_id = config["plugin_id"]
        service_account_preset_id = config["service_account_preset_id"]
        
        validation = validate_plugin_and_preset_ids(plugin_id, service_account_preset_id)
        return {"validation" : validation}
    
    elif payload["method"] == "get_project_key":
        return {"project_key" : dataiku.default_project_key()}
    
    elif payload["method"] == "get_account_summaries":
        
        # Unpack plugin config
        service_account_name = config["service_account"]["name"]
        
        account_summaries = get_account_summaries(service_account_name)
        return {"account_summaries" : account_summaries}
    
    elif payload["method"] == "get_view_properties":
        
        # Unpack plugin config
        service_account_name = config["service_account"]["name"]
        account_id = config["account"]["id"]
        web_property_id = config["web_property"]["id"]
        view_id = config["view"]["id"]
        
        metrics, dimensions = get_metrics_and_dimensions(service_account_name, account_id, web_property_id, view_id)
        segments = get_segments(service_account_name)
        return {"metrics" : metrics, "dimensions" : dimensions, "segments" : segments}

    else:
        raise ValueError("I forgot to define a python helper function... whoops! This is a bug.") 

    
def validate_plugin_and_preset_ids(plugin_id, service_account_preset_id):
    """
    Check that the Plugin and Service Account Preset IDs set in the script.js initialization function actually exist.
    
    This function ensures that, in the unlikely event of either ID changing, that there is a legible error message.
    """
    
    # Retrieve plugin
    client = dataiku.api_client()
    try:
        plugin = client.get_plugin(plugin_id)
    except DataikuException as e:
        raise DataikuException()
            
    settings = plugin.get_settings()
    
        
    return None

    
def get_account_summaries(service_account_name):
    # Get authenticated Google Analytics API service using selected service account
    service = ga_api.get_authenticated_google_analytics_service(API_NAME, API_VERSION, SCOPE, service_account_name)
    
    # Retrieve AccountSummaries from Management API
    response = service.management().accountSummaries().list().execute()
    
    # Parse response
    account_summaries = ga_json.parse_accountSummaries(response)
    
    return account_summaries
 

# Calls Google Analytics API to obtain all metrics and goals associated with the selected View
def get_metrics_and_dimensions(service_account_name, account_id, web_property_id, view_id):   
    # Get authenticated Google Analytics API service using selected service account
    service = ga_api.get_authenticated_google_analytics_service(API_NAME, API_VERSION, SCOPE, service_account_name)
    
    # Default Metrics and Dimensions from Metadata API
    response = service.metadata().columns().list(reportType='ga').execute()
    default_metrics, default_dimensions = ga_json.parse_columnsMetadata(response)
    
    # Retrieve Custom Metrics from Management API
    response = service.management().customMetrics().list(accountId=account_id, webPropertyId=web_property_id,).execute()
    custom_metrics = ga_json.parse_customMetrics(response)
    
    # Retrieve Custom Dimensions from Management API
    response = service.management().customDimensions().list(accountId=account_id, webPropertyId=web_property_id,).execute()
    custom_dimensions = ga_json.parse_customDimensions(response)
    
    # Retrieve Goals from Management API (Goals are a type of Metric)
    response = service.management().goals().list(accountId=account_id, webPropertyId=web_property_id, profileId=view_id).execute()
    goals = ga_json.parse_goals(response)

    # Construct return lists
    metrics = default_metrics + custom_metrics + goals
    dimensions = default_dimensions + custom_dimensions
    
    # Sort by metric and dimension name (this leads to better dropdowns in the UI)
    metrics = sorted(metrics, key=lambda metric: metric['name']) 
    dimensions = sorted(dimensions, key=lambda dimension: dimension['name']) 
    
    return metrics, dimensions


def get_segments(service_account_name):
    # Get authenticated Google Analytics API service using selected service account
    service = ga_api.get_authenticated_google_analytics_service(API_NAME, API_VERSION, SCOPE, service_account_name)
    
    # Retrieve all available Segments from the Management API
    response = service.management().segments().list().execute()
    
    # Parse response
    segments = ga_json.parse_segments(response)
    
    # Sort by segmments by name (this leads to better dropdowns in the UI)
    segments = sorted(segments, key=lambda segment: segment['name'])
    
    return segments