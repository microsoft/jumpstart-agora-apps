$(document).ready(function() {

    // Save button click handler
    $('#btn-save-products').click(function() {
        //open the modal
        $('#saveProductConfirmationModal').modal('show');
    });

    // Confirm Save button click handler
    $('#btn-confirm-save-products').click(function() {
        $('#saveProductConfirmationModal').modal('hide');
        var id = $(this).data('id');
        var name = $('td:eq(1)', $(this).parent().parent()).text();
        var rawPrice = $('td:eq(2)', $(this).parent().parent()).text().replace("$","");

        var price = Number(rawPrice);
        if(isNaN(price)) {
            alert(`Unable to save item '${id}' due to invalid price '${rawPrice}'... `)
        }else{
            $.ajax({
                url: '/update_item',
                method: 'POST',
                data: {
                    id: id,
                    name: name,
                    price: price,
                },
                success: function(response) {
                    alert(response, "alert");
                },
                error: function(xhr) {
                    alert('Error: ' + xhr.status + ' ' + xhr.statusText);
                }
            });
        }
    });

    // Delete button click handler
    $('.btn-delete-product').click(function() {
        //pass the id through to the modal
        var id = $(this).data('id');
        $("#deleteProductConfirmationModal #btn-confirm-delete-product").data('id', id);

        //open the modal
        $('#deleteProductConfirmationModal').modal('show');
    });

    // Confirm Delete button click handler
    $('.btn-confirm-delete-product').click(function() {
        var id = $(this).data('id');
        if (confirm('Are you sure you want to delete this item?')) {
            $.ajax({
                url: '/delete_item',
                method: 'POST',
                data: {
                    id: id
                },
                success: function(response) {
                    $('#item-' + id).remove();
                    alert(response);
                },
                error: function(xhr) {
                    alert('Error: ' + xhr.status + ' ' + xhr.statusText);
                }
            });
        }
    });
});