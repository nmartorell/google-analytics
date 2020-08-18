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
        
        /* Assigned config variables not cleared automatically */
        $scope.config.metrics_and_goals = null;
        $scope.config.dimensions = null;
        $scope.config.segments = null;
    };
    
    var clearViewProperties = function(){
        enableDummyViewProperties();
        clearViewPropertyVars();
        enableDummyViewProperties();
    };
    

    /* Function to retrieve Account Summaries dict */
    $scope.getAccountSummaries = function(){
        
        /* Prevent from running when $scope.config.service_account is null */
        if ($scope.config.service_account == null) {
            return;
        };
        
        /* Clear View Property multiselect fields */
        clearViewProperties();
        
        /* Call Google Analytics API to retrieve Account Summaries */
        $scope.callPythonDo({method: "get_account_summaries"}).then(function(data){
            
            /* Update Accounts dropdown */
            $scope.account_summaries = data['account_summaries'];
            
            /* Clear Web Property and Views dropdowns */
            $scope.web_properties = null;
            $scope.views = null;
            
        });
    };

    
    /* Function to extract the Web Properties associated to the selected Account */
    $scope.listWebProperties = function(){
        
        /* Prevent from running when $scope.config.account is null */
        if ($scope.config.account == null) {
            return;
        };
        
        /* Clear View Property multiselect fields */
        clearViewProperties();
        
        /* Update Web Properties dropdown */
        $scope.web_properties = $scope.config.account.web_properties;
        
        /* Clear Views dropdown */
        $scope.views = null;
    };
    
    /* Function to extract the Views associated to the selected Web Property */
    $scope.listViews = function(){
        
        /* Prevent from running when $scope.config.web_property is null */
        if ($scope.config.web_property == null) {
            return;
        };
        
        /* Clear View Property multiselect fields */
        clearViewProperties();
        
        /* Update Views dropdown */
        $scope.views = $scope.config.web_property.views;
    };
    
    
    /* Function to fetch View Properties */
    $scope.getViewProperties = function(){
        /* Prevent from running when $scope.config.view is null */
        if ($scope.config.view == null) {
            return;
        };

        /* Clear View Property multiselect fields */  
        clearViewProperties();
        
        /* Compute new property values */
        $scope.callPythonDo({method: "get_view_properties"}).then(function(data){
            
            $scope.metricsList = data['metrics'];
            $scope.dimensionsList = data['dimensions'];
            $scope.segmentsList = data['segments'];
            
            /* Refresh view properties fields */
            enableDummyViewProperties(); 
            enableViewProperties();             
        }); 
    };
    
    /* Initialization */
    var init = function(){
        
        
        
        
        
        $scope.getViewProperties(); 
        $scope.listViews();
        $scope.listWebProperties();
        $scope.getAccountSummaries();
        
        
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
        
        /* Call functions to populate UI in case it ... */
       
        console.log($scope.config.service_account);
        console.log($scope.config.account);
        console.log($scope.config.web_property);
        console.log($scope.config.view);
        console.log($scope.config.metrics);
        console.log($scope.config.dimensions);
        console.log($scope.config.segments);
        
        
        
        console.log($scope.config.service_account);
        console.log($scope.config.account);
        console.log($scope.config.web_property);
        console.log($scope.config.view);
        console.log($scope.config.metrics);
        console.log($scope.config.dimensions);
        console.log($scope.config.segments);
    };
        
    init();
    
});