var vm = new Vue({
    el: '#app',
    data: {
        host,
        username: sessionStorage.username || localStorage.username,
        user_id: sessionStorage.user_id || localStorage.user_id,
        token: sessionStorage.token || localStorage.token,
        cart: [],					// 购物车中所有的商品
        total_selected_count: 0,
        origin_input: 0     // 用于记录手动输入前的值
    },

    computed: {
        // 商品总数量
        total_count: function () {
            var total = 0;
            for (var i = 0; i < this.cart.length; i++) {
                total += parseInt(this.cart[i].count);
				//  计算每件商品的小计金额: 小计金额 = 单价 * 数量
                this.cart[i].amount = (parseFloat(this.cart[i].price)
                    * parseFloat(this.cart[i].count)).toFixed(2); // 保留两位小数
            }
            return total;
        },

        // 选中商品的总金额
        total_selected_amount: function () {
            var total = 0;
            this.total_selected_count = 0;
            for (var i = 0; i < this.cart.length; i++) {
                if (this.cart[i].selected) {
                    total += (parseFloat(this.cart[i].price) * parseFloat(this.cart[i].count));
                    this.total_selected_count += parseInt(this.cart[i].count);
                }
            }
            return total.toFixed(2); // 保留两位小数
        },

        // 当前全选按钮是否为勾选状态
        selected_all: function () {
            var selected = true;
            for (var i = 0; i < this.cart.length; i++) {
                if (this.cart[i].selected == false) {
                    selected = false;   // 只要有一个商品没有勾选,全选按钮就不打勾
                    break;
                }
            }
            return selected;
        }
    },

    mounted: function () {
        // 获取购物车数据
        axios.get(this.host + '/cart/',{
            headers:{
                'Authorization':'JWT' + this.token
            },
            responseType:'json',
            withCredentials:true
        })
            .then(response =>{
                this.cart = response.data;
                // 计算每件商品的小计金额: 小计金额 = 单价 * 数量
                for (var i=0;i<=this.cart.length;i++){
                    this.cart[i].amount =(parseFloat(this.cart[i].price) * this.cart[i].count).toFixed(2);
                }
            })
            .catch(error =>{
                console.log(error.response.data);
            })
        
    },

    methods: {
        // 点击了退出
        logout: function () {
            sessionStorage.clear();
            localStorage.clear();
            location.href = '/login.html';
        },

        // 点击减少商品数量
        on_minus: function (index) {
            if (this.cart[index].count > 1) {
                var count = this.cart[index].count - 1;
                this.update_count(index, count);
            }
        },

        // 点击增加商品数量
        on_add: function (index) {
            var count = this.cart[index].count + 1;
            this.update_count(index, count);
        },

        // 全选商品
        on_selected_all: function () {
          var selected = !this.selected_all;
            // 发请求保存商品的勾选状态
            axios.put(this.host + '/cart/selection/', {
                    selected
                }, {
                    responseType: 'json',
                    headers:{
                        'Authorization': 'JWT ' + this.token
                    },
                    withCredentials: true // 传递cookie给服务器
                })
                .then(response => {
                    // 设置商品全选或全不选
                    for (var i=0; i<this.cart.length;i++){
                        this.cart[i].selected = selected;
                    }
                })
                .catch(error => {
                    console.log(error.response.data);
                })
        },

        // 删除购物车商品
        on_delete: function (index) {
            axios.delete(this.host+'/cart/', {
                    data: {  // 注意：delete方法参数的传递方式
                        sku_id: this.cart[index].id
                    },
                    headers:{
                        'Authorization': 'JWT ' + this.token
                    },
                    withCredentials: true
                })
                .then(response => {
                    this.cart.splice(index, 1);
                })
                .catch(error => {
                    console.log(error.response.data);
                })
        },

        // 手动输入商品数量
        on_input: function (index) {
            var val = parseInt(this.cart[index].count);
            if (isNaN(val) || val <= 0) {
                this.cart[index].count = this.origin_input;
            } else {
                // 更新购物车数据
                axios.put(this.host+'/cart/',{
                    sku_id:this.cart[index].id,
                    count:val,
                    selected:this.cart[index].selected
                },{
                    headers:{
                        'Authorization': 'JWT' + this.token
                    },
                    responseType:'json',
                    withCredentials:true
                })
                    .then(response =>{
                        this.cart[index].count = response.data.count;
                    })
                    .catch(error =>{
                        if ('non_field_errors' in error.response.data){
                            alert(error.response.data.non_field_errors[0]);
                        }else {
                            alert('修改购物车失败');
                        }
                        console.log(error.response.data);
                        this.cart[index].count = this.origin_input;
                    })
            }
        },

        // 更新购物车数量
        update_count: function (index, count) {
            axios.put(this.host+'/cart/', {
                    sku_id: this.cart[index].id,
                    count: this.cart[index].count,
                    selected: this.cart[index].selected
                }, {
                    headers: {
                        'Authorization': 'JWT ' + this.token
                    },
                    responseType: 'json',
                    withCredentials: true
                })
                .then(response => {
                    this.cart[index].selected = response.data.selected;
                })
                .catch(error => {
                    if ('non_field_errors' in error.response.data) {
                        alert(error.response.data.non_field_errors[0]);
                    } else {
                        alert('修改购物车失败');
                    }
                    console.log(error.response.data);
                })
        },

        // 更新购物车选中状态
        update_selected: function (index) {

        }
    }
});