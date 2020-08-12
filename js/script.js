var app = angular.module('googleAnalytics.dataset', []);


app.controller('googleAnalyticsDatasetController', function($scope, DataikuAPI) {
    
    /* Helper function to clear View Properties */
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