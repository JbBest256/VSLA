"use strict";
var KTSigninGeneral = function () {
    var t, e, r;
    return {
        init: function () {
            t = document.querySelector("#kt_sign_in_form"),
            e = document.querySelector("#kt_sign_in_submit"),
            r = FormValidation.formValidation(t, {
                fields: {
                    username: {
                        validators: {
                            regexp: {
                                regexp: /^[A-Za-z]+$/,
                                message: "The username can only contain alphabetic letters"
                            },
                            notEmpty: {
                                message: "Username is required"
                            }
                        }
                    },
                    password: {
                        validators: {
                            notEmpty: {
                                message: "The password is required"
                            }
                        }
                    }
                },
                plugins: {
                    trigger: new FormValidation.plugins.Trigger,
                    bootstrap: new FormValidation.plugins.Bootstrap5({
                        rowSelector: ".fv-row",
                        eleInvalidClass: "",
                        eleValidClass: ""
                    })
                }
            }),
            e.addEventListener("click", (function (i) {
                
                
            }));
        }
    }
}
();
KTUtil.onDOMContentLoaded((function () {
    KTSigninGeneral.init()
}));
