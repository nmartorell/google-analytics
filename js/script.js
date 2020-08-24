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
        $scope.config.account_summaries_list = null;
        $scope.config.web_properties_list = null;
        $scope.config.views_list = null;
        $scope.clearViewProperties();
    };
    
    
    /* Function to retrieve Account Summaries dict */
    $scope.getAccountSummaries = function(){
        
        /* Prevent from running before a service account has been selected */
        if ($scope.config.service_account == null) {
            return;
        }; 
        
        /* Clear Account, Web Property, View and View Properties dropdowns */
        $scope.clearAll()
        
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
    
    
    /* Initialization --> Populate the Google Service Account dropdown 
                          There has to be a better way to do this....! */
    var init = function(){
        
        /* Set Plugin and Parameter Set IDs */
        $scope.config.plugin_id = "google-analytics";
        $scope.config.service_account_preset_id = "google-service-accounts";
        $scope.callPythonDo({method: "validate_plugin_and_preset_ids"})
        
        /* Project Key */
        $scope.callPythonDo({method: "get_project_key"}).then(function(data){
            $scope.config.project_key = data.project_key;
        });
        
        /* Retrieve Service Account presets, and populate $scope.config.service_accounts_list */ 
        DataikuAPI.plugins.listAccessiblePresets($scope.config.plugin_id, $scope.config.project_key, $scope.config.service_account_preset_id).success(function(data){
            
            /* Retrieve currently configured, usable Service Accounts on DSS instance */
            var presets = data.presets.filter(p => p.usable);
            
            /* If service_accounts_list already exists, replace "preset" entries with objects with same name  */
            if (typeof $scope.config.service_accounts_list != 'undefined') {
                        
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
            }      
            
            /* Set / Update Service Accounts List */
            $scope.config.service_accounts_list = presets;
        });
    };

    init();    
});







