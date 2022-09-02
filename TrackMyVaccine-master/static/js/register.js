var otp;
function sendOTP () {
    email = document.getElementById('email').value
    document.getElementById('enterotp').hidden = false
    document.getElementById('verifyotp').hidden = false
    link = `http://127.0.0.1:8000/parent/verify/${email}/`
    $.ajax({ url: link, success: function(data) { 
        var data = JSON.parse(data);
        otp = data.otp
        }
    });
}

function verifyOTP () {
    enteredOtp = document.getElementById('OTP').value
    if (otp==enteredOtp) {
        document.getElementById('enterotp').hidden = true
        document.getElementById('verifyotp').hidden = true
        document.getElementById('otpbutton').hidden = true
        document.getElementById('nothing').hidden = false
        document.getElementById('email').readOnly = true
        var form = ["name","aadhar", "password", "confirmpassword", "phone", "radio1", "radio2", "radio5", "radio6", "cname", "cdob", "radio3", "radio4", "city", "state", "zip", "gridCheck"];
        for(var i = 0; i < form.length; i++) {
            document.getElementById(form[i]).disabled = false;
    }
    }
    else{
        var helper = document.getElementById('emailHelp')
        helper.classList.add("text-danger")
        helper.innerHTML = "Incorrect OTP!!"
    }
}

var datePickerId = document.getElementById('cdob');
var myDate = new Date();
datePickerId.max = myDate.toLocaleDateString('en-ca');