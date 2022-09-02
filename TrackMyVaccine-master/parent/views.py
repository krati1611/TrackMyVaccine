from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from email.message import EmailMessage
import smtplib
import random
import math
import bcrypt
import ssl
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Create your views here.
def login(request):
    dictionary = {"alert":False}
    if request.method == 'POST':
        data = request.POST
        email = data['email']
        password = data['password']
        cur = connection.cursor()
        cur.execute("SELECT password from parent where email = %s",[email])
        pswd = cur.fetchone()
        cur.close()
        if pswd is None:
            return render(request, 'parent/login.html', {'alert':True, 'error': 'Invalid email'})
        pswd=pswd[0]
        if bcrypt.checkpw(password.encode('utf-8'), pswd.encode('utf-8')):
            request.session['parent'] = email
            return redirect('/parent/dashboard')
        else:
            return render(request, 'parent/login.html', {'alert':True, 'error': 'Invalid password'})
    return render(request, 'parent/login.html',dictionary)

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
    return render(request, 'parent/forgot.html')

def changepassword(request):
    if request.method == 'POST':
        data = request.POST
        email = data['email']
        password = data['password']
        pswd = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cur = connection.cursor()
        cur.execute("UPDATE parent SET password = %s WHERE email = %s",[pswd, email])
        cur.close()
    return redirect('/parent/login')

def register(request):
    dictionary = {"alert":False}
    if request.method == 'POST':
        data = request.POST
        name = data['name']
        email = data['email']
        d_type = "" if data['document'] == "aadhar" else None
        aadhar = data['aadhar']
        phone = data['phone']
        gender = "" if data['gender']=="Male" else None
        password = data['password']
        confirm = data['confirmpassword']
        cname = data['cname']
        cdob = data['cdob']
        cgender = "" if data['cgender']=="Male" else None
        city = data['city']
        state = data['state']
        pincode = data['pincode']

        if password != confirm:
            return render(request, 'parent/register.html', {'alert':True, 'error': 'Passwords do not match'})
        
        cur = connection.cursor()
        cur.execute("SELECT id from parent where email = %s",[email])
        email_check = cur.fetchone()
        if email_check is not None:
            cur.close()
            return render(request, 'parent/register.html', {'alert':True, 'error': 'Email already exists'})
        cur.execute("SELECT id from parent where phone = %s",[phone])
        phone_check = cur.fetchone()
        if phone_check is not None:
            cur.close()
            return render(request, 'parent/register.html', {'alert':True, 'error': 'Phone Number already exists'})
        cur.execute("SELECT id from parent where d_number = %s",[aadhar])
        aadhar_check = cur.fetchone()
        if aadhar_check is not None:
            cur.close()
            return render(request, 'parent/register.html', {'alert':True, 'error': 'Document Number already exists'})
        
        pswd = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        cur.execute("SELECT id from address where pincode = %s",[pincode])
        pincode_check = cur.fetchone()
        if pincode_check is None:
            cur.execute("INSERT INTO address (city, state, pincode) VALUES (%s, %s, %s)",[city, state, pincode])
        
        cur.execute("SELECT id from address where pincode = %s",[pincode])
        address_id = cur.fetchone()[0]
        cur.execute("INSERT INTO parent (name, email, phone, password, gender, address_id, d_number, d_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",[name, email, phone, pswd, gender, address_id, aadhar, d_type])
        cur.execute("select last_insert_id();")
        p_id = cur.fetchone()[0]
        cur.execute("INSERT INTO child (name, dob, gender, parent_id) values (%s, %s, %s, %s);",[cname,cdob,cgender,p_id])
        cur.close()
        return redirect('/parent/dashboard')
    
    return render(request, 'parent/register.html',dictionary)

def dashboard(request):
    if 'parent' in request.session:
        plot_graph(request)
        return render(request, 'parent/dashboard.html')
    return redirect('/parent/login')

def logout(request):
    if 'parent' in request.session:
        del request.session['parent']
    return redirect('/')

