from django.shortcuts import render,redirect
from django.db import connection
from payu_biz.views import make_transaction
import datetime
cursor=connection.cursor()
def session_live(request,phone,user_class):
    request.session['phone']=phone
    request.session['user_class']=user_class
    return request
def if_session_live(request):
    if request.session.has_key("phone"):
        return request.session['phone']
    else:
        return None
def session_out(request):
    if request.session.has_key("phone"):
        del request.session['phone']
        del request.session['user_class']
        return redirect("/")
    return rdirect("/search/home/")
def database(data):
    phone,fname,lname,password,repassword = data['phone'],data['fname'],data['lname'],data['password'],data['repassword']
    sql="insert into user values("+"'"+fname+"'"+','+"'"+lname+"'"+','+"'"+phone+"'"+','+"'"+password+"'"+')'
    try:
        cursor.execute(sql)
    except:
        return False
    connection.close
    return True
def register(request):
    data=request.POST
    x=database(data)
    if x==False:
        return redirect("/search/incorrect/")
    return render(request,'search/index.html',{})
def authenticate(phone,password):
    sql="select password from user where phone = "+"'"+phone+"'"
    cursor.execute(sql)
    result=cursor.fetchall()
    if result==():
        return False
    elif result[0][0]!=password:
        return False
    return True
def placeOrder(phone,addr,ty,num):
    cursor.execute("select max(id) from orders")
    Id=cursor.fetchone()
    Id=int(Id[0])
    dat=str(datetime.datetime.now())
    sql="insert into orders values("+ str(int(Id)+1)+",'"+phone+"','"+addr+"','"+dat+"',"+str(num)+","+'0'+","+ str(ty)+")"
    cursor.execute(sql)
    connection.close
    return Id
def incorrect(request):
    return render(request,'search/incorrect.html',{})
def index(request):
    return render(request,'search/index.html',{})
def home(request):
    context={}
    phone=if_session_live(request)
    if phone==None:
        return redirect("/")
    cursor.execute("select fname,lname from user where phone = "+"'"+phone+"'")
    name=cursor.fetchone()
    name=name[0]+" "+name[1]
    context['name']=name
    return render(request,'search/profile.html',context)
def adminHome(request):
    if if_session_live(request)==None:
        return redirect("/")
    context={}
    cursor.execute("select * from stock")
    result=cursor.fetchone()
    context['have']=result[0]
    cursor.execute("select count(id) from orders where status=0")
    result=cursor.fetchone()
    context['no']=result[0]
    cursor.execute("select sum(amount) from orders where status=0 and type=1")
    result=cursor.fetchone()
    context['pending']=result[0]
    return render(request, 'search/admin.html',context)
    return render(request, 'search/admin.html', {})
def login(request):
    context={}
    data = request.POST
    phone=data['phone']
    password=data['password']
    cursor.execute("select password from admin")
    admn=cursor.fetchone()
    if phone=='admin' and password==admn[0]:
        session_live(request,'admin','E')        
        return redirect("/search/adminHome/")
    name=authenticate(phone,password)
    if name ==False:
        return redirect("/search/incorrect/")
    session_live(request,phone,'E')
    return redirect("/search/home/")
def signup(request):
    context={}
    return render(request ,'search/sign_up.html' , context)
def order(request):
    context={}
    order=request.POST
    phone=if_session_live(request)
    Id=placeOrder(phone,order['address'],order['type'],order['number'])
    cursor.execute("select fname,lname from user where phone='"+phone+"'")
    result=cursor.fetchone()
    #name=result[0]+" "+result[1]
    #context['name']= name
    #context['no']=order['number']
    #context['type']=order['type']
    cleaned_data = {
        'txnid': str(Id)+result[0], 'amount': 450000, 'productinfo': "sample_produ",
        'firstname':result[0], 'email': "anianandchs@gmail.com", 'udf1': '', 
        'udf2': '', 'udf3': '', 'udf4': '', 'udf5': '', 'udf6': '', 'udf7': '', 
        'udf8': '', 'udf9': '', 'udf10': '','phone':phone
    }
    """if order['type']=='1':
        context['type']="Perfect"
    else:
        context['type']="Quarter"
    context['addr']=order['address']
    context['amount']=0"""
    if order['type']=='1':
        #context['amount']=str(int(order['number'])*5)
        cleaned_data['amount']=str(int(order['number'])*5)
    else:
        #context['amount']=str(int(order['number'])*1.5)
        cleaned_data['amount']=str(int(order['number'])*1.5)
    #return render(request, 'search/order.html', context)
    return make_transaction(cleaned_data)
