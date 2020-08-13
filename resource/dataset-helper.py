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
        return get_account_summaries(config)
    
    if payload["method"] == "get_view_properties":
        
        metrics_and_goals = get_metrics_and_goals(config)
        dimensions = get_dimensions(config)
        segments = get_segments(config)
        
        return {"metrics_and_goals" : metrics_and_goals, "dimensions" : dimensions, "segments" : segments}
    
    
def get_account_summaries(config):
    # Get authenticated Google Analytics API service using selected service account
    service = get_authenticated_google_analytics_service(config)
    
    # Retrieve AccountSummaries from Management API
    response = service.management().accountSummaries().list().execute()
    
    # Parse response
    account_summaries = ga_json.parse_accountSummaries(response)
    
    return {"account_summaries" : account_summaries}
 

# Calls Google Analytics API to obtain all metrics and goals associated with the selected View
def get_metrics_and_goals(config):
    
    # (1) Unpack configuration parameters and get API Service
    
    # (1.1) Unpack configuration parameters
    
    
    # (1.2) Get authenticated Google Analytics API service using selected service account
    service = get_authenticated_google_analytics_service(config)
    
    
    # (2) Default Metrics and Dimensions from Metadata API
    
    # (2.1) Retrieve default Metrics and Dimensions from Metadata API
    response = service.metadata().columns().list(reportType='ga').execute()
    
    # (2.2) Parse response (note: templated columns excluded)
    metrics, dimensions = ga_json.parse_columnsMetadata(response)
    
    
    # (3) Retrieve Custom Metrics from Management API
    
    
    # (4) Retrieve Goals from Management API
    
    
    # (5) Retrieve Custom Dimensions from Management API
    
    
    # Construct choices dict
    metrics_and_goals = [ {"value" : metric, "label" : metric["name"]} for metric in metrics ]

    return metrics_and_goals
            
    
def get_dimensions(config):
    # Get authenticated Google Analytics API service using selected service account
    service = get_authenticated_google_analytics_service(config)
    
    # Retrieve default Metrics and Dimensions from Metadata API
    response = service.metadata().columns().list(reportType='ga').execute()
        
    # Parse response
    metrics, dimensions = ga_json.parse_columnsMetadata(response)
    
    # Construct choices dict
    dimensions = [ {"value" : dimension, "label" : dimension["name"]} for dimension in dimensions ]

    return dimensions


def get_segments(config):
    # Get authenticated Google Analytics API service using selected service account
    service = get_authenticated_google_analytics_service(config)
    
    # Retrieve all available Segments from the Management API
    response = service.management().segments().list().execute()
    
    # Parse response
    segments = ga_json.parse_segments(response)
    
    # Construct choices dict
    segments = [ {"value" : segment, "label" : segment["name"]} for segment in segments ]
    
    return segments
    
    
### CUSTOM UI HELPER FUNCTIONS ##

def get_authenticated_google_analytics_service(config):
    """
    Returns a list service account JSON API key from a preset name
    
    TODO: add some error checking when getting the service account from the JSON.
    """
    # Retrieve name of service account selected in UI
    service_account_name = config["service_account"]["name"]
    
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
