jQuery(document).ready(function($) {
    // CART AJAX LOAD
    function get_cart_widget(){
        $.ajax({
            url: '/store/cart/cart_widget/',
            dataType: 'HTML',
            success: function(response) {
                $('[data-store="cart-widget"]').html(response)
                $('body').trigger('titovantoncore.store.cart-widget-loaded')
            }
        })
    }
    get_cart_widget()

    // ADD TO CART MODALS
    $('[data-store="add-to-cart"]').click(function(){
        $('[data-store="add-to-cart-modal"]')
            .data('titovantoncore.store.add-to-cart-form', $(this).parents('form'))
            .modal()
        return false
    })
    $('[data-store="add-to-cart-action"]').on('click', function(){
        var $this = $(this),
            $modal = $this.parents('[data-store="add-to-cart-modal"]'),
            $form = $modal.data('titovantoncore.store.add-to-cart-form'),
            data = $form.serialize()
        if (!$this.data('titovantoncore.store.busy')) {
            $this.data('titovantoncore.store.busy', true)
            $this.css({cursor: 'wait'})
            $.ajax({
                url: '/store/cart/add/',
                type: 'POST',
                data: data,
                async: false,
                success: function(response) {
                    if ($this.attr('data-action')) {
                        window.self.location = $this.attr('data-action')
                    }
                    else {
                        $modal.modal('hide')
                        get_cart_widget()
                    }
                    $this.data('titovantoncore.store.busy', false)
                    $this.css({cursor: 'pointer'})
                }
            })
        }
    })
});
