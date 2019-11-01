var vm = new Vue({
    el: '#app',

    data: {
        host: host,
        error_username: false,
        error_pwd: false,
        error_pwd_message: '请填写密码',

        username: '',
        password: '',
        remember: false
    },

    methods: {
        // 获取url查询字符串参数值
        // var next = get_query_string('next')     // /user_center_info.html
        // 要获取:next的值:
        // http://www.meiduo.site:8080/login.html?next=/user_center_info.html
        // window.location.search:  ?next=/user_center_info.html
        // window.location.search.substr(1):  next=/user_center_info.html
        get_query_string: function (name) {
            var reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)', 'i');
            var r = window.location.search.substr(1).match(reg);
            if (r !== null) {
                return decodeURI(r[2]);
            }
            return null;
        },

        // 检查用户名是否合法
        check_username: function () {
            if (!this.username) {
                this.error_username = true;
            } else {
                this.error_username = false;
            }
        },

        // 检查密码是否合法
        check_pwd: function () {
            if (!this.password) {
                this.error_pwd_message = '请填写密码';
                this.error_pwd = true;
            } else {
                this.error_pwd = false;
            }
        },

        // 表单提交: 执行登录操作
        on_submit: function(){
            this.check_username();
            this.check_pwd();

            if (this.error_username == false && this.error_pwd == false) {
                // 登录请求
                var data = {
                    username: this.username,
                    password: this.password
                };
                axios.post(this.host+'/authorizations/', data,{withCredentials:true})
                    .then(response => {
                        // 使用浏览器本地存储保存token
                        sessionStorage.clear();
                        localStorage.clear();
                        if (this.remember) {
                            // 记住登录
                            localStorage.token = response.data.token;
                            localStorage.user_id = response.data.user_id;
                            localStorage.username = response.data.username;
                        } else {
                            // 未记住登录
                            sessionStorage.token = response.data.token;
                            sessionStorage.user_id = response.data.user_id;
                            sessionStorage.username = response.data.username;
                        }

                        // 跳转页面
                        // http://www.meiduo.site:8080/login.html?next=/user_center_info.html
                        // /user_center_info.html
                        var return_url = this.get_query_string('next');
                        console.log(return_url);
                        if (!return_url) {
                            return_url = '/index.html';
                        }
                        location.href = return_url;
                    })
                    .catch(error => {
                        if (error.response.status == 400) {
                            this.error_pwd_message = '用户名或密码错误';
                        } else {
                            this.error_pwd_message = '服务器错误';
                        }
                        this.error_pwd = true;
                    })
            }
        },

        // qq登录
        qq_login: function(){
            // 获取登录成功后要跳转的界面
            // http://www.meiduo.site:8080/login.html?next=/user_center_info.html#
            var next = this.get_query_string('next') || 'index.html';

            axios.get(this.host + '/oauth/qq/authorization/?next=' + next)
                .then(response => {
                    // 跳转到QQ登录界面
                    location.href = response.data.login_url;
                })
                .catch(error => {
                    console.log(error.response.data);
                })
        }
    }
});
