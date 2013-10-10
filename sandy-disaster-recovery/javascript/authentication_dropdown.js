$(function(){
    // hide things 
    $(".toggle").hide();

    // prepend non-option
    $("#event").prepend("<option value='' selected='selected'>Choose From Below</option>").val('');

    // bind events on event
    $("#event").on('change keypress', function(){

        // clear the organization select
        $("#organization").children().remove();

        // load organizations
        $.getJSON(
            "/organization_ajax_handler",
            {
                event_name: $(this).val(), ajax: 'true'
            },
            function(data){
                var options = '';
                var temp = $('<select></select>');
     
                $.each(data, function(key, val) {
                    $('<option></option>').attr('value', key).text(val).appendTo(temp);
                });

                $("#organization").children().remove();
                temp.children().detach().appendTo($("#organization"));
                $("#organization").prepend(
                    "<option value='Admin' selected='selected'>Admin</option>"
                );
                
                $(".toggle").show();
            }
        );
    });
});
