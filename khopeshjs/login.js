var Khopesh = Khopesh ? Khopesh : {};

Khopesh.Login = {
	//see if the player is already logged in
	tryLogin: function(callback)
	{
		Controller.proxy('tryLogin', {},
		function(json) {
			var loggedIn = Khopesh.Login.postLogin(json);
			if(!loggedIn)
			{
				Khopesh.console('User was not previously logged in...');
			}
			else
			{
				Khopesh.console('User was previously logged in...');
			}
		});
	},
		
	loginDialogOk: function(callback)
	{
		var username = $('#dialog-login-username').val();
		var password = $('#dialog-login-password').val();

		Khopesh.console('Got username: '+username);
		Khopesh.console('Got password: '+password);
		Khopesh.console('Querying json controller server...');

		Controller.proxy('doLogin', { "username" : username, "password": password},
		function(json) {
			var loggedIn = Khopesh.Login.postLogin(json);
			if (!loggedIn)
			{
				$('#dialog-login-msg').text('Username and password invalid, please try again');
			}
			else
			{
				$('#dialog-login-msg').text('');
				$('#login-dialog').dialog('close');
			}
		});
	},
	
	//takes care of everything that needs to be done right after a player has logged in
	postLogin: function(json)
	{
		if(json == -1)
		{
			Khopesh.console('User failed to log in...');
			return false;
			//if the we came from a dialog display a message to that effect
		}
		else
		{
			Khopesh.player.loggedIn = true;
			Khopesh.player.userId = json;
			Khopesh.player.pullData();
			
			//NOTE: the only case that the player shouldn't have a family and at least 
			//	one avatar defined is when they've died. (we'll take care of initials
			//	in the register process, and we'll worry about after everyone's died
			//	later when we have the whole skill system better defined) So we can
			//	assume that there will always be a family and avatar defined and ready 
			//	to play.
			
			//remember json is the userId
			Khopesh.family = new Khopesh.FamilyModel(json);
			Khopesh.family.update();
			
			Khopesh.avatars = pull all avatars;
			
			//and update the display
			Khopesh.Display.postLogin();
			Khopesh.console('User is succesfully logged in...');
			
			//where are we going to popup the family dialog?
			return true;
		}
	},
}