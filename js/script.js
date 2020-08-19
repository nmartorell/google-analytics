var app = angular.module('googleAnalytics.dataset', []);


app.controller('googleAnalyticsDatasetController', function($scope, DataikuAPI) {
    
    /* Helper functions to clear View Properties */
    $scope.enableViewProperties = function(){
        $scope.metricsReady=true;
        $scope.dummyMetricsReady=false; 

        $scope.dimensionsReady=true;
        $scope.dummyDimensionsReady=false;
        
        $scope.segmentsReady=true;
        $scope.dummySegmentsReady=false;
    };
    
    $scope.enableDummyViewProperties = function(){
        $scope.metricsReady=false;
        $scope.dummyMetricsReady=true; 
        
        $scope.dimensionsReady=false;
        $scope.dummyDimensionsReady=true;
        
        $scope.segmentsReady=false;
        $scope.dummySegmentsReady=true;
    };

    $scope.clearViewPropertyVars = function(){
        $scope.config.metrics_list = null;
        $scope.config.dimensions_list = null;
        $scope.config.segments_list = null;
        
        /* Assigned config variables not cleared automatically */
        $scope.config.metrics = null;
        $scope.config.dimensions = null;
        $scope.config.segments = null; 
    };
    
    $scope.clearViewProperties = function(){
        $scope.enableDummyViewProperties();
        $scope.clearViewPropertyVars();
        $scope.enableViewProperties();
    };
    

    /* Function to retrieve Account Summaries dict */
    $scope.getAccountSummaries = function(){
        
        /* Prevent from running when $scope.config.service_account is null */
        if ($scope.config.service_account == null) {
            return;
        };
        
        /* Clear View Property multiselect fields 
        $scope.clearViewProperties(); */
        
        /* Call Google Analytics API to retrieve Account Summaries */
        $scope.callPythonDo({method: "get_account_summaries"}).then(function(data){
            
            /* Update Accounts dropdown */
            $scope.config.account_summaries = data['account_summaries'];
            
            /* Clear Web Property and Views dropdowns */
            $scope.config.web_properties = null;
            $scope.config.views = null; 
        });
    };

    
    /* Function to extract the Web Properties associated to the selected Account */
    $scope.listWebProperties = function(){
        
        /* Prevent from running when $scope.config.account is null */
        if ($scope.config.account == null) {
            return;
        };
        
        /* Clear View Property multiselect fields 
        enableDummyViewProperties(); */
        
        /* Update Web Properties dropdown */
        $scope.config.web_properties = $scope.config.account.web_properties;
        
        /* Clear Views dropdown */
        $scope.config.views = null;
    };
    
    /* Function to extract the Views associated to the selected Web Property */
    $scope.listViews = function(){
        
        /* Prevent from running when $scope.config.web_property is null */
        if ($scope.config.web_property == null) {
            return;
        };
        
        /* Clear View Property multiselect fields 
        enableViewProperties(); */
        
        /* Update Views dropdown */
        $scope.config.views = $scope.config.web_property.views;
    };
    
    
    /* Function to fetch View Properties */
    $scope.getViewProperties = function(){
        /* Prevent from running when $scope.config.view is null */
        if ($scope.config.view == null) {
            return;
        };

        /* Clear View Property multiselect fields */
        $scope.enableDummyViewProperties();
        $scope.clearViewPropertyVars();
        
        /* Compute new property values */
        $scope.callPythonDo({method: "get_view_properties"}).then(function(data){
            
            $scope.config.metrics_list = data['metrics'];
            $scope.config.dimensions_list = data['dimensions'];
            $scope.config.segments_list = data['segments'];
            
            /* Refresh view properties fields */
            $scope.enableViewProperties();
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
        
        /* TODO: add validation for failure 
        DataikuAPI.plugins.listAccessiblePresets(pluginId, projectKey, parameterSetId).success(function(data){
            $scope.config.presets = data.presets.filter(p => p.usable);
        }); */
        
        /* UI features enable/disable at start */
        $scope.enableViewProperties();  
        
        console.log($scope.config.metrics)
        console.log($scope.config.metrics_lisst)
    };
        
    init();
    
});