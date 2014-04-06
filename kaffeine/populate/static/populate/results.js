/**
 * Created by redskins80 on 22/2/14.
 */

var app = angular.module("SearchResults", []);

app.factory("xhrFactory", function($q, $http) {
    return {
        ajax_results:function(id) {
            return $http.get('/ajax_results/1/', {
                params:{id:id}
            });
        }
    };
});


app.controller("resultCtrl", function($scope, $timeout,$http, xhrFactory) {

    $scope.init = function(id) {
        xhrFactory.ajax_results(id)
            .then(function(results) {
                console.log(results);
                if(!results.data.ready) {
                    console.log("trying again");
                    $timeout(function(){
                        $scope.init(id)
                    },2000);
                } else if(results.data.status == "SUCCESS") {
                    //perform result parsing here
                    console.log(results.data.data.data);
                    $scope.data = results.data.data.data;

                } else {
                    //remaining cases to check
                    //fail cases
                    //ToDo Check and deal with failed cases
                }
                //parse the result
                //update scope var using returned data

            });
    };
});

