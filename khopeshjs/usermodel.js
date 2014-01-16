var Khopesh = Khopesh ? Khopesh : {};

Khopesh.UserModel = function(userId)
{
	this.userId = userId;
	
	var onUpdateListeners = [];
	
	//for callbacks
	var me = this;
	
	//data not pulled from the server
	this.loggedIn = false;
  
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
		Khopesh.ModelSpinner.register("UserModel", this.userId, this.update);	
	};
	
	this.onUpdate = function(callback)
	{
		onUpdateListeners.push(callback);
	};
};