import dataiku
import subprocess
import ast

from googleanalytics import ga_api
from googleanalytics import ga_json

# Google Analytics API definition
API_NAME = 'analytics'
API_VERSION = 'v3'
SCOPE = ['https://www.googleapis.com/auth/analytics.readonly']


def do(payload, config, plugin_config, inputs):
    
    if payload["method"] == "get_project_key":
        return {"project_key" : dataiku.default_project_key()}
    
    
    if payload["method"] == "get_account_summaries":
        
        # Unpack plugin config
        service_account_name = config["service_account"]["name"]
        
        return get_account_summaries(service_account_name)
    
    
    if payload["method"] == "get_view_properties":
        
        # Unpack plugin config
        service_account_name = config["service_account"]["name"]
        account_id = config["account"]["id"]
        web_property_id = config["web_property"]["id"]
        view_id = config["view"]["id"]
        
        metrics, dimensions = get_metrics_and_dimensions(service_account_name, account_id, web_property_id, view_id)
        segments = get_segments(service_account_name)
        
        return {"metrics" : metrics, "dimensions" : dimensions, "segments" : segments}
    
    
    
def get_account_summaries(service_account_name):
    # Get authenticated Google Analytics API service using selected service account
    service = get_authenticated_google_analytics_service(service_account_name)
    
    # Retrieve AccountSummaries from Management API
    response = service.management().accountSummaries().list().execute()
    
    # Parse response
    account_summaries = ga_json.parse_accountSummaries(response)
    
    return {"account_summaries" : account_summaries}
 

# Calls Google Analytics API to obtain all metrics and goals associated with the selected View
def get_metrics_and_dimensions(service_account_name, account_id, web_property_id, view_id)):   
    # Get authenticated Google Analytics API service using selected service account
    service = get_authenticated_google_analytics_service(service_account_name)
    
    # Default Metrics and Dimensions from Metadata API
    response = service.metadata().columns().list(reportType='ga').execute()
    default_metrics, default_dimensions = ga_json.parse_columnsMetadata(response)
    
    # Retrieve Custom Metrics from Management API
    response = service.management().customMetrics().list(accountId=account_id, webPropertyId=web_property_id,).execute()
    custom_metrics = ga_json.parse_customMetrics(response)
    
    # Retrieve Custom Dimensions from Management API
    response = service.management().customDimensions().list(accountId=account_id, webPropertyId=web_property_id,).execute()
    custom_dimensions = ga_json.parse_customDimensions(response)
    
    # Retrieve Goals from Management API
    # TODO

    # Construct choices dicts
    metrics = default_metrics + custom_metrics
    metrics = [ {"value" : metric, "label" : metric["name"]} for metric in metrics ]

    dimensions = default_dimensions + custom_dimensions
    dimensions = [ {"value" : dimension, "label" : dimension["name"]} for dimension in dimensions ]
    
    return metrics, dimensions


def get_segments(service_account_name):
    # Get authenticated Google Analytics API service using selected service account
    service = get_authenticated_google_analytics_service(service_account_name)
    
    # Retrieve all available Segments from the Management API
    response = service.management().segments().list().execute()
    
    # Parse response
    segments = ga_json.parse_segments(response)
    
    # Construct choices dict
    segments = [ {"value" : segment, "label" : segment["name"]} for segment in segments ]
    
    return segments
    
    
### CUSTOM UI HELPER FUNCTIONS ##

def get_authenticated_google_analytics_service(service_account_name):
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
    service_account_credentials_str = subprocess.Popen("$DIP_HOME//bin/dku decrypt-password " + str(service_account_credentials_encrypted), 
                                                       shell=True, stdout=subprocess.PIPE, universal_newlines=True).stdout.read()
    
    service_account_credentials = ast.literal_eval(service_account_credentials_str)
    
    # Retrieve an authenticated Google Analytics API service
    service = ga_api.get_service(API_NAME, API_VERSION, SCOPE, service_account_credentials) 
    
    return service
