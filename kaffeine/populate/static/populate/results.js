/**
 * Created by redskins80 on 22/2/14.
 */

var app = angular.module("SearchResults", []);

app.factory("xhrFactory", function($q, $http) {
    return {
        ajax_results:function(id) {
            return $http.get('/ajax_results/', {
                params:{id:id}
            });
        }
    }
});


app.controller("resultCtrl", function($scope, $timeout, xhrFactory) {
    $scope.test = "Results go here";

    $scope.init = function(id) {
        xhrFactory.ajax_results(id)
            .then(function(results) {
                console.log(results);
                if(!results.data.ready) {
                    console.log("trying again");
                    $timeout(function(){
                        $scope.init(id)
                    },2000);
                } else {
                    //perform result parting here
                    console.log("performing result parsing.. SUCESS");
                }
                //parse the result
                //update scope var using returned data

            });
    }
});

