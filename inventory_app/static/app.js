(function(window, document) {
    const m = window.m;

    const appData = {
        merchantName: "",
        inventory: [],
    }

    const ProductOrderForm = function(initialVnode) {
        let product = null;
        let ordered = false;
        return {
            placeOrder: function(event) {
                event.preventDefault();
                const quantity = parseInt(event.target.elements['orderQuantity'].value)
                const formData = new FormData()
                if (quantity !== NaN && quantity > 0) {
                    formData.append('quantity', quantity)
                    m.request({
                        method: 'POST',
                        url: `/inventory/${product.id}/order/`,
                        body: formData
                    }).then(function(data) {
                        product.ordered = data.ordered;
                        ordered = true;
                    }).catch(function() {
                        alert('Error ordering');
                    })
                }
            },
            view: function(vnode) {
                product = vnode.attrs.product
                return ordered ? m('', 'Order placed!') : m('form', {
                    onsubmit: this.placeOrder
                }, [
                    m('input', { 'type': 'number', 'name': 'orderQuantity' }),
                    m('button', { 'type': 'submit' }, 'Order!')
                ])
            }
        }
    }

    const InventoryApp = {
        data: appData,
        oninit: function() {
            this.syncInventory();
            this.fetchMerchantName();
        },
        view: function() {
            return m("main", [
                m("h1", { class: "title" }, this.data.merchantName ? `Inventory for ${this.data.merchantName}` : 'Inventory'),
                m("table", { id: 'inventory-table' }, [
                    m("tr", [
                        m('th', 'Name'), m('th', 'Stock'), m('th', 'Ordered'), m('th', 'Order more')
                    ]),
                    this.data.inventory.map(function(it) {
                        return m("tr", { key: it.id }, [m('td', it.name), m('td', it.stock || 0), m('td', it.ordered || 0), m('td', m(ProductOrderForm, { product: it }))]);
                    })
                ])
            ])
        },
        fetchInventory: function() {
            return m.request({
                url: '/inventory/'
            })
        },
        fetchMerchantName: function() {
            return m.request({
                url: '/merchant-name/',
                extract: function(xhr) { return xhr }
            }).then(function(response) {
                if (response.status == 200) {
                    this.data.merchantName = response.responseText;
                }
            }.bind(this))
        },
        syncInventory: function() {
            const promise = this.fetchInventory();
            const app = this
            promise.then(function(items) {
                app.data.inventory.length = 0;
                items.forEach(function(it) {
                    app.data.inventory.push(it);
                })
            });
            this.data.inventory.length = 0; // empty inventory
        }
    };
    m.mount(document.body, InventoryApp);
})(window, document);