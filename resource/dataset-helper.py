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
        return {"account_summaries" : [{"name" : "abc"}, {"name" : "def"}]}
    
    if payload["method"] == "get_views":
        return get_views(config)
    
    if payload["method"] == "get_view_properties":
        metrics_and_goals = get_metrics_and_goals(config)
        dimensions = get_dimensions(config)
        segments = get_segments(config)
        return {"metrics_and_goals" : metrics_and_goals, "dimensions" : dimensions, "segments" : segments}
    
    
# Calls Google Analytics API to obtain all views associated to the authenticated account
def get_views(config):
    
    # Retrieve name of service account select in UI
    service_account_name = config["service_account"]["name"]
    
    # Retrieve service account API key
    service_account_credentials = get_service_account_credentials_from_name(service_account_name)
    
    # Retrieve an authenticated Google Analytics API service
    service = ga_api.get_service(API_NAME, API_VERSION, SCOPE, service_account_credentials) 
    
    # Retrieve AccountSummaries from Management API
    response = service.management().accountSummaries().list().execute()
        
    # Parse response 
    accounts, web_properties, views = ga_json.parse_accountSummaries(response) # 'views' is a list of tuples (view name, web_property name, account_name, view id) tuple
    
    # Returns list of views
    views_formatted = [ {"value" : view, "label" : view[2] + " -> " + view[1] + " -> " + view[0] + " (" + str(view[3]) + ")"} for view in views]
    return {"views" : views_formatted}
 

# Calls Google Analytics API to obtain all metrics and goals associated with the selected View
def get_metrics_and_goals(config):
    
    # Retrieve name of service account select in UI
    service_account_name = config["service_account"]["name"]
    
    # Retrieve service account API key
    service_account_credentials = get_service_account_credentials_from_name(service_account_name)
    
    # Retrieve an authenticated Google Analytics API service
    service = ga_api.get_service(API_NAME, API_VERSION, SCOPE, service_account_credentials)
    
    # Retrieve default Metrics and Dimensions from Metadata API
    response = service.metadata().columns().list(reportType='ga').execute()
    
    # Parse response
    metrics, dimensions = ga_json.parse_columnsMetadata(response)
        
    # Construct choices dict
    metrics_and_goals = [ {"value" : metric, "label" : metric[0]} for metric in metrics ]
    
    return metrics_and_goals
            
    
def get_dimensions(config):
    
    # Retrieve name of service account select in UI
    service_account_name = config["service_account"]["name"]
    
    # Retrieve service account API key
    service_account_credentials = get_service_account_credentials_from_name(service_account_name)
    
    # Retrieve an authenticated Google Analytics API service
    service = ga_api.get_service(API_NAME, API_VERSION, SCOPE, service_account_credentials)
    
    # Retrieve default Metrics and Dimensions from Metadata API
    response = service.metadata().columns().list(reportType='ga').execute()
        
    # Parse response
    metrics, dimensions = ga_json.parse_columnsMetadata(response)
        
    # Construct choices dict
    dimensions = [ {"value" : str(dimension), "label" : dimension[0]} for dimension in dimensions ]

    return dimensions

def get_segments(config):
    
    # Retrieve name of service account select in UI
    service_account_name = config["service_account"]["name"]
    
    # Retrieve service account API key
    service_account_credentials = get_service_account_credentials_from_name(service_account_name)
    
    # Retrieve an authenticated Google Analytics API service
    service = ga_api.get_service(API_NAME, API_VERSION, SCOPE, service_account_credentials)
    
    # Retrieve all available Segments from the Management API
    response = service.management().segments().list().execute()
    
    # Parse response
    segments = ga_json.parse_segments(response)
        
    # Construct choices dict
    segments = [ {"value" : str(segment), "label" : segment[0]} for segment in segments ]
    
    return segments
    
    
### CUSTOM UI HELPER FUNCTIONS (might move these to a common plugin_utils.py module)##

def get_service_account_credentials_from_name(name):
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
        
        if (parameter_set["type"] == "parameter-set-google-analytics-google-service-accounts") and (parameter_set["name"] == name):
            service_account_credentials_encrypted = parameter_set["config"]["service_account_credentials"]
    
    # Decrypt service account key    
    service_account_credentials_str = subprocess.Popen("$DIP_HOME//bin/dku decrypt-password " + str(service_account_credentials_encrypted), 
                                                       shell=True, stdout=subprocess.PIPE, universal_newlines=True).stdout.read()
    
    service_account_credentials = ast.literal_eval(service_account_credentials_str)
    
    return service_account_credentials
