$(function() {
	$.get( "/api/site_ajax?id={{site_id}}", function( data ) {
	  console.log(data);
	});
});