//create the global object if it doesn't already exist
var Khopesh = Khopesh ? Khopesh : {}
Khopesh.WorldMap = {
	viewI: 36,
	viewJ: 25,
	viewK: 129,
	zoom: 1,
	
	outerDiv: "#worldmap",
	middleDiv: "#viewport",
	innerDiv: "#innermap",
	
	refImageName: '#reference-image',
	
	//might consider changing these to be dependent on window size and image size
	mapCacheMin: 2,//the point up to where we'll preload map images
	mapCacheMax: 4,//the point where we toss map images out
	
	initialized: false,
	
	init: function()
	{
		//I think jQuery's height and width don't work because the image isn't displayed
		this.refImage =  $(this.refImageName)[0];
		this.outer = $(this.outerDiv);
		
		this.worldSizeX = Khopesh.world.data.worldSizeX;
		this.worldSizeY = Khopesh.world.data.worldSizeY;
		this.worldWrapX = Khopesh.world.data.worldWrapX;
		this.worldWrapY = Khopesh.world.data.worldWrapY;
		
		this.poitMap();
		
		$(this.innerDiv).click(this.moveMapClick);
		
		this.initialized = true;
	},
	
	calcZoomOffset: function(z)
	{
		if(this.zoom > 0){
			return Math.pow(2,(z - 1));
		}
		else{
			return 1;
		}
	},
	
	drawMap: function()
	{
		if(this.initialized != true)
		{
			this.init();
		}
		
		//offset for the center image
		var centerImageLeft = this.outer.width()/2 - this.refImage.width/2;
		var centerImageTop = this.outer.height()/2 - this.refImage.height/2;
		
		var imageIradius = Math.floor(((this.outer.width()/2 ) / this.refImage.width));
		var imageJradius = Math.floor(((this.outer.height()/2 ) / this.refImage.height));
		
		for(var i = (-imageIradius) + this.viewI - this.mapCacheMin; i < imageIradius + this.viewI + this.mapCacheMin; i++)
		{
			for(var j = (-imageJradius) + this.viewJ - this.mapCacheMin; j < imageJradius + this.viewJ + this.mapCacheMin; j++)
			{
				j = Math.floor(j);
				
				if(this.zoom > 0)
				{
					var imageId = "map_" +i+ "i_" +j+ "j_"+this.zoom+"z";
				}
				else
				{
					var imageId = "map_" +i+ "i_" +j+ "j_"+this.viewK+"k_"+this.zoom+"z";
				}
				
				var zoomOffset = this.calcZoomOffset(this.zoom)
				
				//make sure we don't already have this image
				if($('#'+imageId).length < 1)
				{
					//wrap first
					var adjustedDbImageX = (i % Math.ceil(this.worldSizeX/(zoomOffset)));
					var adjustedDbImageY = (j % Math.ceil(this.worldSizeY/(zoomOffset)));
				
					//subtract from the maximum if it is negative
					if(adjustedDbImageX < 0){ 
						adjustedDbImageX = Math.ceil(this.worldSizeX/(zoomOffset)) + adjustedDbImageX; 
					}
					if(adjustedDbImageY < 0){
						adjustedDbImageY = Math.ceil(this.worldSizeY/(zoomOffset)) + adjustedDbImageY; 
					}
					
					//expand out for our zoom
					adjustedDbImageX = adjustedDbImageX * zoomOffset;
					adjustedDbImageY = adjustedDbImageY * zoomOffset;
					
					var imgLeft = centerImageLeft+i*this.refImage.width;
					var imgTop = centerImageTop+j*this.refImage.height;
				
					var newImage = $(document.createElement('img'));
					
					//check if the image is out of bounds
					//  db image space is [0,X),[0,Y), Z is unbounded
					if(this.worldWrapX == false && (i < 0 || i >= Math.ceil(this.worldSizeX/(zoomOffset)))
						|| this.worldWrapY == false && (j < 0 || j >= Math.ceil(this.worldSizeY/(zoomOffset))))
					{
						//show the void image if we are outside the bounds of the image
						var fileName = "img-src/void.png";
					}
					else if(this.zoom > 0)
					{
						var fileName = "img-world/zoom"+this.zoom+"-" +adjustedDbImageX+ "x-" +adjustedDbImageY+ "y.png";  
					}
					else
					{
						var fileName = "img-world/zoom0-" +adjustedDbImageX+ "x-" +adjustedDbImageY+ "y-" +this.viewK+ "z.png";  
					}
					
					newImage.attr('src', fileName);
					newImage.addClass('tileimage');
					newImage.attr('id', imageId);
					newImage.attr('style', "left: "+imgLeft+"px; top: "+imgTop+"px;");
					newImage.error(function() {
						var me = this
						Khopesh.Model.proxy(
							'getImage', 
							{ "zoom": $(this).data('zoom'), "x": $(this).data('x'), 
								"y": $(this).data('y'), "z": $(this).data('z') },
							function(json) {
								$(me).attr('src', json);
							}
						);
					});
						
					$(newImage).data('x',adjustedDbImageX);
					$(newImage).data('y',adjustedDbImageY);
					$(newImage).data('z',this.viewK);
					$(newImage).data('zoom', this.zoom);
					$(newImage).data('i',i);
					$(newImage).data('j',j);
					$(newImage).data('k', this.viewK);
					$(this.innerDiv).append(newImage);
				}
			}
		}
	},
	
	
	//hides or shows the up and down controls based on the current zoom level
	hideZControls: function ()
	{
		if( this.zoom > 0)
		{
// 			$('.z-control-icon').hide();
			$('.z-control-icon').button("disable");
		}
		else
		{
// 			$('.z-control-icon').show();
			$('.z-control-icon').button("enable");
		}		
	},
	
	poitMap: function()
	{
		var left = -1*this.viewI*this.refImage.width;
		var top = -1*this.viewJ*this.refImage.height;
		
		$("#viewport").attr('style', "left: "+left+"px; top: "+top+"px;");
	},
	
	slideMap: function()
	{
		var left = -1*this.viewI*this.refImage.width;
		var top = -1*this.viewJ*this.refImage.height;
		
		$("#viewport").animate( { left: (left+"px")}, {queue: false, duration: 300})
			.animate( { top: (top+"px")}, {queue: false, duration: 300});
	},
	
	moveMap: function (x,y)
	{
		this.viewI += x;
		this.viewJ += y;
		
		//taking out the timeout for now, were having a problem where moving too fast
		//	resulted in some images being missed
		//setTimeout('Khopesh.WorldMap.drawMap();',200)
		this.drawMap();

		//We may want to rewrite the cleanup funtion
	// 	setTimeout("shrinkMap("+x+", "+y+");", 500);
		this.slideMap();
	},
	
	zoomMap: function (z)
	{
		oldZoom = this.zoom;
		this.zoom += z;

		oldOffset = this.calcZoomOffset(oldZoom);
		newOffset = this.calcZoomOffset(this.zoom);

		this.viewI = Math.floor(this.viewI*oldOffset/newOffset);
		this.viewJ = Math.floor(this.viewJ*oldOffset/newOffset);
		
		var str = 'img[id*="_'+oldZoom+'z"]';
		$(str).remove();
		
		this.drawMap();
		this.poitMap();
		this.hideZControls();
	},

	moveMapAbsolute: function (x,y,z,zoom)
	{
		offset = this.calcZoomOffset(zoom);
		this.viewI = Math.floor(x/offset);
		this.viewJ = Math.floor(y/offset);
		this.viewK = z;
		this.zoom = zoom;
		
		this.drawMap();
		this.poitMap();
	},
	
	
	//seperating out z moves because they won't ever slide like an x,y transistion
	//	will. In the future we may look at have levels fade in/fade out
	moveMapZ: function (z)
	{
		kIndex = this.viewK;
		this.viewK += z;

		var str = 'img[id*="_'+kIndex+'k"]';
		$(str).remove();
		
		this.drawMap();
	},
	
	moveMapClick: function (e)
	{
		var clicked = $(e.target);
		
		Khopesh.WorldMap.viewI = clicked.data('i');
		Khopesh.WorldMap.viewJ = clicked.data('j');	  
			
		Khopesh.WorldMap.drawMap();
		Khopesh.WorldMap.slideMap();
	}
}