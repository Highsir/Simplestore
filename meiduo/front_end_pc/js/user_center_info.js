var vm = new Vue({
    el: '#app',
    data: {
        host,
        user_id: sessionStorage.user_id || localStorage.user_id,
        token: sessionStorage.token || localStorage.token,  // jwt
        username: '',
        mobile: '',
        email: '',
        email_active: false,
        set_email: false,
        send_email_btn_disabled: false,
        send_email_tip: '重新发送验证邮件',
        email_error: false,
        histories: []
    },

    mounted: function () {
        // 1. 获取用户个人信息
        // alert('获取用户个人信息')
        var config = {
            headers: { // 通过请求头向后端传递JWT
                'Authorization': 'JWT ' + this.token
            },
        };
        axios.get(this.host + '/user/', config)
            .then(response => { // 显示用户数据
                // ('id', 'username', 'mobile', 'email', 'email_active')
                this.user_id = response.data.id;
                this.username = response.data.username;
                this.mobile = response.data.mobile;
                this.email = response.data.email;
                this.email_active = response.data.email_active;
            })
            .catch(error => {
                // 未登录，跳转到登录界面
                if (error.response.status == 401 || error.response.status == 403) {
                    location.href = '/login.html?next=/user_center_info.html';
                }
            });

        // 2. 补充请求浏览历史
        axios.get(this.host + '/browse_histories/', {
            headers: {
                'Authorization': 'JWT ' + this.token
            },
            responseType: 'json'
        })
            .then(response => {
                this.histories = response.data;
                for (var i = 0; i < this.histories.length; i++) {
                    this.histories[i].url = '/goods/'
                        + this.histories[i].id + '.html';
                }
            })
    },

    methods: {
        // 退出
        logout: function () {
            sessionStorage.clear();
            localStorage.clear();
            location.href = '/login.html';
        },

        check_email: function () {
            var re = /^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$/;
            if (re.test(this.email)) {
                this.email_error = false;
            } else {
                this.email_error = true;
            }
        },

        // 保存email
        save_email: function () {
            this.check_email();
            if (!this.email_error) {
                var data = {email: this.email}   // 提交的表单数据
                var config = {
                    headers: {
                        // 通过请求头往服务器传递jwt
                        'Authorization': 'JWT ' + this.token
                    }
                };
                axios.put(this.host + '/email/', data, config)
                    .then(response => {
                        this.set_email = false;
                        this.send_email_btn_disabled = true;
                        this.send_email_tip = '已发送验证邮件'
                    })
                    .catch(error => {
                        alert(error.data);
                    });
            }
        }
    }
});


