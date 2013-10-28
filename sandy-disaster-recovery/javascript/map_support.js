$(function() {

var pollForCSVDownload = function (filename) {
  var downloadUrl = '/export_bulk_download?filename=' + filename;
  $.ajax({
    url: downloadUrl, 
    complete: function(xhr) {
      if (xhr.status == 202) {
        // try again shortly
        setTimeout(
          function () {
            pollForCSVDownload(filename);
          },
          2000
        );
      } else if (xhr.status == 200) {
        // success: redirect and restore elements (after race avoidance wait)
        setTimeout(
          function() {
            window.location = downloadUrl;
            $('#filtered-export-btn').prop('disabled', false)
              .attr('value', 'Download Spreadsheet (CSV)');
            $('#filtered-export-wait-message').hide();
          },
          1000
        );
      }
    }
  });
};


// bind filtered export button click
$('#filtered-export-btn').click(function () {

  // disable & re-label button and show message
  $('#filtered-export-btn').prop('disabled', true).attr('value', 'Processing... please wait');
  $('#filtered-export-wait-message').show();

  // request export and begin polling
  $.ajax({
      url: '/export_bulk',
      type: 'POST',
      data: {
        id_list: $('.id_list').val()
      }
    }).done(function(data) {
      pollForCSVDownload(data.filename);
    });

  // prevent default
  return false;
});
  
});
