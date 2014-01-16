var Khopesh = Khopesh ? Khopesh : {};
Khopesh.Prototypes = Khopesh.Prototypes ? Khopesh.Prototypes : {}; 

Khopesh.Prototypes.User = (function () {
	var obj = Khopesh.Prototypes.ModelObject.clone();
	
	obj.update = function(values) {
		obj.proto.update.call(this, values);
		this.userId = this.data.userId;		
	};
	
	obj.registerSelf = function() {
		Khopesh.ModelSpinner.register("UserModel", this.userId, this.getUpdater());	
	};
	
	obj.setUserId = function(userId)
	{
		this.userId = userId;
		this.data.userId = userId;
	};
	
	obj.pullData = function()
	{
		//NOTE: we may want to check that we have a valid userId first
		var self = this;
		Khopesh.Model.proxy('pullUserData', 
		{'userId' : this.userId},	//we won't have to pass in a the usedId because this 
				//	should only be used for the logged in player
		function(json) {
			self.update(json);
		});	
	};
	
	return obj;
}());


Khopesh.Prototypes.ControlUser = (function () {
	console.log('calling ControlUser object');
	var obj = Khopesh.Prototypes.User.clone();	
	
	obj.loggedIn = false;

	obj.registerSelf = function() {
		Khopesh.ModelSpinner.register("UserControl", this.userId, this.getUpdater());	
	};
	
	obj.tryLogin = function()
	{
		Khopesh.console('in try login');
		var self = this;
		Khopesh.Controller.proxy('tryLogin', 
		{},
		function(json) {
			Khopesh.console('and back');
			var loggedIn = self.postLogin(json);
			if(!loggedIn)
			{
				Khopesh.console('User was not previously logged in...');
			}
			else
			{
				Khopesh.console('User was previously logged in...');
			}
		});
	};
	
	obj.login = function(username, password)
	{
		var self = this;
		Khopesh.Controller.proxy('doLogin', 
		{ "username" : username, "password": password},
		function(json) {
			var loggedIn = self.postLogin(json);
			if (!loggedIn)
			{
				$('#dialog-login-msg').text('Username and password invalid, please try again');
			}
			else
			{
				$('#dialog-login-msg').text('');
			}
		});	
	};
	
	
	obj.loginDialogOk = function()
	{
		var username = $('#dialog-login-username').val();
		var password = $('#dialog-login-password').val();

		Khopesh.console('Got username: '+username);
		Khopesh.console('Got password: '+password);
		Khopesh.console('Querying json controller server...');

		this.login(username, password);
	};
	
	//takes care of everything that needs to be done right after a player has logged in
	obj.postLogin = function(json)
	{
		//NOTE: json should be the userId if succesful, -1 otherwise
		if(json[0] == -1)
		{
			Khopesh.console('User failed to log in...');
			Khopesh.console(json[1]);
			return false;
			//if the we came from a dialog display a message to that effect
		}
		else
		{
			Khopesh.console(json[1]);
			this.loggedIn = true;
			this.userId = json[0];
			this.pullData();
			
			//NOTE: the only case that the player shouldn't have a family and at least 
			//	one avatar defined is when they've died. (we'll take care of initials
			//	in the register process, and we'll worry about after everyone's died
			//	later when we have the whole skill system better defined) So we can
			//	assume that there will always be a family and avatar defined and ready 
			//	to play.
			
			//remember json is the userId
 			Khopesh.family = Khopesh.Prototypes.ControlFamily.clone();
 			Khopesh.family.pullData();//don't need to set the family id beforehand
 			
 			//this will pull up all the avatar data for the player
 			Khopesh.family.pullAvatarData();
			
			//and update the display
			Khopesh.Display.postLogin();
			Khopesh.console('User is succesfully logged in...');
			
			return true;
		}
	};
	
	obj.pullData = function()
	{
		//NOTE: we may want to check that we have a valid userId first
		var self = this;
		Khopesh.Controller.proxy('pullUserData', 
		{},	//we won't have to pass in a the usedId because this 
				//	should only be used for the logged in player
		function(json) {
			self.update(json);
			Khopesh.Display.updatePlayerInfo();
		});	
	};
	
	return obj;
}());

