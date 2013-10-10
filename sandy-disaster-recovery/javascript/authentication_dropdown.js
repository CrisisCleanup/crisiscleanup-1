$(function(){

    prev_selected_event = '';  // global

    // hide input rows
    $(".toggle").hide();

    // prepend non-option
    $("#event").prepend("<option value='' selected='selected'>Choose From Below</option>").val('');

    // bind events on event
    $("#event").on('change keyup', function(){
        var selected_event = $(this).val();

        if (selected_event !== '' && selected_event != prev_selected_event) {
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
        } else if (selected_event === '') {
            // hide the input rows again
            $(".toggle").hide();
        }

        // save choice
        prev_selected_event = selected_event;
    });
});
