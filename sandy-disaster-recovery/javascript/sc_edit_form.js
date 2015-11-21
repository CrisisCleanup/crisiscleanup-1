$(function() {
	$.get( "/api/site_ajax", { id_param: "{{site_id}}" } )
	  .done(function( data ) {
	  	console.log("start ajax data");
	    console.log(data );
	    console.log("end ajax data");
	  });
});