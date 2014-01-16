//create the global object if it doesn't already exist
var Khopesh = Khopesh ? Khopesh : {};

//note: collection of functions, not an object
Khopesh.Display = {
	//set up for when the page is first displayed
	init: function()
	{
		$("button").button();
		
		$("button-icon").each(function (i){
					var tmp = $(this);
					tmp.button({
						icons: {
							primary: tmp.attr("icon"),
						},
						text: false
					});
				});
				
		$(".z-control-icon").button("disable");
		
		//only the enough to get the page to display the basics here
		$("#tabs-a").tabs({
			show: Khopesh.clickTab,
		});
		
		$("#tabs-a").tabs("disable",2);
		$("#tabs-a").tabs("disable",3);
		$("#tabs-a").tabs("disable",4);
		
		$("#tabs-a").bind('tabsshow', function(event, ui) {
			if (ui.panel.id == "tabs-a-2") {
				Khopesh.WorldMap.drawMap();
			}
		});
		
		$(".console-outer").click(function() {
			Khopesh.console("Blarg");
		});
				
		$('#dialog-login').dialog(
			{buttons: 
			{
				"Cancel": function(){$('#dialog-login').dialog('close');},
				"OK": function(){Khopesh.player.loginDialogOk();},
			}, 
			modal: true, 
			resizeable: false, 
			draggable: false,
			autoOpen: false,
		});
		
		$('#register-dialog').dialog(
			{buttons: 
			{
				"Cancel": function(){$('#register-dialog').dialog('close');},
				"OK": function(){Khopesh.Controller.doRegister();},
			}, 
			modal: true, 
			resizeable: false, 
			draggable: false,
			autoOpen: false,
		});
		
		$('#chat-dialog').dialog(
			{buttons: {}, 
			modal: false, 
			resizeable: true, 
			draggable: true,
			autoOpen: false,
		});
		
		$('#user-control').dialog(
			{buttons: {}, 
			modal: false, 
			resizeable: true, 
			draggable: true,
			autoOpen: true,
		});
		
		$("#header-login").click( function() {
			Khopesh.console('login button clicked, opening modal login dialog');
			$('#dialog-login').dialog('open');	
		});
		
			$("#header-register").click( function() {
			Khopesh.console('register button clicked, opening modal register dialog');
			$('#register-dialog').dialog('open');	
		});
		
		$("#tabs-a-3-chat").click( function() {
			Khopesh.console('chat button clicked, opening chat dialog');
			$('#chat-dialog').dialog('open');	
			$('#chat-dialog').data('user', $("#tabs-a-3-playerlist").val());
		});
		
		$("#chat-dialog-send").click( function() {
			Khopesh.console('chat send button clicked, sending message');
			Khopesh.Controller.sendChat($('#chat-dialog').data('user'), $('#chat-dialog-input').val());
			$('#chat-dialog-input').val('');
		});
		
		
		$("#chat-dialog-recv").click( function() {
			Khopesh.console('chat recv button clicked, getting chat history');
			Khopesh.Controller.pullChat($('#chat-dialog').data('user'),$('#chat-dialog-text').html);
		});
		
	},
	

	//sets up the display for right after a user has logged in
	postLogin: function()
	{
		//add the player tab
		$("#tabs-a").tabs("enable",2);
		$("#tabs-a").tabs("enable",3);
		$("#tabs-a").tabs("enable",4);
		Khopesh.Display.populatePlayerlist();
		Khopesh.Display.updateHeader();
		
		//putting this here for now
		$('#dialog-login').dialog('close');
	},
	
	populatePlayerlist: function()
	{
		//geting directly for now, need to abstract later
		var serverstring = 'http://localhost:8080/getPlayerList?callback=?';
		$.getJSON(serverstring,
			{},	
			function(json)
			{
				var out = "";
				var key;
				for (key in json)
				{
					out += '<option value="'+key+'">'+json[key]+'</option>';
				}
				Khopesh.console(json);
				Khopesh.console(out);
				$('#tabs-a-3-playerlist').html(out);
			});
			
			//use dom.value
	},

	//updates the header so that the right buttons are shown
	updateHeader: function()
	{
		if( !Khopesh.player.loggedIn )
		{
			$("#header-text").hide();
			$("#header-logout").hide();
			$("#header-login").show();
			$("#header-register").show();
			$("#header-recover").show();
		}
		else
		{
			$("#header-text").show();
			$("#header-logout").show();
			$("#header-login").hide();
			$("#header-register").hide();
			$("#header-recover").hide();
		}
		
		//until we get around to implementing it
		$("#header-recover").button("disable");
	},
	
	//should be called when the information in the player object has been updated
	updatePlayerInfo: function()
	{
		var str = Khopesh.player.toString();
		$('#player-info-div').text(str);
	},
	
	updateFamilyInfo: function()
	{
		var str = Khopesh.family.toString();
		$('#family-info-div').text(str);
	},
	
	//call to initialize the avatar info tab
	updateAvatarInfo: function(avatarId)
	{
		var tmp = $('#avatar-info-div-' + avatarId );
		
		if (tmp.length == 0) {
			tmp = $(document.createElement('div'));
			tmp.attr('id', 'avatar-info-div-' + avatarId);
			$('#tabs-a-5').append(tmp);
		}
		
		tmp.html('<div><big>'+Khopesh.avatars[avatarId].data.avatarName
			+'</big><div>'+Khopesh.avatars[avatarId].toString()+'</div></div>');
	},
};