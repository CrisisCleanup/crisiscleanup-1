$(function() {
    
pollForCSVDownload = function (filename, afterDownload) {
  var downloadUrl = '/export_bulk_download?filename=' + filename;
  $.ajax({
    url: downloadUrl, 
    complete: function(xhr) {
      if (xhr.status == 202) {
        // try again shortly
        setTimeout(
          function () {
            pollForCSVDownload(filename, afterDownload);
          },
          2000
        );
      } else if (xhr.status == 200) {
        // success: redirect and restore elements (after race avoidance wait)
        setTimeout(
          function() {
            window.location = downloadUrl;
            afterDownload();
          },
          1000
        );
      }
    }
  });
};

});
