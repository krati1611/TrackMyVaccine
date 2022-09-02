var otp;
function sendOTP () {
    email = document.getElementById('email').value
    document.getElementById('enterotp').hidden = false
    document.getElementById('verifyotp').hidden = false
    link = `http://127.0.0.1:8000/hospital/verify/${email}/`
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
        var form = ["name", "password", "confirmpassword", "phone", "proof", "address", "city", "state", "zip", "gridCheck"];
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
