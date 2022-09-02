from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from email.message import EmailMessage
import smtplib
import random
import math
import bcrypt
import base64
import ssl
import json
from .helper import send_mail

# Create your views here.
def login(request):
    dictionary = {'alert':False}
    if request.method == 'POST':
        data = request.POST
        email = data['email']
        password = data['password']
        cur = connection.cursor()
        cur.execute("SELECT password from hospital where email = %s",[email])
        pswd = cur.fetchone()
        cur.close()
        if pswd is None:
            return render(request, 'hospital/login.html', {'alert':True, 'error': 'Invalid email'})
        pswd=pswd[0]
        if bcrypt.checkpw(password.encode('utf-8'), pswd.encode('utf-8')):
            request.session['hospital'] = email
            return redirect('/hospital/dashboard')
        else:
            return render(request, 'hospital/login.html', {'alert':True, 'error': 'Invalid password'})
    return render(request, 'hospital/login.html', dictionary)

def generateOTP():
    digits = "0123456789"
    OTP = ""
    for i in range(6):
        OTP += digits[math.floor(random.random() * 10)]
    return OTP

def forgot(request):
    if request.method == "POST":

        email=request.POST.get("email")
        otp=generateOTP()
        mail = EmailMessage()
        mail['from'] = 'trackmyvaccine37@gmail.com'
        mail['subject'] = 'OTP request'
        mail['to'] = email
        message = 'Your OTP is '+otp+' to reset password for trackmyvaccine'
        mail.set_content(message)
        
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT')
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        with smtplib.SMTP_SSL('smtp.gmail.com',465,context=ctx) as server:
            server.login('trackmyvaccine37@gmail.com','tgbmlofefkosjifl')
            server.send_message(mail)
        return HttpResponse(otp)
    return render(request, 'hospital/forgot.html')

def changepassword(request):
    if request.method == 'POST':
        data = request.POST
        email = data['email']
        password = data['password']
        pswd = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cur = connection.cursor()
        cur.execute("UPDATE hospital SET password = %s WHERE email = %s",[pswd, email])
        cur.close()
    return redirect('/hospital/login')

def register(request):
    dictionary = {'alert':False}
    if request.method == 'POST':
        data = request.POST
        name = data['name']
        email = data['email']
        phone = data['phone']
        password = data['password']
        confirm = data['confirmpassword']
        street = data['address']
        city = data['city']
        state = data['state']
        pincode = data['pincode']
        file = request.FILES['proof']

        file_name = file.name
        temp = bytes('', encoding='utf-8')
        for chunk in file.chunks():
            temp += chunk
        proof = base64.b64encode(temp)

        if password != confirm:
            return render(request, 'hospital/register.html', {'alert':True, 'error': 'Passwords do not match'})
        
        cur = connection.cursor()
        cur.execute("SELECT id from hospital where email = %s",[email])
        email_check = cur.fetchone()
        if email_check is not None:
            cur.close()
            return render(request, 'hospital/register.html', {'alert':True, 'error': 'Email already exists'})
        cur.execute("SELECT id from hospital where phone = %s",[phone])
        phone_check = cur.fetchone()
        if phone_check is not None:
            cur.close()
            return render(request, 'hospital/register.html', {'alert':True, 'error': 'Phone Number already exists'})
        
        pswd = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        cur.execute("SELECT id from address where pincode = %s",[pincode])
        pincode_check = cur.fetchone()
        if pincode_check is None:
            cur.execute("INSERT INTO address (city, state, pincode) VALUES (%s, %s, %s)",[city, state, pincode])
        
        cur.execute("SELECT id from address where pincode = %s",[pincode])
        address_id = cur.fetchone()[0]
        cur.execute("INSERT INTO hospital (name, email, phone, password, street, certificate, address_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",[name, email, phone, pswd, street, proof, address_id])
        cur.execute("select last_insert_id();")
        hospital_id = cur.fetchone()[0]
        for i in range(2,15):
            cur.execute("INSERT INTO stock (hospital_id, vaccine_id) values (%s,%s)",[hospital_id, i])
        cur.close()
        return redirect('/hospital/dashboard')
    
    return render(request, 'hospital/register.html',dictionary)

def dashboard(request):
    if 'hospital' in request.session:
        return render(request, 'hospital/dashboard.html')
    return redirect('/hospital/login')

def logout(request):
    if 'hospital' in request.session:
        del request.session['hospital']
    return redirect('/')

