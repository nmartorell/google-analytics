## FUNCTIONS FOR MANAGEMENT API ##

def parse_accountSummariesList(response):
    
    """
    Parses the response of the Account Summaries "list" API call:
    https://developers.google.com/analytics/devguides/config/mgmt/v3/mgmtReference/management/accountSummaries/list
    
    Returns:
    A list of account summary dicts. 
    
    account_summary --> {"name":acct_name, "id":acct_id, "web_properties":[...]}
    web_property    --> {"name":wp_name, "id":wp_id, "views":[...]}
    view            --> {"name":view_name, "id":view_id}
    """
    
    # Initialize return variable
    account_summaries = list()
    
    # Parse json
    for account_response in response["items"]:
        
        # Initialize dict for current account
        account = dict()
        
        # Add name and id of account
        account["name"] = account_response["name"]
        account["id"] = account_response["id"]
        
        # Generate web_properties list for account
        account["web_properties"] = list()
        for web_property_response in account_response["webProperties"]:
            
            # Initialize dict for current web property
            web_property = dict()
            
            # Add name and id of web property
            web_property["name"] = web_property_response["name"]
            web_property["id"] = web_property_response["id"]

            # Generate views list for web property
            web_property["views"] = list()
            for view_response in web_property_response["profiles"]:
                
                # Initialize dict for current view
                view = dict()
                
                # Add name and id of view
                view["name"] = view_response["name"]
                view["id"] = view_response["id"]
                
                web_property["views"].append(view)
            account["web_properties"].append(web_property)
        account_summaries.append(account)
        
    return account_summaries


def parse_accountSummaries(response):
    
    """
    Parses the response of the Account Summaries "list" API call:
    https://developers.google.com/analytics/devguides/config/mgmt/v3/mgmtReference/management/accountSummaries/list
    
    Returns:
    Three lists of tuples (name, id) for all Accounts, webProperties and Views available to the authenticated user.
    """
    
    # Initialize return variables
    accounts = list()
    web_properties = list()
    views = list()
    
    # Parse json
    for account_summary in response["items"]:
        accounts.append((account_summary["name"], account_summary["id"])) # (account name, account id) tuple
        
        for web_property in account_summary["webProperties"]:
            web_properties.append((web_property["name"], account_summary["name"], web_property["id"])) # (web_property name, account_name, web property id) tuple
            
            for view in web_property["profiles"]:
                views.append((view["name"], web_property["name"], account_summary["name"], view["id"])) # (view name, web_property name, account_name, view id) tuple
    
    return accounts, web_properties, views

def parse_segments(response):
    
    """
    Parses the response of the Segments "list" API call:
    https://developers.google.com/analytics/devguides/config/mgmt/v3/mgmtReference/management/segments/list
    
    Returns:
    A list of tuples (name, id) for all Segments available to the authenticated user.
    """
    
    # Initialize return variable
    segments = list()
    
    for segment in response["items"]:
        
        identifier = segment["segmentId"]
        name = segment["name"]
        
        segments.append((name, identifier))
        
    return segments


## FUNCTIONS FOR METADATA API ##

def parse_columnsMetadata(response):
    
    """
    Parses the response of the columns "list" API call:
    https://developers.google.com/analytics/devguides/reporting/metadata/v3/reference/metadata/columns/list
   
    Note that both METRICS and DIMENSIONS are defined as "columns".
   
    TODO: change how I deal with templated colums (custom metrics, dimensions, goals, etc.)
    
    Returns:
    Two lists of tuples (name, id) for all default Metrics and Dimensions available in Google Analytics.
    """
    
    # Initialize return variables 
    metrics = list()
    dimensions = list()
    templated_columns = list() # TODO
    
    # Parse json
    for column in response["items"]:
        
        identifier = column["id"]
        name = column["attributes"]["uiName"]
        column_type = column["attributes"]["type"]
        status = column["attributes"]["status"]
        
        templated = column["attributes"].get("minTemplateIndex", None) # TODO

        if status == "DEPRECATED":
            pass
        elif templated:
            templated_columns.append(column)
        elif column_type == "METRIC":
            metrics.append((name, identifier))
        elif column_type == "DIMENSION":
            dimensions.append((name, identifier))
        else:
            raise ValueError("The Metadata API has returned something that's not a METRIC or a DIMENSION.") 
            
    # Parse templated_columns (NOTE: the treatment of templated values will be changed in a future release of the plugin)
    for column in templated_columns:

        # Unpack column data
        identifier = column["id"]
        name = column["attributes"]["uiName"]
        column_type = column["attributes"]["type"]
        
        # Extract number of templates to produce
        min_index = int(column["attributes"]["minTemplateIndex"])
        max_index = int(column["attributes"]["maxTemplateIndex"])
        
        for i in range(min_index, max_index+1):
            # Edit the column name and identifier to replace the "XX" for the template number
            name_i = name.replace("XX", str(i))
            identifier_i = identifier.replace("XX", str(i))
            
            # Add the column to metrics or dimensions
            if column_type == "METRIC":
                metrics.append((name_i, identifier_i))
            elif column_type == "DIMENSION":
                dimensions.append((name_i, identifier_i))
            else:
                raise ValueError("The Metadata API has returned something that's not a METRIC or a DIMENSION.")
            
    return metrics, dimensions


