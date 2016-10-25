var app = angular.module("RepsApp", []);

app.controller('RepsCtrl', ['$scope', '$http', function($scope, $http) {

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
]); // SenatorsCtrl

app.controller('NavCtrl', function($scope, $location) {
  $scope.isActive = function(route) {
    return route === $location.path();
  }
});// NavCtrl

app.directive('errSrc', function() {
  return {
    link: function(scope, element, attrs) {
      element.bind('error', function() {
        if (attrs.src != attrs.errSrc) {
          attrs.$set('src', attrs.errSrc);
        }
      });
    }
  }
});

