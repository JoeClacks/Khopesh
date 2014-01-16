//create the global object if it doesn't already exist
var Khopesh = Khopesh ? Khopesh : {};

Khopesh.Controller = {
	serverstring: Khopesh.Config.controlServer,
	
	proxy: function(func, params, successCallback)
	{
		$.ajax({
			url: this.serverstring+func,
			dataType: 'jsonp',
			data: params,
			success: successCallback
		});
	},
	
	doRegister: function(callback)
	{
		var username = $("#register-username-textbox").val();
		var password = $("#register-password-textbox").val();

		Khopesh.console('Got username: '+username);
		Khopesh.console('Got password: '+password);
		Khopesh.console('Querying json controller server...');

		//$.getJSON(this.serverstring+'doRegister'+this.callbackstring,
		this.proxy('doRegister',
		{ "username" : username, "password": password},
		function(json) {
			if(json != -1)
			{
				Khopesh.player.loggedIn = true;
				Khopesh.player.userId = json;
				// now need to pull data
				Khopesh.Display.login();
				Khopesh.console('User is succesfully registered and logged in...');
			}
			else
			{
				Khopesh.console('User failed to register...');
			}
				
			if(callback != undefined)
			{
				callback();
			}
		});
	},
	
	sendChat: function(to, msg)
	{
		Khopesh.console('sendChat: from: '+Khopesh.player.userId+' to: '+to+' msg: '+msg);
		
		$.getJSON(this.serverstring+'sendChat'+this.callbackstring,
		{ "to" : to, "msg": msg},
		function(json) {
			Khopesh.console('sendChat: comfirmed message sent: from:'+Khopesh.player.userId+' to: '+to+' msg: '+msg);
		});
	},
	
	pullChat: function(to, callback)
	{
		Khopesh.console('pullChat: from: '+Khopesh.player.userId+' to: '+to);
		$.getJSON(this.serverstring+'pullChat'+this.callbackstring,
		{ "to" : to },
		function(json) {
			Khopesh.console('pullChat: returned message: '+json);
			
			var row;
			var out ='';
			for (row in json){
				out += json[row]['msg'] + ' ' + json[row]['time'] + '<br />';
			}
			
			Khopesh.console('setting chat box to: ' + out);
			$('#chat-dialog-text').html(out);
		});
	}
};
