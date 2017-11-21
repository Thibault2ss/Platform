$(document).ready(function(){
    monthNames=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
// ORDER TYPES TOGGLING#####################################
    $(".btn-order-class").click(function(){
        $(".btn-order-class").removeClass("btn-fill");
        $(this).addClass("btn-fill");
        // for rfq
        search_string = '"status": {"id": ' + $(this).val();
        console.log(search_string);
        var rex = new RegExp(search_string, 'i');
        $(".part-row").hide();
        $(".part-row").filter(function () {
            console.log(rex.test($(this).attr('data-part')));
            return rex.test($(this).attr('data-part'));
        }).show();

    });
// end ORDER TYPE TOGGLING ######################################



// REMOVE CAROUSEL AUTO SLIDE#####################################
    $('#ordersCarousel').carousel({
        interval: false
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



// INIT PART DATA ON CLICK ON ONE PART#####################################
    $(".part-row").click(function(){
        // load part data
        var part = $(this).data('part');
        var part_images = $(this).data('part-images');
        // console.log(part_images);
        console.log(part);

        // populate images
        $('#imageCarousel').slick('removeSlide', null, null, true);
        for (var i = 0; i < part_images.length; i++){
            $('#imageCarousel').slick('slickAdd','<img src="' + part_images[i] + '">');
        };
        setTimeout(function(){$('#imageCarousel').slick('setPosition');},250);

        // populate info
        var name, ref, material, length, dimension_unit, weight_unit, date_created, model, bulk_files, color, grade_list, environment_list, status
        name = part.fields.name;
        ref = part.fields.reference;
        if (part.fields.material){material = part.fields.material.name}else{material=null};
        length = part.fields.length, width = part.fields.width, height = part.fields.height, weight = part.fields.weight;
        dimension_unit = part.fields.dimension_unit, weight_unit = part.fields.weight_unit;
        date_created = new Date(part.fields.date_created);
        date_created = date_created.getDate() + " " + monthNames[date_created.getMonth()] + " " + date_created.getFullYear();
        model = part.fields.model;
        color = part.fields.color;
        grade_list = part.fields.grade;
        status = part.fields.status;
        environment_list = part.fields.environment;
        bulk_files = $(this).data("part-bulk-files");
        $("#part-detail-panel").data("part-id",part.pk);
        $(".part-dimensions").text(length + "x" + width + "x" + height + " " + dimension_unit);
        $(".part-weight").text(weight + " " + weight_unit);
        $(".part-name").text(name);
        $(".part-material").text(material);
        $(".part-ref").text(ref);
        $(".part-color").text(color);
        $(".part-status").removeClass().addClass("label part-status").text(status.name);
        if (status.id>=1){
            $(".part-status").addClass("label-default");
            $("#button-action-1").removeClass().addClass("btn btn-warning btn-fill btn-wd request-for-indus-button order-part-button").text("Request Indus");
        };
        if (status.id>=2){
            $(".part-status").addClass("label-warning");
            $("#button-action-1").removeClass().addClass("btn btn-default btn-fill btn-wd disabled").text("Indus Pending");
        };
        if (status.id>=3){
            $(".part-status").addClass("label-danger");
            $("#button-action-1").removeClass().addClass("btn btn-danger btn-fill btn-wd disabled").text("Not Printable");
        };
        if (status.id>=4){
            $(".part-status").addClass("label-success");
            $("#button-action-1").removeClass().addClass("btn btn-success btn-fill btn-wd print-request-button").text("Print");
        };
        $(".id_part").val(part.pk);
        $("#models-attached").empty();
        for (var i = 0; i < model.length; i++){
            var html = "<div class='col-sm-6 col-xs-12'>\
                            <span class='text-muted' style='float:left;font-size:70%;'>Model</span><br>\
                            <div class='part-model' style='margin-left:15px;'>" + model[i].name + "</div>\
                        </div>\
                        <div class='col-sm-6 col-xs-12'>\
                            <span class='text-muted' style='float:left;font-size:70%;'>Family</span><br>\
                            <div class='part-family' style='margin-left:15px;'>" + model[i].family + "</div>\
                        </div>";
            $("#models-attached").append(html);
        };
        $("#grades-attached").empty();
        for (var i = 0; i < grade_list.length; i++){
            var html = "<div class='col-sm-12 col-xs-12'>\
                            <span class='text-muted' style='float:left;font-size:70%;'>Grade</span><br>\
                            <div class='part-grade' style='margin-left:15px;'>" + grade_list[i].name + "</div>\
                        </div>";
            $("#grades-attached").append(html);
        };
        $("#environments-attached").empty();
        for (var i = 0; i < environment_list.length; i++){
            var html = "<div class='col-sm-12 col-xs-12'>\
                            <span class='text-muted' style='float:left;font-size:70%;'>Environment</span><br>\
                            <div class='part-grade' style='margin-left:15px;'>" + environment_list[i].name + "</div>\
                        </div>";
            $("#environments-attached").append(html);
        };
        $(".file-list").empty();
        for (var i = 0; i < bulk_files.length; i++){
            var html = "\
                        <div class='file-row' data-id='" +  bulk_files[i].id + "'><a href='" + bulk_files[i].url + "' target='_blank'>\
                            <i class='ti-download'></i>" + bulk_files[i].name + "</a>\
                            <div class='remove-file remove-icon'><i class='ti-close'></i></div>\
                        </div>"
            if (bulk_files[i].type == "3D" || bulk_files[i].type == "2D"){
                $("#part3dfile_form").find(".file-list").append(html);
            } else {
                $("#partbulkfile_form").find(".file-list").append(html);
            }
        };

        // refresh buttons listeners
        refreshButtons();
        //get Part HISTORY and scroll to bottom of history
        getPartHistory(part.pk, date_created);
        setTimeout(function(){
            $("#timeline-card").animate({ scrollTop: $('#timeline-card').prop("scrollHeight")}, 1000);
        },500);

        // to resize the stl canvas
        setTimeout(function(){
            onWindowResize();
        }, 100);
    });
// END INIT ORDERS DATA ON CLICK ON ONE ORDER#####################################


    $("#stl-demo").click(function(){
        $(this).remove();
        // populate stl dynamic view
        load_stl("/static/hub/stl/assemb6.STL");
    });


// SENDING BULK FILES ASYNCHRONOUSLY#############################################
// NOW I USE DROPZONE INSTEAD OF THIS##################################################################################
    $("#partbulkfile_form").submit(function(event){
        event.preventDefault();
        var $form = $(this);
        var data = new FormData(this);
        // console.log("received");
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
            maxFilesize: 5, // MB
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
                    if (response.success=true){
                        $form.find(".progressBar-inner").css("background-color","green");
                    } else {
                        $form.find(".progressBar-inner").css("background-color","red");
                    };
                    // update part-row:
                    for (var i = 0; i < response.files_success.length; i++){
                        console.log("it pushed");
                        $(".part-row[data-part-id='" + response.id_part + "']").data("part-bulk-files").push(response.files_success[i]);
                        $form.find(".file-list").append("\
                            <div class='file-row' data-id='" + response.files_success[i].id + "'><a href='" + response.files_success[i].url + "' target='_blank'>\
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
                        $('.request-for-indus-button').removeClass().addClass("btn btn-default btn-fill btn-wd disabled");
                        var date_now = new Date();
                        $("span[data-status-id='2']").removeClass().addClass("label label-warning");
                        $(".part-date-requested-indus").text(date_now.getDate() + " " + monthNames[date_now.getMonth()] + " " + date_now.getFullYear());
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
        $('.remove-file').off();
        $(".remove-file").click(function(){
            removeFile($(this).closest(".file-row").data("id"));
        });


    };
    refreshButtons();
// END REQUEST FOR INDUSTRIALIZATION######################################################################




// GET PART HISTORY######################################################################

    function getPartHistory(id_part, date_created){
        $.ajax({
            url: '/digital/parts/get-part-history/',
            data:{
                'id_part':id_part,
            },
            dataType:'json',
            success:function(data){
                if (data.success){
                    console.log(JSON.parse(data.events));
                    fillTimeline(date_created, JSON.parse(data.events));
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

    function fillTimeline(date_created, events){
        $("#timeline-card").empty();
        $("#timeline-card").append(get_HTML_Timeline(date_created, "label", "default", "Created", "Part was created"));
        for (var i = 0; i < events.length; i++){
            var event = events[i].fields;
            var date = new Date(event.date);
            date = date.getDate() + " " + monthNames[date.getMonth()] + " " + date.getFullYear();
            var short_description = event.short_description;
            var label_type, label_class, label_text, last, warning;
            warning = false;
            if (events[i].fields.type == "STATUS_CHANGE"){
                label_type = "label";
                if (event.status.id == 2){
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
            if (i == events.length - 1){last = true}else{last = false};
            $("#timeline-card").append(get_HTML_Timeline(date, label_type, label_class, label_text, event.short_description, last = last, warning = warning));

        };

    };

    function get_HTML_Timeline(date, label_type, label_class, label_text, description, last = false, warning = false){
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
                <span class='text-muted' style='font-size:80%;'>" + date + "</span>\
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
                    // $form.find(".progressBar-inner").css("background-color","green");
                    console.log(JSON.parse(data.part));
                } else {
                    // $form.find(".progressBar-inner").css("background-color","red");
                    console.log(data);
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
//END ADDING NEW PART////////////////////////////////////////////////////////////////////////


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
		camera = new THREE.PerspectiveCamera( 35, width / height, 1, 1500 );
		camera.position.set( 18, 25, 68 );
        // camera.position.set( 217, -229, 133 );
        camera.rotation.set(-0.35,0.24,0.01);
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
		addShadowedLight( 0.5, 1, -1, 0xffaa00, 1 );

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


    function load_stl(filepath){
        loader.load( filepath, function ( geometry ) {
            if (typeof mesh !== 'undefined') {
                scene.remove( mesh );
            };
            var material = new THREE.MeshPhongMaterial( { color: 0xff5533, specular: 0x111111, shininess: 200 } );
            mesh = new THREE.Mesh( geometry, material );
            mesh.position.set( -19, -14, -33 );
            mesh.rotation.set( 0, 0, 0 );
            mesh.scale.set( 1, 1, 1 );
            mesh.castShadow = true;
            mesh.receiveShadow = true;
            scene.add( mesh );
        });
    };

    function remove_stl(){
        scene.remove(mesh);
    };
    $(".label-info").click(function(){
        load_stl("/static/hub/stl/assemb6.STL");
    });

// END FUNCTION TO INIT A STL CANVAS########################################
});
