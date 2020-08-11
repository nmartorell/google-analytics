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
        $scope.$broadcast('clearMultiSelect');
        $scope.metricsList = [{"value":"hello222", "label":"hello222"}, {"value":"goodbye333", "label":"goodbye333"}];
    };
    
    var init = function(){
        
        /* Populate the Google Service Account dropdown */
        let pluginId = "novartis-google-analytics";
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
        
        $scope.metricsList = [{"value":"hello", "label":"hello"}, {"value":"goodbye", "label":"goodbye"}, {"value":"asdf", "label":"asdf"}];
        
        /* TODO: remove
        $scope.colsReady = false;
        $scope.showTableList = false; 
        $scope.showDbList=true;
        $scope.config.url = window.location.href;
        */
    };
        
    init();
    
});