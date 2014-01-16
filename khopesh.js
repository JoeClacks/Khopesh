function resizeWindow()
{
  $("#centercol").height($(window).height() - 4*$("#hidden").height() - $("#footer").height() - $("#header").height());
}

function Log(logContainer)
{
  this.logString = "";
  this.logContainer = logContainer;

  this.update = function()
  {
    this.logContainer.html(this.logString);
    this.logContainer.scrollTop = this.logContainer.scrollHeight;
  }
  
  this.append = function(s)
  {
    this.logString += s;
    this.update()
  }
  
  this.clear = function()
  {
    this.logString = ""
    this.update()
  }
}

function UserData(userId)
{
  this.userId = userId;
  this.userName = "";

  this.userX = 0;
  this.userY = 0;
  this.userZ = 0;

  this.ready = false;
  
  //used for callbacks
  var me = this;

//   this.setLocation = function(strData)
//   {
//     this.userX = strData["userX"];
//     this.userY = strData["userY"];
//     this.userZ = strData["userZ"];
//   }
  
  this.pullData = function ()
  {
    $.getJSON("http://localhost:8080/getUserData?callback=?",
      {"userId" : me.userId },
      function(json)
      {
	
				me.userName = json["userName"];
				me.userX = json["userX"];
				me.userY = json["userY"];
				me.userZ = json["userZ"];
				me.ready = true;
// 				viewData.set(new Array(me.userX, me.userY, me.userZ));
      });
  }
  
//   this.isReady = function()
//   {
//     return this.ready;
//   }
}

function WorldData(worldId)
{
  this.worldId = worldId
  this.worldName = "";

  this.worldSizeX = 0;
  this.worldSizeY = 0;
  
  this.worldWrapX = false;
  this.worldWrapY = false;

  this.ready = false;
  
  //for callbacks
  var me = this;

  this.pullData = function ()
  {
    $.getJSON("http://localhost:8080/getWorldData?callback=?",
      { "worldId" : me.worldId },
      function(json)
      {
				me.worldName = json["worldName"]

				me.worldSizeX = json["worldSizeX"];
				me.worldSizeY = json["worldSizeY"];
				
				me.worldWrapX = json["worldWrapX"];
				me.worldWrapY = json["worldWrapY"];
				
				me.ready = true;
      });
  }  
}

