var Khopesh = Khopesh ? Khopesh : {};

Khopesh.Model = {
	//serverstring: 'http://tessera.ath.cx:8095/',
	serverstring: Khopesh.Config.modelServer,
	
	jsonError: function(XMLHttpRequest, textStatus, errorThrown)
	{
		console.log(textStatus + ": " + errorThrown);	
	},
	
	proxy: function(func, params, successCallback)
	{
		$.ajax({
			url: this.serverstring+func,
			dataType: 'jsonp',
			data: params,
			success: successCallback
		});
	}
};
