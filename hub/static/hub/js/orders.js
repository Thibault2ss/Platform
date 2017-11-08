$(document).ready(function(){

// ORDER TYPES TOGGLING#####################################
    $(".btn-order-class").click(function(){
        $(".btn-order-class").removeClass("btn-fill");
        $(this).addClass("btn-fill");
    });
// end ORDER TYPE TOGGLING ######################################

// REMOVE CAROUSEL AUTO SLIDE#####################################
    $('#ordersCarousel').carousel({
        interval: false
    }); 
// end REMOVE CAROUSEL AUTO SLIDE ######################################
});
