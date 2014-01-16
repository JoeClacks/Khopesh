var Khopesh = Khopesh ? Khopesh : {};
Khopesh.Prototypes = Khopesh.Prototypes ? Khopesh.Prototypes : {}; 

Khopesh.Prototypes.Family = (function () {	
	var obj = Khopesh.Prototypes.ModelObject.clone();
	
	obj.setFamilyId = function(familyId)
	{
		this.familyId = familyId;
		this.data.familyId = familyId;
	};
	
	obj.update = function(values) {
		obj.proto.update.call(this, values);
		this.familyId = this.data.familyId;		
	};

	return obj;
}());

Khopesh.Prototypes.ControlFamily = (function () {
	var obj = Khopesh.Prototypes.Family.clone();
	
	obj.pullData = function()
	{
		//NOTE: we may want to check that we have a valid userId first
		var self = this;
		Khopesh.Controller.proxy('pullFamilyData', 
		{},	//we won't have to pass in a the familyId because this 
				//	should only be used for the logged in player
		function(json) {
			self.update(json);
			Khopesh.Display.updateFamilyInfo();
		});	
	};
	
	//for every player that 1-n avatars, we could as for a list of avatarId's, 
	//	init that many avatar objects, and then tell each to pull it's data, 
	//	or we could do everything in one go - right now I'm thinking that latter,
	//	but at the family level - no reason to have it at the user and closer
	//	to the actual avatar objects seems better
	obj.pullAvatarData = function()
	{
		var self = this;
		Khopesh.Controller.proxy('pullAvatarData', 
		{},	//we'll use nothing as a signal to pull all avatars for the family
		function(json) {
			//expecting a list of all avatar data indexed by the avatarid
			Khopesh.avatars = {};
			
			for(var k in json)
			{
				var avatar = Khopesh.Prototypes.ControlAvatar.clone();
				avatar.setAvatarId(k);
				avatar.pullData();
				Khopesh.avatars[k] = avatar;
			}
		});	
	};
	
	return obj;
}());