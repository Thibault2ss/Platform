$(document).ready(function(){
    monthNames=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
// ORDER TYPES TOGGLING#####################################
    $(".btn-status-filter").click(function(){
        var id_status = $(this).val();
        refresh_with_parameter('status', id_status)
    });
// end ORDER TYPE TOGGLING ######################################


// LAZY LOAD OF PICTURES
var myLazyLoad = new LazyLoad({
    container: document.getElementById('main-panel')
});


// REMOVE CAROUSEL AUTO SLIDE#####################################
    $('#partsCarousel').carousel({
        interval: false
    });
    $('#partsCarousel').bind('slide.bs.carousel', function (ev) {
        console.log('slide event!');
        var id = ev.relatedTarget.id;
        switch (id) {
            case "partsCarousel-slide2":
              $('.button-back').show()
              break;
            default:
              $('.button-back').hide();
          }
    });

    $('#imageCarousel').carousel({
        interval: false
    });

// end REMOVE CAROUSEL AUTO SLIDE ######################################






// INITIALIZE SLICK ###############################################
    $('#imageCarousel').slick({
                dots: false,
                infinite: true,
                speed: 300,
                slidesToShow: 1,
                centerMode: true,
                variableWidth: true,
                focusOnSelect:false,
            });
// end INITIALIZE SLICK /########################################





// INITIALIZE PARAMTERS VIEWS//////////////////////////////////////
    var searchParams = new URLSearchParams(window.location.search);
    $('#number-per-page').change(function(){
        refresh_with_parameter('nb-per-page', $(this).val());
    });

    $('.pagination-link').click(function(e){
            e.preventDefault();
            refresh_with_parameter('page', $(this).data('page'));
        });

// END INITIALIZE PARAMTERS VIEWS//////////////////////////////////////





// ADD IMAGE TO CAROUSEL METHOD////////////////////////////////////////
    function addToCarousel(html, callback){
        $('#imageCarousel').slick('slickAdd',html);
        callback();
        setTimeout(function(){$('#imageCarousel').slick('setPosition')},100);
    };
// END ADD IMAGE TO CAROUSEL METHOD////////////////////////////////////////





// INIT PART DATA ON CLICK ON ONE PART#####################################

    $(".part-row").click(function(){
        // load part data
        var part = $(this).data('part');
        var part_images = $(this).data('part-images');
        // console.log(part_images);
        console.log(part);

        // populate images
        $('#imageCarousel').slick('removeSlide', null, null, true);
        if (part_images.length > 0){
            for (var i = 0; i < part_images.length; i++){
                addToCarousel('<div class="img-container" style="background-image:url(' + part_images[i] + ')"></div>', function(){$('#imageCarousel').slick('slickGoTo', 0, true)});
            };
        }else{
            addToCarousel('<div class="img-container" style="background-image:url(/static/digital/img/default_pic.jpg)"></div>', function(){$('#imageCarousel').slick('slickGoTo', 0, true)})
        };
        // remove old stl from canvas
        remove_stl();
        $("#stl-demo").css("display", "block");

        // populate info
        var name, ref, material, length, dimension_unit, weight_unit, date_created, appliance, bulk_files, status, part_type, characs, name_creator, final_card
        name = part.fields.name;
        if(part.fields.type){part_type = part.fields.type}else{part_type = {'id':''}};
        if(part.fields.reference){ref = part.fields.reference}else{ref = ''};
        final_card = part.fields.final_card;
        characs = part.fields.characteristics;
        if (part.fields.material){material = part.fields.material}else{material={'id':''}};
        length = part.fields.length, width = part.fields.width, height = part.fields.height, weight = part.fields.weight;
        dimension_unit = part.fields.dimension_unit, weight_unit = part.fields.weight_unit;
        date_created = new Date(part.fields.date_created);
        date_created = date_created.getDate() + " " + monthNames[date_created.getMonth()] + " " + date_created.getFullYear();
        name_creator = part.fields.created_by.first_name;
        appliance = part.fields.appliance;
        status = part.fields.status;
        bulk_files = $(this).data("part-bulk-files");

        $(".id_part").val(part.pk);
        $("input[name='id_part']").val(part.pk);
        if (final_card != null && status.id == 4){
            $("#final-card").find("#id_currency").val(final_card.currency);
            $("#final-card").find("#id_unit_price").val(final_card.unit_price);
            $("#final-card").find("#id_techno_material").val(final_card.techno_material.id);
            $("#final-card").find("#id_lead_time").val(final_card.lead_time);
            $("#final-card").show();
        } else {
            $("#final-card").hide();
        };
        $(".part-status").removeClass().addClass("label part-status").text(status.name);
        $("#part-detail-panel").data("part-id",part.pk);
        $("#id_name_1").val(name);
        $("#id_reference_1").val(ref);
        $("#id_material_1").val(material.id);
        $("#id_length_1").val(length);
        $("#id_width_1").val(width);
        $("#id_height_1").val(height);
        $("#id_weight_1").val(weight);
        $("#id_dimension_unit_1").val(dimension_unit);
        $("#id_weight_unit_1").val(weight_unit);
        $("#id_type_1").val(part_type.id);
        if(characs!=null){
            $("#id_min_temp_1").val(characs.min_temp);
            $("#id_max_temp_1").val(characs.max_temp);
            $("#id_temp_unit_1").val(characs.temp_unit);
            $("#id_is_flame_retardant_1").prop("checked",characs.is_flame_retardant);
            $("#id_is_chemical_resistant_1").prop("checked",characs.is_chemical_resistant);
            $("#id_is_food_grade_1").prop("checked",characs.is_food_grade);
            $("#id_is_transparent_1").prop("checked",characs.is_transparent);
            $("#id_is_visual_1").prop("checked",characs.is_visual);
            $("#id_is_water_resistant_1").prop("checked",characs.is_water_resistant);
            $("#id_is_rubbery_1").prop("checked",characs.is_rubbery);
            $("#id_color_1").val(characs.color);
            $("#id_flame_retardancy_1").val(characs.flame_retardancy);
        }else{
            resetCharacteristics();
        };

        $(".collapse").collapse('hide');

        $(".status").attr("data-status-id", "" + status.id);
        if (status.id>=1){
            $("#button-action-1").removeClass().addClass("btn btn-warning btn-fill btn-wd request-for-indus-button order-part-button").text("Request Indus");
        };
        if (status.id>=2){
            $("#button-action-1").removeClass().addClass("btn btn-default btn-fill btn-wd disabled").text("Indus Pending");
        };
        if (status.id>=3){
            $("#button-action-1").removeClass().addClass("btn btn-danger btn-fill btn-wd disabled").text("Not Printable");
        };
        if (status.id>=4){
            $("#button-action-1").removeClass().addClass("btn btn-success btn-fill btn-wd print-request-button").text("Print");
        };
        $("#id_appliance_1").find("option").removeAttr("selected").hide();
        for (var i = 0; i < appliance.length; i++){
            $("#id_appliance_1").find("option[value='" + appliance[i].id + "']").show().attr("selected","");
        };

        $(".file-list").empty();
        for (var i = 0; i < bulk_files.length; i++){
            var stl_button = "";
            if (bulk_files[i].type == 'STL'){
                var stl_button = "<btn class='btn btn-sm btn-warning btn-icon btn-3d-view' data-stl='" + bulk_files[i].data + "'><i class='fa fa-cube'></i></btn>"
            };
            var html = "\
                        <div class='file-row' data-id='" +  bulk_files[i].id + "'>" + stl_button + "<a href='" + bulk_files[i].url + "' target='_blank'>\
                            <i class='ti-download'></i>" + bulk_files[i].name + "</a>\
                            <div class='remove-file remove-icon'><i class='ti-close'></i></div>\
                        </div>"
            if (bulk_files[i].type == "3D" || bulk_files[i].type == "2D"|| bulk_files[i].type == "STL" ){
                $("#part3dfile_form").find(".file-list").append(html);
            } else {
                $("#partbulkfile_form").find(".file-list").append(html);
            }
        };

        // refresh buttons listeners
        refreshButtons();
        //get Part HISTORY and scroll to bottom of history
        getPartHistory(part.pk, date_created, name_creator);
        setTimeout(function(){
            $("#timeline-card").animate({ scrollTop: $('#timeline-card').prop("scrollHeight")}, 1000);
        },500);

        // to resize the stl canvas
        setTimeout(function(){
            onWindowResize();
        }, 100);
    });
// END INIT ORDERS DATA ON CLICK ON ONE ORDER#####################################




// FUNCTION TO RESET CHARACTERISTIC FORM/////////////////////////////////////////
function resetCharacteristics(){
    $("[id^=id_min_temp]").val(0);
    $("[id^=id_max_temp]").val(70);
    $("[id^=id_temp_unit]").val('°C');
    $("[id^=id_is_flame_retardant]").prop("checked", false);
    $("[id^=id_is_chemical_resistant]").prop("checked", false);
    $("[id^=id_is_food_grade]").prop("checked", false);
    $("[id^=id_is_transparent]").prop("checked", false);
    $("[id^=id_is_visual]").prop("checked", false);
    $("[id^=id_is_water_resistant]").prop("checked", false);
    $("[id^=id_is_rubbery]").prop("checked", false);
    $("[id^=id_color]").val('NA');
    $("[id^=id_flame_retardancy]").val('NA');
};
// END FUNCTION TO RESET CHARACTERISTIC FORM/////////////////////////////////////////




// SENDING BULK FILES ASYNCHRONOUSLY#############################################
// NOW I USE DROPZONE INSTEAD OF THIS##################################################################################
    $("#partbulkfile_form").submit(function(event){
        event.preventDefault();
        var $form = $(this);
        var data = new FormData(this);
        $.ajax({
            url: '/digital/parts/upload-part-bulk-file/',
            data: data,
            cache: false,
            contentType: false,
            processData: false,
            method: 'POST',
            type: 'POST', // For jQuery < 1.9
            beforeSend:function(XMLHttpRequest, settings){
                $form.find(".progressBar-inner").css("background-color","blue");
                $form.find(".progressBar").css("opacity",1);
            },
            xhr: function() {
                var myXhr = $.ajaxSettings.xhr();
                if(myXhr.upload){
                    myXhr.upload.addEventListener('progress',uploadProgress, false);
                }
                return myXhr;
            },
            success: function(data){
                console.log(data);
                if (data.success=true){
                    $form.find(".progressBar-inner").css("background-color","green");
                } else {
                    $form.find(".progressBar-inner").css("background-color","red");
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                console.log("Status: " + textStatus); console.log("Error: " + errorThrown);
                $form.find(".progressBar-inner").css("background-color","red");
            },
            complete:function(jqXHR, textStatus){
                setTimeout(function(){$form.find(".progressBar").css("opacity",0)}, 1000);
                setTimeout(function(){$form.find(".progressBar-inner").css("width","0%")}, 1200);
            },

        });
    });

    function uploadProgress(e){
        if(e.lengthComputable){
            var max = e.total;
            var current = e.loaded;
            var Percentage = (current * 100)/max;
            $(".progressBar-inner").css("width", Percentage + "%");
            // console.log(Percentage);
            if(Percentage >= 100)
            {
               console.log("upload complete");
            }

        }
    }
// END NOW I USE DROPZONE INSTEAD OF THIS##################################################################################
    function dropzoneConfig(id_form){
        var config = {
            url: "/digital/parts/upload-part-bulk-file/",
            paramName: "file", // The name that will be used to transfer the file
            maxFilesize: 20, // MB
            createImageThumbnails: false,
            clickable: true,
            // acceptedFiles:".stl,.sldprt,.step,.ico",
            accept: function(file, done) {
                if (file.name == "justin.jpg") {
                  done("Naha, you don't.");
                }
                else { done(); }
            },
            init: function () {
                var $form = $(id_form);
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
                    if (response.success){
                        $form.find(".progressBar-inner").css("background-color","green");
                    } else {
                        $form.find(".progressBar-inner").css("background-color","red");
                    };
                    // update part-row:
                    for (var i = 0; i < response.files_success.length; i++){
                        console.log("it pushed");
                        var stl_button = "";
                        if (response.files_success[i].type == 'STL'){
                            var stl_button = "<btn class='btn btn-sm btn-warning btn-icon btn-3d-view' data-stl='" + response.files_success[i].data + "'><i class='fa fa-cube'></i></btn>"
                        };
                        $(".part-row[data-part-id='" + response.id_part + "']").data("part-bulk-files").push(response.files_success[i]);
                        $form.find(".file-list").append("\
                            <div class='file-row' data-id='" + response.files_success[i].id + "'>" + stl_button + "<a href='" + response.files_success[i].url + "' target='_blank'>\
                                <i class='ti-download'></i>" + response.files_success[i].name + "</a>\
                                <div class='remove-file remove-icon'><i class='ti-close'></i></div>\
                            </div>");
                    };
                    refreshButtons();
                });
            },
            error:function(file, response){
                console.log(response.message);
                $("#partbulkfile_form").find(".progressBar-inner").css("background-color","red");
            },
        }
        return config;
    };

    $("#partbulkfile_form").dropzone(dropzoneConfig("#partbulkfile_form"));
    $("#part3dfile_form").dropzone(dropzoneConfig("#part3dfile_form"));

    $(".card-plus-icon").click(function(){
        $(this).closest(".dropzone").click();
    });

// END SENDING BULK FILES ASYNCHRONOUSLY#############################################





// DELETING BULK FILES###############################################################
    $(".allow-remove").click(function(){
        $(this).closest(".card").find(".remove-file").each(function(i){
            var $this = $(this);
            setTimeout(function(){
                $this.toggleClass("visible");
                console.log("yes");
            },50*i);
        });

        $(this).toggleClass("allowed");
    });

    function removeFile(id_file){
        console.log(id_file);
        if (id_file){
            $.ajax({
                url: '/digital/parts/delete-bulk-file/',
                data:{
                    'id_file':id_file,
                },
                dataType:'json',
                success:function(data){
                    if (data.success){
                        console.log(data.success);
                        $(".file-row[data-id='" + id_file + "']").css("padding", "0px").css("height", "0px");
                        setTimeout(function(){$(".file-row[data-id='" + id_file + "']").remove()}, 200);
                        var id_part = $("#part-detail-panel").data("part-id");
                        var old_data = $(".part-row[data-part-id='" + id_part + "']").data("part-bulk-files");
                        var new_data = [];
                        for (var i=0; i < old_data.length; i++){
                            if(old_data[i].id != id_file){
                                new_data.push(old_data[i]);
                            }
                        };
                        $(".part-row[data-part-id='" + id_part + "']").data("part-bulk-files",new_data);
                        setTimeout(function(){refreshButtons();},200);
                        refreshButtons();
                    };
                    if (data.error){
                        console.log(data.error);
                    };
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    console.log("Status: " + textStatus); console.log("Error: " + errorThrown);
                }
            });
        };
    };


// END DELETING BULK FILES###############################################################





// ADDING IMAGES AJAX/////////////////////////////////////////////////////////////////////
    $("#image_form").dropzone({
        url: "/digital/parts/upload-part-image/",
        paramName: "image", // The name that will be used to transfer the file
        maxFilesize: 7, // MB
        createImageThumbnails: false,
        clickable: true,
        acceptedFiles:".png,.gif,.jpg",
        accept: function(file, done) {
            if (file.name == "justin.jpg") {
              done("Naha, you don't.");
            }
            else { done(); }
        },
        init: function () {
            var $form = $("#image_form");
            this.on("sending", function(file, xhr, formData) {
                console.log("sending");
                $form.find(".progressBar-inner").css("background-color","#6dbad8");
                $form.find(".progressBar").css("opacity",1);
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
                if (response.success){
                    $form.find(".progressBar-inner").css("background-color","green");
                    $('#imageCarousel').find("img[src='/static/digital/img/default_pic.jpg']").each(function(){
                        $('#imageCarousel').slick('slickRemove', $(this).data('slick-index'));
                    });
                } else {
                    $form.find(".progressBar-inner").css("background-color","red");
                };
                for (var i = 0; i < response.images_success.length; i++){
                    addToCarousel('<img src="' + response.images_success[i].url + '">', function(){$('#imageCarousel').slick('slickGoTo', 0, false)})
                    $(".part-row[data-part-id='" + response.id_part + "']").data("part-images").push(response.images_success[i].url);
                };
            });
        },
        error:function(file, response){
            console.log(response.message);
            $("#partbulkfile_form").find(".progressBar-inner").css("background-color","red");
        },
    });
// END ADDING IMAGES AJAX/////////////////////////////////////////////////////////////////////





// REQUEST FOR INDUSTRIALIZATION######################################################################
    function refreshButtons(){
        $('.request-for-indus-button').off();
        $('.request-for-indus-button').click(function(){
            var id_part = $("#part-detail-panel").data("part-id");
            $.ajax({
                url: '/digital/parts/request-for-indus/',
                data:{
                    'id_part':id_part,
                },
                dataType:'json',
                success:function(data){
                    if (data.success){
                        console.log(data.success);
                        var date_now = new Date();
                        $('.status').attr("data-status-id", "" + id_status);
                        $('.request-for-indus-button').removeClass().addClass("btn btn-default btn-fill btn-wd disabled");
                        var updated_part = $(".part-row[data-part-id='" + id_part + "']").data("part");
                        updated_part.fields.status.id = 2;
                        $(".part-row[data-part-id='" + id_part + "']").data("part", updated_part);
                    };
                    if (data.error){
                        console.log(data.error);
                    };
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    console.log("Status: " + textStatus); console.log("Error: " + errorThrown);
                }
            });
        });
        $('.button-change-status').off();
        $('.button-change-status').click(function(){
            var id_part = $("#part-detail-panel").data("part-id");
            var id_status = $(this).data("status-id");
            $.ajax({
                url: '/digital/parts/change-part-status/',
                data:{
                    'id_part':id_part,
                    'id_status':id_status,
                },
                dataType:'json',
                success:function(data){
                    if (data.success){
                        console.log(data.success);
                        $('.status').attr("data-status-id", "" + id_status)
                        var date_now = new Date();
                        var updated_part = $(".part-row[data-part-id='" + id_part + "']").data("part");
                        updated_part.fields.status.id = id_status;
                        $(".part-row[data-part-id='" + id_part + "']").data("part", updated_part);
                        if (id_status==4){
                            $("#final-card").find("input").removeAttr("disabled");
                            $("#final-card").find("select").removeAttr("disabled");
                            $("#final-card").show();
                        };
                    };
                    if (data.error){
                        console.log(data.error);
                    };
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    console.log("Status: " + textStatus); console.log("Error: " + errorThrown);
                }
            });
        });

        $('.remove-file').off();
        $(".remove-file").click(function(){
            removeFile($(this).closest(".file-row").data("id"));
        });

        // DYNAMICALLY ADD STL TO VIEW//////////////////////////////////////////////////////////
        $('#stl-demo').off();
        $("#stl-demo").click(function(){
            var $stlButton = $(".btn-3d-view");
            if ($stlButton.length !== 0){
                $stlButton.first().click();
                $stlButton.first().closest(".file-row").animateCss('tada');
            } else {
                // $(this).css("display","none");
                // load_stl("/static/hub/stl/assemb6.STL", null);
                $(this).animateCss('tada');
                $.notify({
                    icon: 'ti-info',
                    message: "There are no STL files !"
                },{
                    type: 'warning',
                    timer: 500,
                    delay: 200,
                });
            };
        });
        $('.btn-3d-view').off();
        $(".btn-3d-view").click(function(){
            var url = $(this).siblings("a").attr('href');
            var stl_data = $(this).data('stl');
            $("#stl-demo").css("display","none");
            load_stl(url, stl_data);
        });

        $('.print-request-button').off();
        $(".print-request-button").click(function(){
            $(this).animateCss('tada');
            $.notify({
                icon: 'ti-info',
                message: "Not available for Beta testers :)"
            },{
                type: 'warning',
                timer: 1000,
                delay: 1000,
            });
        });


        // END DYNAMICALLY ADD STL TO VIEW//////////////////////////////////////////////////////////

    };
    refreshButtons();
// END REQUEST FOR INDUSTRIALIZATION######################################################################




// GET PART HISTORY######################################################################

    function getPartHistory(id_part, date_created, name_creator){
        $.ajax({
            url: '/digital/parts/get-part-history/',
            data:{
                'id_part':id_part,
            },
            dataType:'json',
            success:function(data){
                if (data.success){
                    console.log(JSON.parse(data.events));
                    fillTimeline(date_created, name_creator, JSON.parse(data.events));
                };
                if (data.error){
                    console.log(data.error);
                };
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                console.log("Status: " + textStatus); console.log("Error: " + errorThrown);
            }
        });
    };

    function fillTimeline(date_created, name_creator, events){
        $("#timeline-card").empty();
        $("#timeline-card").append(get_HTML_Timeline(date_created, "label", "default", "Created", "Part was created", name_creator));
        for (var i = 0; i < events.length; i++){
            var event = events[i].fields;
            var date = new Date(event.date);
            date = date.getDate() + " " + monthNames[date.getMonth()] + " " + date.getFullYear();
            var short_description = event.short_description;
            var label_type, label_class, label_short_description, label_first_name, label_text, last, warning;
            warning = false;
            if (events[i].fields.type == "STATUS_CHANGE"){
                label_type = "label";
                if (event.status.id == 2 && event.status){
                    label_class = "warning";
                } else if(event.status.id == 3){
                    label_class = "danger";
                } else if(event.status.id == 4){
                    label_class = "success";
                };
                label_text = event.status.name;
            } else if (event.type == "REQUEST"){
                label_type = "text";
                label_class = "danger";
                label_text = "Request";
                warning = true;
            } else if (event.type == "INFO"){
                label_type ="text";
                label_class = "default";
                label_text = 'Info'
            };
            last = (i == events.length - 1) ? true : false;
            label_short_description = event.short_description ? event.short_description:"Description Missing";
            label_first_name = event.created_by.first_name ? event.created_by.first_name:"Unknown";
            $("#timeline-card").append(get_HTML_Timeline(date, label_type, label_class, label_text, label_short_description, label_first_name, last = last, warning = warning));

        };

    };

    function get_HTML_Timeline(date, label_type, label_class, label_text, description, name, last = false, warning = false){
        var label, icon_warning;
        var icon = "circle-o";
        if(last){icon = "circle"};
        if (warning){icon_warning = "<i class='fa fa-warning' style='color:red'></i>"}else{icon_warning=""};
        if (label_type == "label"){
            label = "<span class='label label-" + label_class + "' style='font-size:100%'>" + label_text + "</span>";
        } else if (label_type == "text"){
            label = "<span class='text-" + label_class + "' style='font-size:100%;font-weight:900;'>" + label_text + "</span>";
        };
        var html = "\
        <div class='row equal-height'>\
            <div class='col-xs-4 timeline-date'>\
                <span class='text-muted' style='font-size:80%;'>" + date + "</span><br>\
                <span class='text-muted' style='font-size:80%'> by " + name + "</span>\
            </div>\
            <div class='col-xs-1 timeline-circles no-padding'>\
                <div class='border-right'><i class='fa fa-" + icon + "'></i></div>\
                <div class='border-right'></div>\
            </div>\
            <div class='col-xs-8 timeline-description'>\
                <div>" + icon_warning + label + "</div>\
                <div>" + description + "</div>\
            </div>\
        </div>"
        return html;
    };


// END GET PART HISTORY######################################################################




//ADDING A NEW PART///////////////////////////////////////////////////////////////////////////
    $("#new_part_form").submit(function(event){
        console.log("fewfef");
        event.preventDefault();
        var $form = $(this);
        var data = new FormData(this);
        // console.log("received");
        $.ajax({
            url: '/digital/parts/new-part/',
            data: data,
            cache: false,
            contentType: false,
            processData: false,
            method: 'POST',
            type: 'POST', // For jQuery < 1.9
            beforeSend:function(XMLHttpRequest, settings){
                // $form.find(".progressBar-inner").css("background-color","blue");
                // $form.find(".progressBar").css("opacity",1);
            },
            xhr: function() {
                var myXhr = $.ajaxSettings.xhr();
                if(myXhr.upload){
                    // myXhr.upload.addEventListener('progress',uploadProgress, false);
                }
                return myXhr;
            },
            success: function(data){
                console.log(data);
                if (data.success){
                    console.log(JSON.parse(data.part));
                    $('#modalNewPart').modal('hide');
                    $.notify({
                        icon: 'ti-check',
                        message: "New Part Created"
                    },{
                        type: 'success',
                        timer: 1000,
                        delay: 1000,
                    });
                    resetCharacteristics();
                    setTimeout(function(){location.reload()},1000);
                } else {
                    $.notify({
                        icon: 'ti-face-sad',
                        message: "Part Creation failed"
                    },{
                        type: 'danger',
                        timer: 1000,
                        delay: 1000,
                    });
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                $.notify({
                    icon: 'ti-face-sad',
                    message: "Part Creation failed"
                },{
                    type: 'danger',
                    timer: 1000,
                    delay: 1000,
                });
                console.log("Status: " + textStatus); console.log("Error: " + errorThrown);
            },
            complete:function(jqXHR, textStatus){
                // setTimeout(function(){$form.find(".progressBar").css("opacity",0)}, 1000);
                // setTimeout(function(){$form.find(".progressBar-inner").css("width","0%")}, 1200);
            },

        });
    });
    // filter according to appliance family choice
    $("#new_part_form").find("#id_appliance_family").change(function(){
        var appliance_family;
        if ($(this).val()){
            appliance_family = RegExp($(this).find("option[value='" + $(this).val() + "']").text(), 'i');
        }else{
            appliance_family = RegExp('','i');
        };
        $("#new_part_form").find("#id_type option, #id_appliance option").hide();
        $("#new_part_form").find("#id_type option, #id_appliance option").filter(function () {
            return appliance_family.test($(this).text());
        }).show();
    });
    // show flame retardancy level il is_flame_retardant
    $("#new_part_form").find("#id_is_flame_retardant").change(function(){
        if(this.checked) {
            $("#fg-flame-retardancy").show();
            if ($("#id_flame_retardancy").val() == 'NA'){
                $("#id_flame_retardancy").val("HB");
            };
        }else{
            $("#fg-flame-retardancy").hide();
            $("#id_flame_retardancy").val("NA");
        };
    });


    // auto fill characteristics
    $("#new_part_form").find("#id_type").change(function(){
        var $form = $('#new_part_form');
        var id_type=$(this).val();
        if (id_type && parseInt(id_type)!=='NaN'){
            $.ajax({
                url: '/digital/parts/get-characteristics/',
                data: {id_type:id_type},
                method: 'POST',
                type: 'POST', // For jQuery < 1.9
                beforeSend:function(XMLHttpRequest, settings){
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        XMLHttpRequest.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                },
                success: function(data){
                    console.log(data);
                    if (data.success && data.characteristics){
                        var characteristics = data.characteristics;
                        console.log(characteristics);
                        for (key in characteristics){
                            var value = characteristics[key];
                            if(typeof(value) === "boolean"){
                                $form.find("#id_" + key).prop("checked",value).trigger('change');
                            }else{
                                $form.find("#id_" + key).val(value);
                            };
                        };
                    }else{
                        resetCharacteristics();
                    };
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    console.log("Status: " + textStatus); console.log("Error: " + errorThrown);
                },
                complete:function(jqXHR, textStatus){
                },
            });
        }else{
            resetCharacteristics();
        };
    });
//END ADDING NEW PART////////////////////////////////////////////////////////////////////////




// refresh button appear on key down
    $("#new_part_form").find("#id_name").keyup(function(){
        if ($(this).val()){
            $("#find-part-type").show().removeClass("rotate-infinite");
        }else{
            $("#find-part-type").hide();
        }
    });



// GET PART TYPE bASED ON NAME#############################################################
    $("#find-part-type").click(function(){
        $self = $(this);
        $self.addClass("rotate-infinite");
        var part_name=$("#id_name").val();
        var $form=$(this).closest("form");
        $.ajax({
            url: '/digital/parts/get-part-type/',
            data: {part_name:part_name},
            method: 'POST',
            type: 'POST', // For jQuery < 1.9
            beforeSend:function(XMLHttpRequest, settings){
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    XMLHttpRequest.setRequestHeader("X-CSRFToken", csrftoken);
                }
            },
            success: function(data){
                console.log(data);
                if (data.success && data.characteristics){
                    var characteristics = data.characteristics;
                    var id_part_type = data.id_part_type;
                    var id_appliance_family = data.id_appliance_family;
                    console.log(characteristics);
                    $form.find("#id_appliance_family").val(id_appliance_family).trigger('change');
                    $form.find("#id_type").val(id_part_type);
                    for (key in characteristics){
                        var value = characteristics[key];
                        if(typeof(value) === "boolean"){
                            $form.find("#id_" + key).prop("checked",value).trigger('change');
                        }else{
                            $form.find("#id_" + key).val(value);
                        };
                    };
                }else{
                    resetCharacteristics();
                };
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                console.log("Status: " + textStatus); console.log("Error: " + errorThrown);
            },
            complete:function(jqXHR, textStatus){
                $self.hide().removeClass("rotate-infinite");
            },
        });

    });
// END GET PART TYPE bASED ON NAME#############################################################





// UPDATING FINAL CARD/////////////////////////////////////////////////////////////////////////
    $("#final_card_form").submit(function(event){
        event.preventDefault();
        var $form = $(this);
        var data = new FormData(this);
        var id_part = $("#part-detail-panel").data("part-id");
        data.append("id_part", id_part);
        // console.log("received");
        $.ajax({
            url: '/digital/parts/update-final-card/',
            data: data,
            cache: false,
            contentType: false,
            processData: false,
            method: 'POST',
            type: 'POST', // For jQuery < 1.9
            beforeSend:function(XMLHttpRequest, settings){
                // $form.find(".progressBar-inner").css("background-color","blue");
                // $form.find(".progressBar").css("opacity",1);
            },
            xhr: function() {
                var myXhr = $.ajaxSettings.xhr();
                if(myXhr.upload){
                    // myXhr.upload.addEventListener('progress',uploadProgress, false);
                }
                return myXhr;
            },
            success: function(data){
                console.log(data);
                if (data.success){
                    var updated_part = $(".part-row[data-part-id='" + id_part + "']").data("part");
                    var final_card_model = JSON.parse(data.final_card);
                    updated_part.fields.final_card = final_card_model.fields;
                    console.log("updated_part:");console.log(updated_part);
                    $(".part-row[data-part-id='" + id_part + "']").data("part", updated_part);

                    $.notify({
                        icon: 'ti-check',
                        message: "Final Card Updated"
                    },{
                        type: 'success',
                        timer: 1000,
                        delay: 1000,
                    });
                } else {
                    $.notify({
                        icon: 'ti-face-sad',
                        message: "Could not Update final card"
                    },{
                        type: 'danger',
                        timer: 1000,
                        delay: 1000,
                    });
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                console.log("Status: " + textStatus); console.log("Error: " + errorThrown);
                // $form.find(".progressBar-inner").css("background-color","red");
            },
            complete:function(jqXHR, textStatus){
                // setTimeout(function(){$form.find(".progressBar").css("opacity",0)}, 1000);
                // setTimeout(function(){$form.find(".progressBar-inner").css("width","0%")}, 1200);
            },

        });
    });

    $(".allow-inputs").click(function(){
        $(this).closest(".card").find("input,select").removeAttr("disabled");
        $(this).closest(".card").find("select[multiple='multiple']").find("option").show();
    });
// END UPDATING FINAL CARD/////////////////////////////////////////////////////////////////////////







// UPDATING PART CARD/////////////////////////////////////////////////////////////////////////
    $("#update_part_form").submit(function(event){
        event.preventDefault();
        var $form = $(this);
        var data = new FormData(this);
        var id_part = $("#part-detail-panel").data("part-id");
        data.append("id_part", id_part);
        // console.log("received");
        $.ajax({
            url: '/digital/parts/update-part-card/',
            data: data,
            cache: false,
            contentType: false,
            processData: false,
            method: 'POST',
            type: 'POST', // For jQuery < 1.9
            beforeSend:function(XMLHttpRequest, settings){
                // $form.find(".progressBar-inner").css("background-color","blue");
                // $form.find(".progressBar").css("opacity",1);
            },
            xhr: function() {
                var myXhr = $.ajaxSettings.xhr();
                if(myXhr.upload){
                    // myXhr.upload.addEventListener('progress',uploadProgress, false);
                }
                return myXhr;
            },
            success: function(data){
                console.log(data);
                if (data.success){
                    $(".part-row[data-part-id='" + id_part + "']").data("part", JSON.parse(data.part));
                    $.notify({
                        icon: 'ti-check',
                        message: "Part Successfully Updated"
                    },{
                        type: 'success',
                        timer: 1000,
                        delay: 1000,
                    });
                } else {
                    $.notify({
                        icon: 'ti-face-sad',
                        message: "Could not Update Part"
                    },{
                        type: 'danger',
                        timer: 1000,
                        delay: 1000,
                    });
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                console.log("Status: " + textStatus); console.log("Error: " + errorThrown);
                // $form.find(".progressBar-inner").css("background-color","red");
            },
            complete:function(jqXHR, textStatus){
                // setTimeout(function(){$form.find(".progressBar").css("opacity",0)}, 1000);
                // setTimeout(function(){$form.find(".progressBar-inner").css("width","0%")}, 1200);
            },

        });
    });


// ENDUPDATING PART CARD/////////////////////////////////////////////////////////////////////////




// BUTTON GET SOLUTION###################################################################
    $("#button-get-best-solution").click(function(){
        var id_part = $("#part-detail-panel").data("part-id");
        $.ajax({
            url: '/digital/parts/get-best-solution/',
            data: {id_part:id_part},
            method: 'POST',
            type: 'POST', // For jQuery < 1.9
            beforeSend:function(XMLHttpRequest, settings){
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    XMLHttpRequest.setRequestHeader("X-CSRFToken", csrftoken);
                }
            },
            success: function(data){
                console.log(data);
                if (data.success){
                    techno_materials = JSON.parse(data.techno_material_list);
                    if (data.perfect_match){
                        console.log('PERFECT MATCH !');
                    }else{
                        console.log('NOT PERFECT MATCH... Discarded Criterias: ');
                        console.log(data.discarded_criterias);
                    };

                    for (var i = 0; i < techno_materials.length; i++){
                        console.log(techno_materials[i].fields.technology.name + " + " + techno_materials[i].fields.material.name);
                    }
                }else{
                    for (var i = 0; i < data.errors.length; i++){
                        console.log('ERROR: ' + data.errors[i]);
                    }
                    // console.log(data.errors);
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                console.log("Status: " + textStatus); console.log("Error: " + errorThrown);
            },
            complete:function(jqXHR, textStatus){
            },

        });
    });

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
// END BUTTON GET SOLUTION###################################################################



// PART SEARCH///////////////////////////////////////////////////////////
    $(document).on('keyup','.part-search',function () {
        if ($(this).val()) {
            $('.btn-reset-search').show();
        } else {
            $('.btn-reset-search').hide();
        };

        var rex = new RegExp($(this).val(), 'i');
        $(".part-row").hide();
        $(".part-row").filter(function () {
            return rex.test($(this).text());
        }).show();
    });

    $('.btn-reset-search').click(function(){
        if ($(this).siblings(".part-search").val()){
            $(this).siblings(".part-search").val("");
            refresh_with_parameter('search', '');
        }
    });

    $(".form-part-search").submit(function(event){
        event.preventDefault();
        var string = $(this).find("input[name='search']").val();
        refresh_with_parameter('search', string);

    });
// END PART SEARCH///////////////////////////////////////////////////////////




// UPLOAD SOLUTION MATRIX################################################
    $("#form_solution_matrix").submit(function(event){
        event.preventDefault();
        var $form = $(this);
        var data = new FormData(this);
        $.ajax({
            url: '/digital/upload-solution-matrix/',
            data: data,
            cache: false,
            contentType: false,
            processData: false,
            method: 'POST',
            type: 'POST', // For jQuery < 1.9
            beforeSend:function(XMLHttpRequest, settings){
            },
            success: function(data){
                console.log(data);
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                console.log("Status: " + textStatus); console.log("Error: " + errorThrown);
            },
            complete:function(jqXHR, textStatus){
            },
        });
    });

// END UPLOAD SOLUTION MATRIX################################################





// FUNCTION TO INIT A STL CANVAS########################################

    if ( ! Detector.webgl ) Detector.addGetWebGLMessage();
	var stl_container, stats;
	var camera, cameraTarget, controls, scene, renderer;
    // var width = $("#stlcanvas").closest(".container").width();
    // var height = $("#stlcanvas").closest(".container").width();
    var width = $('#stl-canvas').width();
    var height = $('#stl-canvas').width();
    // console.log("WIDTH IS: " + width);
    // console.log("HEIGHT IS: " + height);
	init();
	animate();
	function init() {
		stl_container = document.getElementById('stl-canvas')
        // console.log("CONTAINER IS : " + stl_container)
		// document.body.appendChild( stl_container );
		camera = new THREE.PerspectiveCamera( 35, width / height, 1, 5000 );
        // camera.position.set( 217, -229, 133 );
        // camera.rotation.set(90 * Math.PI / 180,90 * Math.PI / 180,90 * Math.PI / 180);
        // camera.rotation.y = 90 * Math.PI / 180;
        // camera.rotation.z = 90 * Math.PI / 180;
        // camera.position.set( 3, 0.15, 3 );

		cameraTarget = new THREE.Vector3( 0, 0, -1 );
        // cameraTarget = new THREE.Vector3( 0, -0.25, 0 );
		scene = new THREE.Scene();
		scene.background = new THREE.Color( 0xF4F3EF );
		// scene.fog = new THREE.Fog( 0x72645b, 2, 15 );
        // controls
        controls = new THREE.TrackballControls( camera, stl_container);
        // controls.target.set( 0, 0, 0 );

		// controls.rotateSpeed = 1.0;
		// controls.zoomSpeed = 1.2;
		// controls.panSpeed = 0.8;
        // //
		// controls.noZoom = false;
		// controls.noPan = false;
        // //
		// controls.staticMoving = true;
		// controls.dynamicDampingFactor = 0.3;
        // //
		// controls.keys = [ 65, 83, 68 ];

        stl_container.onclick = function(){
            // console.log("clicked");
            // controls.addEventListener( 'change', render );
        };




		// PLANE
		// var plane = new THREE.Mesh(
		// 	new THREE.PlaneBufferGeometry( 225, 145 ),
		// 	new THREE.MeshPhongMaterial( { color: 0x999999, specular: 0x101010 } )
		// );
		// plane.rotation.x = 0;
		// plane.position.y = 0;
        // // plane.rotation.x = -Math.PI/2;
		// // plane.position.y = -0.5;
        // scene.add( plane );
        // plane.receiveShadow = true;



		// ASCII file
		loader = new THREE.STLLoader();
        // loader.addEventListener( 'load', function ( event ) {
        //     console.log(event.content);
        // });
        // loader.addEventListener( 'progress', function ( event ) {
        //     console.log("total" + event.total);
        //     console.log("progress" + event.loaded);
        // });
		// loader.load( filepath, function ( geometry ) {
		// 	var material = new THREE.MeshPhongMaterial( { color: 0xff5533, specular: 0x111111, shininess: 200 } );
		// 	var mesh = new THREE.Mesh( geometry, material );
		// 	mesh.position.set( 0, 0, 0 );
		// 	mesh.rotation.set( 0, 0, 0 );
		// 	mesh.scale.set( 1, 1, 1 );
		// 	mesh.castShadow = true;
		// 	mesh.receiveShadow = true;
		// 	scene.add( mesh );
		// } );

		// BNIARY FILES
		// var material = new THREE.MeshPhongMaterial( { color: 0xAAAAAA, specular: 0x111111, shininess: 200 } );
		// loader.load( filepath, function ( geometry ) {
		// 	var mesh = new THREE.Mesh( geometry, material );
		// 	mesh.position.set( 0, - 0.37, - 0.6 );
		// 	mesh.rotation.set( - Math.PI / 2, 0, 0 );
		// 	mesh.scale.set( 2, 2, 2 );
		// 	mesh.castShadow = true;
		// 	mesh.receiveShadow = true;
		// 	scene.add( mesh );
		// } );
		// loader.load( './models/stl/binary/pr2_head_tilt.stl', function ( geometry ) {
		// 	var mesh = new THREE.Mesh( geometry, material );
		// 	mesh.position.set( 0.136, - 0.37, - 0.6 );
		// 	mesh.rotation.set( - Math.PI / 2, 0.3, 0 );
		// 	mesh.scale.set( 2, 2, 2 );
		// 	mesh.castShadow = true;
		// 	mesh.receiveShadow = true;
		// 	scene.add( mesh );
		// } );

        // COLORED BINARY STL
		// loader.load( filepath, function ( geometry ) {
		// 	var meshMaterial = material;
		// 	if (geometry.hasColors) {
		// 		meshMaterial = new THREE.MeshPhongMaterial({ opacity: geometry.alpha, vertexColors: THREE.VertexColors });
		// 	}
		// 	var mesh = new THREE.Mesh( geometry, meshMaterial );
		// 	mesh.position.set( 0.5, 0.2, 0 );
		// 	mesh.rotation.set( - Math.PI / 2, Math.PI / 2, 0 );
		// 	mesh.scale.set( 0.3, 0.3, 0.3 );
		// 	mesh.castShadow = true;
		// 	mesh.receiveShadow = true;
		// 	scene.add( mesh );
		// } );

		// Lights
		scene.add( new THREE.HemisphereLight( 0x443333, 0x111122 ) );
		addShadowedLight( 1, 1, 1, 0xffffff, 1.35 );
		addShadowedLight( 0.5, 1, -1, 0xffffff, 1 );

		// renderer
		renderer = new THREE.WebGLRenderer( { antialias: true } );
		renderer.setPixelRatio( width/height );
		renderer.setSize( width, height );
		renderer.gammaInput = true;
		renderer.gammaOutput = true;
		renderer.shadowMap.enabled = true;
		renderer.shadowMap.renderReverseSided = false;
		stl_container.appendChild( renderer.domElement );
		// stats
		// stats = new Stats();
		// stl_container.appendChild( stats.dom );
		//
		window.addEventListener( 'resize', onWindowResize, false );
	}
	function addShadowedLight( x, y, z, color, intensity ) {
		var directionalLight = new THREE.DirectionalLight( color, intensity );
		directionalLight.position.set( x, y, z );
		scene.add( directionalLight );
		directionalLight.castShadow = true;
		var d = 1;
		directionalLight.shadow.camera.left = -d;
		directionalLight.shadow.camera.right = d;
		directionalLight.shadow.camera.top = d;
		directionalLight.shadow.camera.bottom = -d;
		directionalLight.shadow.camera.near = 1;
		directionalLight.shadow.camera.far = 4;
		directionalLight.shadow.mapSize.width = 1024;
		directionalLight.shadow.mapSize.height = 1024;
		directionalLight.shadow.bias = -0.005;
	}
	function onWindowResize() {
        var width = $('#stl-canvas').width();
        var height = $('#stl-canvas').width();
        // console.log("RESIZE WIDTH: "+ width);
        // console.log("RESIZE HEIGHT: "+ height);
		camera.aspect = width / height;
		camera.updateProjectionMatrix();
        controls.handleResize();
		renderer.setSize( width, height );
	}
	function animate() {
		requestAnimationFrame( animate );
        controls.update();
		render();
		// stats.update();
	}
	function render() {
		// var timer = Date.now() * 0.0005;
		// camera.position.x = Math.cos( timer ) * 3;
		// camera.position.z = Math.sin( timer ) * 3;
		camera.lookAt( cameraTarget );
        // console.log(camera.position);
        // console.log(camera.rotation);
            // camera.position.set( 217, -229, 133 );)
        // camera.rotation.x = 90 * Math.PI / 180;
        // console.log("CAMERA X: " + camera.position.x);
        // console.log("CAMERA Y: " + camera.position.y);
        // console.log("CAMERA Z: " + camera.position.z);
        // console.log("CAMERA RX: " + camera.rotation.x);
        // console.log("CAMERA RY: " + camera.rotation.y);
        // console.log("CAMERA RZ: " + camera.rotation.z);
		renderer.render( scene, camera );
	}


    function load_stl(filepath, data){
        var $stl_canvas = $('#stl-canvas');
        var $progressBar = $stl_canvas.find(".progressBar");
        var $progressBarInner = $stl_canvas.find(".progressBar-inner");
        $('#stl-loading').show();
        $progressBarInner.css("width","0%");
        $progressBar.css("opacity",1);
        loader.load(
            filepath,
            function ( geometry ) {
                remove_stl();
                geometry.computeBoundingSphere();
                var centrer_x = -19, centrer_y = -14, centrer_z = -33;
                // if (data){
                //     centrer_x = - data.cog[0];
                //     centrer_y = - data.cog[1];
                //     centrer_z = - data.cog[2];
                // };
                if (geometry.boundingSphere != null){
                    centrer_x = - geometry.boundingSphere.center.x;
                    centrer_y = - geometry.boundingSphere.center.y;
                    centrer_z = - geometry.boundingSphere.center.z;
                    var dist = geometry.boundingSphere.radius / ( Math.tan( camera.fov * Math.PI / 360 ) );
                    camera.position.set( 0, 0, geometry.boundingSphere.radius + dist );
                };
                var material = new THREE.MeshPhongMaterial( { color: 0x2B5E7F, specular: 0x111111, shininess: 200 } );
                mesh = new THREE.Mesh( geometry, material );

                mesh.scale.set( 1, 1 , 1 );
                mesh.position.set( centrer_x, centrer_y, centrer_z );
                mesh.rotation.set( 0, 0, 0 );
                mesh.castShadow = true;
                mesh.receiveShadow = true;
                scene.add( mesh );

                $('#stl-loading').hide();
                $progressBar.css('opacity',0);
        },
        function(event){
            // console.log(event);
            var progress = (event.loaded*100)/event.total;
            console.log('progress: ' + progress)
            $progressBarInner.css("width", progress + "%");
        });
    };

    function remove_stl(){
        if (typeof mesh !== 'undefined') {
            scene.remove(mesh);
        }
    };
    $(".label-info").click(function(){
        load_stl("/static/hub/stl/assemb6.STL");
    });

// END FUNCTION TO INIT A STL CANVAS########################################
});


// URL PARAMETER REDIRECTION////////////////////////////////////////
function refresh_with_parameter(param_name, value){
    var searchParams = new URLSearchParams(window.location.search);

    var page = "&page=1";
    var status = "&status=" + searchParams.get("status");
    var nb_per_page = "&nb-per-page=" + searchParams.get("nb-per-page");
    var search = "&search=" + searchParams.get("search");

    if (param_name == 'page'){
        page = "&page=" + value;
    } else if (param_name == "status") {
        status = "&status=" + value;
    } else if (param_name == "nb-per-page") {
        nb_per_page = "&nb-per-page=" + value;
    } else if (param_name == "search") {
        search = "&search=" + value;
    }

    var params_list = [page, status, nb_per_page, search]
    var params=""
    for (var i in params_list) {
        if (!params_list[i].match(/null/)){
            params += params_list[i];
        }
    };
    console.log("params:" + params);
    console.log( window.location.pathname + "?" + params);
    document.location.href = window.location.pathname + "?" + params;
}
