/**
 * Created by root on 08/04/14.
 */

var myApp = angular.module('communityApp', []);
myApp.controller('communityCtrl', ['$scope', '$http', 'communityScope', function ($scope, $http, businessScope) {
    $scope.getItems = function(){
        businessScope.getAllItems().then(function(data){
            $scope.communities = data;
        }, function(errorMessage){
            $scope.error = errorMessage;
        });
    };
    $scope.getItems();
}]);
myApp.factory('communityScope', function($http, $q){
    return {
        apiPath: '/communities/get-community-map/',
        getAllItems: function () {
            //Creating a deferred object
            var deferred = $q.defer();

            //Calling Web API to fetch shopping cart items
            $http.get(this.apiPath).success(function (data) {
                //Passing data to deferred's resolve function on successful completion
                deferred.resolve(data);
            }).error(function () {

                //Sending a friendly error message in case of failure
                deferred.reject("An error occured while fetching items");
            });

            //Returning the promise object
            return deferred.promise;
        }
    }
});