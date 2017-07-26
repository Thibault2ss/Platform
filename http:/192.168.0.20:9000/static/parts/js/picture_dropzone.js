// $(document).ready(function(){
//
//     var $myDropzone=$("#picture-dropzone").dropzone({
//         url: "/file-upload" ,
//         paramName: "file", // The name that will be used to transfer the file
//         maxFilesize: 2, // MB
//         previewsContainer: "#previews", // Define the container to display the previews
//         clickable: "#clickable",
//         accept: function(file, done) {
//             if (file.name == "justinbieber.jpg") {
//                 done("Naha, you don't.");
//             }
//             else { done(); }
//         }
//     });
// });
console.log("OUI MAN CA CEST FAIT");
$(document).ready(function(){
    console.log("FAIIT CAAAA");
    // var previewNode = document.querySelector("#template");
    // previewNode.id = "";
    // var previewTemplate = previewNode.parentNode.innerHTML;
    // previewNode.parentNode.removeChild(previewNode);
    console.log("FAIIT CAAAA AAAUSSSSI");

    var myDropzone = new Dropzone(document.body, { // Make the whole body a dropzone
      url: "/parts/part-detail/upload-image/", // Set the url
      thumbnailWidth: 80,
      thumbnailHeight: 80,
      parallelUploads: 20,
      // previewTemplate: previewTemplate,
      autoQueue: false, // Make sure the files aren't queued until manually added
      previewsContainer: "#previews", // Define the container to display the previews
      clickable: "#clickable" // Define the element that should be used as click trigger to select files.
    });

    myDropzone.on("addedfile", function(file) {
      // Hookup the start button
      document.querySelector(".start").onclick = function() { myDropzone.enqueueFile(file); };
    });

    // Update the total progress bar
    myDropzone.on("totaluploadprogress", function(progress) {
      document.querySelector(" .progress-bar").style.width = progress + "%";
    });

    myDropzone.on("sending", function(file) {
      // Show the total progress bar when upload starts
    //   document.querySelector("#total-progress").style.opacity = "1";
      // And disable the start button
      document.querySelector(".start").setAttribute("disabled", "disabled");
    });

    // Hide the total progress bar when nothing's uploading anymore
    myDropzone.on("queuecomplete", function(progress) {
      document.querySelector("#total-progress").style.opacity = "0";
    });

    // Setup the buttons for all transfers
    // The "add files" button doesn't need to be setup because the config
    // `clickable` has already been specified.
    document.querySelector(".start").onclick = function() {
      myDropzone.enqueueFiles(myDropzone.getFilesWithStatus(Dropzone.ADDED));
    };
    document.querySelector(".cancel").onclick = function() {
      myDropzone.removeAllFiles(true);
    };

})
