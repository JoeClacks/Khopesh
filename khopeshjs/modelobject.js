var Khopesh = Khopesh ? Khopesh : {};
Khopesh.Prototypes = Khopesh.Prototypes ? Khopesh.Prototypes : {};

Khopesh.Prototypes.ModelObject = (function () {
	var obj = Khopesh.Prototypes.ProtoObject.clone();
	
// 	obj.id = -1;//we'll keep each id separate
	
	obj.onUpdateListeners = [];
	
	obj.data = {};
	
	//should only be true when we have current data from the server
	obj.ready = false;
	
	obj.clone = function() {
		var ret = obj.proto.clone.call(this);
		
		//have to create new copies for these
		ret.onUpdateListeners = [];
		ret.data = {};
		
		return ret;
	};
	
	obj.toString = function() {
		var out = "";
		for(var k in this.data)
		{
			out += k + ": " + this.data[k] + " ";
		}
		return out;
	};
	
	obj.getUpdater = function() {
		var self = this;
		return function (values)
		{
			self.update(values);
		};
	};
	
	obj.update = function(values) {
		for(var k in values)
		{
			this.data[k] = values[k];
		}
			
		this.ready = true;
		
		for(var x in this.onUpdateListeners)
		{
			this.onUpdateListeners[x]();
		}
	};
	
	obj.onUpdate = function(callback)
	{
		this.onUpdateListeners.push(callback);
	};
	
	return obj;
}());