var Khopesh = Khopesh ? Khopesh : {};

Khopesh.WorldModel = function(worldId)
{
	this.worldId = worldId;
	
	var onUpdateListeners = [];
	
	//for callbacks
	var me = this;
  
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
		Khopesh.ModelSpinner.register("WorldModel", this.worldId, this.update);	
	};
	
	this.onUpdate = function(callback)
	{
		onUpdateListeners.push(callback);
	};
};