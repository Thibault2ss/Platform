$(document).ready(function(){
    monthNames=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
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
                variableWidth: true
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
        setTimeout(function(){$('#imageCarousel').slick('setPosition');},150);

        // populate info
        var name, ref, material, length, dimension_unit, weight_unit, date_created, model, bulk_files, color, grade_list, environment_list, status
        name = part.fields.name;
        ref = part.fields.reference;
        if (part.fields.material){material = part.fields.material.name}else{material=null};
        length = part.fields.length, width = part.fields.width, height = part.fields.height, weight = part.fields.weight;
        dimension_unit = part.fields.dimension_unit, weight_unit = part.fields.weight_unit;
        date_created = new Date(part.fields.date_created);
        model = part.fields.model;
        color = part.fields.color;
        grade_list = part.fields.grade;
        status = parseInt(part.fields.status);
        environment_list = part.fields.environment;
        bulk_files = $(this).data("part-bulk-files");
        $("#part-detail-panel").data("part-id",part.pk);
        $(".part-date").text("");
        $(".part-date-created").text(date_created.getDate() + " " + monthNames[date_created.getMonth()] + " " + date_created.getFullYear());
        $(".part-dimensions").text(length + "x" + width + "x" + height + " " + dimension_unit);
        $(".part-weight").text(weight + " " + weight_unit);
        $(".part-name").text(name);
        $(".part-material").text(material);
        $(".part-ref").text(ref);
        $(".part-color").text(color);
        $(".row-status").find("span").removeClass();
        if (status>=1){
            $("span[data-status-id='1']").addClass("label label-default");
            $("#button-action-1").removeClass().addClass("btn btn-warning btn-fill btn-wd request-for-indus-button order-part-button").text("Request Indus");
        };
        if (status>=2){
            $("span[data-status-id='2']").addClass("label label-warning");
            $("#button-action-1").removeClass().addClass("btn btn-default btn-fill btn-wd disabled").text("Indus Pending");
        };
        if (status>=3){
            $("span[data-status-id='3']").addClass("label label-danger").text("Not Printable");
            $("#button-action-1").removeClass().addClass("btn btn-danger btn-fill btn-wd disabled").text("Not Printable");
        };
        if (status>=4){
            $("span[data-status-id='3']").removeClass().addClass("label label-success").text("Digitalized");
            $("#button-action-1").removeClass().addClass("btn btn-success btn-fill btn-wd print-request-button").text("Print");
        };
        $("#id_part").val(part.pk);
        $("#models-attached").empty();
        for (var i = 0; i < model.length; i++){
            var html = "<div class='row text-center' style='margin-bottom:10px;'>\
                        <div class='col-sm-6 col-xs-12'>\
                            <span class='text-muted' style='float:left;font-size:70%;'>Model</span><br>\
                            <div class='part-model' style='margin-left:15px;'>" + model[i].name + "</div>\
                        </div>\
                        <div class='col-sm-6 col-xs-12'>\
                            <span class='text-muted' style='float:left;font-size:70%;'>Family</span><br>\
                            <div class='part-family' style='margin-left:15px;'>" + model[i].family + "</div>\
                        </div>\
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
        $("#environment-attached").empty();
        for (var i = 0; i < environment_list.length; i++){
            var html = "<div class='col-sm-12 col-xs-12'>\
                            <span class='text-muted' style='float:left;font-size:70%;'>Grade</span><br>\
                            <div class='part-grade' style='margin-left:15px;'>" + environment_list[i].name + "</div>\
                        </div>";
            $("#environment-attached").append(html);
        };
        $("#bulk-file-list").empty();
        for (var i = 0; i < bulk_files.length; i++){
                $("#bulk-file-list").append("<div class='file-row'><a href='" + bulk_files[i].url + "' target='_blank'><i class='ti-download'></i></href> " + bulk_files[i].name + "</a></div>");
        };

        // refresh buttons listeners
        refreshButtons();
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

    $("#partbulkfile_form").dropzone({
        url: "/digital/parts/upload-part-bulk-file/",
        paramName: "file", // The name that will be used to transfer the file
        maxFilesize: 5, // MB
        createImageThumbnails: false,
        // clickable: true,
        // acceptedFiles:".stl,.sldprt,.step,.ico",
        accept: function(file, done) {
            if (file.name == "justin.jpg") {
              done("Naha, you don't.");
            }
            else { done(); }
        },
        init: function () {
            var $form = $("#partbulkfile_form");
            this.on("sending", function(file, xhr, formData) {
            //    formData.append("csrfmiddlewaretoken", csrftoken);
                $form.find(".progressBar-inner").css("background-color","#6dbad8");
                $form.find(".progressBar").css("opacity",1);
            });
            this.on('uploadprogress',function(file, progress, bytesSent){
                $(".progressBar-inner").css("width", progress + "%");
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
                    $("#bulk-file-list").append("<div class='file-row'><a href='" + response.files_success[i].url + "' target='_blank'><i class='ti-download'></i></href> " + response.files_success[i].name + "</a></div>");
                };
            });
        },
        error:function(file, response){
            console.log(response.message);
            $("#partbulkfile_form").find(".progressBar-inner").css("background-color","red");
        },
    });
// END SENDING BULK FILES ASYNCHRONOUSLY#############################################



// REQUEST FOR INDUSTRIALIZATION######################################################################
    function refreshButtons(){
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
                        updated_part.fields.status = 2;
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
    };
    refreshButtons();
// END REQUEST FOR INDUSTRIALIZATION######################################################################


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