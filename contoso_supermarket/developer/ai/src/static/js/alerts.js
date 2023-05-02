
  const alertPlaceholder = document.getElementById('liveAlertPlaceholder')

  const alert = (message, type) => {
    const wrapper = document.createElement('div')
    wrapper.innerHTML = [
      `<div class="alert alert-${type} alert-dismissible" role="alert">`,
      `   <div>${message}</div>`,
      '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
      '</div>'
    ].join('')

    alertPlaceholder.append(wrapper)
  }

  $(document).ready(function(){
    $(".add-to-cart").click(function(){
      var product_id = $(this).attr('data-product');
      var product_name = $(this).attr('data-product-name');
      var product_price = $(this).attr('data-product-price');
      $.ajax({
        url: "/add_to_cart",
        type: "POST",
        data: { 
          product_id: product_id,
          product_name: product_name,
          product_price: product_price
         },
        success: function(response){
          //alert(response);
        },
        error: function(xhr){
          alert("An error occured: " + xhr.status + " " + xhr.statusText);
        }
      });
    });
  });