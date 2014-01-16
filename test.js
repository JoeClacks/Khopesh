"use strict";
/*jslint onevar: true, undef: true, nomen: true, eqeqeq: true, plusplus: true, bitwise: true, regexp: true, strict: true, newcap: true, immed: true */
var Khopesh = Khopesh ? Khopesh : {};
Khopesh.worldId = 1;

Khopesh.console = function(text)
{
// 	$(".console-inner").append(text + '<br />');
// 	$("#console-outer").scrollTop(($("#console-inner").height()- $("#console-outer").height()) + 100);
//  	$(".console-outer").scrollTop($(".console-inner").height());
	console.log(text);
}

//to fake out the display functions for testing
Khopesh.Display = {};
Khopesh.Display.postLogin = function () {};


$(document).ready(function(){
	console.log('setup finished, starting tests');

	Khopesh.player = Khopesh.ControlUser.clone();
	Khopesh.player.tryLogin();

	Khopesh.player.login('joe','badpass');
	Khopesh.player.login('joe','pass');
// 	
// 	console.log(Khopesh.player);
// 	console.log(Khopesh.family);
// 	var k;
// 	for(k in Khopesh.avatars)
// 	{
// 		console.log(Khopesh.avatars[k]);
// 	}
// 	
	console.log('login test complete');
});
