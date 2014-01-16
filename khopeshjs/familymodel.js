//create the global object if it doesn't already exist
var Khopesh = Khopesh ? Khopesh : {};

Khopesh.FamilyModel = function(userId, familyId)
{
	this.userId = userId;
	this.familyId = familyId;
	
	var onUpdateListeners = [];
	
	//for callbacks
	var me = this;
	
	//data not pulled from the server
	this.valid = false;
  
  this.toString = function()
	{
		var out = "";
		for(var k in this)
		{
			if($.isFunction(this[k]))
			{
// 				out += k + ": function() ";
			}
			else
			{
				out += k + ": " + this[k] + " ";
			}
		}
		return out;
	};

	//used as a callback, cannot use 'this'
	this.update = function(values)
	{
		for(var k in values)
		{
			me[k] = values[k];
		}
		
		me.ready = true;
				
		for(var x in onUpdateListeners)
		{
			onUpdateListeners[x]();
		}
	};
  
	this.registerSelf = function()
	{
		Khopesh.ModelSpinner.register("FamilyModel", this.familyId, this.update);	
	};
	
	this.onUpdate = function(callback)
	{
		onUpdateListeners.push(callback);
	};
};