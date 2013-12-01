$(function() {

$searchForm = $('form#search-form');
$exportForm = $('form#export-form');


/* Add sort ordering */

$('th[data-field]').click(function(event) {
    // flip or set the sort order
    var orderField = $(this).attr('data-field');
    if (orderField) {
        var currentOrder = $('input[name=order]').val();
        var newOrder = orderField != currentOrder ? orderField : '-' + orderField;
        $('input[name=order]').val(newOrder).parent('form').submit();
    }
});


/* Export Results */

$exportAllResultsButton = $('#export-all-results-btn');

$exportAllResultsButton.click(function(event) {
    event.preventDefault();
    var laddaManager = Ladda.create(this);
    laddaManager.start();
    $exportAllResultsButton.attr('disabled', true);
    $.ajax({
        url: '/admin-export-work-orders-by-query',
        type: 'POST',
        data: $exportForm.serialize(),
    }).done(function(data) {
        pollForCSVDownload(
            data.filename,
            function() {
                laddaManager.stop();
                $exportAllResultsButton.attr('disabled', false);
            }
        );
    });
});


/* reload page if event/incident select changed */

$('select[name=event]').change(function() {
    $searchForm.submit();
    $searchForm.find('input,select,button').attr('disabled', true);
});


/* Bulk Actions */

$selectAllCheckbox = $('input[type=checkbox].checkbox-all');
$siteCheckboxes = $('input[type=checkbox].checkbox-site');
$bulkActionButtons = $('button.bulk-action-btn');
$bulkActionExportButton = $bulkActionButtons.filter('[data-action=export]');
$bulkActionOrgSelect = $('select#select-bulk-org');
$bulkActionStatusSelect = $('select#select-bulk-status');

var invokeBulkAction = function(action) {
    // construct list of checked site ids
    var siteIds = $siteCheckboxes.filter(':checked').map(function() {
        return $(this).attr('data-site-id');
    }).get().join(',');
    var org_key = $bulkActionOrgSelect.val();
    var status = $bulkActionStatusSelect.val();

    if (action == 'export') {
        var laddaManager = Ladda.create($bulkActionExportButton[0]);
        laddaManager.start();
        $bulkActionExportButton.attr('disabled', true);
        $.ajax({
            url: '/admin-export-work-orders-by-id',
            type: 'POST',
            data: {id_list: siteIds}
        }).done(function(data) {
            pollForCSVDownload(
                data.filename,
                function() {
                    laddaManager.stop();
                    enableBulkActionButtons();
                }
            );
        });

    } else {

        // post the action and refresh the page (to maintain search)
        $('body').toggleClass('wait-cursor');
        $.ajax({
            url: '/admin-work-orders-bulk-action',
            type: 'POST',
            data: {
                action: action,
                ids: siteIds,
                org: org_key,
                status: status
            }
        }).success(function () {
            location.reload();
        });
    }
};

// enable bulk action buttons as appropriate
var enableBulkActionButtons = function() {
    var anyCheckboxesChecked = $siteCheckboxes.filter(':checked').length !== 0;
    var orgIsSelected = Boolean($bulkActionOrgSelect.val());
    var statusIsSelected = Boolean($bulkActionStatusSelect.val());

    $bulkActionButtons.each(function(i, btn) {
        var $btn = $(btn);
        var enable = (
            anyCheckboxesChecked && (
                orgIsSelected || !$btn.hasClass('requires-org')
            ) && (
                statusIsSelected || !$btn.hasClass('requires-status')
            )
        );
        $btn.attr('disabled', !enable);
    });
};

// bind bulk action button clicks
$bulkActionButtons.click(function(event) {
    $bulkActionButtons.attr('disabled', true);
    invokeBulkAction($(this).attr('data-action'));
});

// update button enablements
$siteCheckboxes.change(enableBulkActionButtons);
$bulkActionOrgSelect.change(enableBulkActionButtons);
$bulkActionStatusSelect.change(enableBulkActionButtons);

// check <th> checkbox to select & unselect all
$selectAllCheckbox.click(function() {
    $siteCheckboxes.prop('checked', $selectAllCheckbox.prop('checked'));
    enableBulkActionButtons();
});

// checking all checkboxes checks the <th>
$siteCheckboxes.click(function () {
    $selectAllCheckbox.prop(
        'checked',
        $siteCheckboxes.not(':checked').length === 0
    );
    enableBulkActionButtons();
});


// pass clicks of checkbox-containing td to the checkbox
$siteCheckboxes.closest('td').click(function() {
    $(this).find('input[type=checkbox]').trigger('click');
});

$siteCheckboxes.click(function(event) {
    event.stopPropagation();
});

});
