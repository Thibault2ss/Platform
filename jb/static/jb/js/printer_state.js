// printer_state handler: fetch and update printer state: printing or not printing
// writen by Thibault2ss : thibault.de-saint-sernin@sp3d.co

//!!!!!!!!!!!!!!!!!!!!!!!IMPORTANT: DON'T FORGET TO INCLUDE THE SOCKETIO SCRIPT IN THE TEMPLATE PAGE !!!!!!!!!!!!!!!!!!!

$(document).ready(function(){

	var $printer_dropdown=$(".printer_dropdown");
    var $printer_statusbar=$(".printer_statusbar");
    var socket=[];
    var _id_3mf = 0;
    var _direct_print = false;

    var STATUS_COLOR = {
        1: "default",
        2: "primary",
        3: "success",
        4: "info",
        5: "warning",
        6: "danger",
        };

//////////////////////////////////////////////////////////////REFRESH PRINTERS LABEL///////////////////////////////////////////////
    function refreshPrinterLabel(label, id){
        try{
            if (typeof socket[id] == 'undefined'){
                socket[id]=io.connect("http://" + myPrinters[id]["ip"]+ ":5000/test");
                socket[id].on('connect_error', function() {
                    socket[id].disconnect();
                    label.removeClass("label-success").removeClass("label-danger").removeClass("label-warning").text(myPrinters[id]["name"].toUpperCase() + " disconnected");
                    console.log("CLASS REMOVED");
                    console.log('Failed to connect to server');
                });

                socket[id].on('connected', function(msg) {
                    console.log("CLASS ADDED");
                    console.log(msg.data + " on printer " + myPrinters[id]["name"] + " !!");

                });

                socket[id].on('printer state', function(msg) {
                    // console.log('Printer State: ' + myPrinters[id]["name"] + " is " + "OFF OR ON");
                    var state=msg.data;
                    console.log(myPrinters[id]["name"] + ": STATE IS " + state);
                    if (state=="0"){
                        label.removeClass("label-danger").removeClass("label-warning").addClass("label-success").text(myPrinters[id]["name"].toUpperCase() + " available");
                    }
                    else if (state=="-1") {
                        label.removeClass("label-success").removeClass("label-danger").addClass("label-warning").text(myPrinters[id]["name"].toUpperCase() + " OFF");
                    }
                    else {
                        label.removeClass("label-success").removeClass("label-warning").addClass("label-danger").text(myPrinters[id]["name"].toUpperCase() + " printing");
                    }

                });
            }
            socket[id].emit('printer state request');

        } catch(err){
            console.log("ERROR WAS CATCHED BOY");
            socket[id].disconnect();
        }
        return socket[id];
    };

    function statusPrinterLabel(){
        $(".printer-label").each(function(){
            var id = $(this).attr("id").split("-")[2];
            console.log("trying to connect on printer "+ myPrinters[id]["name"]);
            try {socket[id] = refreshPrinterLabel($(this),id);}
            catch(err) {
                console.log("Printer " + myPrinters[id]["name"] + " had trouble connecting, and threw error: " + err);
            };
        });
    };

    // refresh labels on page load
    statusPrinterLabel()
    // setup timer for refreshing
    var timerPrinterLabelID = setInterval(function() {
        statusPrinterLabel()
    }, 10 * 1000);
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

/////////////////////////////////////////////////////////////REFRESH PRINTERS BUTTONS AND EVENT LISTENERS////////////////////////////////////////////
    $(".btn-print").click(function(){
        _direct_print = false;
        _id_3mf = $(this).attr("id").split("-")[1];
        console.log(_id_3mf);
        $('.id_3mf').val(_id_3mf);
    });
    $(".btn-print-gcode").click(function(){
        _direct_print = true;
        _id_bulk_gcode = $(this).attr("id").split("-")[1];
        console.log("BULK GCODE ID: "+_id_bulk_gcode);
        $('._id_bulk_gcode').val(_id_bulk_gcode);
    });

    // launch at page load, and set timer for later
    statusPrinterButton();
    // timer
    var timerPrinterButtonID = setInterval(function() {
        statusPrinterButton();
    }, 5 * 1000);

    function statusPrinterButton(){
        $(".btn-printer").each(function(){
            var id = $(this).attr("id").split("-")[2];
            console.log("trying to connect on printer "+ myPrinters[id]["name"]);
            try {socket[id] = refreshPrinterButton($(this),id);}
            catch(err) {
                console.log("Printer " + myPrinters[id]["name"] + " had trouble connecting, and threw error: " + err);
            };
        });
    };

    function refreshPrinterButton(button, id){
        try{
            if (typeof socket[id] == 'undefined'){
                socket[id]=io.connect("http://" + myPrinters[id]["ip"]+ ":5000/test");
                socket[id].on('connect_error', function() {
                    socket[id].disconnect();
                    button.removeClass("btn-success").removeClass("btn-danger").removeClass("btn-warning");
                    button.off("click");
                    button.on("click", function(e){e.preventDefault();alert(myPrinters[id]["name"] + " is Disconnected");});
                    console.log("CLASS REMOVED");
                    console.log('Failed to connect to server');
                });

                socket[id].on('connected', function(msg) {
                    console.log("CLASS ADDED");
                    console.log(msg.data + " on printer " + myPrinters[id]["name"] + " !!");

                });

                socket[id].on('printer state', function(msg) {
                    // console.log('Printer State: ' + myPrinters[id]["name"] + " is " + "OFF OR ON");
                    var state=msg.data;
                    console.log(myPrinters[id]["name"] + ": STATE IS " + state);
                    if (state=="0"){
                        button.removeClass("btn-danger").removeClass("btn-warning").addClass("btn-success");
                        button.off("click");
                        var id_printer=button.attr("id").split("-")[2];

                        button.on("click", function(e){
                            e.preventDefault();
                            if (_direct_print){
                                print_gcode_direct(_id_bulk_gcode, id_printer);
                            } else {
                                print_3mf(_id_3mf, id_printer);
                            };
                        });
                    }
                    else if (state=="-1"){
                        button.removeClass("btn-danger").removeClass("btn-success").addClass("btn-warning");
                        button.off("click");
                        button.on("click", function(e){e.preventDefault();alert(myPrinters[id]["name"] + " is OFF");});
                    }
                    else {
                        button.removeClass("btn-success").removeClass("btn-warning").addClass("btn-danger");
                        button.off("click");
                        button.on("click", function(e){e.preventDefault();alert(myPrinters[id]["name"] + " is already printing");});
                    }

                });
            }


            socket[id].emit('printer state request');

        } catch(err){
            console.log("ERROR WAS CATCHED BOY");
            socket[id].disconnect();

        }
        return socket[id];
    };

// PRINT FROM 3MF
    function print_3mf(id_3mf, id_printer){
        var z_offset= $("#z-offset-"+id_printer).val();
        console.log("ID 3MF is:" +id_3mf)
        console.log("ID PRINTER is:" + id_printer);
        console.log("Z offset is wqidhwid:" + z_offset);

        if (isNaN(z_offset) || !$.isNumeric(z_offset)){
            alert("z-offset is not valid");
        } else {
            $.ajax({
                url: '/jb/ajax/print/',
                data:{
                    'printer_id':id_printer,
                    'id_3mf':id_3mf,
                    'z_offset':z_offset,
                },
                dataType:'json',
                success:function(data){
                    if (data.gcode_sent){
                        console.log(data.gcode_sent)
                    };
                    if (data.error){
                        alert(data.error)
                    };
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    alert("Status: " + textStatus); alert("Error: " + errorThrown);
                }
            });
            // refresh printer status
            // setTimeout(function(){socket[id_printer].emit('printer state request');console.log("refreshed");}, 2000);
        };

    };

// PRINT FROM BULK GCODE
    function print_gcode_direct(_id_bulk_gcode, id_printer){
        var z_offset= $("#z-offset-"+id_printer).val();
        console.log("ID BULK GCODE is:" +_id_bulk_gcode)
        console.log("ID PRINTER is:" + id_printer);
        console.log("Z offset is wqidhwid:" + z_offset);

        if (isNaN(z_offset) || !$.isNumeric(z_offset)){
            alert("z-offset is not valid");
        } else {
            $.ajax({
                url: '/jb/ajax/print-direct-gcode/',
                data:{
                    'printer_id':id_printer,
                    'id_bulk_gcode':_id_bulk_gcode,
                },
                dataType:'json',
                success:function(data){
                    if (data.gcode_sent){
                        console.log(data.gcode_sent)
                    };
                    if (data.error){
                        alert(data.error)
                    };
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    alert("Status: " + textStatus); alert("Error: " + errorThrown);
                }
            });
            // refresh printer status
            // setTimeout(function(){socket[id_printer].emit('printer state request');console.log("refreshed");}, 2000);
        };

    };



//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


});
