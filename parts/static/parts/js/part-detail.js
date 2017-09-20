$(document).ready(function(){


    var STATUS_COLOR = {
        1: "default",
        2: "primary",
        3: "success",
        4: "info",
        5: "warning",
        6: "danger",
        };

    // inline mode for the editables
    $.fn.editable.defaults.mode = 'inline';
    $('.notes-editable').editable({
        inputclass:'part-notes',
        success: function(response, newValue) {
            // location.reload();
        console.log(response.result); //msg will be shown in editable form
        },
    });

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

        //  ajax for 3mf deletion
        function delete_3mf(id_3mf){
                console.log(id_3mf)
                $.ajax({
                    url: '/parts/ajax/delete-3mf/',
                    data:{
                        'id_3mf':id_3mf,
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

    //  ajax for cad2d deletion
    function delete_cad2d(id_cad2d){
            console.log(id_cad2d)
            $.ajax({
                url: '/parts/ajax/delete-cad2d/',
                data:{
                    'id_cad2d':id_cad2d,
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

    //  ajax for stl deletion
    function delete_stl(id_stl){
            console.log(id_stl)
            $.ajax({
                url: '/parts/ajax/delete-stl/',
                data:{
                    'id_stl':id_stl,
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

    //  ajax for cad deletion
    function delete_cad(id_cad){
            console.log(id_cad)
            $.ajax({
                url: '/parts/ajax/delete-cad/',
                data:{
                    'id_cad':id_cad,
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
    //  ajax for bulk file deletion
    function delete_bulk(id_bulk){
            console.log(id_bulk)
            $.ajax({
                url: '/parts/ajax/delete-bulk/',
                data:{
                    'id_bulk':id_bulk,
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
    //  ajax for part deletion
    function delete_part(id_part){
            console.log(id_part)
            $.ajax({
                url: '/parts/ajax/delete-part/',
                data:{
                    'id_part':id_part,
                },
                dataType:'json',
                success:function(data){
                    if (data.result){
                        console.log(data.result)
                        window.location.replace("http://192.168.0.20:7000/parts");
                    }
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    alert("Status: " + textStatus); alert("Error: " + errorThrown);
                }

        });
    }


    function change_status_eng(id_part, id_status){
            console.log("id part is: " + id_part);
            console.log("id status is: " + id_status);
            $.ajax({
                url: '/parts/ajax/change-status-eng/',
                data:{
                    'id_part':id_part,
                    'id_status':id_status,
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

// click listener on delete image buttons
    $(".delete-image").click(function(){
        delete_image($(this).val());
    });
// click listener on delete 3mf buttons
    $(".delete-3mf").click(function(){
        delete_3mf($(this).val());
    });
// click listener on delete cad2d buttons
    $(".delete-cad2d").click(function(){
        delete_cad2d($(this).val());
    });
// click listener on delete stl buttons
    $(".delete-stl").click(function(){
        delete_stl($(this).val());
    });
// click listener on delete stl buttons
    $(".delete-cad").click(function(){
        delete_cad($(this).val());
    });
// click listener on delete part buttons
    $(".delete-part").click(function(){
        delete_part($(this).val());
    });
// click listener on delete bulk buttons
    $(".delete-bulk").click(function(){
        delete_bulk($(this).val());
    });


// click listener on delete image buttons
    $(".change-status-eng").click(function(e){
        var id = $(this).attr('id');
        var id_part = id.split("-")[0];
        console.log("ID PART IS: " + id_part);
        var id_status = id.split("-")[1];
        console.log("ID STATUS IS: " + id_status);
        change_status_eng(id_part, id_status);
        e.stopPropagation();
    });

// color to the status labels
for (var key in STATUS_COLOR){
    console.log
    $(".label-" + key).addClass("label-" + STATUS_COLOR[key]);
};

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
            if ( id=="cad" ){
                var f=$(this).val().split('.').pop().toLowerCase();
                if($.inArray(f, ['sldasm','sldprt']) == -1) {
                    alert('invalid extension! need a .sldasm or .sldprt for the fields "CAD"');
                    submitme = false;
                }
            }
            if ( id=="cad2d" ){
                var f=$(this).val().split('.').pop().toLowerCase();
                if($.inArray(f, ['slddrw','pdf']) == -1) {
                    alert('invalid extension! need a .slddrw or .pdf for the fields "2D Drawing"');
                    submitme = false;
                }
            }
            if ( id=="stl" ){
                var f=$(this).val().split('.').pop().toLowerCase();
                if($.inArray(f, ['stl']) == -1) {
                    alert('invalid extension! need a .stl "STL"');
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
        maxFilesize: 5, // MB
        createImageThumbnails: false,
        paramName: "image",
        clickable: false,
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

    Dropzone.options.bulkDropzone = {
        paramName: "file", // The name that will be used to transfer the file
        maxFilesize: 5, // MB
        createImageThumbnails: false,
        paramName: "bulk",
        clickable: false,
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
            this.on("sending", function(file, xhr, formData) {
               var id_part = $('#bulk-dropzone #id_part').val();
               var notes = $('#bulk-dropzone #notes').val();
               var bulk_type = $('#bulk-dropzone #bulk_type').val();
               console.log("FORMDATA:"+formData);
               console.log("id part:" + id_part);
               console.log("notes:" + notes);
               formData.append("part_id", id_part); // Append all the additional input data of your form here!
               formData.append("notes", notes);
               formData.append("bulk_type", bulk_type);
               console.log("ADDDED");
            });
        }
    };


    ///////////////////////////////////////////////////LIVE Z-OFFSET HANDLING////////////////////////////////////////////////

    // live qtty handling: plus button
        $('.z-offset-right-plus').click(function(e){
           // Stop acting like a button
           e.preventDefault();
           var id_printer = $(this).attr("id").split("-")[1];
           var z_offset = parseFloat($('#z-offset-'+id_printer).val());
           console.log(id_printer);

        //    check if is negative, not integer or not number
           if (isNaN(z_offset) || z_offset<0 || !$.isNumeric(z_offset)){
               z_offset = 0;
               console.log("weird")
           }
               $('#z-offset-'+id_printer).val((z_offset + 0.05).toFixed(2));
               console.log("value is: " + $('#z-offset-'+id_printer).val());

       });


     // live qtty handling: minus button
        $('.z-offset-left-minus').click(function(e){
            console.log("clicked minus");
           // Stop acting like a button
           e.preventDefault();
           var id_printer = $(this).attr("id").split("-")[1];
           var z_offset = parseFloat($('#z-offset-'+id_printer).val());
           if (isNaN(z_offset) || z_offset<0 || !$.isNumeric(z_offset)){
               z_offset = 0;
           }
           // If is not undefined
               // Increment
               if(z_offset>0){
                   $('#z-offset-'+id_printer).val((z_offset - 0.05).toFixed(2));
                   console.log("value is: " + $('#z-offset-'+id_printer).val());
               }

       });

    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

});