def pending(request):
    context={}
    cursor.execute("select * from orders where status=0")
    result=cursor.fetchall()
    context['data']=result
    return render(request, 'search/pending.html', context)
def ChangeStatus(request):
    context={}
    return render(request, 'search/ChangeStatus.html', context)
def change(request):
    Id=int(request.POST['id'])
    cursor.execute("select amount,type from orders where id="+str(Id))
    result=cursor.fetchone()
    cursor.execute("update orders set status=1 where id="+str(Id))
    if result[1]==1:
        cursor.execute("update stock set have=have-"+str(int(result[0])))
    connection.close
    return redirect("/search/adminHome/")
def confirmed(request):
    context={}
    cursor.execute("select * from orders where status=1")
    result=cursor.fetchall()
    context['data']=result
    return render(request, 'search/confirmed.html', context)
def cleanConfirmed(request):
    cursor.execute("delete from orders where status=1")
    connection.close
    return redirect("/search/adminHome/")
def newRate(request):
    return render(request, 'search/changeRate.html',{})
def changeRate(request):
    data=request.POST
    perfect=data['perfect']
    quarter=data['quarter']
    cursor.execute("update stock set rate1="+str(perfect)+",rate0="+str(quarter))
    connection.close
    return redirect("/search/adminHome/")
def incr(request):
    return render(request, 'search/addStock.html',{})
def addStock(request):
    data=request.POST
    cursor.execute("update stock set have=have+"+str(data['no']))
    connection.close
    return redirect("/search/adminHome/")
def about(request):
    return render(request,'search/about.html',{})
def rates(request):
    context={}
    cursor.execute("select rate1,rate0 from stock")
    result=cursor.fetchone()
    context['perfect'],context['quarter']=result[0],result[1]
    return render(request,'search/rates.html',context)
def myOrders(request):
    data=if_session_live(request)
    cursor.execute("select * from orders where phone='"+str(data)+"'")
    result=cursor.fetchall()
    context={}
    context['data']=result
    return render(request,'search/myOrders.html',context)
def rworker(request):
    return render(request,'search/rworker.html',{})
def wregister(request):
    data=request.POST
    phone=data['phone']
    fname=data['fname']
    lname=data['lname']
    cursor.execute("insert into worker (phone,fname,lname) values('"+phone+"','"+fname+"','"+lname+"')")
    connection.close
    return redirect("/search/adminHome/")
def delete(request):
    return render(request,'search/delete.html',{})
def cdelete(request):
    phone=request.POST['phone']
    if request.POST['type']=='user':
        cursor.execute("delete from user where phone='"+phone+"'")
    else:
        cursor.execute("delete from worker where phone='"+phone+"'")
    connection.close
    return redirect("/search/adminHome/")
def attendance(request):
    return render(request,'search/attendance.html',{}) 
def markAttend(request):
    cursor.execute("update worker set attend=attend+1 where phone='"+request.POST['id']+"'")
    connection.close
    return redirect("/search/attendance/")
def pswd(request):
    return render(request,'search/pswd.html',{})
def chgPaswd(request):
    cursor.execute("update admin set password='"+request.POST['id']+"'")
    connection.close
    return redirect("/")
def payWorker(request):
    return render(request,'search/paym.html',{})
def paySuccess(request):
    phone=request.POST['id']
    amount=int(request.POST['amount'])
    try:
        dat=str(datetime.datetime.now())
        sql="insert into payment (amount,person,time) values("+str(amount)+",'"+phone+"','"+dat+"')"
        cursor.execute(sql)
        sql="update worker set paid=paid+"+str(amount)
        print sql
        cursor.execute(sql)
        connection.close
        return redirect("/search/adminHome/")
    except:
        return redirect('/search/payWorker/')
def allPay(request):
    context={}
    cursor.execute("select * from payment")
    result=cursor.fetchall()
    context['data']=result
    return render(request,'search/allPay.html',context)
def cleanPayment(request):
    cursor.execute("delete from payment")
    cursor.execute("update worker set paid=0,attend=0")
    connection.close
    return redirect("/search/adminHome/")
def workerPayment(request):
    return render(request,'search/payWorker.html',{})
def payInd(request):
    context={}
    phone=request.POST['id']
    sql="select id,time,amount from payment where person="+phone
    cursor.execute(sql)
    result=cursor.fetchall()
    context['data']=result
    return render(request,'search/payInd.html',context)
def successfulTransact(request):
    return render(request,'search/successfulTransact.html',{})
def failedTransact(request):
    return render(request,'search/failedTransact.html',{})
