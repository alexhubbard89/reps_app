var app = angular.module("RepsApp", []);

app.controller('RepsCtrl', ['$scope', '$http', function($scope, $http) {

  $scope.getReps = function() {

    let zipcode = $scope.zipcode;
    $scope.senators = [];
    $scope.congress = [];
    $scope.isValid;

    $http.post('/api', {"zipcode": zipcode})
      .success(function(results) {
        if (results.results) {
          let senators = results.results[0];
          let congress = results.results[1];
          $scope.senators = senators;
          $scope.congress = congress;
          $scope.isValid = true;
          console.log(results)
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



