var Khopesh = Khopesh ? Khopesh : {};
Khopesh.Prototypes = Khopesh.Prototypes ? Khopesh.Prototypes : {};

Khopesh.Prototypes.ProtoObject = (function () {
	console.log('calling proto object');
	var obj = {};
	obj.clone = function () {
		console.log('calling clone');
		var self = this;
		function F() {this.proto = self;}
		F.prototype = this;
		return new F();
	};
	
	return obj;
}());