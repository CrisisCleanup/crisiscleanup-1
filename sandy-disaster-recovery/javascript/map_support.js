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
        // success: redirect (after race avoidance)
        setTimeout(
          function() {
            window.location = downloadUrl;
            $('#filtered-export-btn').prop('disabled', false)
              .attr('value', 'Download Spreadsheet (CSV)');
          },
          1000
        );
      }
    }
  });
};


// bind filtered export button click
$('#filtered-export-btn').click(function () {

  // disable button and rewrite button
  $('#filtered-export-btn').prop('disabled', true).attr('value', 'Processing... please wait');

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