def edit(request):
    if 'parent' in request.session:
        dictionary = {'alert':False}
        cur = connection.cursor()
        if request.method == "POST":
            dictionary['alert'] = True
            data = request.POST
            name = data['name']
            phone = data['phone']
            gender = "" if data['gender'] == "Male" else None
            city = data['city']
            state = data['state']
            pincode = data['pincode']
            cname = data['cname']
            cdob = data['cdob']
            cgender = "" if data['cgender'] == "Male" else None
            cur.execute("SELECT id from parent where phone = %s and email <> %s;",[phone,request.session['parent']])
            phone_check = cur.fetchone()
            if phone_check is not None:
                cur.close()
                dictionary['status'] = "danger"
                dictionary['message'] = "Phone number already exists"
            else:
                query = '''update parent set name = %s, phone = %s, gender = %s where email = %s;'''
                cur.execute(query,[name, phone, gender, request.session['parent']])
                cur.execute("SELECT id FROM parent WHERE email=%s",[request.session['parent']])
                p_id = cur.fetchone()[0]
                cur.execute("UPDATE child set name = %s, dob = %s, gender = %s where parent_id = %s;",[cname,cdob,cgender,p_id])
                cur.execute("select id from address where pincode = %s",[pincode])
                address_id = cur.fetchone()
                if address_id is None:
                    cur.execute("insert into address (city, state, pincode) values (%s, %s, %s)",[city, state, pincode])
                    cur.execute("select last_insert_id();")
                    address_id = cur.fetchone()[0]
                    cur.execute("update parent set address_id = %s where email = %s",[address_id, request.session['parent']])
                else:
                    cur.execute("update address set city = %s, state = %s where id = %s",[city, state, address_id[0]])
                dictionary['status'] = "success"
                dictionary['message'] = "details updated successfully"
        query = '''select p.id, p.name, p.email, p.phone, p.gender, a.city, a.state, a.pincode, c.name, DATE_FORMAT(c.dob, "%%Y-%%m-%%d"), c.gender
        from parent as p
        inner join address as a
        on p.address_id = a.id
        inner join child as c
        on p.id = c.parent_id
        where p.email = %s;
        '''
        cur.execute(query,[request.session['parent']])
        record = cur.fetchone()
        temp = {
        'id' :record[0],
        'name' :record[1],
        'email' :record[2],
        'phone' :record[3],
        'gender' :True if record[4] == "" else False,
        'city' :record[5],
        'state' :record[6],
        'pincode' :record[7],
        'cname' :record[8],
        'cdob' :record[9],
        'cgender' :True if record[10] == "" else False
        }
        print(record[9])
        dictionary = {**dictionary, **temp}
        cur.close()
        return render(request, 'parent/edit.html',dictionary)
    return redirect('/parent/login')

def appointment(request):
    if 'parent' in request.session:
        dictionary = {}
        parent_email = request.session['parent']
        cur = connection.cursor()
        
        query = '''SELECT c.name, ROUND(DATEDIFF(CURDATE(), c.dob)/7, 0), c.gender 
                   FROM child AS c
                   INNER JOIN parent AS p
                   ON c.parent_id = p.id
                   WHERE p.email = %s;'''
        cur.execute(query,[parent_email])
        record = cur.fetchone()
        dictionary['child'] = {
            'name': record[0],
            'age': record[1],
            'gender': "Male" if record[2]=="" else "Female"
        }
        
        query = '''SELECT a.id, v.name, d.dose_number, a.vaccine_date
                   FROM appointment AS a
                   INNER JOIN vaccine AS v
                   ON a.vaccine_id = v.id
                   INNER JOIN child AS c
                   ON a.child_id = c.id
                   INNER JOIN parent AS p
                   ON c.parent_id = p.id
                   INNER JOIN dose AS d
                   ON a.dose_id = d.id
                   WHERE p.email = %s AND a.h_status = 2 AND status IS NULL;'''
        cur.execute(query,[parent_email])
        records = cur.fetchall()
        taken_vaccines = []
        for record in records:
            taken_vaccines.append({
                'name': record[1],
                'dose': record[2],
                'date': record[3]
            })
        dictionary['taken_vaccines'] = taken_vaccines
        
        query = '''SELECT a.id, v.name, d.dose_number, a.vaccine_date, h.name
                   FROM appointment AS a
                   INNER JOIN vaccine AS v
                   ON a.vaccine_id = v.id
                   INNER JOIN child AS c
                   ON a.child_id = c.id
                   INNER JOIN parent AS p
                   ON c.parent_id = p.id
                   INNER JOIN dose AS d
                   ON a.dose_id = d.id
                   INNER JOIN hospital AS h
                   ON a.hospital_id = h.id
                   WHERE p.email = %s AND a.vaccine_date >= CURRENT_DATE() AND a.h_status<>2 AND status IS NULL;'''
        cur.execute(query,[parent_email])
        records = cur.fetchall()
        upcoming_appointments = []
        for record in records:
            upcoming_appointments.append({
                'a_id' : record[0],
                'name': record[1],
                'dose': record[2],
                'date': record[3],
                'hospital': record[4]
            })
        dictionary['upcoming_appointments'] = upcoming_appointments


        query = '''select d.id,d.vaccine_id, v.name, d.dose_number, d.gap
        from dose as d
        inner join vaccine as v
        on d.vaccine_id = v.id
        where d.id not in (select aa.dose_id 
        from appointment as aa
        inner join child as cc
        on aa.child_id = cc.id
        inner join parent as pp
        on cc.parent_id = pp.id 
        where pp.email = %s and aa.status is null)
        and d.gap-ROUND(DATEDIFF(CURDATE(), (select dob from child where parent_id=(select id from parent where email=%s)))/7, 0) BETWEEN 0 AND 4 order by d.gap;
        '''
        cur.execute(query,[parent_email,parent_email])
        records = cur.fetchall()
        upcoming_vaccinations = []
        for record in records:
            upcoming_vaccinations.append({
                'name': record[2],
                'dose': record[3],
                'within': record[4]
            })
        dictionary['upcoming_vaccinations'] = upcoming_vaccinations

        query = '''select d.id,d.vaccine_id, v.name, d.dose_number, d.gap
        from dose as d
        inner join vaccine as v
        on d.vaccine_id = v.id
        where d.id not in (select aa.dose_id 
        from appointment as aa
        inner join child as cc
        on aa.child_id = cc.id
        inner join parent as pp
        on cc.parent_id = pp.id 
        where pp.email = %s and aa.status is null)
        and ROUND(DATEDIFF(CURDATE(), (select dob from child where parent_id=(select id from parent where email=%s)))/7, 0) > d.gap order by d.gap;
        '''
        cur.execute(query,[parent_email,parent_email])
        records = cur.fetchall()
        missed_vaccines = []
        for record in records:
            missed_vaccines.append({
                'name': record[2],
                'dose': record[3],
                'within': record[4]
            })
        dictionary['missed_vaccines'] = missed_vaccines

        return render(request, 'parent/appointment.html',dictionary)
    return redirect('/parent/login')

