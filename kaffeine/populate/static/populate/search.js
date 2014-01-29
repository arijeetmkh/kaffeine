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
            if (args.label) {
                url = "http://0.0.0.0:7475/db/data/cypher";
                data = {
//                    "query":"MATCH (r:" + $filter('capitalize')(args.label) + ")-[t]->() RETURN collect(type(t))"
                    "query":"MATCH (:" + $filter('capitalize')(args.label) + ")-[t]->() RETURN labels(startnode(t)), type(t), labels(endnode(t))"
                }
            } else {
//                TEMPORARY CODE
//                REMOVE THIS WHEN dishes are implemented
//                Currently dishes messes up the elastic query by trying to look for dishes index
//                This block removes dishes from args.index
                if (args.index) {
                    var temp = args.index.split(',');
                    var index = temp.indexOf("dish");
                    if (index > -1) {
                        temp.splice(index);
                    }
                    args.index = temp.join();
                }

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

                            if (data.hasOwnProperty(result.data.hits.hits[i]._source.name)) {
                                data[result.data.hits.hits[i]._source.name]['index'] = result.data.hits.hits[i]._index;
                            } else {
                                data[result.data.hits.hits[i]._source.name] = {
                                    "index":result.data.hits.hits[i]._index
                                }
                            }
//                            data[i] = {
//                                "name":result.data.hits.hits[i]._source.name,
//                                "index":result.data.hits.hits[i]._index
//                            }
                        }
                    } else {

                        for (var i=0; i<result.data.data.length;i++) {

                            if (data.hasOwnProperty(result.data.data[i][1])) {
                                data[result.data.data[i][1]]['end_nodes'] = (data[result.data.data[i][1]]['end_nodes'] || []).concat([result.data.data[i][2][0]]);
                                data[result.data.data[i][1]]['index'] = "Rel";
                            } else {
                                data[result.data.data[i][1]] = {
                                    'end_nodes':[result.data.data[i][2][0]],
                                    'index':"Rel"
                                }
                            }
//                            data[i] = {
//                                "name":result.data.data[i][1],
//                                "index":"Rel",
//                                "endnode":result.data.data[i][2][0]
//
//                            }
                        }
                    }
                    return data;

                })
        }

    };
})


app.controller("autoSuggest", function($scope, $filter, xhrFactory) {

    $scope.tagger = {
        'meta':{
            "q":"", //Contains raw query entered in full
            "last_token":{
                "token":null, "type":null, "next_node":null
            }
        },
        'Restaurant':[],
        'Subzone':[],
        'Cuisine':[],
        'Feature':[],
        'Dish':[]
    };

    $scope.sendRequest = function(inputPhrase) {

        if (!inputPhrase || inputPhrase.length <=1 ||  ($scope.tagger.meta.last_token.type && $scope.tagger.meta.last_token.type != "Rel")) {
            return;
        }

        //Enter this point only if not rel type

        var args = {
            "inputPhrase":$filter('lowercase')(inputPhrase),
            "index":($scope.tagger.meta.last_token.next_node ? $scope.tagger.meta.last_token.next_node : null), //Which elastic index to query
            "label":null, //Confirms ajax request only to Elastic
            "meta":$scope.tagger.meta
        };

        xhrFactory.searchService(args)
            .then(function(data) {
                $scope.results = data;
            });

    };

    $scope.confirmTag = function(name, index, endnode) {

        index = $filter('capitalize')(index);
        index != 'Rel' ? $scope.tagger[index].push(name):$scope.tagger.meta.last_token[index] = name;
        $scope.tagger.meta.q += name + " ";
        $scope.tagger.meta.last_token.token = name;
        $scope.tagger.meta.last_token.type = index;
        $scope.results = null;
        $scope.model.inputPhrase = "";

        if (index != "Rel") {
            xhrFactory.searchService({"label":index})
                .then(function(data) {
                    $scope.results = data;
                })
        } else {
            $scope.tagger.meta.last_token.next_node = endnode.join(",").toLowerCase();
        }
    };

    return $scope;
});


app.filter("capitalize", function () {
    return function(input) {
        return input.substring(0,1).toUpperCase() + input.substring(1);
    }

});

//
//function searchCtrl($scope) {
//    $scope.searchPhrase = "Enter a Phrase";
//
//    $scope.suggest = function(rec) {
//        alert($scope.input);
//    }
//}