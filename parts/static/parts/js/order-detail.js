$(document).ready(function(){

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
               var id_order = $('#bulk-dropzone #id_order').val();
               var notes = $('#bulk-dropzone #notes').val();
               var bulk_type = $('#bulk-dropzone #bulk_type').val();
               console.log("FORMDATA:"+formData);
               console.log("id order:" + id_order);
               console.log("notes:" + notes);
               formData.append("order_id", id_order); // Append all the additional input data of your form here!
               formData.append("notes", notes);
               formData.append("bulk_type", bulk_type);
               console.log("ADDDED");
            });
        }
    };


    // click listener on delete bulk buttons
    $(".delete-bulk").click(function(){
        delete_bulk($(this).val());
    });

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

    ////////////////////////////////////////////////////////FILTERS///////////////////////////////////////////////////////////////
    $(document).on('keyup','#filter-parts-to-order',function () {
        console.log("search");
        var rex = new RegExp($(this).val(), 'i');
        $(".searchable-parts-to-order tr").hide();
        $(".searchable-parts-to-order tr").filter(function () {
            return rex.test($(this).text());
        }).show();
    });

    //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
});
