## FUNCTIONS FOR MANAGEMENT AND METADATA APIs ##

def parse_account_summaries(response):
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
    
    # Parse json into desired format
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


def parse_columns_metadata(response): 
    """
    Parses the response of the default Columns via the Metadata "list" API call:
    https://developers.google.com/analytics/devguides/reporting/metadata/v3/reference/metadata/columns/list
   
    Note that both METRICS and DIMENSIONS are defined as "columns".
    
    Returns:
    Two lists of dicts {name, id} for all default Metrics and Dimensions available in Google Analytics.
    """
    
    # Initialize return variables 
    metrics = list()
    dimensions = list()
    templated_columns = list()
    
    # Parse json
    for column in response["items"]:
        
        identifier = column["id"]
        name = column["attributes"]["uiName"]
        column_type = column["attributes"]["type"]
        status = column["attributes"]["status"]
        
        templated = column["attributes"].get("minTemplateIndex", None) 

        if status == "DEPRECATED":
            continue
        elif templated:
            templated_columns.append(column)
        elif column_type == "METRIC":
            metrics.append({"name":name, "id":identifier})
        elif column_type == "DIMENSION":
            dimensions.append({"name":name, "id":identifier})
        else:
            raise ValueError("The Metadata API has returned something that's not a METRIC or a DIMENSION.") 
    
    # Parse templated_columns
    
    # Note: the templated columns include custom metrics, custom dimensions, generic goal metrics, and generic dimensions.
    #       Custom metrics, custom dimensions, and goals are obtained via subsequent calls to the Management API.
    #       Generic dimensions cannot be obtained via any other Google Analytics API, so are populated here with their generic names.
    
    generic_dimensions_ids = {"ga:customVarNameXX",
                              "ga:customVarValueXX",
                              "ga:contentGroupUniqueViewsXX",
                              "ga:landingContentGroupXX",
                              "ga:previousContentGroupXX",
                              "ga:contentGroupXX",
                              "ga:productCategoryLevelXX"}
    
    for column in templated_columns:
        
        # Unpack column data
        identifier = column["id"]
        name = column["attributes"]["uiName"]
        column_type = column["attributes"]["type"]
        
        # Pass if not in generic dimensions set
        if identifier not in generic_dimensions_ids:
            continue
        
        # Extract number of templates to produce
        min_index = int(column["attributes"]["minTemplateIndex"])
        max_index = int(column["attributes"]["maxTemplateIndex"])
        
        for i in range(min_index, max_index+1):
            # Edit the column name and identifier to replace the "XX" for the template number
            name_i = name.replace("XX", str(i))
            identifier_i = identifier.replace("XX", str(i))
            
            # Add the column to metrics or dimensions
            if column_type == "METRIC":
                metrics.append({"name":name_i, "id":identifier_i})
            elif column_type == "DIMENSION":
                dimensions.append({"name":name_i, "id":identifier_i})
            else:
                raise ValueError("The Metadata API has returned something that's not a METRIC or a DIMENSION.")
    
    return metrics, dimensions


def parse_custom_metrics(response):
    """
    Parses the response of the Custom Metrics "list" API call:
    https://developers.google.com/analytics/devguides/config/mgmt/v3/mgmtReference/management/customMetrics/list
    
    Returns:
    A list of dicts {name, id} for all Custom Metrics available at the Web Property level requested.
    """
    
    # Initialize return variable
    custom_metrics = list()
    
    # Parse response
    for custom_metric in response["items"]:
        
        identifier = custom_metric["id"]
        name = custom_metric["name"]
        
        custom_metrics.append({"name":name, "id":identifier})
    
    return custom_metrics


def parse_custom_dimensions(response):
    """
    Parses the response of the Custom Dimensions "list" API call:
    https://developers.google.com/analytics/devguides/config/mgmt/v3/mgmtReference/management/customDimensions/list
    
    Returns:
    A list of dicts {name, id} for all Custom Dimensions available at the Web Property level requested.
    """
    
    # Initialize return variable
    custom_dimensions = list()
    
    # Parse response
    for custom_dimension in response["items"]:
        
        identifier = custom_dimension["id"]
        name = custom_dimension["name"]
        
        custom_dimensions.append({"name":name, "id":identifier})
    
    return custom_dimensions


