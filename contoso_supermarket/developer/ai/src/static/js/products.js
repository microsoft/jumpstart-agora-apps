$(document).ready(function() {
    // Save button click handler
    $('.btn-primary').click(function() {
        var id = $(this).data('id');
        var name = $('td:eq(1)', $(this).parent().parent()).text();
        var price = $('td:eq(2)', $(this).parent().parent()).text();
        
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
    });

    // Delete button click handler
    $('.btn-delete').click(function() {
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

    // Add button click handler
    $('#btn-add').click(function() {
        window.location.href = '{{ url_for("add_item") }}';
    });
});