def stock(request):
    if 'hospital' in request.session:
        if request.method == 'POST':
            data = request.POST
            vaccine_id = data['vaccine']
            quantity = data['amount']
            expiry = data['expiry']
            cur = connection.cursor()
            cur.execute("INSERT INTO expiry (vaccine_id, hospital_id, count, expiry_date) values (%s,(select id from hospital where email=%s),%s,%s);",[vaccine_id, request.session['hospital'],quantity, expiry])
            cur.execute("UPDATE stock SET count = count + %s, doli = curdate() where vaccine_id=%s and hospital_id=(select id from hospital where email=%s);",[quantity, vaccine_id, request.session['hospital']])
            cur.close()
            return redirect('/hospital/stock')
        dictionary = {}
        cur = connection.cursor()
        query = '''select v.id,v.name,v.prevents,s.count,s.doli,s.dolu 
        from stock as s 
        inner join vaccine as v 
        on s.vaccine_id = v.id 
        inner join hospital as h 
        on s.hospital_id = h.id 
        where h.email = %s;'''
        cur.execute(query,[request.session['hospital']])
        records = cur.fetchall()
        def helper(a,i):
            try:
                return a[i][0]
            except Exception:
                return "-"
        cards = []
        for record in records:
            cur.execute('select gap from dose where vaccine_id = %s;',[record[0]])
            gaps = cur.fetchall()
            cards.append({
                'id': record[0],
                'name': record[1],
                'prevents': record[2],
                'count': record[3],
                'doli': record[4],
                'dolu': record[5],
                'd1': helper(gaps,0),
                'd2': helper(gaps,1),
                'd3': helper(gaps,2),
                'd4': helper(gaps,3),
                'd5': helper(gaps,4)
            })
        dictionary['vaccines'] = cards

        query = '''SELECT e.id, v.name, e.count, e.expiry_date, e.intake_date
                   from expiry as e
                   inner join vaccine as v
                   on e.vaccine_id = v.id
                   inner join hospital as h
                   on e.hospital_id = h.id
                   where h.email = %s order by e.intake_date desc;
        '''
        cur.execute(query,[request.session['hospital']])
        records = cur.fetchall()
        cards = []
        for record in records:
            cards.append({
                'id': record[0],
                'name': record[1],
                'count': record[2],
                'expiry': record[3],
                'intake': record[4]
            })
        dictionary['expiry'] = cards
        cur.close()
        return render(request, 'hospital/stock.html',dictionary)
    return redirect('/hospital/login')

def edit(request):
    if 'hospital' in request.session:
        dictionary = {'alert':False}
        if request.method == "POST":
            dictionary['alert'] = True
            data = request.POST
            name = data['name']
            phone = data['phone']
            street = data['street']
            city = data['city']
            state = data['state']
            pincode = data['pincode']
            cur = connection.cursor()
            cur.execute("SELECT id from hospital where phone = %s and email <> %s;",[phone,request.session['hospital']])
            phone_check = cur.fetchone()
            if phone_check is not None:
                cur.close()
                dictionary['status'] = "danger"
                dictionary['message'] = "Phone number already exists"
            else:
                query = '''update hospital set name = %s, phone = %s, street = %s where email = %s;'''
                cur.execute(query,[name, phone, street, request.session['hospital']])
                cur.execute("select id from address where pincode = %s",[pincode])
                address_id = cur.fetchone()
                if address_id is None:
                    cur.execute("insert into address (city, state, pincode) values (%s, %s, %s)",[city, state, pincode])
                    cur.execute("select last_insert_id();")
                    address_id = cur.fetchone()[0]
                    cur.execute("update hospital set address_id = %s where email = %s",[address_id, request.session['hospital']])
                else:
                    cur.execute("update address set city = %s, state = %s where id = %s",[city, state, address_id[0]])
                cur.close()
                dictionary['status'] = "success"
                dictionary['message'] = "details updated successfully"
        cur = connection.cursor()
        query = '''select h.id, h.name, h.email, h.phone, h.street, h.certificate, a.city, a.state, a.pincode
        from hospital as h
        inner join address as a
        on h.address_id = a.id
        where h.email = %s;
        '''
        cur.execute(query,[request.session['hospital']])
        record = cur.fetchone()
        dictionary['id'] = record[0]
        dictionary['name'] = record[1]
        dictionary['email'] = record[2]
        dictionary['phone'] = record[3]
        dictionary['street'] = record[4]
        dictionary['certificate'] = "data:image/png;base64,"+record[5].decode('utf-8')
        dictionary['city'] = record[6]
        dictionary['state'] = record[7]
        dictionary['pincode'] = record[8]
        cur.close()
        return render(request, 'hospital/edit.html', dictionary)
    return redirect('/hospital/login')

