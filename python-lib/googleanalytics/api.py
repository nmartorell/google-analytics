import dataiku
import subprocess
import ast
import json

from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build



def get_service_account_credentials(plugin_id, service_account_preset_id, service_account_name):
    """
    This function retrieves the encrypted Service Account secret, and decrypts it.
    
    Returns:
    Decrypted Service Account secret
    """
    
    # Retrieve per-user credentials
    client = dataiku.api_client()
    user = client.get_own_user()
    settings = user.get_settings().settings
    per_user_credentials = settings["credentials"]
    
    # Extract the encrypted credentials for the selected service_account_name
    for credentials_key, credentials_dict in per_user_credentials:
        
        # Unpack credentials key
        credentials_key_list = ast.literal_eval(credentials_key.split(','))
        
        # Pass on any connection per-user credentials
        if len(credentials_key_list) != 5:
            continue
            
        # Validate that the credentials key matches the user selection
        credentials_plugin_id = credentials_key_list[1]
        credentials_service_account_preset_id = credentials_key_list[2]
        credentials_service_account_name = credentials_key_list[3]
        
        print(credentials_plugin_id)   
        print(credentials_service_account_preset_id)
        print(credentials_service_account_name)
        asdf
        
    
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
            service_account_credentials_encrypted = parameter_set["config"].get("service_account_credentials", None)
    
    if not service_account_credentials_encrypted:
        raise Exception("No Service Account credentials have been entered for this preset, please contact your DSS Administrator.")
    
    # Decrypt preset account key
    service_account_credentials = subprocess.Popen("$DIP_HOME/bin/dku decrypt-password " + str(service_account_credentials_encrypted), 
                                                    shell=True, stdout=subprocess.PIPE, universal_newlines=True).stdout.read()
    
    return service_account_credentials
   

def get_authenticated_service(api_name, api_version, scope, service_account_credentials):
    """
    This function retrieves an authenticated Google Analytics service object.
    
    Returns:
    An authenticated Google Analytics service object.
    """
    
    # Retreieve Google Analytics service
    try:
        service_account_credentials_json = json.loads(service_account_credentials)
        #service_account_credentials_json = ast.literal_eval(service_account_credentials)
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(service_account_credentials_json, scope)
        service = build(api_name, api_version, credentials=credentials)    
    except Exception as e:
        raise Exception("Failed to retreive authenticated Google Analytics API Service. Caused by an invalid Serivce Account Secret. " + \
                        "See stacktrace for further details, and contact your DSS Administrator.") from e
    
    return service


## FUNCTIONS FOR MANAGEMENT AND METADATA APIs ##

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
        raise Exception("Failed to query for Account Summaries from Google Analytics Management API. See the stacktrace for further details.") from e
    
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
        raise Exception("Failed to query for Columns from Google Analytics Metadata API. See the stacktrace for further details.") from e
    
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
        raise Exception("Failed to query for Custom Metrics from Google Analytics Management API. See the stacktrace for further details.") from e
    
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
        raise Exception("Failed to query for Custom Dimensions from Google Analytics Management API. See the stacktrace for further details.") from e
    
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
        raise Exception("Failed to query for Goals from Google Analytics Management API. See the stacktrace for further details.") from e
    
    return response


def get_segments(service):
    """
    Queries for Segments via the Management "list" API call:
    https://developers.google.com/analytics/devguides/config/mgmt/v3/mgmtReference/management/segments/list
    
    Returns:
    The raw JSON response from the API call.
    """
    
    try:
        response = service.management().segments().list().execute()
    except Exception as e:
        raise Exception("Failed to query for Segments from Google Analytics Management API. See the stacktrace for further details.") from e
    
    return response


def get_segments(service):
    """
    Queries for Segments via the Management "list" API call:
    https://developers.google.com/analytics/devguides/config/mgmt/v3/mgmtReference/management/segments/list
    
    Returns:
    The raw JSON response from the API call.
    """
    
    try:
        response = service.management().segments().list().execute()
    except Exception as e:
        raise Exception("Failed to query for Segments from Google Analytics Management API. See the stacktrace for further details.") from e
    
    return response


## FUNCTIONS FOR REPORTING API ##

def get_report(service, query_body):
    """
    Query for Google Analytics data via the Reporting "batchGet" API call:
    https://developers.google.com/analytics/devguides/reporting/core/v4/rest/v4/reports/batchGet
    
    Returns:
    The raw JSON response from the API call.
    """
    
    try:
        response = service.reports().batchGet(body=query_body).execute()
    except Exception as e:
        raise Exception("Failed to query for the requested Google Analytics data. See the stacktrace for further details.") from e
        
    return response
