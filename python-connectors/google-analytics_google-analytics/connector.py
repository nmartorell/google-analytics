# This file is the actual code for the custom Python dataset google-analytics_google-analytics

# import the base class for the custom dataset
from six.moves import xrange
from dataiku.connector import Connector

from googleanalytics import ga_api
from googleanalytics import ga_json

from datetime import datetime
import pytz

"""
A custom Python dataset is a subclass of Connector.

The parameters it expects and some flags to control its handling by DSS are
specified in the connector.json file.

Note: the name of the class itself is not relevant.
"""
class MyConnector(Connector):

    def __init__(self, config, plugin_config):
        """
        The configuration parameters set up by the user in the settings tab of the
        dataset are passed as a json object 'config' to the constructor.
        The static configuration parameters set up by the developer in the optional
        file settings.json at the root of the plugin directory are passed as a json
        object 'plugin_config' to the constructor
        """
        Connector.__init__(self, config, plugin_config)  # pass the parameters to the base class

        # (1) Validate Service Account and get Service Object
        assert self.config.get("service_account", None), "No Google Analytics Service Account has been selected. If none are available, please contact your DSS Administrator."
        
        # API configuration
        scope = ['https://www.googleapis.com/auth/analytics.readonly']
        api_name = 'analyticsreporting'
        api_version = 'v4'
        
        # Get service object
        service_account_name = self.config["service_account"]["name"]
        self.service = ga_api.get_authenticated_google_analytics_service(api_name, api_version, scope, service_account_name) 

        # (2) Validate Query Targets
        assert self.config.get("account", None), "No Google Analytics \"Account\" has been selected; please select one." 
        assert self.config.get("web_property", None), "No Google Analytics \"Web Property\" has been selected; please select one."
        assert self.config.get("view", None), "No Google Analytics \"View\" has been selected; please select one." 
        
        # (3) Validate Query Parameters
        assert len(self.config["metrics"]) >= 1, "No Google Analytics \"Metrics and Goals\" have been selected; please select at least one."
        assert len(self.config["metrics"]) <= 10, "More than 10 Google Analytics \"Metrics and Goals\" have been selected; please select a maximum of 10."
   
        assert len(self.config["dimensions"]) <= 9, "More than 9 Google Analytics \"Dimensions\" have been selected; please select a maximum of 9."
        assert len(self.config["segments"]) <= 4, "More than 4 Google Analytics \"Segments\" have been selected; please select a maximum of 4."
    
        # (4) Validate Query Dates
        assert self.config.get("start_date", None), "No \"Start Date\" has been selected; please select one." 
        assert self.config.get("end_date", None), "No \"End Date\" has been selected; please select one."
        
        # Note: start and end times are coerced into UTC from the local system timezone by DSS.
        #       In order to retrieve the date entered by the user, the start and end dates need to be reverted to the system timezone.
        
        start_date = pytz.utc.localize(datetime.strptime(self.config.get("start_date"), "%Y-%m-%dT%H:%M:%S.%fZ")).astimezone()
        end_date = pytz.utc.localize(datetime.strptime(self.config.get("end_date"), "%Y-%m-%dT%H:%M:%S.%fZ")).astimezone()
        
        assert end_date >= start_date, "The selected \"End Date\" must be after (or equal to) \"Start Date\"."

        # Format start and end dates to string with "YYYY-MM-DD" format
        self.config["start_date"] = start_date.strftime("%Y-%m-%d")
        self.config["end_date"] = end_date.strftime("%Y-%m-%d")
        
    
    def get_read_schema(self):
        """
        Returns the schema that this connector generates when returning rows.

        The returned schema may be None if the schema is not known in advance.
        In that case, the dataset schema will be infered from the first rows.

        If you do provide a schema here, all columns defined in the schema
        will always be present in the output (with None value),
        even if you don't provide a value in generate_rows

        The schema must be a dict, with a single key: "columns", containing an array of
        {'name':name, 'type' : type}.

        Example:
            return {"columns" : [ {"name": "col1", "type" : "string"}, {"name" :"col2", "type" : "float"}]}

        Supported types are: string, int, bigint, float, double, date, boolean
        """

        # In this example, we don't specify a schema here, so DSS will infer the schema
        # from the columns actually returned by the generate_rows method
        return None

    def generate_rows(self, dataset_schema=None, dataset_partitioning=None,
                            partition_id=None, records_limit = -1):
        """
        The main reading method.

        Returns a generator over the rows of the dataset (or partition)
        Each yielded row must be a dictionary, indexed by column name.

        The dataset schema and partitioning are given for information purpose.
        """
        # Initialize starting index (must be string)
        next_record_index = "0"
        
        # Fetch all available rows, or until the records_limit
        while next_record_index:
            
            # Build query
            query_body = ga_json.reporting_query_builder(self.view,
                                                         self.start_date,
                                                         self.end_date,
                                                         self.metrics_and_goals,
                                                         self.dimensions,
                                                         self.segments,
                                                         next_record_index)
        
            # Parse response and return generator
            response = self.service.reports().batchGet(body=query_body).execute()
            yield from ga_json.reporting_row_generator(response, self.metrics_and_goals, self.dimensions)
            
            # Retrieve next record index, None is all records retrieved
            next_record_index = ga_json.get_next_index(response)
            
            # Stop fetching records if records_limit is reached
            if next_record_index and (records_limit > 0) and (int(next_record_index) > records_limit):
                break


    def get_writer(self, dataset_schema=None, dataset_partitioning=None,
                         partition_id=None):
        """
        Returns a writer object to write in the dataset (or in a partition).

        The dataset_schema given here will match the the rows given to the writer below.

        Note: the writer is responsible for clearing the partition, if relevant.
        """
        raise Exception("Unimplemented")


    def get_partitioning(self):
        """
        Return the partitioning schema that the connector defines.
        """
        raise Exception("Unimplemented")


    def list_partitions(self, partitioning):
        """Return the list of partitions for the partitioning scheme
        passed as parameter"""
        return []


    def partition_exists(self, partitioning, partition_id):
        """Return whether the partition passed as parameter exists

        Implementation is only required if the corresponding flag is set to True
        in the connector definition
        """
        raise Exception("unimplemented")


    def get_records_count(self, partitioning=None, partition_id=None):
        """
        Returns the count of records for the dataset (or a partition).

        Implementation is only required if the corresponding flag is set to True
        in the connector definition
        """
        raise Exception("unimplemented")


class CustomDatasetWriter(object):
    def __init__(self):
        pass

    def write_row(self, row):
        """
        Row is a tuple with N + 1 elements matching the schema passed to get_writer.
        The last element is a dict of columns not found in the schema
        """
        raise Exception("unimplemented")

    def close(self):
        pass