def parse_goals(response):
    """
    Parses the response of the View Goals "list" API call:
    https://developers.google.com/analytics/devguides/config/mgmt/v3/mgmtReference/management/goals/list
    
    Returns:
    A list of dicts {name, id} for all Goals associated to the requested View.
    """
    
    # Parse response to extract goals
    goals = list()
    for goal in response["items"]:
        
        num = goal["id"] 
        name = goal["name"]
        
        goals.append({"name":name, "num":num})
    
    # Goals are not directly passed as metrics to the Reporting API. Instead, the associated "goal metrics"
    # need to be constructed from the goal names and numbers.
    goal_metrics_generic = [{"id":"ga:goalXXStarts", "name":"Goal XX Starts"},
                            {"id":"ga:goalXXCompletions", "name":"Goal XX Completions"},
                            {"id":"ga:goalXXValue", "name":"Goal XX Value"},
                            {"id":"ga:goalXXConversionRate", "name":"Goal XX Conversion Rate"},
                            {"id":"ga:goalXXAbandons", "name":"Goal XX Abandons"},
                            {"id":"ga:goalXXAbandonRate", "name":"Goal XX Abandons Rate"},
                            {"id":"ga:searchGoalXXConversionRate", "name":"Search Goal XX Conversion Rate"}] # extracted from Metadata API
    
    # Initialize return variable
    goal_metrics = list()
    
    # Construct the non-generic goal metrics 
    for goal in goals:
        
        # Name and number of current goal
        goal_num = goal["num"]
        goal_name = goal["name"]
        
        for generic_metric in goal_metrics_generic:
            
            # Generic name and id of current goal metric
            id_generic = generic_metric["id"]
            name_generic = generic_metric["name"]
            
            # Replace name and number of current goals into generics
            metric_id = id_generic.replace("XX", goal_num)
            metric_name = goal_name + " (" + name_generic.replace("XX", goal_num) + ")"
            
            goal_metrics.append({"id":metric_id, "name":metric_name})

    return goal_metrics


def parse_segments(response):
    """
    Parses the response of the Segments "list" API call:
    https://developers.google.com/analytics/devguides/config/mgmt/v3/mgmtReference/management/segments/list
    
    Returns:
    A list of dicts {name, id} for all Segments available to the authenticated user.
    """
    
    # Initialize return variable
    segments = list()
    
    # Parse response
    for segment in response["items"]:
        
        identifier = segment["segmentId"]
        name = segment["name"]
        
        segments.append({"name":name, "id":identifier})
        
    return segments


## FUNCTIONS FOR REPORTING API ##

def reporting_query_builder(view, start_date, end_date, metrics, dimensions, segments, next_record_index):
    """
    Creates the query body for the "batchGet" API call:
    https://developers.google.com/analytics/devguides/reporting/core/v4/rest/v4/reports/batchGet
    
    Returns:
    A properly formatted query body json (python dict).
    """

    # Unpack query inputs
    view_id = view["id"]
    metrics_ids = [{"expression" : m["id"]} for m in metrics]
    
    # Note: dimensions and segments may be empty, so require special treatment
    dimensions_ids = list()
    if dimensions:
        dimensions_ids = [{"name" : d["id"]} for d in dimensions] 
    
    segments_ids = list()
    if segments:    
        segments_ids = [{"segmentId" : s["id"]} for s in segments]
    
    # Build query body   
    query_body = {
        'reportRequests': [
            {
                'viewId': view_id,
                'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
                'metrics': metrics_ids,
                'dimensions': dimensions_ids,
                'segments' : segments_ids,
                'pageToken' : next_record_index 
            }]
    }
    
    return query_body
        
def reporting_row_generator(response, metrics, dimensions):
    """
    Returns a generator of rows for the reponse of the "batchGet" API call:
    https://developers.google.com/analytics/devguides/reporting/core/v4/rest/v4/reports/batchGet
    
    Note that there may be no dimensions in a response, and the dimensions input may be an empty list.
    
    Returns:
    A generator that returns rows from the query as a dictionary, indexed by column name
    """
    
    # Create dicts of {"id" : "name"} for metrics and dimensions 
    metrics_and_goals_dict = dict([(metric["id"], metric["name"]) for metric in metrics])
    dimensions_dict = dict([(dim["id"], dim["name"]) for dim in dimensions])
    
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
    