def data_fetcher():
    cur = connection.cursor()
    cur.execute("SELECT id,name from vaccine")
    records = cur.fetchall()
    cur.close()
    vaccine = []
    for i in records:
        vaccine.append({
            'id':i[0],
            'name':i[1]
        })
    return vaccine

def book(request):
    if 'parent' in request.session:
        dictionary = {'first':True,'alert':False,'ok':False,'second':False}
        dictionary['vaccine'] = data_fetcher()
        return render(request, 'parent/book.html',dictionary)
    return redirect('/parent/login')

def book1(request):
    if 'parent' in request.session:
        if request.method == "POST":
            dictionary = {'first':False,'alert':False,'ok':False,'second':False}
            dictionary['vaccine'] = data_fetcher()
            data = request.POST
            vaccine = data['vaccine']
            dose = data['dose']
            pin = data['pincode']
            city = data['city']
            date = data['dateOfAppointment']
            
            cur = connection.cursor()
            query = '''SELECT a.id
            FROM appointment AS a
            INNER JOIN child AS c
            ON a.child_id = c.id
            INNER JOIN parent AS p
            ON c.parent_id = p.id
            INNER JOIN dose AS d
            ON a.dose_id = d.id
            WHERE p.email = %s AND a.vaccine_id = %s AND d.dose_number = %s AND a.status IS NULL;
            '''
            cur.execute(query,[request.session['parent'],vaccine,dose])
            previous = cur.fetchone()
            if previous is not None:
                dictionary['first'] = True
                dictionary['alert'] = True
                dictionary['error'] = "You have already taken this vaccine, please book the next dose"
                cur.close()
                return render(request,'parent/book.html',dictionary)

            query = '''SELECT id
            FROM dose WHERE vaccine_id = %s AND dose_number = %s; 
            '''
            cur.execute(query,[vaccine,dose])
            previous = cur.fetchone()
            if previous is None:
                dictionary['first'] = True
                dictionary['alert'] = True
                dictionary['error'] = "Decrease the dose number as this vaccine does not have enough doses"
                cur.close()
                return render(request,'parent/book.html',dictionary)
            dictionary['d_id'] = previous[0]
            if pin != '':
                query = '''SELECT id 
                FROM address
                WHERE pincode = %s;
                '''
                cur.execute(query,[pin])
                address_id = cur.fetchone()
                if address_id is None:
                    dictionary['first'] = True
                    dictionary['alert'] = True
                    dictionary['error'] = "No hospitals in this pincode"
                    cur.close()
                    return render(request,'parent/book.html',dictionary)

                query = '''select id,name from hospital where address_id = %s;'''
                cur.execute(query,[address_id])
                hospital_id = cur.fetchall()
                if len(hospital_id)==0:
                    dictionary['first'] = True
                    dictionary['alert'] = True
                    dictionary['error'] = "No hospitals in this pincode"
                    cur.close()
                    return render(request,'parent/book.html',dictionary)
            else:
                query = '''SELECT id 
                FROM address
                WHERE city = %s;
                '''
                cur.execute(query,[city])
                address_id = cur.fetchall()
                if address_id is None:
                    dictionary['first'] = True
                    dictionary['alert'] = True
                    dictionary['error'] = "No hospitals in this city"
                    cur.close()
                    return render(request,'parent/book.html',dictionary)

                query = '''select id,name from hospital where address_id in (SELECT id FROM address WHERE city = %s);'''
                cur.execute(query,[city])
                hospital_id = cur.fetchall()
                if len(hospital_id)==0:
                    dictionary['first'] = True
                    dictionary['alert'] = True
                    dictionary['error'] = "No hospitals in this city"
                    cur.close()
                    return render(request,'parent/book.html',dictionary)
                
            query1 = '''select s.id, s.count-(select count(id) 
            from appointment 
            where hospital_id = %s and vaccine_date=%s and slot_id = s.id and status is null), s.start, s.end
            from slot as s
            where s.hospital_id = %s;'''
            hospitals = []
            for i in hospital_id:
                temp = {}
                temp['id'] = i[0]
                temp['name'] = i[1]
                cur.execute("select count from stock where hospital_id = %s and vaccine_id = %s;",[i[0],vaccine])
                try:
                    z =  cur.fetchone()[0]
                except:
                    z = 0
                temp['stock'] = z
                cur.execute(query1,[i[0],date,i[0]])
                slots = cur.fetchall()
                temp['slots'] = [{'id':j[0],'count':j[1],'color':"success" if j[1]>0 else "danger",'start':j[2],'end':j[3]} for j in slots]
                hospitals.append(temp)
            
            dictionary['hospitals'] = hospitals
            dictionary['second'] = True
            
            cur.execute("select name from child where parent_id = (select id from parent where email = %s)",[request.session['parent']])
            dictionary['child_name'] = cur.fetchone()[0]
            cur.execute("select name from vaccine where id = %s;",[vaccine])
            dictionary['vaccine_name'] = cur.fetchone()[0]
            dictionary['dose_number'] = dose
            dictionary['vaccine_date'] = date
            dictionary['pincode'] = pin
            dictionary['city'] = city
            dictionary['v_id'] = vaccine

            cur.close()
            return render(request,'parent/book.html',dictionary)
        return redirect('/parent/book')
    return redirect('/parent/login')

