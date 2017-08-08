// printer_state handler: fetch and update printer state: printing or not printing
// writen by Thibault2ss : thibault.de-saint-sernin@sp3d.co

//!!!!!!!!!!!!!!!!!!!!!!!IMPORTANT: DON'T FORGET TO INCLUDE THE SOCKETIO SCRIPT IN THE TEMPLATE PAGE !!!!!!!!!!!!!!!!!!!

$(document).ready(function(){

	var $printer_dropdown=$(".printer_dropdown");
    var $printer_statusbar=$(".printer_statusbar");
    var $replicator_link=$(".replicator-link");
    var socket=[];
    var myPrinters= {
        1: {name:"replicator",ip:"192.168.0.206"},
        2: {name:"c2",ip:"192.168.0.211"},
        3: {name:"wanaho",ip:"192.168.0.214"},
        4: {name:"c1",ip:"192.168.0.212"},
        5: {name:"c3",ip:"192.168.0.210"},
        6: {name:"c4",ip:"192.168.0.204"},
        7: {name:"c5",ip:"192.168.0.205"},
        8: {name:"c6",ip:"192.168.0.207"}
        };
    var STATUS_COLOR = {
        1: "default",
        2: "primary",
        3: "success",
        4: "info",
        5: "warning",
        6: "danger",
        };

    // for (var id in myPrinters) {
    //   console.log("key " + id + " has name " + myPrinters[id]["name"]);
    // }
    function initSocket(id){
        var $link=$("." + myPrinters[id]["name"]);
        var $label=$("." + myPrinters[id]["name"] + "-label");
        try{
            var socket=io.connect("http://" + myPrinters[id]["ip"]+ ":5000/test");
            socket.on('connect_error', function() {
                socket.disconnect();
                $link.removeClass("printing").removeClass("ready");//removes the class that will allow them tho send print order
                $label.removeClass("label-success").removeClass("label-danger").text("Disconnected");
                console.log("CLASS REMOVED");
                console.log('Failed to connect to server');
            });

            socket.on('connected', function(msg) {
                // $link.addClass(myPrinters[id]["name"] + "-link") //adds the class that will allow them tho send print order
                console.log("CLASS ADDED");
                console.log(msg.data + " on printer " + myPrinters[id]["name"] + " !!");

            });

            socket.on('printer state', function(msg) {
                console.log('Printer State: ' + myPrinters[id]["name"] + " is " + "OFF OR ON");
                var state=msg.data;
                console.log("STATE IS: " + state);
                if (state=="0"){
                    $label.removeClass("label-danger").addClass("label-success").text("available");
                    $link.removeClass("printing").addClass("ready");
                    // $link.addClass(myPrinters[id]["name"] + "-link") //prevent from printing if already printing
                }
                else if (state=="-1"){
                    $label.removeClass("label-danger").removeClass("label-success").text("Disconnected");
                    $link.removeClass("printing").removeClass("ready");
                    $link.off('click');
                    // $link.addClass(myPrinters[id]["name"] + "-link") //prevent from printing if already printing
                }
                else {
                    $label.removeClass("label-success").addClass("label-danger").text("printing");
                    $link.addClass("printing").removeClass("ready");
                    // $link.removeClass(myPrinters[id]["name"] + "-link")
                }

            });

            socket.emit('printer state request');

        } catch(err){
            console.log("ERROR WAS CATCHED BOY");
            socket.disconnect();
            // $link.removeClass(myPrinters[id]["name"] + "-link");//removes the class that will allow them tho send print order
            $link.off('click');
        }
        return socket;
    };


    function refreshPrinters(id){
        var $label=$("." + myPrinters[id]["name"] + "-label");
        try{
            if (typeof socket[id] == 'undefined'){
                socket[id]=io.connect("http://" + myPrinters[id]["ip"]+ ":5000/test");
                socket[id].on('connect_error', function() {
                    socket[id].disconnect();
                    $label.removeClass("label-success").removeClass("label-danger").text(myPrinters[id]["name"].toUpperCase() + " disconnected");
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
                        $label.removeClass("label-danger").addClass("label-success").text(myPrinters[id]["name"].toUpperCase() + " available");
                    }
                    else {
                        $label.removeClass("label-success").addClass("label-danger").text(myPrinters[id]["name"].toUpperCase() + " printing");
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



    function print_with(printer_id){

        $("."+ myPrinters[printer_id]["name"]).click(function(e){
            if ($(this).hasClass('ready')){
                console.log("print button is cliiiiiicked");
                var c_id = $(this).attr('id')
                var id_3mf = c_id.split("-")[1];
                console.log("ID 3MF is:" + id_3mf);
                $.ajax({
                    url: '/parts/ajax/print/',
                    data:{
                        'printer_id':printer_id,
                        'id_3mf':id_3mf,
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
            } else if ($(this).hasClass('printing')) {
                alert("printer already in use");
            } else {
                alert("printer not available");
            }
        });
    }
// set print on click
    for (var id in myPrinters){
        print_with(id);
    }
// set refresh on click
    $printer_dropdown.click(function(){
        for (var id in myPrinters){

            console.log("trying to connect on printer "+ myPrinters[id]["name"]);
            try {
            	socket[id] = initSocket(id);
            }
            catch(err) {
                console.log("Printer " + myPrinters[id]["name"] + " had trouble connecting, and threw error: " + err);
            };
        }
    });

    //for HOME page
    if (document.title == "SpareParts3D - Catalogue"){
        // launch a first refresh when page loads fo printer state
        for (var id in myPrinters){

            console.log("trying to connect on printer "+ myPrinters[id]["name"]);
            try {

               socket[id] = refreshPrinters(id);
               console.log("REFRESHED PRINTERS "+ myPrinters[id]["name"])

            }
            catch(err) {
                console.log("Printer " + myPrinters[id]["name"] + " had trouble connecting, and threw error: " + err);
            };
        }
    // refresh printer state every 10 seconds
        var timerID = setInterval(function() {
            for (var id in myPrinters){

                console.log("trying to connect on printer "+ myPrinters[id]["name"]);
                try {

        	       socket[id] = refreshPrinters(id);
                   console.log("REFRESHED PRINTERS "+ myPrinters[id]["name"])

                }
                catch(err) {
                    console.log("Printer " + myPrinters[id]["name"] + " had trouble connecting, and threw error: " + err);
                };
            }
        }, 10 * 1000);
    }
    // color to the status labels
    // for (var key in STATUS_COLOR){
    //     console.log
    //     $(".label-" + key).addClass("label-" + STATUS_COLOR[key]);
    // };

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

        // $("#catalogue").click(function(){
        //         console.log("catalogue is clicked");
        //
        //         });

    });

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

});
