// Senators

(function () {

  'use strict';

  angular.module('RepsApp', [])
  .controller('SenatorsController', ['$scope', '$log', '$http',
  function($scope, $log, $http) {

  $scope.getResults = function() {

    $log.log("hitting getResults function");

    var zip = $scope.zip;

    // fire the API request
    $http.post('/api', {"zip": zip}).
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