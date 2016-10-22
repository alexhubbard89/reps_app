(function () {
  'use strict';
  angular.module('RepsApp', [])
  .controller('SenatorsController', ['$scope', '$log', '$http',
  function($scope, $log, $http) {

    $scope.getResults = function() {

      let zipcode = $scope.zipcode;
      $scope.senators = [];

      $http.post('/api', {"zipcode": zipcode})
        .success(function(results) {
          if (results.results) {
            let reps = results.results[0];
            $scope.senators = reps;
            // for (var i = 0; i < reps.length; i++) {
            //   let firstName =  reps[i].first_name;
            //   let lastName = reps[i].last_name;
            //   let fullName = `${firstName} ${lastName}`;
            // }
          } else {
            console.log('Not a valid ZIP code')
          }
        })
        .error(function(error) {
          $log.log(error);
        });
    };
  }
])
})();