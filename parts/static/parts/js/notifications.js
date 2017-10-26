$(document).ready(function(){




});
// outside of document ready for a reason
////////////////////////////////////////////////////LIVE NOTIFICATION HANDLING/////////////////////////////////////////

    function fill_notification_list_custom(data) {
        console.log(data);
        // initialize variables
        var $notif_list = $(".live_notify_list");
        var $notif_badge = $(".notification-count");

        // empty list and count
        $notif_list.find("li").not("#template-notif").remove();
        $notif_badge.empty();
        if (data.unread_count){
            $notif_badge.text(data.unread_count);
        }
        // loop through data and fill list and count
        for (var i=0; i < data.unread_list.length; i++) {
            var msg = data.unread_list[i];
            var $new_model = $("#template-notif").clone();
            $new_model.attr("id", msg.id);
            console.log(msg);
            console.log(Date(msg.timestamp));
            console.log(typeof Date(msg.timestamp));
            $new_model.find(".notif-title").text(msg.verb);
            $new_model.find(".notif-date").text($.datepicker.formatDate('dd M yy', new Date(msg.timestamp)));
            $new_model.find(".notif-order-id").text(msg.target_object_id);
            $new_model.find(".notif-description").text(msg.description);
            // assign link url
            if (msg.data){
                var msg_data = JSON.parse(msg.data);
                if (msg_data.target_path){
                    var arr = window.location.href.split("/");
                    var current_domain = arr[0] + "//" + arr[2];
                    console.log(current_domain);
                    $new_model.find("a").attr("href", current_domain + msg_data.target_path);
                };
                // $new_model.find("a").attr("href", msg.description);
            }
            $new_model.css("display","");
            // append to list and reveal
            $notif_list.append($new_model);
        }
        // refresh click listeners
        $notif_list.find(".notif-read-check").click(function(e){
            e.preventDefault();
            e.stopPropagation();

            var $notif_item = $(this).closest(".notif-item");
            var id_notif = $notif_item.attr("id");
            console.log(id_notif);
            $.ajax({
                url: '/parts/ajax/notification/mark-as-read/',
                data:{
                    'id_notif':id_notif,
                },
                dataType:'json',
                success:function(data){
                    if (data.success){
                        console.log("success: " + data.success);
                        squeeze_disappear($notif_item);
                        $notif_badge.text(parseInt($notif_badge.text())-1);

                    } else if (data.error){
                        console.log("error: " + data.error);
                    }
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    alert("Status: " + textStatus); alert("Error: " + errorThrown);
                }

            });
        });

        function squeeze_disappear($item){
            $item.animate({
                opacity:0,
                height:"toggle"
            }, 300);
        }
    }
