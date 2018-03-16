$(document).ready(function() {
    $('[data-role=item_name]').on('click', '[data-action=plus]', function(e){
        var $item_name = $(e.delegateTarget);
        var $plus = $(e.currentTarget);
        var $item_qty = $item_name.find('[data-role=item_qty]');
        var list_id = $plus.data("list_id");
        var food_item = $plus.data("food_item");
        $.get('/groceryList/increment/', {list_id: list_id, food_item: food_item}, function(data){
            $item_qty.html(data);
        });
    });
});

$(document).ready(function() {
    $('[data-role=item_name]').on('click', '[data-action=minus]', function(e){
        var $item_name = $(e.delegateTarget);
        var $minus = $(e.currentTarget);
        var $item_qty = $item_name.find('[data-role=item_qty]');
        var list_id = $minus.data("list_id");
        var food_item = $minus.data("food_item");
        $.get('/groceryList/decrement/', {list_id: list_id, food_item: food_item}, function(data){
            $item_qty.html(data);
        });
    });
});

