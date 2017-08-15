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
        inputclass:'order-notes',
        success: function(response, newValue) {
            // location.reload();
        console.log(response.result); //msg will be shown in editable form
        },
    });

//////////////////////////////////////////////////////////////////DATE LABEL COLORING////////////////////////////////////////////
    $('.due_date').each(function(){
        var $this = $(this);
        if (/^In/.test($this.text())){
            $this.css( "background-color", "#51A351" );
        } else if (/^Today/.test($this.text())) {
            $this.css( "background-color", "#F89406" );
        } else if (/^Tomorrow/.test($this.text())) {
            $this.css( "background-color", "#F89406" );
        } else if (/ago!$/.test($this.text())) {
            $this.css( "background-color", "#f44242" );
        }
    });

    $('.completion_date').each(function(){
        var $this = $(this);
        if (/^In/.test($this.text())){
            $this.css( "background-color", "#f44242" );
        } else if (/^Today/.test($this.text())) {
            $this.css( "background-color", "#51A351" );
        } else if (/^Tomorrow/.test($this.text())) {
            $this.css( "background-color", "#f44242" );
        } else if (/ago!$/.test($this.text())) {
            $this.css( "background-color", "#F89406" );
        }
    });
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////ERROR FOR CUSTOM SCROLLBAR//////////////////////////////////////////////

/////////////////////////////////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////UPDATE ORDER DATA//////////////////////////////
    $("#update_order").click(function(){
        $("input[name=name]").val($("#order-name").text());
        var myDate = new Date(Date.parse($("#order-due-date").text()));
        var dd = pad(myDate.getDate(),2);
        var mm = pad(myDate.getMonth() + 1,2);
        var yyyy = myDate.getFullYear();
        $("input[name=date]").val(dd + "-" + mm + "-" + yyyy);
        $("input[name=quote-number]").val($("#order-quote-number").text());
        $("input[name=po-number]").val($("#order-po-number").text());
        $("#assign-to option[value=" + $("#order-assigned-to").text() + "]").attr('selected', 'selected');
        $("#type option[value=" + $("#order-type").text() + "]").attr('selected', 'selected');
        console.log($("#order-notes").text());
        $("#notes").val($("#order-notes").text());
    });
    // function to pad zeros in front of numeric
    function pad(num, size) {
        var s = num+"";
        while (s.length < size) s = "0" + s;
        return s;
    }

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////SEARCHES FILTERS//////////////////////////////////////////////////

    // for rfq
    $(document).on('keyup','#filter-rfq',function () {
        var rex = new RegExp($(this).val(), 'i');
        var rex_user = new RegExp($(".nav-pills-users .active .filter-user-id").attr("id"), 'i');
        $(".searchable-rfq .list-group-item").hide();
        $(".searchable-rfq .list-group-item").filter(function () {
            return rex.test($(this).text()) && rex_user.test($(this).text());
        }).show();
    });
    // for prod
    $(document).on('keyup','#filter-prod',function () {
        var rex = new RegExp($(this).val(), 'i');
        var rex_user = new RegExp($(".nav-pills-users .active .filter-user-id").attr("id"), 'i');
        $(".searchable-prod .list-group-item").hide();
        $(".searchable-prod .list-group-item").filter(function () {
            return rex.test($(this).text()) && rex_user.test($(this).text());
        }).show();
    });
    // for indus
    $(document).on('keyup','#filter-indus',function () {
        var rex = new RegExp($(this).val(), 'i');
        var rex_user = new RegExp($(".nav-pills-users .active .filter-user-id").attr("id"), 'i');
        $(".searchable-indus .list-group-item").hide();
        $(".searchable-indus .list-group-item").filter(function () {
            return rex.test($(this).text()) && rex_user.test($(this).text());
        }).show();
    });

    // for persons filters
    $(".filter-user-id").click(function () {
        console.log("filter user id");
        var rex_user = new RegExp($(this).attr("id"), 'i');
        var rex_rfq = new RegExp($("#filter-rfq").val(), 'i');
        var rex_prod = new RegExp($("#filter-prod").val(), 'i');
        var rex_indus = new RegExp($("#filter-indus").val(), 'i');

        $(".searchable-rfq .list-group-item").hide();
        $(".searchable-rfq .list-group-item").filter(function () {
            return rex_user.test($(this).text()) && rex_rfq.test($(this).text());
        }).show();

        $(".searchable-prod .list-group-item").hide();
        $(".searchable-prod .list-group-item").filter(function () {
            return rex_user.test($(this).text()) && rex_prod.test($(this).text());
        }).show();

        $(".searchable-indus .list-group-item").hide();
        $(".searchable-indus .list-group-item").filter(function () {
            return rex_user.test($(this).text()) && rex_indus.test($(this).text());
        }).show();

    });

