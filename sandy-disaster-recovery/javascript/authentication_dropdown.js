$(function(){

    prev_selected_event = '';  // global

    $organizationSelect = $('#organization');
    $existingOrganizationSelect = $('#existing-organization');

    // show existingOrganizationSelect if "Other" org is selected
    $organizationSelect.on('change keyup', function() {
        if ($(this).val() == 'Other') {
            $('.existing-organization-toggle').show();
        } else {
            $('.existing-organization-toggle').hide();
        }
    });

    // prepend non-option
    $("#event").prepend("<option value='' selected='selected'>Choose From Below</option>").val('');

    // bind events on event
    $("#event").on('change keyup', function(){
        var selected_event = $(this).val();

        $('.existing-organization-toggle').hide();

        if (selected_event !== '' && selected_event != prev_selected_event) {
            // clear the organization selects
            $organizationSelect.children().remove();
            $existingOrganizationSelect.children().remove();

            // load organizations
            $.getJSON(
                "/organization_ajax_handler",
                {
                    event_name: $(this).val(), ajax: 'true'
                },
                function(data){
                    // attach orgs to organization select

                    $organizationSelect.children().remove();
                    $existingOrganizationSelect.children().remove();

                    $.each(data.event_orgs, function(key, val) {
                        $('<option></option>').attr('value', val).text(val)
                            .appendTo($organizationSelect);
                    });
                    $.each(data.other_orgs, function(key, val) {
                        $('<option></option>').attr('value', val).text(val)
                            .appendTo($existingOrganizationSelect);
                    });

                    $organizationSelect.prepend(
                        "<option value='' selected='selected'>--Select--</option>"
                    );
                    $organizationSelect.append(
                        "<option value='Other'>Other (Existing)</option>"
                    );

                    if (data.other_orgs.length === 0) {
                        $existingOrganizationSelect.append(
                            "<option value='' selected>(None available)</option>"
                        );
                    }

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
