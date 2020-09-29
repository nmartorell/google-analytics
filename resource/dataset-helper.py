import dataiku
import googleanalytics

# Parameters for Google Analytics V3 API (Metadata and Managements APIs)
API_NAME = 'analytics'
API_VERSION = 'v3'
SCOPE = ['https://www.googleapis.com/auth/analytics.readonly']

def do(payload, config, plugin_config, inputs):
    
    # Unpack config
    plugin_id = config.get("plugin_id", "")
    service_account_preset_id = config.get("service_account_preset_id", "")
    service_account_name = config.get("service_account", dict()).get("name", "")
    
    account_id = config.get("account", dict()).get("id", "")
    web_property_id = config.get("web_property", dict()).get("id", "")
    view_id = config.get("view", dict()).get("id", "")
    
    # Select appropriate method based on payload
    if payload["method"] == "validate_plugin_and_preset_ids":        
        validation = validate_plugin_and_preset_ids(plugin_id, service_account_preset_id)
        return {"validation" : validation}
    
    elif payload["method"] == "get_project_key":
        return {"project_key" : dataiku.default_project_key()}
    
    elif payload["method"] == "get_preset_credentials":
        
        return 
    
    elif payload["method"] == "get_account_summaries":        
        account_summaries = get_account_summaries(plugin_id, service_account_preset_id, service_account_name)
        return {"account_summaries" : account_summaries}
    
    elif payload["method"] == "get_view_properties":        
        metrics, dimensions = get_metrics_and_dimensions(plugin_id, service_account_preset_id, service_account_name, account_id, web_property_id, view_id)
        segments = get_segments(plugin_id, service_account_preset_id, service_account_name)
        return {"metrics" : metrics, "dimensions" : dimensions, "segments" : segments}

    else:
        raise ValueError("I forgot to define a python helper function... whoops! This is a bug.") 

    
def validate_plugin_and_preset_ids(plugin_id, service_account_preset_id):
    """
    Check that the Plugin and Service Account Preset IDs set in the script.js initialization function actually exist.
    This function ensures that, in the unlikely event of either ID changing, there is a legible error message.
    """
    
    # Retrieve plugin settings
    client = dataiku.api_client()
    
    try:
        plugin = client.get_plugin(plugin_id)
        settings = plugin.get_settings()
    except Exception as e:
        raise ValueError("There is a mismatch between the plugin ID and the ID hardcoded in the initialization function of script.js." + \
                         "This is likely due to the plugin ID having been manually changed. Please update the value in the script.js.") from e
            
    # Check the service account preset ID is correct
    parameter_set_type = "parameter-set-{0}-{1}".format(plugin_id, service_account_preset_id)
    parameter_set_list = [ param_set["type"] for param_set in settings.settings["presets"]]
    
    if parameter_set_type not in parameter_set_list:
        raise ValueError("The Google Service Account parameter ID hardcoded in the script.js does not correspond to any parameters in the plugin." + \
                          "This is likely due to the parameter ID having been manually changed. Please update the value in the script.js.")

    return "OK"

    
def get_account_summaries(plugin_id, service_account_preset_id, service_account_name):
    """
    Retrieve Account, Web Property and View information accessible to the authenticated Google Service account. 
    """
    
    # Get authenticated Google Analytics API service using selected service account
    service = googleanalytics.api.get_authenticated_service(API_NAME, 
                                                            API_VERSION, 
                                                            SCOPE, 
                                                            plugin_id, 
                                                            service_account_preset_id, 
                                                            service_account_name)
    
    # Retrieve AccountSummaries from Management API
    response = googleanalytics.api.get_account_summaries(service)
    
    # Parse response
    account_summaries = googleanalytics.json.parse_account_summaries(response)
    
    return account_summaries
 

def get_metrics_and_dimensions(plugin_id, service_account_preset_id, service_account_name, account_id, web_property_id, view_id):   
    """
    Retrieve all Metrics and Dimensions associated to the selected Web Property and View.
    """
    
    # Get authenticated Google Analytics API service using selected service account
    service = googleanalytics.api.get_authenticated_service(API_NAME, 
                                                            API_VERSION, 
                                                            SCOPE, 
                                                            plugin_id, 
                                                            service_account_preset_id, 
                                                            service_account_name)
    
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


def get_segments(plugin_id, service_account_preset_id, service_account_name):
    """
    Retrieve the Segments accessible to the authenticated Google Service account.
    """
    
    # Get authenticated Google Analytics API service using selected service account
    service = googleanalytics.api.get_authenticated_service(API_NAME, 
                                                            API_VERSION, 
                                                            SCOPE, 
                                                            plugin_id, 
                                                            service_account_preset_id, 
                                                            service_account_name)
    
    # Retrieve all available Segments from the Management API
    response = googleanalytics.api.get_segments(service)
    segments = googleanalytics.json.parse_segments(response)
    
    # Sort by segmments by name (this leads to better dropdowns in the UI)
    segments = sorted(segments, key=lambda segment: segment['name'])
    
    return segments