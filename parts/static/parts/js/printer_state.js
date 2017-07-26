// printer_state handler: fetch and update printer state: printing or not printing
// writen by Thibault2ss : thibault.de-saint-sernin@sp3d.co

$(document).ready(function(){

	var $printer_dropdown=$(".printer_dropdown");
    var $replicator_link=$(".replicator-link");
    var socket=[];
    var myPrinters= {
        1: {name:"replicator",ip:"192.168.0.133"},
        2: {name:"c2",ip:"192.168.0.211"},
        3: {name:"wanaho",ip:"192.168.0.213"},
        4: {name:"c1",ip:"192.168.0.201"},
        5: {name:"c3",ip:"192.168.0.202"},
        6: {name:"c4",ip:"192.168.0.203"},
        7: {name:"c5",ip:"192.168.0.204"},
        8: {name:"c6",ip:"192.168.0.205"}
        };

    // for (var id in myPrinters) {
    //   console.log("key " + id + " has name " + myPrinters[id]["name"]);
    // }
    function initSocket(id){
        try{
            var socket=io.connect("http://" + myPrinters[id]["ip"]+ ":5000/test");
            socket.on('connect_error', function() {
                socket.disconnect();
                console.log('Failed to connect to server');
            });
            socket.on('connected', function(msg) {
                console.log(msg.data + " on printer " + myPrinters[id]["name"] + " !!");
            });
            socket.on('printer state', function(msg) {
                console.log('Printer State: ' + myPrinters[id]["name"] + " is " + "OFF OR ON");
                var state=msg.data;
                var $label=$("." + myPrinters[id]["name"] + "-label");
                if (state=="0"){
                    $label.removeClass("label-danger").addClass("label-success").text("available");
                }
                else {
                    $label.removeClass("label-success").addClass("label-danger").text("printing");
                }
            });
            socket.emit('printer state request');
        }
        catch(err){
            socket.disconnect();
        }
        return socket;
    }

    function print_with(printer_id){
        $("."+ myPrinters[printer_id]["name"] + "-link").click(function(){
            var part_id = $(this).attr('id');
            $.ajax({
                url: './ajax/print/',
                data:{
                    'printer_id':printer_id,
                    'part_id':part_id
                },
                dataType:'json',
                success:function(data){
                    if (data.gcode_sent){
                        console.log(data.gcode_sent)
                    }
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    alert("Status: " + textStatus); alert("Error: " + errorThrown);
                }
            });
        });
    }

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


    for (var id in myPrinters){
        print_with(id);
    }


});
