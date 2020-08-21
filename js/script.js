var app = angular.module('googleAnalytics.dataset', []);


app.controller('googleAnalyticsDatasetController', function($scope, DataikuAPI) {   

    /* Helper function to clear View Properties */
    var clearViewProperties = function(){
        $scope.config.metrics_list = null;
        $scope.config.dimensions_list = null;
        $scope.config.segments_list = null;
    };
    
    
    /* Function to retrieve Account Summaries dict */
    $scope.getAccountSummaries = function(){
               
        /* Clear Account, Web Property, View and View Properties dropdowns */
        $scope.config.account_summaries_list = null;
        $scope.config.web_properties_list = null;
        $scope.config.views_list = null;
        clearViewProperties();
        
        /* Call Google Analytics API to retrieve Account Summaries */
        $scope.callPythonDo({method: "get_account_summaries"}).then(function(data){
            $scope.config.account_summaries_list = data['account_summaries'];
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
        clearViewProperties();
        
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
        clearViewProperties();  
        
        /* Update Views dropdown */
        $scope.config.views_list = $scope.config.web_property.views;
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
    
    
    /* Initialization --> Populate the Google Service Account dropdown 
                          There has to be a better way to do this....!!!!!!! */
    var init = function(){        
        
        /* Set and Validate Plugin and Parameter Set IDs */
        let plugin_id = "google-analytics";
        let service_account_preset_id = "google-service-account";
        
        /* Validate here */
        
        /* Project Key */
        let project_key = ""
        $scope.callPythonDo({method: "get_project_key"}).then(function(data){
            project_key = data.project_key;
        });
        
        /* Retrieve Service Account presets, and populate $scope.config.service_accounts_list */ 
        DataikuAPI.plugins.listAccessiblePresets(plugin_id, project_key, service_account_preset_id).success(function(data){
            
            /* Retrieve currently configured, usable Service Accounts on DSS instance */
            var presets = data.presets.filter(p => p.usable);
            
            /* If $scope.config.presets already exists, update it --> this will be the case when the dataset is initially created */
            if (typeof $scope.config.service_accounts_list === 'undefined') {
                $scope.config.service_accounts_list = presets;
            } 
            
            /* When navigating to a the settings of a previously created dataset, may need to update the available Service Accounts */
            else {
            
                /* Generate dict of previously used presets {name --> preset object} */
                var previous_service_accounts = {};
                $scope.config.service_accounts_list.forEach(function (service_account, index) {
                    previous_service_accounts[service_account.name] = service_account;
                });
            
                /* Loop over current presets, and replace by the object in $scope.config.presets 
                   This is done to ensure the $$hashKeys match with those stored in $scope.config.service_account */
                presets.forEach(function (service_account, index) {
                    if (service_account.name in previous_service_accounts) {
                        presets[index] = previous_service_accounts[service_account.name]
                    }
                });
                
                $scope.config.service_accounts_list = presets;
            }            
        });
    };

    init();    
});







