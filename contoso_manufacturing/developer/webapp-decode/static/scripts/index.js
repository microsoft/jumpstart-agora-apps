$(document).ready(function() {

    /**
     * Handles the click event for the #Enterprise element.
     */
    $('.level1 #Enterprise').on("click", function() {
        zoomToLevel(2, 'enterprise');
    });

    /**
     * Handles the click event for the #Site element.
     */
    $('.level1 #Site').on("click", function() {
        zoomToLevel(2, 'site');
    });

    /**
     * Handles the click event for the #Welding element.
     */
    $('.level2 .site #Welding').on("click", function() {
        zoomToLevel(3, 'site', "welding", "Welding");
    });

    /**
     * Handles the click event for the #RoboticArm element.
     */
    $('.level2 .site #RoboticArm').on("click", function() {
        zoomToLevel(3, 'site', "human-pose-estimation", "Pose Estimation");
    });

    /**
     * Handles the click event for elements with id starting with "Field_Maintenance" under .level2 .site.
     */
    $('.level2 .site [id^="Field_Maintenance"]').on("click", function() {
        zoomToLevel(3, 'site', "safety-yolo8", "Helmet Detection");
    });

    /**
     * Handles the click event for elements with id starting with "Site_IT_Engineer" under .level2 .site.
     */
    $('.level2 .site [id^="Site_IT_Engineer"]').on("click", function() {
        console.log("Site_IT_Engineer clicked");
        zoomToLevel(3, 'site', "yolov8n", "Object Detection");
    });

    /**
     * Handles the click event for the #SystemAdmin element.
     */
    $('.level2 .enterprise #SystemAdmin').on("click", function() {
        zoomToLevel(3, 'enterprise', "infra", "Infrastructure Monitoring");
    });

    /**
     * Handles the click event for the #BusinessDecisionMaker element.
     */
    $('.level2 .enterprise #BusinessDecisionMaker').on("click", function() {
        zoomToLevel(3, 'enterprise', "aimetrics", "AI Inferencing Metrics");
    });
});

/**
 * Shows an element with a transition effect.
 * @param {string} selector - The CSS selector of the element to show.
 */
function showWithTransition(selector) {
    $(selector)
        .css('opacity', '0') // Set initial opacity to 0
        .show() // Show the element (if it's hidden)
        .animate({ opacity: 1 }, 800, 'linear'); // Animate opacity to 1 over 0.5 seconds
}

/**
 * Retrieves the URL for the specified iframe name and sets it as the source of the iframe element.
 * @param {string} iframeName - The name of the iframe.
 */
function getIframeUrl(iframeName){
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/iframe?name=' + iframeName);
    xhr.onload = function() {
        if (xhr.status === 200) {
            var url = xhr.responseText;
            window.open(url, '_blank');   
        } else {
            console.log('Request failed.  Returned status of ' + xhr.status);
        }
    };
    xhr.send();
}

/**
 * Zooms to the specified level and updates the UI accordingly.
 * @param {number} level - The level to zoom to.
 * @param {string} type - The type of the zoom (site or enterprise).
 * @param {string} video - The video name (optional).
 * @param {string} scenario - The scenario name (optional).
 */
function zoomToLevel(level, type = "", video = "", scenario = "") {
    if (level == 0) {
        showWithTransition(".level0");
        $(".level1").hide();
        $(".bd-level1").hide();
        $(".level2").hide();
        $(".bd-level2").hide();
        $(".level3").hide();
        $(".bd-level3").hide();
    } else if (level == 1) {
        $(".level0").hide();
        showWithTransition(".level1");
        $(".bd-level1").show();
        $(".bd-level2").hide();
        $(".level2").hide();
        $(".level3").hide();
        $(".bd-level3").hide();
    } else if (level == 2) {
        $(".level0").hide();
        $(".level1").hide();
        $(".bd-level1").show();
        if (type == "site") {
            $(".bd-level2.site").show();
            $(".level2 .site").show();
            $(".level2 .enterprise").hide();
            $("#imgContainer").hide();
        } else {
            $(".bd-level2.enterprise").show();
            $(".level2 .site").hide();
            $(".level2 .enterprise").show();
            $("#imgContainer").hide();
        }
        $("#caseContainer").addClass("col-md-12");
        $("#caseContainer").removeClass("col-md-6");
        showWithTransition(".level2");
        $(".level3").hide();
        $(".bd-level3").hide();
        $("#imgContainer").hide();
        $("#imgVideoPreview").attr("src", "/static/images/video_placeholder.png");
    } else if (level == 3) {
        $(".level0").hide();
        $(".level1").hide();
        $(".bd-level1").show();
        if (type == "site") {
            $(".bd-level2.site").show();
            $(".level2 .site").show();
            $(".level2 .enterprise").hide();
            $("#imgContainer").show();
            $("#imgVideoPreview").attr("src", `/video_feed?video=${video}`);
            $("#caseContainer").addClass("col-md-6");
            $("#caseContainer").removeClass("col-md-12");
        } 
        else {
            $(".bd-level2.enterprise").show();
            $(".level2 .site").hide();
            $(".level2 .enterprise").show();
            if(video == "infra"){
                video = "infra_monitoring";
                $("#imgContainer").show();;
                $("#imgVideoPreview").attr("src", "/static/images/adx.png");
            }
            else{
                $("#imgContainer").hide();
            }
            getIframeUrl(video);
        }
     
        showWithTransition(".level2");
        $(".bd-level3").html(scenario);
        $(".bd-level3").show();
    }
}