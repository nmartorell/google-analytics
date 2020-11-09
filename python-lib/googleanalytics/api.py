import dataiku
import subprocess
import ast
import json
import socket

from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

# for exponential backoff implementation
import random
import time
from apiclient.errors import HttpError


def get_service_account_credentials(user_secret):
    """
    Extract user secret value, and decrypts if necessary.
    
    Returns:
    Decrypted Service Account secret
    """
    
    # Retrieve user secrets
    client = dataiku.api_client()
    auth_info = client.get_auth_info(with_secrets=True)
    user_secrets = auth_info["secrets"]

    # Select credential from user secret selected by user
    for secret in user_secrets:
        if user_secret == secret["key"]:
            service_account_credentials = secret["value"]
            break
    
    return service_account_credentials
   

def get_authenticated_service(api_name, api_version, scope, service_account_credentials):
    """
    This function retrieves an authenticated Google Analytics service object.
    
    Returns:
    An authenticated Google Analytics service object.
    """
    
    # Set timeout to 10 minutes (as sometimes fails)
    socket.setdefaulttimeout(600) 
    
    # Retreieve Google Analytics service
    try:
        service_account_credentials_json = json.loads(service_account_credentials)
        #service_account_credentials_json = ast.literal_eval(service_account_credentials)
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(service_account_credentials_json, scope)
        service = build(api_name, api_version, credentials=credentials)    
    except Exception as e:
        raise Exception("Failed to retreive authenticated Google Analytics API Service. Caused by an invalid Serivce Account Secret.") from e
    
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
    
    Exponential backoff implemented from as described in:
    https://developers.google.com/analytics/devguides/reporting/core/v3/errors#backoff
    
    Returns:
    The raw JSON response from the API call.
    """
     
    try:
        response = service.reports().batchGet(body=query_body).execute()
    except Exception as e:
        raise Exception("Failed to query for the requested Google Analytics data. See the stacktrace for further details.") from e
        
    return response








