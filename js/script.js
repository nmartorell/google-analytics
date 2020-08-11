var app = angular.module('googleAnalytics.dataset', []);


app.controller('googleAnalyticsDatasetController', function($scope, DataikuAPI) {
    
    /*
    $scope.getColumns = function(){
       
        $scope.callPythonDo({method:"get_columns"}).then(function(data){
            console.log(data);
            var columns=data['columns'];
            
            $scope.showColumnList = true;
            $scope.colList = columns;
            $scope.colsReady = true;
            $scope.showTableList=false;
        })
    };
    
    $scope.getTables = function(){
        $scope.callPythonDo({method: "get_tables"}).then(function(data){
        $scope.tableOptions = data['tables']
        }); 
        
        $scope.showTableList=true;
        $scope.showDbList=false;

    };
    */
    
    $scope.getViews = function(){
        $scope.callPythonDo({method: "get_views"}).then(function(data){
        $scope.views = data['views']
        }); 
        
        $scope.disableListPropertiesButton=false;
    };
    
    $scope.getViewProperties = function(){
        /* Start by refreshing all property fields */        
        $scope.metricsReady=false;
        $scope.dummyMetricsReady=true; 
        
        $scope.dimensionsReady=false;
        $scope.dummyDimensionsReady=true;
        
        $scope.segmentsReady=false;
        $scope.dummySegmentsReady=true;
        
        /* Compute new property values */
        $scope.callPythonDo({method: "get_metrics_and_goals"}).then(function(data){
        $scope.metricsList = data['metrics_and_goals'];
        
        $scope.metricsReady=true;
        $scope.dummyMetricsReady=false; 
        }); 
        
        /* Compute new property values */
        $scope.callPythonDo({method: "get_dimensions"}).then(function(data){
        $scope.metricsList = data['dimensions'];
        
        $scope.metricsReady=true;
        $scope.dummyMetricsReady=false; 
        }); 
        

        /* TODO: add python calls for segments and dimensions */
    };
    
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
        
        /* UI features to be disabled at start */
        $scope.disableListPropertiesButton=true;

        $scope.metricsReady=false;
        $scope.dummyMetricsReady=true; 
        
        $scope.dimensionsReady=false;
        $scope.dummyDimensionsReady=true;
        
        $scope.segmentsReady=false;
        $scope.dummySegmentsReady=true;
        
        /* TODO: remove
        $scope.colsReady = false;
        $scope.showTableList = false; 
        $scope.showDbList=true;
        $scope.config.url = window.location.href;
        */
    };
        
    init();
    
});