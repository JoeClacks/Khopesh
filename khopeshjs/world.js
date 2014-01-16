var Khopesh = Khopesh ? Khopesh : {};
Khopesh.Prototypes = Khopesh.Prototypes ? Khopesh.Prototypes : {};

Khopesh.Prototypes.World = (function () {
	var obj = Khopesh.Prototypes.ModelObject.clone();
	
	obj.update = function(values) {
		obj.proto.update.call(this, values);
		this.worldId = this.data.worldId;
	};
	
	obj.registerSelf = function() {
		Khopesh.ModelSpinner.register("WorldModel", this.userId, this.getUpdater());	
	};
	
	obj.setWorldId = function(worldId)
	{
		this.worldId = worldId;
		this.data.worldId = worldId;
	};
	
	obj.pullData = function(callback)
	{
		var self = this;
		Khopesh.Model.proxy('pullWorldData', 
		{'worldId' : this.worldId},
		function(json) {
			self.update(json);
			
			if(callback !== undefined)
			{
				callback();
			}
		});
	};
	
	obj.clone = function(worldId) {
		var ret = obj.proto.clone.call(this);
		
		ret.setWorldId(worldId);
		
		return ret;
	};
	
	return obj;
}());