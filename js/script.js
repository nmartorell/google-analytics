var app = angular.module('googleAnalytics.dataset', []);


app.controller('googleAnalyticsDatasetController', function($scope, DataikuAPI) {   

    /* Function to clear View Properties */
    $scope.clearViewProperties = function(){
        $scope.config.metrics_list = null;
        $scope.config.dimensions_list = null;
        $scope.config.segments_list = null;
    };
    
    
    /* Function to clear View Properties and Query Targets */
    $scope.clearAll = function() {
        $scope.config.service_account_credentials = null;
        $scope.config.account_summaries_list = null;
        $scope.config.web_properties_list = null;
        $scope.config.views_list = null;
        $scope.clearViewProperties();
    };
    
    
    /* Function to retrieve Service Account Credentials and Account Summaries dict */
    $scope.getCredentialsAndAccountSummaries = function(){
        
        /* Clear Account, Web Property, View and View Properties dropdowns */
        $scope.clearAll()
        
        /* Retrieve Service Account Credentials */
        $scope.callPythonDo({method: "get_service_account_credentials"}).then(function(data){
            $scope.config.service_account_credentials = data['service_account_credentials'];
            
            /* Call Google Analytics API to retrieve Account Summaries */
            $scope.callPythonDo({method: "get_account_summaries"}).then(function(data){
                $scope.config.account_summaries_list = data['account_summaries'];
            });
        });
    };
    
    
    /* Function to extract the Web Properties associated to the selected Account */
    $scope.listWebProperties = function(){
        
        /* Prevent from running when $scope.config.account is null */
        if ($scope.config.account == null) {
            return;
        };
        
        /* Clear Web Property, View and View Properties dropdowns */
        $scope.config.web_properties_list = null;
        $scope.config.views_list = null;
        $scope.clearViewProperties();
        
        /* Update Web Properties dropdown */
        $scope.config.web_properties_list = $scope.config.account.web_properties;
    };
    
    
    /* Function to extract the Views associated to the selected Web Property */
    $scope.listViews = function(){
        
        /* Prevent from running when $scope.config.web_property is null */
        if ($scope.config.web_property == null) {
            return;
        };
        
        /* Clear View and View Properties dropdowns */
        $scope.config.views_list = null;
        $scope.clearViewProperties();  
        
        /* Update Views dropdown */
        $scope.config.views_list = $scope.config.web_property.views;
    };
    
    
    /* Function to fetch View Properties */
    $scope.getViewProperties = function(){
        
        /* Prevent from running when $scope.config.view is null */
        if ($scope.config.view == null) {
            return;
        };
        
        /* Clear View Properties dropdowns */
        $scope.clearViewProperties(); 
        
        /* Compute new View Property values */
        $scope.callPythonDo({method: "get_view_properties"}).then(function(data){
            $scope.config.metrics_list = data['metrics'];
            $scope.config.dimensions_list = data['dimensions'];
            $scope.config.segments_list = data['segments'];
        }); 
    };
    
    
    /* Initialization */
    var init = function(){  
        
        /* Generate list of Available User Secrets */
        $scope.callPythonDo({method: "get_user_secrets_list"}).then(function(data){
            $scope.config.user_secrets_list = data['user_secrets_list'];
        });
        
    };

    init();    
});

