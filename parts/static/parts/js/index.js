$(document).ready(function(){

///////////////////////////////////////////////AJAX TO ADD A PART//////////////////////////////////////////
    $("#add_part").click(function(){
        console.log("add part is clicked");
        var $part_number = $("#part-number");
        $.ajax({
            url: '/parts/ajax/new-part-number/',
            data:{

            },
            dataType:'json',
            success:function(data){
                if (data.part_number){
                    console.log(data.part_number)
                    $part_number.val(data.part_number);
                };
                if (data.error){
                    alert(data.error)
                };
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                alert("Status: " + textStatus); alert("Error: " + errorThrown);
            }

        });
    });
////////////////////////////////////////////////////////////////////////////////////////////////////////////////
});
