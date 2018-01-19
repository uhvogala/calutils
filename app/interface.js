
var calendarApp = angular.module('calendarApp', ["ngMaterial", "ngRoute"]);

calendarApp.config(['$interpolateProvider', function($interpolateProvider) {
	$interpolateProvider.startSymbol('[[');
	$interpolateProvider.endSymbol(']]');
}]);

calendarApp.config(function($routeProvider, $locationProvider) {
	$routeProvider
	
		.when('/calapp',{
			templateUrl : 'calapp/pages/load.html',
			controller: 'loadController'
		})
		.when('/calapp/edit',{
			templateUrl : 'calapp/pages/calapp.html',
			controller: 'calController'
		});
	$locationProvider.html5Mode(true);
});

// create the controller and inject Angular's $scope
calendarApp.controller('mainController', function($scope, $rootScope, $location) {
	
    $scope.$watch('currentController', function(newValue, oldValue) {
    	if (newValue === 'loadController'){
    		$scope.page_class = 'status-load';
    	}
    	else if (newValue === 'calController'){
    		$scope.page_class = 'status-edit';
    	}
    	console.log($scope.currentController);
    });
    
    $scope.$watch('fileAccepted', function(newValue, oldValue) {
    	console.log(newValue);
    	if (newValue === true){
    		setTimeout(function() {
    			console.log("change page");
    			$location.path("/calapp/edit");
    		}, 500);
    	}
    });
    
});

calendarApp.controller('loadController', function($scope, $route, $rootScope) {
	$rootScope.currentController = $route.current.controller;
	$rootScope.progress = 20;
	$scope.isDragged = false;
	$scope.fileAccepted = false;

	$rootScope.drop_handler = function(event){
		event.preventDefault();
		console.log(event);
		if ($(event.target).hasClass("drop-area")){
			var dt = event.dataTransfer;
			for (var i=0; i < dt.items.length; i++){
				var item = dt.items[i];
				if (item.kind === "file" && item.type === "text/calendar"){
					$rootScope.calfile = item.getAsFile();
					$scope.isDragged = false;
					$scope.fileAccepted = true;
					$rootScope.$apply();
				}
			}			
		}
	}
	
	$rootScope.dragover_handler = function(event){
		event.preventDefault();
		if (event.target.id === 'drop-box'){
			$scope.isDragged = true;
			$scope.$apply();			
		}
	}
	
	$rootScope.dragleave_handler = function(event){
		event.preventDefault();
		if (event.relatedTarget.id === 'load-container'){
			$scope.isDragged = false;
			$scope.$apply();			
		}
	}
	
	$rootScope.file_handler = function(files){
		for (var i = 0; i < files.length; i++){
			var item = files[i];
			if (item.type === "text/calendar"){
				$rootScope.calfile = item;
				$scope.fileAccepted = true;
				$rootScope.$apply();
			}
		}
	}
	
});

calendarApp.controller('calController', function($scope, $route, $rootScope) {
	$rootScope.currentController = $route.current.controller;
	$rootScope.progress = 80;
});

function ng_scope() {
	return scope = angular.element($('#page-container')).injector().get("$rootScope");
}

function dragover_handler(event){
	event.preventDefault();
}