## FUNCTIONS FOR REPORTING API ##

def reporting_query_builder(view, start_date, end_date, metrics_and_goals, dimensions, segments, next_record_index):
    
    """
    Creates the query body for the "batchGet" API call:
    https://developers.google.com/analytics/devguides/reporting/core/v4/rest/v4/reports/batchGet
    
    TODO: document format of function inputs!
    
    Returns:
    A properly formatted query body json (python dict).
    """

    # Unpack query inputs
    view_q = view[3]
    metrics_q = [{"expression" : m[1]} for m in metrics_and_goals]
    
    # Note: dimensions and segments may be empty, so require special treatment
    dimensions_q = list()
    if dimensions:
        dimensions_q = [{"name" : d[1]} for d in dimensions] 
    
    segments_q = list()
    if segments:    
        segments_q = [{"segmentId" : s[1]} for s in segments]
    
    # Build query body   
    query_body = {
        'reportRequests': [
            {
                'viewId': view_q,
                'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
                'metrics': metrics_q,
                'dimensions': dimensions_q,
                'segments' : segments_q,
                'pageToken' : next_record_index 
            }]
    }
    
    return query_body
        
def reporting_row_generator(response, metrics_and_goals, dimensions):
    
    """
    Returns a generator of rows for the reponse of the "batchGet" API call:
    https://developers.google.com/analytics/devguides/reporting/core/v4/rest/v4/reports/batchGet
    
    TODO: it would probably be better to have the metrics_and_goals and dimensions be dicts from the start, istead of a list of tuples (!)
    Note that there may be no dimensions in a response, and the dimensions input may be an empty list.
    
    Returns:
    A generator that returns rows from the query as a dictionary, indexed by column name
    """
    
    # Create dicts of {"id" : "name"} for metrics (fix this in the future, see note in function description)
    metrics_and_goals_dict = dict([(identifier, name) for name, identifier in metrics_and_goals])
    dimensions_dict = dict([(identifier, name) for name, identifier in dimensions])
    
    # Obtain identifiers of dimensions and metrics returned in response
    metric_ids = list()
    for metric in response["reports"][0]["columnHeader"]["metricHeader"]["metricHeaderEntries"]:
        metric_ids.append(metric["name"])
    
    dimension_ids = list()
    if dimensions:
        dimension_ids = response["reports"][0]["columnHeader"]["dimensions"]
        
    # Replace the identifiers of the dimensions and metrics for their names
    metric_names = [metrics_and_goals_dict[metric_id] for metric_id in metric_ids]
    dimension_names = [dimensions_dict[dim_id] for dim_id in dimension_ids]
    
    # Create geenrator of rows (check first if response is empty)
    if not response["reports"][0]["data"].get("rowCount", None): 
        yield dict([(metric, None) for metric in metric_names])
    
    else:
        for row in response["reports"][0]["data"]["rows"]:
            metrics_dict = dict(zip(metric_names, row["metrics"][0]["values"]))

            dimensions_dict = dict()
            if dimensions:
                dimensions_dict = dict(zip(dimension_names, row["dimensions"]))

            yield {**dimensions_dict, **metrics_dict}

def get_next_index(response):
    """
    Returns the "nextPageToken" of the response to the "batchGet" API call:
    https://developers.google.com/analytics/devguides/reporting/core/v4/rest/v4/reports/batchGet
    
    Returns:
    Returns the "nextPageToken" of the response; if none, returns None.
    """
    
    return response["reports"][0].get("nextPageToken", None)
    