def appointment(request,key='vaccine'):
    if 'hospital' in request.session:
        if request.method == 'POST':
            vaccinetaken(request.POST)
            return redirect('/hospital/appointment/')
        mapper={
            'vaccine': 'v.name',
            'dose': 'dose_number',
            'date': 'a.vaccine_date',
            'slot': 's.start',
            'parent': 'p.name',
            'd_type': 'p.d_type',
            'd_number': 'p.d_number',
            'child': 'c.name',
            'dob': 'c.dob',
            'gender': 'c.gender'
        }
        cur = connection.cursor()
        hospital_email = request.session['hospital']
        query = ''' select v.name, c.name, c.dob, c.gender, p.name, a.vaccine_date, (select dose_number from dose where id=a.dose_id) as dose_number, s.start, s.end, p.d_number, a.h_status, a.id, p.d_type, v.id, h.id, a.expiry_id
        from appointment as a
        inner join vaccine as v
        on a.vaccine_id = v.id
        inner join child as c
        on a.child_id = c.id
        inner join parent as p
        on c.parent_id = p.id
        inner join hospital as h
        on a.hospital_id = h.id
        left join slot as s
        on a.slot_id = s.id
        where h.email = %s and a.vaccine_date >= CURRENT_DATE() and (a.h_status = 2 or a.status is null) order by '''+ mapper[key]+';'
        cur.execute(query,[hospital_email])
        records = cur.fetchall()
        appointments = []
        for record in records:
            if record[15] is None:
                cur.execute("select id, count, expiry_date from expiry where vaccine_id = %s and hospital_id = %s;",[record[13],record[14]])
                temp = cur.fetchall()
                expiries = []
                for i in temp:
                    expiries.append({
                        'id': i[0],
                        'count': i[1],
                        'expiry': i[2]
                    })
            else:
                cur.execute("select expiry_date, count from expiry where id = %s;",[record[15]])
                expiry = cur.fetchone()
                expiries = {
                    'expiry': expiry[0],
                    'count': expiry[1]
                }
            appointments.append({
            'vaccine_name' : record[0],
            'child_name': record[1],
            'child_dob' : record[2],
            'child_gender' : "Male" if record[3]=="" else "Female",
            'parent_name' : record[4],
            'date' : record[5],
            'dose' : record[6],
            'start' : record[7] if record[7] else "-",
            'end' : record[8] if record[8] else "-",
            'd_number' : record[9],
            'h_status': record[10],
            'id': record[11],
            'd_type': 'aadhar' if record[12] == "" else 'birth certificate',
            'expiries': expiries
            })
        dictionary={'appointments':appointments}

        query = ''' select v.name, c.name, c.dob, c.gender, p.name, a.vaccine_date, (select dose_number from dose where id=a.dose_id) as dose_number, s.start, s.end, p.d_number, a.h_status, a.id, a.status, p.d_type, (select expiry_date from expiry where id=a.expiry_id) as expiry_date
        from appointment as a
        inner join vaccine as v
        on a.vaccine_id = v.id
        inner join child as c
        on a.child_id = c.id
        inner join parent as p
        on c.parent_id = p.id
        inner join hospital as h
        on a.hospital_id = h.id
        left join slot as s
        on a.slot_id = s.id
        where h.email = %s order by '''+ mapper[key]+';'
        cur.execute(query,[hospital_email])
        records = cur.fetchall()
        appointments = []
        for record in records:
            if record[12] is None:
                if record[10] == 2:
                    status = 2
                else:
                    status = 1
            else:
                status = 0
            appointments.append({
            'vaccine_name' : record[0],
            'child_name': record[1],
            'child_dob' : record[2],
            'child_gender' : "Male" if record[3]=="" else "Female",
            'parent_name' : record[4],
            'date' : record[5],
            'dose' : record[6],
            'start' : record[7] if record[7] else "-",
            'end' : record[8] if record[8] else "-",
            'd_number' : record[9],
            'h_status': record[10],
            'id': record[11],
            'status': status,
            'd_type': 'aadhar' if record[13] == "" else 'birth certificate',
            'expiry_date': "-" if record[14] is None else record[14]
            })
        dictionary['all_appointments'] = appointments
        cur.close()
        return render(request, 'hospital/appointment.html',dictionary)
    return redirect('/hospital/login')

