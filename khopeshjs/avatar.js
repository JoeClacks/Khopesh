var Khopesh = Khopesh ? Khopesh : {};
Khopesh.Prototypes = Khopesh.Prototypes ? Khopesh.Prototypes : {};

Khopesh.Prototypes.Avatar = (function () {	
	var obj = Khopesh.Prototypes.ModelObject.clone();
	
	obj.update = function(values) {
		obj.proto.update.call(this, values);
		this.avatarId = this.data.avatarId;
	};
	
	obj.setAvatarId = function(avatarId)
	{
		this.avatarId = avatarId;
		this.data.avatarId = avatarId;
	};
	
	return obj;
}());

Khopesh.Prototypes.ControlAvatar = (function () {
	var obj = Khopesh.Prototypes.Avatar.clone();
	
	obj.pullData = function()
	{
		//NOTE: we may want to check that we have a valid userId first
		var self = this;
		Khopesh.Controller.proxy('pullAvatarData', 
		{"avatarId" : this.avatarId },
		function(json) {
			self.update(json);
			Khopesh.Display.updateAvatarInfo(self.avatarId);
		});	
	};
	
	return obj;
}());