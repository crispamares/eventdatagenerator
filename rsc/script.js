var myApp = angular.module('myApp',['ui.directives']);

function EventForm($scope, $http, $location) {
    var eventsDef = [{'type':'Stroke', 'class':"Point", 'prop': 1},
		     {'type':'Admitted', 'class':"Point", 'prop': 1},
		     {'type':'Diagnosed', 'class':"Point", 'prop': 1},
		     {'type':'Drug A', 'class':"Interval", 'prop': 1},
		     {'type':'Drug B', 'class':"Interval", 'prop': 1}
		    ];
    
    var serverClasses = {
	Point: "Milestone",
	Interval: "Interval"
    };

    var allParams = {
	numberOfRecords:{
	    label: "Number Of Records",
	    required: true,
	    min: 1,
	    step: 1,
	    type: "number",
	    placeholder: "Integer",
	    help: "Introduce in this field the number of records (e.g. number of patients) that you want to generate",
	    value: 5
	    },
	numberOfNodes:{
	    label: "Nodes per Record",
	    required: true,
	    min: 1,
	    step: 1,
	    type: "number",
	    help: "Introduce in this field the number of nodes per record that you want to generate. "
		  + "Remember that one point event is represented internally with one node and an interval event as two nodes.",
	    placeholder: "Integer",
	    value: null
	    },
	numberOfEvents:{
	    label: "Events per Record",
	    required: true,
	    min: 1,
	    step: 1,
	    type: "number",
	    help: "Introduce in this field the number of records (e.g. number of patients) that you want to generate.",
	    placeholder: "Integer",
	    value: 5
	    },
	copies:{
	    label: "Number Of Copies",
	    required: false,
	    min: 1,
	    step: 1,
	    type: "number",
	    help: "This contol allows you to create a particular number of copies of the generated records. You can think of it as just an easy way of creating large dataset with repeated patterns.",
	    placeholder: "Integer",
	    value: null
	    },
	stddev:{
	    label: "Dates Jitter",
	    required: false,
	    min: 0,
	    step: "any",
	    type: "number",
	    placeholder: "Decimal",
	    value: 0.0
	    },
	numberOfYears:{
	    label: "Number of Years",
	    required: true,
	    min: 1,
	    step: 1,
	    type: "number",
	    placeholder: "Integer",
	    value: 2
	    }
	};

    var params = ["numberOfRecords", "numberOfEvents", "copies"];
    var tempParams = ["numberOfYears", "stddev"];
    var useNodesCount = false;   // true: Use number of Nodes
    var nodesCountHelp = "Use this control if you want to toggle between counting events or counting nodes per record. "
			 + "Usually you will want to generate datasets based on the events per record.";
    var eventCategoriesHelp = "<dl><dt>Event Type</dt><dd>Could be point event or interval event</dd>"
			      + "<dt>Category's name</dt><dd>Don't use the same name in two categories</dd>"
			      + "<dt>Proportion</dt><dd>The frequency of occurrences is directly correlated with this number</dd>"
			      + "</dl>";

    var prepareArgs = function() {
	var getParams = {};
	angular.forEach(params.concat(tempParams), function(param) {getParams[param] = allParams[param].value;});
	var events = [];
	angular.forEach($scope.events, function(event) {
			    var e = {};
			    e['type'] = event['type'];
			    e['class'] = serverClasses[event['class']];
			    e['prop'] = event['prop'];
			    events.push(e);
			});
	getParams.events = JSON.stringify(events);
	return getParams;
    };
    
    $scope.allParams = allParams;
    $scope.params = params;
    $scope.tempParams = tempParams;
    $scope.useNodesCount = useNodesCount;
    $scope.nodesCountHelp = nodesCountHelp;
    $scope.eventCategoriesHelp = eventCategoriesHelp;
    $scope.eventsDef = eventsDef;
    
    $scope.changeUseNodesCount = function() {
	useNodesCount = ! useNodesCount;
	params[1] = (useNodesCount) ? "numberOfNodes" : "numberOfEvents";	    
    };

    $scope.state = /^\w\w$/;
    $scope.zip = /^\d\d\d\d\d$/;

    $scope.cancel = function() {
	$scope.events = angular.copy(eventsDef);
    };

    $scope.save = function() {
	master = $scope.events;
	$scope.cancel();
    };

    $scope.addEvent = function() {
	$scope.events.push({'type':'', 'class':"Point"});
    };

    $scope.removeEvent = function(event) {
	var events = $scope.events;
	for (var i = 0, ii = events.length; i < ii; i++) {
	    if (event === events[i]) {
		events.splice(i, 1);
	    }
	}
    };

    $scope.download = function() {
	getParams = prepareArgs();
	window.open($location.absUrl() + 'download?' + $.param(getParams));	    
    };

    $scope.preview = function() {
	if (!  $scope.myForm.$invalid ) {
	    getParams = prepareArgs();
	    $http.get($location.absUrl() + 'download?' + $.param(getParams)).success( function(data) {
			  $scope.result = data;
		      });	    
	}
    };

    $scope.isCancelDisabled = function() {
	return angular.equals(master, $scope.form);
    };

    $scope.isSaveDisabled = function() {
	return $scope.myForm.$invalid || angular.equals(master, $scope.form);
    };



    $scope.cancel();
}

EventForm.$inject = ['$scope','$http', '$location'];