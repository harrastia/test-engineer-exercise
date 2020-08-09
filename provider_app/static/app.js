(function(window, document) {
    const m = window.m;

    const appData = {
        orders: [],
        products: [],
        syncProducts: function() {
            return m.request({
                url: '/products/'
            }).then(function(results) {
                this.products.length = 0;
                results.forEach(function(it) {
                    this.products.push(it);
                }.bind(this));
            }.bind(this))
        },
        syncOrders: function() {
            return m.request({
                url: '/orders/'
            }).then(function(results) {
                this.orders.length = 0;
                results.forEach(function(it) {
                    this.orders.push(it);
                }.bind(this));
            }.bind(this))
        },
        deliverOrder: function(orderId) {
            return m.request({
                method: 'post',
                url: `/orders/${orderId}/deliver_order/`
            }).then(function() {
                this.syncProducts();
                const el = this.orders.find(it => it.id == orderId);
                const index = this.orders.indexOf(el);
                if (index > -1) {
                    this.orders.splice(index, 1);
                }
            }.bind(this))
        }
    }

    const ProductsComponent = {
        data: appData,
        view: function() {
            return [
                m("h1", { class: 'title' }, 'Products'),
                m("table", { id: 'products-table' }, [
                    m("tr", [
                        m('th', 'Name'), m('th', 'Stock')
                    ]),
                    this.data.products.map(function(it) {
                        return m("tr", { key: it.id }, [m('td', it.id), m('td', it.stock || 0)]);
                    })
                ])
            ]
        }
    };

    const OrdersComponent = {
        data: appData,
        view: function() {
            const app = this
            return m("main", [
                m("h1", { class: 'title' }, 'Orders'),
                m("table", { id: 'orders-table' }, [
                    m("tr", [
                        m('th', 'Customer'), m('th', 'Product'), m('th', 'Quantity'), m('th')
                    ]),
                    this.data.orders.map(function(it) {
                        return m("tr", [m('td', it.customer.name), m('td', it.product.id), m('td', it.quantity), m('td', [
                            m('button', { onclick: () => app.data.deliverOrder(it.id) }, 'Deliver')
                        ])]);
                    }.bind(this))
                ])
            ])
        }
    };

    const WarehouseApp = {
        data: appData,
        view: function() {
            return m('div', { class: 'columns' }, [
                m('div', { class: 'column' }, m(ProductsComponent)),
                m('div', { class: 'column' }, m(OrdersComponent))
            ]);
        },
        oninit: function() {
            appData.syncProducts()
            appData.syncOrders()
        }
    }

    m.mount(document.body, WarehouseApp);
})(window, document);