def confirmbook(request,h_id,v_id,d_id,date,s_id):
    if 'parent' in request.session:
        dictionary = {'first':False,'alert':False,'ok':False,'second':False}
        cur = connection.cursor()
        query = '''insert into appointment (child_id, hospital_id, vaccine_id, dose_id, vaccine_date, slot_id)
                    values ((select c.id from child as c inner join parent as p on c.parent_id=p.id where p.email = %s),%s,%s,%s,%s,%s);'''
        cur.execute(query,[request.session['parent'],h_id,v_id,d_id,date,s_id])
        cur.execute("select last_insert_id();")
        a_id = cur.fetchone()[0]
        query = '''update stock
        set count = count-1, dolu = curdate()
        where hospital_id = %s and vaccine_id = %s;'''
        cur.execute(query,[h_id,v_id])
        
        query = '''select p.name, c.name, v.name, d.dose_number, a.vaccine_date, h.name, s.start, s.end, h.email
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
        cur.close()
        parent = data[0]
        child = data[1]
        vaccine = data[2]
        dose = data[3]
        date = data[4]
        hospital = data[5]
        slot = str(data[6]) + " - " + str(data[7])
        hospital_email = data[8]
        body = f"Dear {parent},\nYour appointment has been confirmed.\nYour appointment details are as follows:\n\nChild Name: {child}\nVaccine: {vaccine}\nDose: {dose}\nDate: {date}\nHospital: {hospital}\nSlot: {slot}\n\nThank you for choosing us.\nRegards,\nTeam TrackMyVaccine."
        send_mail('Vaccination Booked successfully', body, request.session['parent'])

        body = f"Dear {hospital},\nAn appointment has been booked for your hospital.\nAppointment details are as follows:\n\nParent Name: {parent}\nChild Name: {child}\nVaccine: {vaccine}\nDose: {dose}\nDate: {date}\nSlot: {slot}\n\nThank you for choosing us.\nRegards,\nTeam TrackMyVaccine."
        send_mail('Appointment booked successfully', body, hospital_email)
        dictionary['ok'] = True
        dictionary['first'] = True
        dictionary['vaccine'] = data_fetcher()
        return render(request,'parent/book.html',dictionary)
    return redirect('/parent/login')

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

def send_mail(subject, body, to_email):
    try:
        mail = EmailMessage()
        mail['from'] = 'trackmyvaccine37@gmail.com'
        mail['subject'] = subject
        mail['to'] = to_email
        mail.set_content(body)
        
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT')
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        with smtplib.SMTP_SSL('smtp.gmail.com',465,context=ctx) as server:
            server.login('trackmyvaccine37@gmail.com','tgbmlofefkosjifl')
            server.send_message(mail)
        return True
    except Exception as e:
        print(e)
        return False

def plot_graph(request):
    cur = connection.cursor()
    cur.execute("select id, name from vaccine;")
    vaccines = cur.fetchall()
    data = []
    for vaccine in vaccines:
        column = []
        # taken
        query = '''select count(a.id)
                from appointment as a
                inner join child as c
                on a.child_id = c.id
                inner join parent as p
                on c.parent_id = p.id
                where a.h_status = 2 and a.status is null and p.email = %s and a.vaccine_id = %s;'''
        cur.execute(query,[request.session['parent'],vaccine[0]])
        column.append(cur.fetchone()[0])

        # booked
        query = '''select count(a.id)
            from appointment as a
            inner join child as c
            on a.child_id = c.id
            inner join parent as p
            on c.parent_id = p.id
            where a.h_status <> 2 and a.status is null and p.email = %s and a.vaccine_id = %s;'''
        cur.execute(query,[request.session['parent'],vaccine[0]])
        column.append(cur.fetchone()[0])
        
        # not taken
        query='''select (select count(id) from dose where vaccine_id=%s)-count(a.id) as missing
                from appointment as a
                inner join child as c
                on a.child_id = c.id
                inner join parent as p
                on c.parent_id = p.id
                where a.status is null and p.email = %s and a.vaccine_id = %s;'''
        cur.execute(query,[vaccine[0],request.session['parent'],vaccine[0]])
        column.append(cur.fetchone()[0])
        data.append(column)
    data = np.array(data)
    df = pd.DataFrame(data,columns=['Taken','Booked','Not Taken'],index=[i[1] for i in vaccines])
    df.plot(kind='bar',stacked=True,title="Your statistics",color=['#38ab48','#2d47ba','#9e1919'])
    plt.xlabel("Vaccines")
    plt.ylabel("Doses")
    figure = plt.gcf()
    figure.set_size_inches(8, 6)
    plt.savefig("static/images/parentstats.png", dpi=100)

def cancel_appointment(request,a_id):
    if 'parent' in request.session:
        query = '''update appointment as a
                    inner join stock as s
                    on a.hospital_id = s.hospital_id
                    set a.status = "", s.count = s.count + 1
                    where a.id = %s and s.vaccine_id = a.vaccine_id;'''
        cur = connection.cursor()
        cur.execute(query,[a_id])
        query = '''select p.email, h.email, p.name, c.name, v.name, (select dose_number from dose where id=a.dose_id), a.vaccine_date, h.name
                        from appointment as a
                        inner join child as c
                        on a.child_id = c.id
                        inner join parent as p
                        on c.parent_id = p.id
                        inner join vaccine as v
                        on a.vaccine_id = v.id
                        inner join hospital as h
                        on a.hospital_id = h.id
                        where a.id = %s;'''
        cur.execute(query,[a_id])
        data = cur.fetchone()
        cur.close()
        body = f"Dear {data[2]},\nYour appointment has been cancelled.\nYour appointment details were as follows:\n\nChild Name: {data[3]}\nVaccine: {data[4]}\nDose: {data[5]}\nDate: {data[6]}\nHospital: {data[7]}\n\nThank you for choosing us.\nRegards,\nTeam TrackMyVaccine."
        send_mail("Cancellation of vaccine booking", body, data[0])
        body = f"Dear {data[2]},\nAppointment for Mr/Mrs. {data[2]} has been cancelled by the user.\nYour appointment details were as follows:\n\nChild Name: {data[3]}\nVaccine: {data[4]}\nDose: {data[5]}\nDate: {data[6]}\n\nThank you for choosing us.\nRegards,\nTeam TrackMyVaccine."
        send_mail(f"Cancellation of vaccine booking by {data[2]}", body, data[1])
        return redirect('/parent/appointment')
    return redirect('/parent/login')