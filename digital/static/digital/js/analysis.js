$(document).ready(function(){


    // UPLOAD CSV PRINTABILITY PREDICTION################################################
        $("#form_printability_analysis").submit(function(event){
            event.preventDefault();
            var $form = $(this);
            var $wait_screen = $(this).closest(".card").find(".wait-screen");
            var data = new FormData(this);
            $.ajax({
                url: '/digital/analysis/bulk-part-upload/',
                data: data,
                cache: false,
                contentType: false,
                processData: false,
                method: 'POST',
                type: 'POST', // For jQuery < 1.9
                beforeSend:function(XMLHttpRequest, settings){
                    $wait_screen.css("display", "flex");
                },
                success: function(data){
                    console.log(data);
                    if (data.success){
                        $wait_screen.css("background-color", "rgba(170, 255, 203, 0.7)");
                        setTimeout(function(){location.reload();}, 1000);
                    }else{
                        $wait_screen.css("background-color", "rgba(255, 207, 207,0.7)");
                    }
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    console.log("Status: " + textStatus); console.log("Error: " + errorThrown);
                    $wait_screen.css("background-color", "rgba(255, 207, 207,0.7)");
                },
                complete:function(jqXHR, textStatus){
                    setTimeout(function(){
                        $wait_screen.css("background-color", "rgba(255, 255, 255,0.7)");
                        $wait_screen.css("display", "none");
                    },2000);
                },
            });
        });

    // END UPLOAD CSV PRINTABILITY PREDICTION################################################






// BAR CHART FOR PART TYPE DISTRIB#####################################################
    var parttype_labels = [];
    var serie = [];
    for (var i = 0; i<parttype_distrib.length; i++){
        parttype_labels.push(parttype_distrib[i].type__name);
        serie.push(parttype_distrib[i].count);
    };
    var dataViews = {
        labels: parttype_labels,
          series: [
             serie
          ]
    };
    var optionsViews = {
        height: "250px",
        seriesBarDistance: 10,
        reverseData: true,
        horizontalBars: true,
      classNames: {
        bar: 'ct-bar'
      },
      axisY: {
          offset: 70
      },
      axisX: {
        showGrid: true,
        divisor:2
      },

    };
    var responsiveOptionsViews = [
      ['screen and (max-width: 640px)', {
        seriesBarDistance: 5,
        axisX: {
          labelInterpolationFnc: function (value) {
            return value[0];
          }
        }
      }]
    ];
    var chart_parttype = Chartist.Bar('#partTypeBarChart', dataViews,optionsViews, responsiveOptionsViews);
// END BAR CHART FOR PART TYPE DISTRIB#####################################################








// BAR CHART FOR TECHNOMATERIAL DISTRIB#####################################################
    var technomaterial_labels = [];
    var serie = [];
    for (var i = 0; i<techno_material_distrib.length; i++){
        technomaterial_labels.push(techno_material_distrib[i].final_card__techno_material__technology__name + " + " + techno_material_distrib[i].final_card__techno_material__material__name);
        serie.push(techno_material_distrib[i].count);
    };
    var dataViews = {
        labels: technomaterial_labels,
          series: [
             serie
          ]
    };
    var optionsViews = {
        height: "250px",
        seriesBarDistance: 10,
        reverseData: true,
        horizontalBars: true,
      classNames: {
        bar: 'ct-bar'
      },
      axisY: {
          offset: 70
      },
      axisX: {
        showGrid: true,
        divisor:2
      },

    };
    var responsiveOptionsViews = [
      ['screen and (max-width: 640px)', {
        seriesBarDistance: 5,
        axisX: {
          labelInterpolationFnc: function (value) {
            return value[0];
          }
        }
      }]
    ];
    var chart_parttype = Chartist.Bar('#TechnoMaterialDistrib', dataViews,optionsViews, responsiveOptionsViews);
// END BAR CHART FOR PART TYPE DISTRIB#####################################################







// PIE CHART APPLIANCE FAMILY DISTRIB######################################################
    var app_fam_labels = [];
    var serie = [];
    if (total_parts == 0){total_parts=1};//safety

    for (var i = 0; i<appliance_fam_distrib.length; i++){
        var percent = (appliance_fam_distrib[i].count*100)/total_parts;
        app_fam_labels.push(appliance_fam_distrib[i].type__appliance_family__name + ": " + percent.toFixed(0) + '%' );
        serie.push(appliance_fam_distrib[i].count);
    };

    var dataPreferences = {
        series:serie,
        labels: app_fam_labels
    };

    var optionsPreferences = {
        donut: true,
        showLabel: false,
        donutWidth: 60,
        startAngle: 0,
        total: total_parts,
        showLabel: true,
    };

    var chart3 = Chartist.Pie('#ApplianceFamilyPieChart', dataPreferences, optionsPreferences);
// END PIE CHART APPLIANCE FAMILY DISTRIB######################################################
});
