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

    var clearViewPropertyVars = function(){
        $scope.metricsList = null;
        $scope.dimensionsList = null;
        $scope.segmentsList = null;
        
        /* */
        $scope.config.metrics_and_goals = null;
        $scope.config.dimensions = null;
        $scope.config.segments = null;
    };
    
    var clearViewProperties = function(){
        enableDummyViewProperties();
        clearViewPropertyVars();
        enableDummyViewProperties()
    };
    

    /* Function to Account Summaries dict */
    $scope.getAccountSummaries = function(){
        
        clearViewProperties()
        
        /* Prevent from running when $scope.config.service_account is null */
        if ($scope.config.service_account == null) {
            return;
        };
        
        /* Call Google Analytics API to retrieve Account Summaries */
        $scope.callPythonDo({method: "get_account_summaries"}).then(function(data){
            
            /* Update Accounts dropdown */
            $scope.account_summaries = data['account_summaries'];
            
            /* Clear Web Property and Views dropdowns */
            $scope.web_properties = null;
            $scope.views = null;
            
        });
        
        /* TODO: deal with View Properties to be removed !!! */
    };

    
    /* Function to extract the Web Properties associated to the selected Account */
    $scope.listWebProperties = function(){
        
        /* Prevent from running when $scope.config.account is null */
        if ($scope.config.account == null) {
            return;
        };
        
        /* Update Web Properties dropdown */
        $scope.web_properties = $scope.config.account.web_properties;
        
        /* Clear Views dropdown */
        $scope.views = null;
        
        /* TODO: deal with View Properties to be removed !!! */
    };
    
    /* Function to extract the Views associated to the selected Web Property */
    $scope.listViews = function(){
        
        /* Prevent from running when $scope.config.web_property is null */
        if ($scope.config.web_property == null) {
            return;
        };
        
        /* Update Views dropdown */
        $scope.views = $scope.config.web_property.views;
        
        /* TODO: deal with elements that need to be removed !!! */
    };
    
    
    /* Function to fetch View Properties */
    $scope.getViewProperties = function(){
        /* Prevent from running when $scope.config.view, 
                                     $scope.config.web_property or 
                                     $scope.config.service_account are null */
        
        if (($scope.config.view == null) || ($scope.config.web_property == null) || ($scope.config.service_account == null)) {
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
        
        /* Populate the Google Service Account dropdown (TODO: add validation for failure) */
        let pluginId = "google-analytics";
        let parameterSetId = "google-service-accounts";
        
        let projectKey = ""
        $scope.callPythonDo({method: "get_project_key"}).then(function(data){
            let projectKey = data.project_key;
        });
        
        /* TODO: add validation for failure */
        DataikuAPI.plugins.listAccessiblePresets(pluginId, projectKey, parameterSetId).success(function(data){
            $scope.presets = data.presets.filter(p => p.usable);
        });
        
        /* UI features enable/disable at start */
        enableViewProperties();
    };
        
    init();
    
    
    
    
    /* Function to fetch Views (TODO: DELETE!!!) */
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
    
});