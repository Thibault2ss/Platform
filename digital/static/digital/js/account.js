$(document).ready(function(){

// INIT MAP
// initmap for google maps###################################################
    function initMap(){
        var myLatlng = new google.maps.LatLng(1.311033, 103.862287);
        var mapOptions = {
          zoom: 13,
          center: myLatlng,
          scrollwheel: false, //we disable de scroll over the map, it is a really annoing when you scroll through page
          styles: [{"featureType":"water","stylers":[{"saturation":43},{"lightness":-11},{"hue":"#0088ff"}]},{"featureType":"road","elementType":"geometry.fill","stylers":[{"hue":"#ff0000"},{"saturation":-100},{"lightness":99}]},{"featureType":"road","elementType":"geometry.stroke","stylers":[{"color":"#808080"},{"lightness":54}]},{"featureType":"landscape.man_made","elementType":"geometry.fill","stylers":[{"color":"#ece2d9"}]},{"featureType":"poi.park","elementType":"geometry.fill","stylers":[{"color":"#ccdca1"}]},{"featureType":"road","elementType":"labels.text.fill","stylers":[{"color":"#767676"}]},{"featureType":"road","elementType":"labels.text.stroke","stylers":[{"color":"#ffffff"}]},{"featureType":"poi","stylers":[{"visibility":"off"}]},{"featureType":"landscape.natural","elementType":"geometry.fill","stylers":[{"visibility":"on"},{"color":"#b8cb93"}]},{"featureType":"poi.park","stylers":[{"visibility":"on"}]},{"featureType":"poi.sports_complex","stylers":[{"visibility":"on"}]},{"featureType":"poi.medical","stylers":[{"visibility":"on"}]},{"featureType":"poi.business","stylers":[{"visibility":"simplified"}]}]

        }
        var map = new google.maps.Map(document.getElementById("map"), mapOptions);

        var marker = new google.maps.Marker({
            position: myLatlng,
            title:"Hello World!"
        });

        // To add the marker to the map, call setMap();
        marker.setMap(map);
    };
    // end init map #########################################################3

    initMap();
// END INIT MAP







// UPLOAD PROFILE PICTURE###########################################################

    $("#profile_pic_form").dropzone({
        url: "/digital/account/upload-profile-pic/",
        paramName: "profile_pic", // The name that will be used to transfer the file
        maxFiles: 2,
        maxFilesize: 2, // MB
        createImageThumbnails: false,
        clickable: true,
        acceptedFiles:".png,.jpg,.gif",
        accept: function(file, done) {
            if (file.name == "justin.jpg") {
              done("Naha, you don't.");
            }
            else { done(); }
        },
        init: function () {
            var $form = $("#profile_pic_form");
            this.on("sending", function(file, xhr, formData) {
            //    formData.append("csrfmiddlewaretoken", csrftoken);
                $form.find(".progressBar-inner").css("background-color","#6dbad8");
                $form.find(".progressBar").css("opacity",1);
                $form.find(".remove-file").removeClass("visible");
            });
            this.on('uploadprogress',function(file, progress, bytesSent){
                $form.find(".progressBar-inner").css("width", progress + "%");
            });
            this.on('complete', function () {
                setTimeout(function(){$form.find(".progressBar").css("opacity",0)}, 1000);
                setTimeout(function(){$form.find(".progressBar-inner").css("width","0%")}, 1200);
            });
            this.on("success", function(file, response) {
                console.log(response);
                $('#modalProfilePic').modal('hide');
                if (response.success){
                    $form.find(".progressBar-inner").css("background-color","green");
                    $('.user-pic,.user .avatar').css('background-image', "url(" + response.thumbnail + ")");
                } else {
                    $form.find(".progressBar-inner").css("background-color","red");
                    $.notify({
                        icon: 'ti-face-sad',
                        message: "Picture Upload failed"
                    },{
                        type: 'danger',
                        timer: 1000,
                        delay: 1000,
                    });
                };
            });
        },
        error:function(file, response){
            console.log(response);
            $('#modalProfilePic').modal('hide');
            $("#profile_pic_form").find(".progressBar-inner").css("background-color","red");
            $.notify({
                icon: 'ti-face-sad',
                message: "Picture Upload failed"
            },{
                type: 'danger',
                timer: 1000,
                delay: 1000,
            });
        },
    });

    $("#modalProfilePic .modal-body").click(function(){
        $(this).closest(".dropzone").click();
    });


// END UPLOAD PROFILE PICTURE###########################################################
});
