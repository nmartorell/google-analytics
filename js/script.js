var app = angular.module('googleAnalytics.dataset', []);


app.controller('googleAnalyticsDatasetController', function($scope, DataikuAPI) {   

    /* Function to retrieve Account Summaries dict ADD BUTTON! */
    $scope.getAccountSummaries = function(){
               
        /* Clear Web Property, View and View Properties dropdowns */
        $scope.config.web_properties = null;
        $scope.config.views = null;
        
        $scope.config.metrics_list = null;
        $scope.config.dimensions_list = null;
        $scope.config.segments_list = null;
        
        /* Call Google Analytics API to retrieve Account Summaries */
        $scope.callPythonDo({method: "get_account_summaries"}).then(function(data){
            $scope.config.account_summaries = data['account_summaries'];
        });
    };

    
    /* Function to extract the Web Properties associated to the selected Account */
    $scope.listWebProperties = function(){
        
        /* Prevent from running when $scope.config.account is null */
        if ($scope.config.account == null) {
            return;
        };
        
        /* Clear View and View Properties dropdowns */
        $scope.config.views = null;
        
        $scope.config.metrics_list = null;
        $scope.config.dimensions_list = null;
        $scope.config.segments_list = null;
        
        /* Update Web Properties dropdown */
        $scope.config.web_properties = $scope.config.account.web_properties;
    };
    
    /* Function to extract the Views associated to the selected Web Property */
    $scope.listViews = function(){
        
        /* Prevent from running when $scope.config.web_property is null */
        if ($scope.config.web_property == null) {
            return;
        };
        
        /* Clear View Properties dropdowns */
        $scope.config.metrics_list = null;
        $scope.config.dimensions_list = null;
        $scope.config.segments_list = null;  
        
        /* Update Views dropdown */
        $scope.config.views = $scope.config.web_property.views;
    };
    
    
    /* Function to fetch View Properties */
    $scope.getViewProperties = function(){
        
        /* Prevent from running when $scope.config.view is null */
        if ($scope.config.view == null) {
            return;
        };
        
        /* Compute new View Property values */
        $scope.callPythonDo({method: "get_view_properties"}).then(function(data){
            $scope.config.metrics_list = data['metrics'];
            $scope.config.dimensions_list = data['dimensions'];
            $scope.config.segments_list = data['segments'];
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
            $scope.config.presets = data.presets.filter(p => p.usable);
        }); 
        
        /* UI features enable/disable at start */
        $scope.enableViewProperties();  
    };
        
    init();
    
});