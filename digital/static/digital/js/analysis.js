$(document).ready(function(){


    // UPLOAD CSV PRINTABILITY PREDICTION################################################
        $("#form_printability_analysis").submit(function(event){
            event.preventDefault();
            var $form = $(this);
            var data = new FormData(this);
            $.ajax({
                url: '/digital/analysis/bulk-part-upload/',
                data: data,
                cache: false,
                contentType: false,
                processData: false,
                method: 'POST',
                type: 'POST', // For jQuery < 1.9
                beforeSend:function(XMLHttpRequest, settings){
                },
                success: function(data){
                    console.log(data);
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    console.log("Status: " + textStatus); console.log("Error: " + errorThrown);
                },
                complete:function(jqXHR, textStatus){
                },
            });
        });

    // END UPLOAD CSV PRINTABILITY PREDICTION################################################

});
