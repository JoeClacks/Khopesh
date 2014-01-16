function ViewData()
{
  this.viewX = 0;
  this.viewY = 0;
  this.viewZ = 0;

	this.zoom = 0;
  
  this.ready = false;
  
  this.set = function(a)
  {
    this.viewX = a[0];
    this.viewY = a[1];
    this.viewZ = a[2]; 
		this.zoom = a[3];
    this.ready = true;
  }
  
  this.get = function()
  {
    return [this.viewX, this.viewY, this.viewZ, this.zoom];
  }
}



function doLogon()
{
	var username = $("#username-textbox").val();

	divConsoleLog('Got username: '+username);

	divConsoleLog('Querying json server for username...');
	$.getJSON("http://localhost:8080/logonUser?callback=?",
	{ "username" : username},
	function(json) {
		if(json != -1)
		{
			divConsoleLog('Got userid: "'+json+'"');
			
			divConsoleLog('Reqesting user and world data');
			
			viewData = new ViewData();
					
			userData = new UserData(json);
			userData.pullData(setup);
			
			worldData = new WorldData(worldId);
			worldData.pullData(setup);
		}
		else
		{
			divConsoleLog('Username not found, creating...');
			$.getJSON("http://localhost:8080/createUser?callback=?",
			{ "username" : username},
			function(json) {
				if(json != -1)
				{
					divConsoleLog('New user created');
					divConsoleLog('Got userid: "'+json+'"');
			
					divConsoleLog('Reqesting user and world data');
					viewData = new ViewData();
					
					userData = new UserData(json);
					userData.pullData(setup);
					
					worldData = new WorldData(worldId);
					worldData.pullData(setup);
				}
				else
				{
					divConsoleLog('Could not create a new user at this time, please try again later');
				}
			});
		}
	});
}

function setup()
{
	if(worldData.ready != true)
	{	divConsoleLog('setup() was called and worldData was not ready'); }
	else if(userData.ready != true)
	{ divConsoleLog('setup() was called and userData was not ready'); }
	else
	{ 
		divConsoleLog('setup() was called and both userData and worldData were ready'); 
		
		familyData = new FamilyData();
		familyData.pullData(userData.userId, setup2);
	}
}

function setup2()
{
// 	if(familyData.ready != true)
// 	{	divConsoleLog('setup2() was called and familyData was not ready'); }
// 	else
// 	{ 
// 		divConsoleLog('setup2() was called and familyData was ready'); 
// 	}
}