var vm = new Vue({
    el: '#app',
    data: {
        // var host = 'http://127.0.0.1:8000';
        // host: 'http://127.0.0.1:8000',
        // host: host,
        host,
        error_name: false,
        error_password: false,
        error_check_password: false,
        error_phone: false,
        error_allow: false,
        error_sms_code: false,

        username: '',
        password: '',
        password2: '',
        mobile: '',
        sms_code: '',
        allow: false,

        sms_code_tip: '获取短信验证码',
        sending_flag: false, 			// 正在发送短信标志
        error_name_message: '', 		// 用户名错误提示
        error_phone_message: '', 		// 手机号错误提示
        error_sms_code_message: '' 		// 短信验证码错误
    },

    methods: {
        check_username: function () {
            let len = this.username.length;
            if (len < 5 || len > 20) {
                this.error_name_message = '请输入5-20个字符的用户名';
                this.error_name = true;
            } else {
                this.error_name = false;
            }

            // 请求服务器,判断用户名是否存在
            if (!this.error_name) {
                var config = { // 服务器返回的数据类型,默认就是json
                    responseType: 'json'
                };
                axios.get(this.host + '/usernames/' + this.username + '/count/', config)
                    .then(response => {
                        if (response.data.count > 0) {
                            this.error_name_message = '用户名已存在';
                            this.error_name = true;
                        } else {
                            this.error_name = false;
                        }
                    })
                    .catch(error => {
                        console.log(error.response.data);
                    })
            }
        },

        check_pwd: function () {
            let len = this.password.length;
            if (len < 8 || len > 20) {
                this.error_password = true;
            } else {
                this.error_password = false;
            }
        },
        check_cpwd: function () {
            if (this.password !== this.password2) {
                this.error_check_password = true;
            } else {
                this.error_check_password = false;
            }
        },
        check_phone: function () {
            let re = /^1[345789]\d{9}$/;
            if (re.test(this.mobile)) {
                this.error_phone = false;
            } else {
                this.error_phone_message = '请输入正确的手机号码';
                this.error_phone = true;
            }
        },
        check_sms_code: function () {
            if (!this.sms_code) {
                this.error_sms_code = true;
            } else {
                this.error_sms_code = false;
            }
        },
        check_allow: function () {
            if (!this.allow) {
                this.error_allow = true;
            } else {
                this.error_allow = false;
            }
        },

        // 发送短信验证码功能
        send_sms_code: function () {
            // 如果显示了短信验证码出错提示, 则隐藏它
            this.error_sms_code = false;
            // alert('发送短信')

            if (this.sending_flag) {
                return
            }

            this.check_phone();
            if (this.error_phone) {
                // 短信验证码校验出错
                this.sending_flag = false;
                return
            }

            this.sending_flag = true;  // 正在下发短信

            axios.get(this.host + '/sms_codes/'+ this.mobile +'/')
                .then(response => {
                    console.log('获取短信验证码成功');

                    // 倒计时60秒，60秒后允许用户再次点击发送短信验证码的按钮
                    var num = 60;
                    // 设置一个计时器
                    var t = setInterval(() => {
                        if (num == 1) {
                            // 如果计时器到最后, 清除计时器对象
                            clearInterval(t);
                            // 将点击获取验证码的按钮展示的文本恢复成原始文本
                            this.sms_code_tip = '获取短信验证码';
                            // 将点击按钮的onclick事件函数恢复回去
                            this.sending_flag = false;
                        } else {
                            num -= 1;
                            // 展示倒计时信息
                            this.sms_code_tip = num + '秒';
                        }
                    }, 1000, 60);

                })
                .catch(error => {
                    // 显示出错信息
                    this.error_sms_code = true;
                    this.error_sms_code_message = error.response.data.message;
                    this.sending_flag = false;
                })
        },

        // 注册
        on_submit: function () {
            this.check_username();
            this.check_pwd();
            this.check_cpwd();
            this.check_phone();
            this.check_sms_code();
            this.check_allow();
            // alert('注册')

            // 演示功能: 测试使用
            localStorage.name = 'localStorage'
            sessionStorage.name2 = 'sessionStorage'

            if (!this.error_name &&
                this.error_password === false &&
                this.error_check_password === false &&
                this.error_phone === false &&
                this.error_sms_code === false &&
                this.error_allow === false) {

                // 发post请求
                let data = {
                    username: this.username,
                    password: this.password,
                    password2: this.password2,
                    mobile: this.mobile,
                    sms_code: this.sms_code,
                    allow: this.allow,
                };

                axios.post(this.host + '/users/', data)
                    .then(response => {

                        // todo: 保存用户登录状态 user_id username token
                        localStorage.clear();
                        sessionStorage.clear();

                        localStorage.user_id = response.data.id
                        localStorage.username = response.data.username
                        localStorage.token = response.data.token

                        // 注册成功, 进入到首页
                        location.href = '/index.html'
                    })
                    .catch(error => {
                        console.log(error);
                        if (error.response.status === 400) {
                            if ('non_field_errors' in error.response.data) {
                                this.error_sms_code = true;
                                // 短信验证码不正确
                                this.error_sms_code_message = error.response
                                    .data.non_field_errors[0];
                            } else {
                                alert('注册失败')
                            }
                        } else {
                            alert('注册失败')
                        }
                    })
            }
        }
    }
});




/**
var vm = new Vue({      // viewmodel :
    el: '#app',         // el 元素
    data: {
        username: 'xx',
        password2: '',
    },
    methods: {
        check_username: function () {
        },
        check_pwd:function () {
        }
    },

    // vue对象创建的勾子函数: 挂载
    // 用法: 请求服务器数据, 初始化界面显示
    mounted: function () {
    }
});
*/