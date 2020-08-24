import dataiku
import subprocess
import ast

from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

def get_authenticated_service(api_name, api_version, scope, plugin_id, service_account_preset_id, service_account_name):
    """
    This function retrieves the encrypted Service Account secret, decrypts it, and uses it to retrieve an authenticated
    Google Analytics service object.
    
    Returns:
    An authenticated Google Analytics service object.
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
    except Exception as e:
        raise Exception("Failed to retreive authenticated Google Analytics API Service. Caused by an invalid Serivce Account Secret. " + \
                        "See stacktrace for further details, and contact your DSS Administrator.") from e
    
    return service


def get_account_summaries(service):
    """
    Queries for the Account Summaries "list" API call:
    https://developers.google.com/analytics/devguides/config/mgmt/v3/mgmtReference/management/accountSummaries/list

    Returns:
    The raw JSON response from the API call.
    """
    
    try:
        response = service.management().accountSummaries().list().execute()
    except Exception as e:
        raise Exception("Failed to query for Account Summaries. See the stacktrace for further details.") from e
    
    return response


def get_default_metrics_and_dimensions(service):
    """
    Queries for default Columns via the Metadata "list" API call:
    https://developers.google.com/analytics/devguides/reporting/metadata/v3/reference/metadata/columns/list
   
    Note that both METRICS and DIMENSIONS are defined as "columns".
    
    Returns:
    The raw JSON response from the API call.
    """
    
    try:
        response = service.metadata().columns().list(reportType='ga').execute()
    except Exception as e:
        raise Exception("Failed to query for Columns from Metadata API. See the stacktrace for further details.") from e
    
    return response


def get_custom_metrics(service, account_id, web_property_id):
    """
    Queries for Custom Metrics via the Management "list" API call:
    https://developers.google.com/analytics/devguides/config/mgmt/v3/mgmtReference/management/customMetrics/list
    
    Returns:
    The raw JSON response from the API call.
    """
    
    try:
        response = service.management().customMetrics().list(accountId=account_id, webPropertyId=web_property_id,).execute()
    except Exception as e:
        raise Exception("Failed to query for Custom Metrics from Management API. See the stacktrace for further details.") from e
    
    return response


def get_custom_dimensions(service, account_id, web_property_id):
    """
    Queries for Custom Dimensions via the Management "list" API call:
    https://developers.google.com/analytics/devguides/config/mgmt/v3/mgmtReference/management/customDimensions/list
    
    Returns:
    The raw JSON response from the API call.
    """
    
    try:
        response = service.management().customDimensions().list(accountId=account_id, webPropertyId=web_property_id,).execute()
    except Exception as e:
        raise Exception("Failed to query for Custom Dimensions from Management API. See the stacktrace for further details.") from e
    
    return response


def get_goals(service, account_id, web_property_id, view_id):
    """
    Queries for Goals via the Management "list" API call:
    https://developers.google.com/analytics/devguides/config/mgmt/v3/mgmtReference/management/goals/list
    
    Returns:
    The raw JSON response from the API call.
    """
    
    try:
        response = service.management().goals().list(accountId=account_id, webPropertyId=web_property_id, profileId=view_id).execute()
    except Exception as e:
        raise Exception("Failed to query for Goals from Management API. See the stacktrace for further details.") from e
    
    return response


def get_segments(service, account_id, web_property_id, view_id):
    """
    Queries for Goals via the Management "list" API call:
    https://developers.google.com/analytics/devguides/config/mgmt/v3/mgmtReference/management/goals/list
    
    Returns:
    The raw JSON response from the API call.
    """
    
    try:
        response = service.management().goals().list(accountId=account_id, webPropertyId=web_property_id, profileId=view_id).execute()
    except Exception as e:
        raise Exception("Failed to query for Goals from Management API. See the stacktrace for further details.") from e
    
    return response
    
    