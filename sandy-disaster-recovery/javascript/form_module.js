// function SimpleController($scope) {
//   $scope.names = [
//     { name: "John Smith", city: "Phoenix"},
//     { name: "John Doe", city: "New York"},
//     { name: "Jane Doe", city: "San Francisco"}
//   ];
// }
// formBuilderApp.controller('SimpleController', SimpleController);



var formBuilderApp = angular.module('formBuilderApp', [], function ($interpolateProvider) {
    $interpolateProvider.startSymbol('<[');
    $interpolateProvider.endSymbol(']>');
}); 




formBuilderApp.factory('incidentsFactory', function($http) {
  return {
      getIncidentsAsync: function(callback) {
          $http.get('/incident_definition_ajax').success(callback);
      }
  };
});


formBuilderApp.controller('incidentsController', function($scope, incidentsFactory) {
  incidentsFactory.getIncidentsAsync(function(results) {
      $scope.incidents = results;
  });
  
});



