
$.fn.extend({
    animateCss: function (animationName, callback=null) {
        var animationEnd = 'webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend';
        this.addClass('animated ' + animationName).one(animationEnd, function() {
            $(this).removeClass('animated ' + animationName);
            if (typeof callback == 'function'){
                callback.call(this);
            }
        });
        return this;
    }
});

$(document).ready(function(){

    // INITIAL ANIMATIONS/////////////////////////////////////////////////////////////////////
    if(has_signin_error){
        $('.container h1').css("opacity", 1);
        $('.toggle-form').css("opacity",1);
        $('#login_form').show().css("opacity",1);
        console.log("1");
    } else if(has_signup_error){
        $('.container h1').css("opacity", 1);
        $('.toggle-form').css("opacity",1);
        $('#signup_form').show().css("opacity",1);
        console.log("2");
    } else {
        console.log("3");
        wordAppearance('.container h1');
        setTimeout(function(){
            $('.toggle-form').animateCss('fadeInUp', function(){$(this).css('opacity',1)});
        },1000);
    };
////////////////////////////////////////////////////////////////////////////////





// FORM AND USERTYPE TOGGLING////////////////////////////////////////////////////////////////////

    $(".toggle-form").click(function(){
        var id_form = $(this).data("toggle-form");
        var animationList = {'signup_form': 'fadeIn', 'login_form': 'fadeIn',}
        $(".toggle-form").removeClass('active');
        $(this).addClass('active');
        $("form").each(function(){
            if ($(this).attr("id") != id_form){
                $(this).css("display","none");
            } else {
                $(this).show().animateCss(animationList[id_form], function(){$(this).css("display", "block")});
            };
        });
    });

    $(".usertype-button").click(function(){
        usertype = $(this).data("usertype");
        $(".usertype-button").removeClass("active");
        $(this).addClass("active");
        $("input[name='usertype'][value='" + usertype + "']").prop("checked", true);
        if ($(this).siblings('.signup-step2').css("display") == "none"){
            $(this).siblings('.signup-step2').show().animateCss('fadeIn');
        };
    });
//////////////////////////////////////////////////////////////////////////////////////////////////////////






//LAUCHNING SOCIAL ACCOUNTS LOGIN IN IFRAME MODAL/////////////////////////////////////////////////////////
// DOESN't WORK BECAUSE OF LINKEDIN SAME ORIGIN PROTECTION
    // $("#social-signup-modal").iziModal({
    //     iframe: true,
    //     iframeHeight: 800,
    // });
    // $(".social-signin-button").click(function (event) {
    //     event.preventDefault();
    //     $('#social-signup-modal').iziModal('open', event); // Use "event" to get URL href
    // });
/////////////////////////////////////////////////////////////////////////////////////////////////////////////





// function to animate bringing text word by word/////////////////////////////////////////////////////////
    function wordAppearance(selector){
        var list1 = splitIntoWords(document.querySelector(selector));
        var list2 = list1.map(function(string, index){
            new_string = "<div style='display:inline-block;opacity:0;' class='animate-order'>" + string + "</div>"
            return new_string
        });
        block_count = list2.length;
        $(selector).html(list2.join(" "));


        $(selector).show().css('opacity',1).find('.animate-order').each(function(index){
            var $this = $(this);
            setTimeout(
                function(){$this.animateCss('fadeInLeft',function(){$this.css('opacity',1)});},
                index*300);
        });
    };


    function splitIntoWords(div) {
      function removeEmptyStrings(k) {
        return k !== '';
      }
      var rWordBoundary = /[\s\n\t]+/; // Includes space, newline, tab
      var output = [];
      for (var i = 0; i < div.childNodes.length; ++i) { // Iterate through all nodes
        var node = div.childNodes[i];
        if (node.nodeType === Node.TEXT_NODE) { // The child is a text node
          var words = node.nodeValue.split(rWordBoundary).filter(removeEmptyStrings);
          if (words.length) {
            output.push.apply(output, words);
          }
        } else if (node.nodeType === Node.COMMENT_NODE) {
          // What to do here? You can do what you want
        } else {
          output.push(node.outerHTML);
        }
      }
      return output;
    }
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////



});