def addvaccine(request):
    if 'hospital' in request.session:
        if request.method == 'POST':
            data = request.POST
            name = data['name']
            prevents = data['prevents']
            count = data['count']
            d1 = int(data['d1'])
            d2 = None if data['d2']=="" else int(d1)+int(data['d2'])
            d3 = None if data['d3']=="" else int(d2)+int(data['d3'])
            d4 = None if data['d4']=="" else int(d3)+int(data['d4'])
            d5 = None if data['d5']=="" else int(d4)+int(data['d5'])
            expiry = data['expiry']
            cur = connection.cursor()
            cur.execute("INSERT INTO vaccine (name, prevents) VALUES (%s, %s)",[name, prevents])
            cur.execute("select last_insert_id();")
            vaccine_id = cur.fetchone()[0]
            for i,j in enumerate([d1,d2,d3,d4,d5]):
                if j is None:
                    break
                cur.execute("INSERT INTO dose (vaccine_id, dose_number, gap) VALUES (%s, %s, %s)",[vaccine_id, i, j])
            cur.execute("INSERT INTO stock (hospital_id,vaccine_id,count) VALUES ((select id from hospital where email=%s), %s, %s)",[request.session['hospital'], vaccine_id, count])
            cur.execute("INSERT INTO expiry (hospital_id, vaccine_id, count, expiry_date) values ((select id from hospital where email=%s),%s,%s,%s);",[request.session['hospital'], vaccine_id, count, expiry])
            cur.close()
            return redirect('/hospital/stock')
        return render(request, 'hospital/addvaccine.html')
    return redirect('/hospital/login')

def slot(request):
    if 'hospital' in request.session:
        cur = connection.cursor()
        hospital_email = request.session['hospital']
        query = '''select id, start, end, count
        from slot
        where hospital_id=(select id from hospital where email=%s);
        '''
        cur.execute(query,[hospital_email])
        records = cur.fetchall()
        dictionary = {}
        slots = []
        ids = []
        dictionary['n'] = len(records)
        for i,record in enumerate(records):
            slots.append({
            "id" : record[0],
            "start" : str(record[1]),
            "end" : str(record[2]),
            "count" : record[3]})
            ids.append(record[0])
        dictionary['slots'] = slots
        cur.close()
        if request.method == 'POST':
            data = request.POST
            n = int(data['n'])
            cur = connection.cursor()
            cur.execute("select id from hospital where email = %s",[request.session['hospital']])
            hospital_id = cur.fetchone()[0]
            if len(ids)>0:
                query = '''select p.email, p.name, c.name, v.name, (select dose_number from dose where id=a.dose_id), a.vaccine_date, h.name, v.id
                        from appointment as a
                        inner join child as c
                        on a.child_id = c.id
                        inner join parent as p
                        on c.parent_id = p.id
                        inner join vaccine as v
                        on a.vaccine_id = v.id
                        inner join hospital as h
                        on a.hospital_id = h.id
                        where a.slot_id in (%s) and a.h_status <>2;
                '''
                format_strings = ','.join(['%s'] * len(ids))
                cur.execute(query%format_strings,tuple(ids))
                records = cur.fetchall()
                vaccine_ids = []
                for i in records:
                    parent_email = i[0]
                    parent_name = i[1]
                    child_name = i[2]
                    vaccine_name = i[3]
                    dose = i[4]
                    date = i[5]
                    hospital_name = i[6]
                    vaccine_ids.append(i[7])
                    subject = "Cancellation of vaccine booking"
                    body = f"Dear {parent_name},\n Your vaccination booking for Mr/Mrs {child_name} for {vaccine_name} on {date} at {hospital_name} has been cancelled, Since the hospital has changed their slots.Kindly book another available slot.\n\nRegards,\nHospital Management"
                    send_mail(subject, body, parent_email)
                
                for i in vaccine_ids:
                    query = '''update stock as s
                    inner join appointment as a
                    on a.hospital_id = s.hospital_id
                    set s.count = s.count+1 
                    where s.vaccine_id = %s and s.hospital_id = %s and a.h_status <> 2;'''
                    cur.execute(query,[i,hospital_id])

                query = '''update appointment set status = "" where slot_id in (%s) and h_status <>2;'''
                cur.execute(query%format_strings,tuple(ids))
                
                query = '''delete from slot where id in (%s);'''
                cur.execute(query%format_strings,tuple(ids))

            for i in range(n):
                start = data[f'start{i}']+':00'
                to = data[f'to{i}']+':00'
                count = int(data[f'count{i}'])
                query = '''INSERT INTO slot (hospital_id, start, end, count) VALUES ( %s, %s, %s, %s);'''
                cur.execute(query,[hospital_id, start, to, count])
            cur.close()
            return redirect('/hospital/slot')
        return render(request, 'hospital/slot.html',dictionary)
    return redirect('/hospital/login')

