var reps = angular.module('directives.rep', []);
reps.directive('rep', function () {
    return{
        retrict: 'E',
        scope: {object: '='},
        templateUrl: "templates/partials/rep.html"
    };
});