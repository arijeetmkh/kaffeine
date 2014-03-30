var app = angular.module("RestaurantDetails", []);


app.factory("xhrFactory", function($q, $http) {
    return {
        ajax_results:function(id, uid, disconnect) {
//            return $http.post('/user_recommend/', { 'id':id}, {
//                headers:{
//                    'Content-Type': 'application/x-www-form-urlencoded'
//                }
//            });

            return $http({
                method  : 'POST',
                url     : disconnect == 'true' ? '/user_dislike/' : '/user_like/',
                data  : {'id':id},
                headers : { 'Content-Type': 'application/x-www-form-urlencoded' }  // set the headers so angular passing info as form data (not request payload)
            });
        }
    };
});

app.controller("DetailCtrl", function($scope, xhrFactory) {
    $scope.like = function(id, uid, disconnect) {
        xhrFactory.ajax_results(id, uid, disconnect)
            .success(function(response) {
                //Do something here on success
            });
    };
});