def verifyemail(request,email):
    otp = generateOTP()
    body = f''' Hi,
    Your OTP is {otp}. Please verify this OTP to continue your registration.
    Thank you,
    Team TrackMyVaccine.
    '''
    send_mail("Verify your account", body, email)
    data = json.dumps({'otp':otp})
    return HttpResponse(data)

def verifyaadhar(request, a_id):
    if 'hospital' in request.session:
        cur = connection.cursor()
        cur.execute("update appointment set h_status = 1 where id = %s;",[a_id])
        query = '''select p.name, c.name, v.name, d.dose_number, a.vaccine_date, h.name, s.start, s.end, p.email
        from appointment as a
        inner join child as c
        on a.child_id = c.id
        inner join parent as p
        on c.parent_id = p.id
        inner join vaccine as v
        on a.vaccine_id = v.id
        inner join dose as d
        on a.dose_id = d.id
        inner join hospital as h
        on a.hospital_id = h.id
        inner join slot as s
        on a.slot_id = s.id
        where a.id = %s;
        '''
        cur.execute(query,[a_id])
        data = cur.fetchone()
        parent = data[0]
        child = data[1]
        vaccine = data[2]
        dose = data[3]
        date = data[4]
        hospital = data[5]
        slot = str(data[6]) + " - " + str(data[7])
        email = data[8]
        body = f"Dear {parent},\nYour document has been verified at {hospital} for the appointment.\nYour appointment details are as follows:\n\nChild Name: {child}\nVaccine: {vaccine}\nDose: {dose}\nDate: {date}\nHospital: {hospital}\nSlot: {slot}\n\nThank you for choosing us.\n\nRegards,\nTeam TrackMyVaccine."
        send_mail('Document Verified', body, email)
        cur.close()
        return redirect('/hospital/appointment/')
    return redirect('/hospital/login')

def vaccinetaken(data):
    cur = connection.cursor()
    a_id = data['a_id']
    expiry_id = data['expiry']
    cur.execute("update appointment set h_status = 2, expiry_id = %s where id = %s;",[expiry_id, a_id])
    cur.execute("update expiry set count = count-1 where id = %s;",[expiry_id])
    query = '''select p.name, c.name, v.name, d.dose_number, a.vaccine_date, h.name, s.start, s.end, p.email
    from appointment as a
    inner join child as c
    on a.child_id = c.id
    inner join parent as p
    on c.parent_id = p.id
    inner join vaccine as v
    on a.vaccine_id = v.id
    inner join dose as d
    on a.dose_id = d.id
    inner join hospital as h
    on a.hospital_id = h.id
    inner join slot as s
    on a.slot_id = s.id
    where a.id = %s;
    '''
    cur.execute(query,[a_id])
    data = cur.fetchone()
    parent = data[0]
    child = data[1]
    vaccine = data[2]
    dose = data[3]
    date = data[4]
    hospital = data[5]
    slot = str(data[6]) + " - " + str(data[7])
    email = data[8]
    body = f"Dear {parent},\nYour child {child} has been vaccinated at {hospital}.\nYour vaccination details are as follows:\n\nChild Name: {child}\nVaccine: {vaccine}\nDose: {dose}\nDate: {date}\nHospital: {hospital}\nSlot: {slot}\n\nThank you for choosing us.\n\nRegards,\nTeam TrackMyVaccine."
    send_mail('Vaccination Successful', body, email)
    cur.close()

def expiryremove(request,e_id):
    if 'hospital' in request.session:
        cur = connection.cursor()
        cur.execute("select vaccine_id,count from expiry where id = %s;",[e_id])
        temp = cur.fetchone()
        vaccine_id, count = temp[0], temp[1]
        cur.execute("update stock set count = count - %s where hospital_id = (select id from hospital where email = %s) and vaccine_id = %s;",[count,request.session['hospital'],vaccine_id])
        cur.execute("delete from expiry where id = %s;",[e_id])
        cur.close()
        return redirect('/hospital/stock/')
    return redirect('/hospital/login')
