var app = angular.module("RepsApp", ['directives.rep']);

app.controller('RepsCtrl', ['$scope', '$http', function($scope, $http) {

  $scope.getReps = function() {

    let zipcode = $scope.zipcode;
    $scope.senators = [];
    $scope.congress = [];
    $scope.isValid;

    $http.post('/api', {"zipcode": zipcode})
      .success(function(results) {
        if (results.results) {
          $scope.senators = results.results[0];
          $scope.congress = results.results[1];
          $scope.isValid = true;
          console.log($scope.senators[0].first_name)
        } else {
          $scope.isValid = false;
        }
      })
      .error(function(error) {
        console.log(error);
      });
    };
  }
]); // SenatorsCtrl





