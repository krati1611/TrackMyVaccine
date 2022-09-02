$.ajax({ url: 'http://127.0.0.1:8000/session', success: function(data) { 
        var status = JSON.parse(data);
        var logindiv = document.getElementById('divlogin');
        var logoutdiv = document.getElementById('divlogout');
        var logoutbutton = document.getElementById('logoutbutton');
        var dashboard = document.getElementById('dashboard');
        var profile = document.getElementById('profile');
        var appointment = document.getElementById('appointment');
        var stock = document.getElementById('stock');
        var slot = document.getElementById('slot');
        var manager = document.getElementById('manager');
        if(status.parent == true){
          manager.style.display = "inline-flex";
          logindiv.style.display = "none";
          logoutdiv.style.display = "inline";
          logoutbutton.href = "/parent/logout";
          dashboard.href = "/parent/dashboard";
          profile.href = "/parent/edit";
          appointment.href = "/parent/appointment";
          stock.style.display = "none"
          slot.style.display = "none"
        }
        if(status.hospital == true){
          manager.style.display = "inline-flex";
          logindiv.style.display = "none";
          logoutdiv.style.display = "inline";
          logoutbutton.href = "/hospital/logout";
          dashboard.href = "/hospital/dashboard";
          profile.href = "/hospital/edit";
          appointment.href = "/hospital/appointment";
          stock.style.display = "inline"
          slot.style.display = "inline"
        }
      } });