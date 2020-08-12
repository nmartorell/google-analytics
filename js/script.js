var app = angular.module('googleAnalytics.dataset', []);


app.controller('googleAnalyticsDatasetController', function($scope, DataikuAPI) {
    
    /* Helper functions to clear View Properties */
    var enableViewProperties = function(){
        $scope.metricsReady=true;
        $scope.dummyMetricsReady=false; 

        $scope.dimensionsReady=true;
        $scope.dummyDimensionsReady=false;
        
        $scope.segmentsReady=true;
        $scope.dummySegmentsReady=false;
    };
    
    var enableDummyViewProperties = function(){
        $scope.metricsReady=false;
        $scope.dummyMetricsReady=true; 
        
        $scope.dimensionsReady=false;
        $scope.dummyDimensionsReady=true;
        
        $scope.segmentsReady=false;
        $scope.dummySegmentsReady=true;
    };

    /* Function to Account Summaries dict */
    $scope.getAccountSummaries = function(){
        $scope.callPythonDo({method: "get_account_summaries"}).then(function(data){
            $scope.account_summaries = data['account_summaries'];  
        });
        
        /* TODO: deal with elements that need to be removed !!! */
    };
    
    /* Function to extract the Web Properties for the chosen account */
    $scope.listWebProperties() = function(){
        $scope.web_properties = $scope.config.account.web_properties;
    };
    
    /* Function to fetch Views */
    $scope.getViews = function(){
        /* Enable dummy multiselect fields */  
        enableDummyViewProperties();
        
        /* Get Views associated to Service Account */
        $scope.callPythonDo({method: "get_views"}).then(function(data){
            $scope.views = data['views'];  
            
            /* Refresh view properties fields */
            $scope.metricsList = null;
            $scope.dimensionsList = null;
            $scope.segmentsList = null;
            
            enableViewProperties();
        }); 
    };
    
    /* Function to fetch View Properties */
    $scope.getViewProperties = function(){
        /* Prevent from running when $scope.config.view is null */
        if ($scope.config.view == null) {
            return;
        };

        /* Enable dummy multiselect fields */  
        enableDummyViewProperties(); 
        
        /* Compute new property values */
        $scope.callPythonDo({method: "get_view_properties"}).then(function(data){
            
            $scope.metricsList = data['metrics_and_goals'];
            $scope.dimensionsList = data['dimensions'];
            $scope.segmentsList = data['segments'];

            $scope.config.metrics_and_goals = null;
            $scope.config.dimensions = null;
            $scope.config.segments = null;
            
            /* Refresh view properties fields */
            enableViewProperties();             
        }); 
    };
    
    /* Initialization */
    var init = function(){
        
        /* Populate the Google Service Account dropdown */
        let pluginId = "google-analytics";
        let parameterSetId = "google-service-accounts";
        
        let projectKey = ""
        $scope.callPythonDo({method: "get_project_key"}).then(function(data){
            let projectKey = data.project_key;
        });
        
        DataikuAPI.plugins.listAccessiblePresets(pluginId, projectKey, parameterSetId).success(function (data) {
            $scope.presets = data.presets.filter(p => p.usable);
        });
        
        /* UI features enable/disable at start */
        enableViewProperties();
    };
        
    init();
    
});