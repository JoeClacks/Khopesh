//create the global object if it doesn't already exist
var Khopesh = Khopesh ? Khopesh : {};

Khopesh.worldId = 1;

Khopesh.resizeWindow = function()
{
	//3.4 is an approximation to get it to fit the window
  $(".tab-content-clipped").height($(window).height() - (3.4*$("#header").height()));
  //for some reason the header always has a padding of 6, so this makes it line up right
	//$(".tab-content-clipped").width($("#tabs-a-header").width() - 6);
};

Khopesh.console = function(text)
{
	$(".console-inner").append(text + '<br />');
// 	$("#console-outer").scrollTop(($("#console-inner").height()- $("#console-outer").height()) + 100);
 	$(".console-outer").scrollTop($(".console-inner").height());
};

// Khopesh.prototypes.World = function(worldId) {
// 	var obj = this.WorldPrototype.clone();
// 	obj.setWorldId(worldId);
// 	
// 	return obj;
// }

Khopesh.boot1 = function()
{
	Khopesh.console("Stage 1: entering");
	Khopesh.world = Khopesh.Prototypes.World.clone(Khopesh.worldId);	
	
 	Khopesh.player = Khopesh.Prototypes.ControlUser.clone();
	
	Khopesh.player.tryLogin();	
	
	$(window).resize(Khopesh.resizeWindow);
	Khopesh.resizeWindow();
	
	Khopesh.Display.init();
	Khopesh.Display.updateHeader();

	Khopesh.world.pullData(Khopesh.boot2);
	
	Khopesh.console("Stage 1: exiting");
};

Khopesh.boot2 = function()
{
	Khopesh.console("Stage 2: entering");
// 
// 	Khopesh.WorldMap.drawMap();


// 	Khopesh.WorldMap.moveMapAbsolute(5,5,100,4);
// 	$("#innermap").click(Khopesh.WorldMap.moveMapClick);
// 
// 				
	Khopesh.console("Stage 2: exiting");
};

Khopesh.clickTab = function(event, ui)
{
// 	Khopesh.WorldMap.drawMap();
};