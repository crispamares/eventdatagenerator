function EventForm($scope, $http, $location) {
    var eventsDef = [{'type':'Stroke', 'class':"Point"},
		     {'type':'Admitted', 'class':"Point"},
		     {'type':'Diagnosed', 'class':"Point"},
		     {'type':'Drug A', 'class':"Interval"},
		     {'type':'Drug B', 'class':"Interval"}
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
	    value: 5
	    },
	numberOfNodes:{
	    label: "Number Of Nodes",
	    required: true,
	    min: 1,
	    step: 1,
	    type: "number",
	    placeholder: "Integer",
	    value: null
	    },
	numberOfEvents:{
	    label: "Number Of Events",
	    required: true,
	    min: 1,
	    step: 1,
	    type: "number",
	    placeholder: "Integer",
	    value: 5
	    },
	copies:{
	    label: "Number Of Copies",
	    required: false,
	    min: 1,
	    step: 1,
	    type: "number",
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

    var prepareArgs = function() {
	var getParams = {};
	angular.forEach(params.concat(tempParams), function(param) {getParams[param] = allParams[param].value;});
	var events = [];
	angular.forEach($scope.events, function(event) {
			    var e = {};
			    e.type = event.type;
			    e.class = serverClasses[event.class];
			    events.push(e);
			});
	getParams.events = JSON.stringify(events);
	return getParams;
    };
    
    $scope.allParams = allParams;
    $scope.params = params;
    $scope.tempParams = tempParams;
    $scope.useNodesCount = useNodesCount;
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