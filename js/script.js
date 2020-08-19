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
        $scope.config.account_summaries = null;
        $scope.config.web_properties = null;
        $scope.config.views = null;
        clearViewProperties();
        
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
        clearViewProperties();
        
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
        clearViewProperties();  
        
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
        
        /* Populate the Google Service Account dropdown */
        let pluginId = "google-analytics";
        let parameterSetId = "google-service-accounts";
        
        let projectKey = ""
        $scope.callPythonDo({method: "get_project_key"}).then(function(data){
            let projectKey = data.project_key;
        });
        
        DataikuAPI.plugins.listAccessiblePresets(pluginId, projectKey, parameterSetId).success(function(data){
            
            /* Retrieve currently configured, usable Service Accounts on DSS instance */
            var presets = data.presets.filter(p => p.usable);
            
            /* If $scope.config.presets already exists, update it, else set it. 
               Note that $scope.config.presets will only exist when the dataset settings tab is opened after it is created */
            if (typeof $scope.config.presets === 'undefined') {
                $scope.config.presets = presets;
            } 
            else {
            
                /* Generate dict of previously used presets {name --> preset object} */
                var previous_presets_lookup = {};
                $scope.config.presets.forEach(function (preset, index) {
                    previous_presets_lookup[preset.name] = preset;
                });
            
                console.log("previous preset names");
                console.log(previous_presets_lookup);
                console.log(presets)
            
                /* Loop over current presets, and replace by the object in $scope.config.presets 
                   This is done to ensure the $$hashKeys match with those stored in $scope.config.service_account (for the UI) */
                presets.forEach(function (preset, index) {
                    console.log(preset);
                    if (preset.name in previous_presets_lookup) {
                        console.log("here1234");
                        presets[index] = previous_presets_lookup[preset.name]
                    }
                });
            
                $scope.config.presets = presets;
                console.log("scope presets");
                console.log($scope.config.presets);
            }
        });
    };

                                                                                                          
  
    init();    
});