/////////////////////////////////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////ADD QUOTE OR PO WHEN CHANGE//////////////////////////////////////////////////

    $('#type').change(function(){
        var $this = $(this);
        console.log($this.val());
        if ($this.val() == "quote"){
            console.log("entered quote");
            $("#form-group-quote").show();
            $("#form-group-prod").hide();
        } else if ($this.val() == "prod" || $this.val() == "sample"){
            $("#form-group-prod").show();
            $("#form-group-quote").hide();
        } else {
            $("#form-group-prod").hide();
            $("#form-group-quote").hide();
        }
    });
/////////////////////////////////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////GENERATE QUOTE OR PO number//////////////////////////////////////////////////

        $('#generate-po-nb').click(function(){
            var id_client= $("#client").val();
            $.ajax({
                url: '/parts/orders/ajax-generate-po-nb/',
                data:{
                    'id_client':id_client,
                },
                dataType:'json',
                success:function(data){
                    if (data.result){
                        console.log(data.result)
                        $("#po-number").val(data.result);
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

        $('#generate-quote-nb').click(function(){
            var id_client= $("#client").val();
            $.ajax({
                url: '/parts/orders/ajax-generate-quote-nb/',
                data:{
                    'id_client':id_client,
                },
                dataType:'json',
                success:function(data){
                    if (data.result){
                        console.log(data.result)
                        $("#quote-number").val(data.result);
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
/////////////////////////////////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////SAVINGS QUANTITIES//////////////////////////////////////////////////
// live qtty handling: plus button
    $('.quantity-right-plus').click(function(e){
       // Stop acting like a button
       e.preventDefault();
       var id_part = $(this).attr("id").split("-")[1];
       var quantity = parseInt($('#quantity-'+id_part).val());
    //    check if is negative, not integer or not number
       if (isNaN(quantity) || quantity<0 || !(Math.floor(quantity) == quantity && $.isNumeric(quantity))){
           quantity = 0;
       }
           $('#quantity-'+id_part).val(quantity + 1);
           $("#save-" + id_part).show();
   });


 // live qtty handling: minus button
    $('.quantity-left-minus').click(function(e){
        console.log("clicked minus");
       // Stop acting like a button
       e.preventDefault();
       var id_part = $(this).attr("id").split("-")[1];
       var quantity = parseInt($('#quantity-'+id_part).val());
       if (isNaN(quantity) || quantity<0 || !(Math.floor(quantity) == quantity && $.isNumeric(quantity))){
           quantity = 0;
       }
       // If is not undefined
           // Increment
           if(quantity>0){
               $('#quantity-'+id_part).val(quantity - 1);
           }
           $("#save-" + id_part).show();
   });

   $('.input-quantity').keyup(function(){
       console.log("CHANGED");
       var id_part = $(this).attr("id").split("-")[1];
       $("#save-" + id_part).show();
   });

   $('.save-qtty').click(function(){
       console.log("SAVED CLICKED");
       var id_part = $(this).attr("id").split("-")[1];
       var quantity = $('#quantity-'+id_part).val();
       var id_order = $('#order-id').val();
       ajax_quantity_save(id_order, id_part, quantity);
       if (parseInt(quantity) == 0){
           $(this).closest(".list-group-item").remove();
       };

   });

   function ajax_quantity_save(id_order, id_part, quantity){
       if ($.isNumeric(id_order) && $.isNumeric(id_part) && $.isNumeric(quantity) && Math.floor(quantity) == quantity && quantity>=0){
           $.ajax({
               url: '/parts/orders/ajax-save-quantity/',
               data:{
                   'id_order':id_order,
                   'id_part':id_part,
                   'quantity':quantity,
               },
               dataType:'json',
               success:function(data){
                   if (data.result){
                       console.log(data.result)
                       $("#save-" + id_part).hide();
                   };
                   if (data.error){
                       alert(data.error)
                   };
               },
               error: function(XMLHttpRequest, textStatus, errorThrown) {
                   alert("Status: " + textStatus); alert("Error: " + errorThrown);
               }
           });
       } else {
           alert("Did not send Quantity Change Request, because quantity is probably wrong format")
       };
   };
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


/////////////////////////////////////////////////////////////////Order Deletion////////////////////////////////////////////////////////////

    // ajax for image deletion
    function delete_order(id_order){
            console.log(id_order)
            $.ajax({
                url: '/parts/ajax/delete-order/',
                data:{
                    'id_order':id_order,
                },
                dataType:'json',
                success:function(data){
                    if (data.result){
                        location.reload();
                        console.log(data.result)
                    }
                    if (data.error){
                        alert(data.error)
                    }
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    alert("Status: " + textStatus); alert("Error: " + errorThrown);
                }

        });
    }

    // click listener on delete stl buttons
    $(".delete-order").click(function(){
        console.log("YES");
        delete_order($(this).val());
    });

    // change status  button
        $(".change-status-order").click(function(e){
            var id = $(this).attr('id');
            var id_order = id.split("-")[0];
            console.log("ID ORDER IS: " + id_order);
            var id_status = id.split("-")[1];
            console.log("ID STATUS IS: " + id_status);
            change_status_order(id_order, id_status);
            e.stopPropagation();
        });

    function change_status_order(id_order, id_status){
            console.log("id order is: " + id_order);
            console.log("id status is: " + id_status);
            $.ajax({
                url: '/parts/ajax/change-status-order/',
                data:{
                    'id_order':id_order,
                    'id_status':id_status,
                },
                dataType:'json',
                success:function(data){
                    if (data.result){
                        location.reload();
                        console.log(data.result);
                    }
                    if (data.error){
                        alert(data.result);
                    }
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    alert("Status: " + textStatus); alert("Error: " + errorThrown);
                }

        });
    }
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////DATE PICKER SETUP/////////////////////////////////////////////////////////////////
// datetime fields
var date_input=$('input[id="date"]'); //our date input has the name "date"
var container=$('.bootstrap-iso form').length>0 ? $('.bootstrap-iso form').parent() : "body";
var options={
    format: 'dd-mm-yyyy',
    container: container,
    todayHighlight: true,
    autoclose: true,
};
date_input.datepicker(options);

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
});
///////////////////////////////////////////////////////END OF DOCUMENT READY//////////////////////////////////////////////////////////////////////////


///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// outside of document ready, because used in document
var saved_parts = {};
function toggle_qtty(id_part) {
    if (document.getElementById("cb-"+id_part).checked){
                $("#qtty-"+id_part).prop("disabled", true);
                $("#qtty-"+id_part).val(null);
                delete saved_parts[id_part];
                update_sumup();
            } else {
                $("#qtty-"+id_part).prop("disabled", false);
                saved_parts[id_part] = 0;
                // we set timeout otherwise focus conflict
                setTimeout(function () {
                    $("#qtty-"+id_part).focus();
                }, 1);
            }
    return true;
}

function save_qtty(id_part) {
    saved_parts[id_part] = $("#qtty-"+id_part).val();
    update_sumup();
    console.log(saved_parts);
}

function update_sumup(){
    var sumup = "" ;
    for (key in saved_parts){
        sumup += "id " + key + ": " + saved_parts[key] + ", "
    };
    $("#sumup").text(sumup);
}

function clear_all() {
    $("input[name=parts]").each(function(){
        console.log("A");
        $(this).prop("checked", false);
        });
    $("input[type=number]").each(function(){
        $(this).val(null);
        $(this).prop("disabled", true);
        console.log("B");
        });
    saved_parts={};
    update_sumup();
    }
