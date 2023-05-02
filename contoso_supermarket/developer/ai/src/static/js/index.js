$( document ).ready(function() {
    $("#success-alert").hide();
    $("#error-alert").hide();
});

function addPurchase(productId) {
    return;

    $.ajax({
        type: "POST",
        url: "/addPurchase",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({ ProductId: productId }), 
        success: function(message){
            if(message == "Ok"){
                $("#success-alert").fadeTo(2000, 500).slideUp(500, function () {
                    $("#success-alert").slideUp(500);
                });
            }
            else{
                $("#error-alert").fadeTo(2000, 500).slideUp(500, function () {
                    $("#error-alert").slideUp(500);
                });
            }
        },
        error: function(error){
            $("#error-alert").fadeTo(2000, 500).slideUp(500, function () {
                $("#error-alert").slideUp(500);
            });
        }
      });
};
