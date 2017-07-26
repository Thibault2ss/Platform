$(document).ready(function(){
// ajax for image deletion
    function delete_image(image_id){
            console.log(image_id)
            $.ajax({
                url: '/parts/ajax/delete-image/',
                data:{
                    'image_id':image_id,
                },
                dataType:'json',
                success:function(data){
                    if (data.result){
                        location.reload();
                        console.log(data.result)
                    }
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    alert("Status: " + textStatus); alert("Error: " + errorThrown);
                }

        });
    }

        $(".delete-image").click(function(){
            delete_image($(this).val());
        });

// file extension validation

    $("form").submit(function() {
        var submitme = true;
        var queryString = $(this).serialize();
        $(this).find("input[type=file]").each(function() { // loop through each file input
            id = $(this).attr('id'); // get the name of its set
            if (id=="amf"){
                var f=$(this).val().split('.').pop().toLowerCase();
                if($.inArray(f, ['amf']) == -1) {
                    alert('invalid extension! need a .amf for the field "AMF"');
                    submitme = false;
                }
            }
            if ( id=="config" || id=="configb" ){
                var f=$(this).val().split('.').pop().toLowerCase();
                if($.inArray(f, ['ini']) == -1) {
                    alert('invalid extension! need a .ini for the fields "Config" and "Config Bundle"');
                    submitme = false;
                }
            }
            if ( id=="image" ){
                var f=$(this).val().split('.').pop().toLowerCase();
                if($.inArray(f, ['png','jpg']) == -1) {
                    alert('invalid extension! need a .png or .jpg for the fields "Image"');
                    submitme = false;
                }
            }
            if ( id=="gcode" ){
                var f=$(this).val().split('.').pop().toLowerCase();
                if($.inArray(f, ['gcode']) == -1) {
                    alert('invalid extension! need a .gcode for the fields "GCode" ');
                    submitme = false;
                }
            }

        });
        return submitme; // cancel the form submit
    });

// Image dropzone options

    Dropzone.options.imageDropzone = {
    paramName: "file", // The name that will be used to transfer the file
    maxFilesize: 2, // MB
    createImageThumbnails: false,
    paramName: "image",
    clickable: true,
    acceptedFiles: "image/jpeg,image/png",
    accept: function(file, done) {
        if (file.name == "justinbieber.jpg") {
          done("Naha, you don't.");
        }
        else { done(); }
    },
    init: function () {
        // Set up any event handlers
        this.on('complete', function () {
            this.removeAllFiles(true);
            location.reload();
        });

    }

    };

});
