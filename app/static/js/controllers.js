(function () {
  'use strict';

  angular.module('RepsApp', [])

  .controller('RepsCtrl', ['$scope', '$http', function($scope, $http) {

    $scope.getReps = function() {

      let zipcode = $scope.zipcode;
      $scope.senators = [];
      $scope.congress = [];

      $http.post('/api', {"zipcode": zipcode})
        .success(function(results) {
          if (results.results) {
            let senators = results.results[0];
            let congress = results.results[1];
            $scope.senators = senators;
            $scope.congress = congress;
          } else {
            console.log('Not a valid ZIP code')
          }
        })
        .error(function(error) {
          console.log(error);
        });
      };
    }
  ]) // SenatorsCtrl

  .controller('NavCtrl', function($scope, $location) {
    $scope.isActive = function(route) {
      return route === $location.path();
    };
  }); // NavCtrl


})();