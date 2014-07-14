$(function(){

    prev_selected_event = '';  /* global prev_selected_event */
    active_xhr = null;  /* global active_xhr */

    var $eventSelect = $('#event');
    var $organizationSelect = $('#organization');
    var $existingOrganizationSelect = $('#existing-organization');

    // show existingOrganizationSelect if "Other" org is selected
    $organizationSelect.on('change keyup', function() {
        if ($(this).val() === 'Other') {
            $('.existing-organization-toggle').show();
        } else {
            $('.existing-organization-toggle').hide();
        }
    });

    // prepend non-option
    $eventSelect
        .prepend("<option value='' selected='selected'>Choose From Below</option>")
        .val('');

    // bind to load orgs on event change
    var selectEvent = function(selectedEventName) {

        $('.existing-organization-toggle').hide();

        if (selectedEventName !== '' && selectedEventName != prev_selected_event) {
            // clear the organization selects
            $organizationSelect.children().remove();
            $existingOrganizationSelect.children().remove();

            // abort any previous call
            if (active_xhr) active_xhr.abort();

            // load organizations
            $('.loading').show();
            active_xhr = $.getJSON(
                "/organization_ajax_handler",
                {
                    event_name: selectedEventName,
                    ajax: 'true'
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
                    $(".loading").hide();
                }
            );
        } else if (selectedEventName === '') {
            // hide the input rows again
            $(".toggle").hide();
        }

        // save choice
        prev_selected_event = selectedEventName;
    };


    // bind select dropdown
    $eventSelect.on('change keyup', function() {
        var selectedEventName = $(this).val();
        selectEvent(selectedEventName);
    });

    
    // load initially specified event if any
    var initialEventName = $(document).data('initialEventName');
    if (initialEventName) {
        $eventSelect.val(initialEventName);
        selectEvent(initialEventName);
    }
});
