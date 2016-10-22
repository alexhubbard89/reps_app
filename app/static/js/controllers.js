// Senators

(function () {
  'use strict';
  angular.module('RepsApp', [])
  .controller('SenatorsController', ['$scope', '$log', '$http',
  function($scope, $log, $http) {

    $scope.getResults = function() {

      var zipcode = $scope.zipcode;
      console.log(zipcode);

      $http.post('/api', {"zipcode": zipcode}).
        success(function(results) {
          $log.log(results);
        }).
        error(function(error) {
          $log.log(error);
        });
    };
  }
])
})();