/**
 * Created with PyCharm.
 * User: redskins80
 * Date: 11/12/13
 * Time: 10:30 PM
 * To change this template use File | Settings | File Templates.
 */

var app = angular.module("SearchApp", []);

app.controller("searchCtrl", function ($scope) {

    $scope.makeCall = function(message, number, network) {
        alert(message + number + network);
    };

    return $scope;

});

app.directive("panel", function() {
    return {
        restrict:"E",
        scope: {
            callfunc: "&",
            number: "@",
            network: "="
        },
        template: '<span>Number is : {{ number }}</span>' +
            '<select ng-model="network" ng-options="net for net in networks"></select>' +
            '<input type="text" ng-model="inputTest">' +
            '<button ng-click="callfunc({message:inputTest, number:number, network:network})">Call</button>',
        link: function(scope) {
            scope.networks = ["Airtel", "Idea", "Reliance"];
            scope.network = scope.networks[0];
        }
    }
});


app.factory("xhrFactory", function($q, $http, $filter) {

    return {
        searchService: function(args) {
            var url = null;
            //if (args.label) {
            if (args.label) {
                url = "http://0.0.0.0:7475/db/data/cypher";
                data = {
//                    "query":"MATCH (r:" + $filter('capitalize')(args.label) + ")-[t]->() RETURN type(t)"
                    "query":"MATCH (r:" + $filter('capitalize')(args.label) + ")-[t]->() RETURN collect(type(t))"
                }
            } else {
                url = "http://0.0.0.0:9200/" + (args.index ? args.index:"_all") + "/static/_search";
                data = {
                    "query": {
                        "term": {
                            "name":args.inputPhrase
                        }
                    },
                    "size":"20"
                }
            }
            return $http.post(url, data)
                .then(function(result) {

                    data = {}

                    if (result.data.hasOwnProperty('hits')) {

                        for(var i=0; i<result.data.hits.hits.length; i++) {
                            data[i] = { "name":result.data.hits.hits[i]._source.name, "index":result.data.hits.hits[i]._index}
                        }
                    } else {
                        for (var i=0; i<result.data.data[0][0].length;i++) {
                            data[i] = {"name":result.data.data[0][0][i], "index":"Rel"}

                        }
                    }

                    return data;
//                    return result.data;

                })
        }
    };
})


app.controller("autoSuggest", function($scope, $filter, xhrFactory) {

    $scope.tagger = {
        'meta':{
            "q":"", //Contains raw query entered in full
            "last_token":{
                "token":null, "type":null
            }
        },
        'Restaurant':null,
        'Subzone':null,
        'Cuisine':null
    };

    $scope.sendRequest = function(inputPhrase) {

        if (inputPhrase.length <=1) {
            return;
        }

        args = {
            "inputPhrase":$filter('lowercase')(inputPhrase),
            "index":null,
            "label":null,
            "meta":$scope.tagger.meta
        }


        if ($scope.tagger.meta.last_token.type != "Rel") {
            args.label = $scope.tagger.meta.last_token.type;
        }


        xhrFactory.searchService(args)
//        xhrFactory.searchService($filter('lowercase')(inputPhrase), null)
            .then(function(data) {
                $scope.results = data;
                console.log(data);
            });

    };

    $scope.confirmTag = function(name, index) {

        index = $filter('capitalize')(index);
        $scope.tagger[index] = name;
//        $scope.model.inputPhrase += name;
        $scope.tagger.meta.q += name + " ";
        $scope.tagger.meta.last_token.token = name;
        $scope.tagger.meta.last_token.type = index;
        $scope.results = null;
        $scope.model.inputPhrase = "";
    }

    return $scope;
})


app.filter("capitalize", function () {
    return function(input) {
        return input.substring(0,1).toUpperCase() + input.substring(1);
    }

})

//
//function searchCtrl($scope) {
//    $scope.searchPhrase = "Enter a Phrase";
//
//    $scope.suggest = function(rec) {
//        alert($scope.input);
//    }
//}