function ViewData()
{
  this.viewX = 0;
  this.viewY = 0;
  this.viewZ = 0;

	this.zoom = 0;
  
  this.ready = 0;
  
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

function shrinkMap(deltaX, deltaY)
{
  //determines the 'center' image
  var centerImageX = viewData.viewX;
  var centerImageY = viewData.viewY;
  var centerImageZ = viewData.viewZ;
  
  //determine how far on the sides we will display
  var imageXradius = Math.floor((($("#worldmap").width()/2 ) / imgWidth));
  var imageYradius = Math.floor((($("#worldmap").height()/2 ) / imgHeight));
  
  //if deltaX is 0 we shouldn't bother
  for(var i = 0; i < Math.abs(deltaX); i++)
  {
    if(deltaX > 0)
    {
      var iIndex = centerImageX + (mapCacheMax + i + imageXradius);
    }
    else
    {
      var iIndex = centerImageX - (mapCacheMax + i + imageXradius);
    }
    
    var str = 'img[id*="_'+iIndex+'i"]';
    $(str).remove();
  }
  
  for(var i = 0; i < Math.abs(deltaY); i++)
  {
    if(deltaY > 0)
    {
      var jIndex = centerImageY + (mapCacheMax + i + imageYradius);
    }
    else
    {
      var jIndex = centerImageY - (mapCacheMax + i + imageYradius);
    }
    
    var str = 'img[id*="_'+jIndex+'j"]';
    $(str).remove();
  }
}


function moveMapAbsolute(l)
{
	viewData.set(l);
	console.log(l);
	//move, draw in cells, clean up old cells in that order
 	

	var p = $("#viewport").position();
	console.log("p.top: "+ p.top +" p.left"+ p.left);
	p.top = -1*l[1]*imgHeight;
	p.left = -1*l[0]*imgWidth;
	console.log("i.top: "+ p.top +" i.left"+ p.left);
	$("#viewport").attr('style', "left: "+p.left+"px; top: "+p.top+"px;");
	drawMap();
}

function moveMap(x,y)
{
	viewData.viewX += x;
	viewData.viewY += y;

	//move, draw in cells, clean up old cells in that order
 	setTimeout('drawMap();',400)

	//We may want to rewrite the cleanup funtion
// 	setTimeout("shrinkMap("+x+", "+y+");", 500);

	var p = $("#viewport").position();
	p.left -= x*imgWidth;
	p.top -= y*imgHeight;
	$("#viewport").animate( { left: (p.left+"px")}, {queue: false, duration: 300})
		.animate( { top: (p.top+"px")}, {queue: false, duration: 300});
}


//seperating out z moves because they won't ever slide like an x,y transistion
//	will. In the future we may look at have levels fade in/fade out
function moveMapZ(z)
{
	kIndex = viewData.viewZ;
	viewData.viewZ += z;

	var str = 'img[id*="_'+kIndex+'k"]';
	$(str).remove();
	
	drawMap()
}

function zoomMap(z)
{
	zoom = viewData.zoom;
 	viewData.zoom += z;

 	var str = 'img[id*="_'+zoom+'z"]';
 	$(str).remove();
 	
 	drawMap()
 	hideUpDownControls()
}

function moveMapClick(e)
{
	var clicked = $(e.target);
	var deltaX = viewData.viewX - clicked.data('iIndex');
	var deltaY = viewData.viewY - clicked.data('jIndex');
	
	viewData.viewX = clicked.data('iIndex');
	viewData.viewY = clicked.data('jIndex');	  
		
	//move, draw in cells, clean up old cells in that order
	setTimeout('drawMap();',400)

	//and cleanup, but wait to do it until after the animation has finished
	setTimeout("shrinkMap("+deltaX+", "+deltaY+");", 500);
	
	var p = $("#viewport").position();
	p.left += (deltaX)*imgWidth;
	p.top += (deltaY)*imgHeight;
	$("#viewport").animate( { left: (p.left+"px")}, {queue: false, duration: 300})
		.animate( { top: (p.top+"px")}, {queue: false, duration: 300});
}




function drawMap()
{
  if(worldData.ready != true || viewData.ready != true)
  {
    //loop until we're ready to draw
    timeout += 1;
    if(timeout > 10)
    {
      console.log("Timeout, did not get data from server....");
      return;
    }
    
    setTimeout("drawMap()", 100);
    return;
  }
  
  //gives us where the center image should be displayed in px
  var centerImageLeft = $("#worldmap").width()/2 - imgWidth/2;
  var centerImageTop = $("#worldmap").height()/2 - imgHeight/2;

  //determines the 'center' image
  console.log(viewData.get());
  var centerImageX = viewData.viewX;
  var centerImageY = viewData.viewY;
  var centerImageZ = viewData.viewZ;
	var zoomLevel = viewData.zoom;
  
  var adjustedDbImageZ = centerImageZ;
  
  //determine how far on the sides we will display
  var imageXradius = Math.floor((($("#worldmap").width()/2 ) / imgWidth));
  var imageYradius = Math.floor((($("#worldmap").height()/2 ) / imgHeight));
  
  var k = centerImageZ;

  for(var i = (-imageXradius) + centerImageX - mapCacheMin; i < imageXradius + centerImageX + mapCacheMin; i++)
  {
    //clean up i before we index off of it
    i = Math.floor(i);

    for(var j = (-imageYradius) + centerImageY - mapCacheMin; j < imageYradius + centerImageY + mapCacheMin; j++)
    {
      j = Math.floor(j);
      
      if(zoomLevel > 0)
      {
				var imageId = "map_" +i+ "i_" +j+ "j_"+zoomLevel+"z";
				zoom = Math.pow(2,(zoomLevel - 1));
			}
			else
			{
				var imageId = "map_" +i+ "i_" +j+ "j_"+k+"k";
				zoom = 1;
			}
//       console.log(imageId);
      
      //check if we've allready have the image
      if( $('#'+imageId).length < 1 )
      {
				
				
				var adjustedDbImageX = (i % Math.ceil(worldData.worldSizeX/(zoom)));
				var adjustedDbImageY = (j % Math.ceil(worldData.worldSizeY/(zoom)));
				var adjustedDbImageZ = k; //k is never out of bounds and never wraps
				
				if(adjustedDbImageX < 0){ adjustedDbImageX = Math.ceil(worldData.worldSizeX/(zoom)) + adjustedDbImageX; }
				if(adjustedDbImageY < 0){ adjustedDbImageY = Math.ceil(worldData.worldSizeY/(zoom)) + adjustedDbImageY; }
			
				adjustedDbImageX = adjustedDbImageX * zoom;
				adjustedDbImageY = adjustedDbImageY * zoom;
				
				var imgLeft = centerImageLeft+i*imgWidth;
				var imgTop = centerImageTop+j*imgHeight;
									
				
				var newImage = $(document.createElement('img'));
				
				
				//check if the image is out of bounds
				//  db image space is [0,X),[0,Y), Z is unbounded
				if(worldData.worldWrapX == false && (i < 0 || i >= Math.ceil(worldData.worldSizeX/(zoom)))
					|| worldData.worldWrapY == false && (j < 0 || j >= Math.ceil(worldData.worldSizeY/(zoom))))
				{
					//show the void image if we are outside the bounds of the image
					var fileName = "img-src/void.png";
				}
				else if(zoomLevel > 0)
				{
					var fileName = "img-world-" + worldData.worldId + "/zoom"+zoomLevel+"-" +adjustedDbImageX+ "x-" +adjustedDbImageY+ "y.png";  
				}
				else
				{
					var fileName = "img-world-" + worldData.worldId + "/zoom0-" +adjustedDbImageX+ "x-" +adjustedDbImageY+ "y-" +adjustedDbImageZ+ "z.png";  
					newImage.error(
					function() {
						var me = this
						
						$.getJSON("http://localhost:8080/generateWorldmap?callback=?",
						{ "worldId" : worldData.worldId, "x": $(this).data('x'), "y": $(this).data('y'), "z": $(this).data('z'), },
						function(json) {
							$(me).attr('src', json);
						});
					});
				}
				
				newImage.attr('src', fileName);
				newImage.addClass('tileimage');
				newImage.attr('id', imageId);
				newImage.attr('style', "left: "+imgLeft+"px; top: "+imgTop+"px;");
					
				$(newImage).data('x',adjustedDbImageX);
				$(newImage).data('y',adjustedDbImageY);
				$(newImage).data('z',adjustedDbImageZ);
				$(newImage).data('iIndex',i);
				$(newImage).data('jIndex',j);
				$(newImage).data('kIndex',k);
// 				console.log([[i,j,k,zoomLevel],[adjustedDbImageX, adjustedDbImageY,adjustedDbImageZ]]);
				$("#innermap").append(newImage);
      }
    }
  }
}

//hides or shows the up and down controls based on the current zoom level
function hideUpDownControls()
{
	if( viewData.zoom > 0)
	{
		//hide
		$('#control-up').hide();
		$('#control-down').hide();
	}
	else
	{
		$('#control-up').show();
		$('#control-down').show();
	}
	
}

function divConsoleLog(text)
{
	$("#innertext").append(text);
	$("#centercol").scrollTop(($("#innertext").height()- $("#centercol").height()) + 100);
}

function logon()
{
	$('#login-dialog').dialog('close');
	var username = $("#username-textbox").val();
	
	divConsoleLog('Got username: "'+username+'"<br />');

	divConsoleLog('Querying json server for username...<br />');
	$.getJSON("http://localhost:8080/logonUser?callback=?",
	{ "username" : username},
	function(json) {
		divConsoleLog('Got userid: "'+json+'"<br />');
		
		divConsoleLog('Reqesting user and world data<br />');
		
		viewData = new ViewData();
				
		userData = new UserData(json);
		userData.pullData();
		
		worldData = new WorldData(worldId);
		worldData.pullData();
		
		setupWait(10);
	});
}

function setupWait(timeout)
{
	if(worldData.ready != true || viewData.ready != true)
  {
    //loop until we've recieved the data from the server
    timeout -= 1;
    if(timeout < 0)
    {
      divConsoleLog("Timeout, did not get data from server....");
      return;
    }
    
    setTimeout("drawMap("+timeout+")", 100);
    return;
  }
  
  //we only hit this once the data has been recieved
  divConsoleLog("Got data from server");
}