$( document ).ready(function() {
    $('.level1 #Enterprise').on("click", function(){ 
        zoomToLevel(2, 'enterprise')
    });

    $('.level1 #Site').on("click", function(){ 
        zoomToLevel(2, 'site')
    });

    $('.level2 .site #Welding').on("click", function(){ 
        zoomToLevel(3, 'site', "welding", "Welding" )
    });

    $('.level2 .site #RoboticArm').on("click", function(){ 
        zoomToLevel(3, 'site', "yolov8n", "Pose Estimation" )
    });

    $('.level2 .site [id^="Field_Maintenance"]').on("click", function(){ 
        zoomToLevel(3, 'site', "safety-yolo8", "Helmet Detection" );
    });

    $('.level2 .enterprise #SystemAdmin').on("click", function(){ 
        zoomToLevel(3, 'enterprise', "infra", "Infrastructure Monitoring" )
    });

    $('.level2 .enterprise #BusinessDecisionMaker').on("click", function(){ 
        zoomToLevel(3, 'enterprise', "aimetrics", "AI Inferencing Metrics" )
    });
});

function showWithTransition(selector) {
    $(selector)
        .css('opacity', '0') // Set initial opacity to 0
        .show() // Show the element (if it's hidden)
        .animate({ opacity: 1 }, 800, 'linear'); // Animate opacity to 1 over 0.5 seconds
}

function zoomToLevel(level, type = "", video = "", scenario = "") {
    if (level == 0) {
        showWithTransition(".level0");
        $(".level1").hide();
        $(".bd-level1").hide();
        $(".level2").hide();
        $(".bd-level2").hide();
        $(".level3").hide();
        $(".bd-level3").hide();
    }
    else if (level == 1) {
        $(".level0").hide();
        showWithTransition(".level1");
        $(".bd-level1").show();
        $(".bd-level2").hide();
        $(".level2").hide();
        $(".level3").hide();
        $(".bd-level3").hide();
    }
    else if (level == 2) {
        $(".level0").hide();
        $(".level1").hide();
        $(".bd-level1").show();
        if (type == "site") {
            $(".bd-level2.site").show();
            $(".level2 .site").show();
            $(".level2 .enterprise").hide();
            $("#imgContainer").hide();
            $("#iframeContainer").hide();
        }
        else {
            $(".bd-level2.enterprise").show();
            $(".level2 .site").hide();
            $(".level2 .enterprise").show();
            $("#imgContainer").hide();
            $("#iframeContainer").hide();  
        }
        $("#caseContainer").addClass("col-md-12");
        $("#caseContainer").removeClass("col-md-6");
        showWithTransition(".level2");
        $(".level3").hide();
        $(".bd-level3").hide();
        $("#imgContainer").hide();
        $("#imgVideoPreview").attr("src", "/static/images/video_placeholder.png");

    }
    else if (level == 3) {
        $(".level0").hide();
        $(".level1").hide();
        $(".bd-level1").show();
        if (type == "site") {
            $(".bd-level2.site").show();
            $(".level2 .site").show();
            $(".level2 .enterprise").hide();
            $("#imgContainer").show();
            $("#iframeContainer").hide();
        }
        else {
            $(".bd-level2.enterprise").show();
            $(".level2 .site").hide();
            $(".level2 .enterprise").show();
            $("#imgContainer").hide();
            $("#iframeContainer").show();
        }
        $("#caseContainer").addClass("col-md-6");
        $("#caseContainer").removeClass("col-md-12");
        showWithTransition(".level2");
        $(".bd-level3").html(scenario);
        $(".bd-level3").show();
        
        $("#imgVideoPreview").attr("src", `/video_feed?video=${video}`);
    }
}