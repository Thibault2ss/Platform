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


    $('.due_date').each(function(){
        console.log("AGAHGHAGHKG");
        var $this = $(this);
        console.log($this.text());
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

    function pad(num, size) {
        var s = num+"";
        while (s.length < size) s = "0" + s;
        return s;
    }

});
