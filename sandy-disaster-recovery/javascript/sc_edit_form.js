$(function() {
	$.get( "/api/site_ajax", { id_param: "{{site_id}}" } )
	  .done(function( data ) {
	    console.log(data );
	  });
});