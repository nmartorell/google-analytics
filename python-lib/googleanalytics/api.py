import dataiku
import subprocess
import ast

from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

def get_authenticated_service(api_name, api_version, scope, plugin_id, service_account_preset_id, service_account_name):
    """
    Returns a list service account JSON API key from a preset name
    """
    
    # Retrieve plugin settings
    client = dataiku.api_client()
    plugin = client.get_plugin(plugin_id)
    settings = plugin.get_settings()
    
    # Contruct parameter set type from parameter set and plugin IDs
    service_account_preset_type = "parameter-set-{0}-{1}".format(plugin_id, service_account_preset_id)
    
    # Retrieve encrypted service account preset
    service_account_credentials_encrypted = None
    for parameter_set in settings.settings["presets"]:
        
        if (parameter_set["type"] == service_account_preset_type) and (parameter_set["name"] == service_account_name):
            service_account_credentials_encrypted = parameter_set["config"]["service_account_credentials"]
    
    if not service_account_credentials_encrypted:
        raise Exception("Service Account Preset not found, most likely due to it having been deleted. Select a different Service Account under the dataset settings, " + \
                        "or contact yout DSS Administrator if none are available.")
    
    # Decrypt preset account key
    service_account_credentials_str = subprocess.Popen("$DIP_HOME/bin/dku decrypt-password " + str(service_account_credentials_encrypted), 
                                                       shell=True, stdout=subprocess.PIPE, universal_newlines=True).stdout.read()
    
    # Retreieve Google Analytics service
    try:
        service_account_credentials_json = ast.literal_eval(service_account_credentials_str)
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(service_account_credentials_json, scope)
        service = build(api_name, api_version, credentials=credentials)    
    except:
        raise Exception("Failed to retreive authenticated Google Analytics API Service. Caused by an invalid Serivce Account Secret key. " + \
                        "See stacktrace for more details, and contact your DSS Administrator.")
    
    return service