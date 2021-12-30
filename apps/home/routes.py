# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request ,redirect, url_for
from flask_login import (
    login_required,
    current_user
)
from jinja2 import TemplateNotFound
from apps import orders , wcapi,wc_oauth
import json
import os

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@blueprint.route('/index')
@login_required
def index():

    # return current_user.get_id()
    # user_id = session["user_id"]

    params = {'role': "all"}

    user_list=wcapi.get("customers",params=params)


    user_list=json.loads(user_list.text)

    user_id=-1
    user_role=""
    for user in user_list:
        if (user["username"]==str(current_user)):
            user_id=user["id"]
            user_role=user["role"]
            break

    user= str(current_user)

    return render_template('home/index.html',user_role=user_role,weekend=current_user,segment='index')


@blueprint.route('/all_pending')
@login_required
def all_pending():
    params = {'status': 'pending'}

    response=wcapi.get("orders",params=params)

    # return current_user.get_id()
    # user_id = session["user_id"]
    # user= str(current_user)

    # data=orders.all()
    data=json.loads(response.text)
    for item in data:
        item["total"]=int(item["total"].split(".")[0])

    params = {'role': "all"}

    user_list=wcapi.get("customers",params=params)


    user_list=json.loads(user_list.text)

    user_id=-1
    user_role=""
    for user in user_list:
        if (user["username"]==str(current_user)):
            user_id=user["id"]
            user_role=user["role"]
            break
    
    

    return render_template('home/tables_pending_all.html',user_role=user_role,weekend=current_user,data=data,segment='all_pending')



@blueprint.route('/all')
@login_required
def all():

    response=wcapi.get("orders")

    # return current_user.get_id()
    # user_id = session["user_id"]
    # user= str(current_user)

    # data=orders.all()
    data=json.loads(response.text)
    for item in data:
        item["total"]=int(item["total"].split(".")[0])

    params = {'role': "all"}

    user_list=wcapi.get("customers",params=params)


    user_list=json.loads(user_list.text)

    user_id=-1
    user_role=""
    for user in user_list:
        if (user["username"]==str(current_user)):
            user_id=user["id"]
            user_role=user["role"]
            break
    

    return render_template('home/tables_all.html',user_role=user_role,weekend=current_user,data=data,segment='all_order')




@blueprint.route('/action_pending',methods=['POST'])
@login_required
def action_pending():
    

    order_id=str(request.form["id"])

 
    
    params = {'status': 'pending'}
    if(request.form["action"]=="approve"):
        params = {'status': 'processing',
                    "billing":{
                        "company":"processing"
                    }
                    }
    elif(request.form["action"]=="delete"):
        params = {'status': 'cancelled'}
    elif (request.form["action"]=="unpaidprocessing"):
        params = {'status': 'unpaidprocessing',

                    "billing":{
                        "company":"processing"
                    }

                    }

    
    url=f'orders/{order_id}'
    response=wcapi.put(url,params)

    # return response.text
    if(response.status_code==200):
        pass
    return redirect('/all_pending')

    # # return current_user.get_id()
    # # user_id = session["user_id"]
    # # user= str(current_user)

    # # data=orders.all()
    # data=json.loads(response.text)
    # for item in data:
    #     item["total"]=int(item["total"].split(".")[0])
    

    return render_template('home/tables_all.html',weekend=current_user,data=data,segment='index')



@blueprint.route('/print_pending')
@login_required
def print_pending():

    
    params = {'role': "all"}

    user_list=wcapi.get("customers",params=params)


    user_list=json.loads(user_list.text)

    user_id=-1
    for user in user_list:
        if (user["username"]==str(current_user)):
            user_id=user["id"]
            break

    data_=[["processing",0],["processing",user_id],["unpaidprocessing",0],["unpaidprocessing",user_id]]
    
    data=[]

    for dd in data_:
        params = {'status': dd[0] , "customer_id":dd[1]}

        response=wcapi.get("orders",params=params)
        # return str(response.text)
        for item in json.loads(response.text):
            if(item["customer_id"]==dd[1]):
                data.append(item)


    # data=json.loads(response.text)

    # params = {'status': "unpaidprocessing"}

    # response=wcapi.get("orders",params=params)

    for item in data:
        item["customer_id"]=str(item["customer_id"])
        item["total"]=int(item["total"].split(".")[0])/4

  
    user_id=-1
    user_role="bb"
    for user in user_list:
        if (user["username"]==str(current_user)):
            user_id=user["id"]
            user_role=user["role"]
            break

    

    return render_template('home/print_pending.html',user_role=user_role,current_user=current_user,current_user_id=str(user_id),data=data,segment='pending')


@blueprint.route('/activate_print_pending',methods=['POST'])
@login_required
def activate_print_pending():
    return str(request.files['file'])

    order_id=str(request.form["id"])

    if(request.form["action"]=="roll"):
        user_id=0
        params = {'customer_id': user_id}

        url=f'orders/{order_id}'
        response=wcapi.put(url,params)

        return redirect('/print_pending')



    if(request.form["action"]=="complete"):
        user_id=0
        params = {'status': "complete"}

        url=f'orders/{order_id}'
        response=wcapi.put(url,params)

        return redirect('/print_pending')

    params = {'role': "all"}

    user_list=wcapi.get("customers",params=params)


    user_list=json.loads(user_list.text)

    user_id=0
    for user in user_list:
        if (user["username"]==str(current_user)):
            user_id=user["id"]
            break

    
    order_id=str(request.form["id"])

    params = {'customer_id': user_id}

    url=f'orders/{order_id}'
    response=wcapi.put(url,params)


    if(response.status_code==200):
        pass

    return redirect('/print_pending')




@blueprint.route('/print_action',methods=['POST'])
@login_required
def print_action():

    # return str(request.form)
    order_id=str(request.form["id"])
    if(request.form["action"]=="roll"):
        user_id=0
        params = {'customer_id': user_id}

        url=f'orders/{order_id}'
        response=wcapi.put(url,params)

        return redirect('/print_pending')



    if(request.form["action"]=="complete"):
        user_id=0
        params = {'status': "complete"}

        url=f'orders/{order_id}'
        response=wcapi.put(url,params)

        return redirect('/print_pending')

    params = {'role': "all"}

    user_list=wcapi.get("customers",params=params)

    # url="http://127.0.0.1/wordpress/wp-json/wp/v2/users"
    # user_list=wc_oauth.get(url)

    user_list=json.loads(user_list.text)

    user_id=0
    for user in user_list:
        if (user["username"]==str(current_user)):
            user_id=user["id"]
            break

    
    order_id=str(request.form["id"])

    params = {'customer_id': user_id}

    url=f'orders/{order_id}'
    response=wcapi.put(url,params)


    if(response.status_code==200):
        pass

    return redirect('/print_pending')




@blueprint.route('/coures')
@login_required
def coures():
    # return str(login_user)
    
    params = {'role': "all"}

    user_list=wcapi.get("customers",params=params)


    user_list=json.loads(user_list.text)

    user_id=-1
    user_role=""

    for user in user_list:
        if (user["username"]==str(current_user)):
            user_id=user["id"]
            break

    category=wcapi.get("products/categories")

    categories=json.loads(category.text)


    

    return render_template('home/coures.html',user_role=user_role,categories=categories,current_user=current_user,current_user_id=str(user_id),segment='coures')

# @blueprint.route('/coures_upload_action', methods = [ 'POST'])
# def upload_file():
#    if request.method == 'POST':
#       f = request.files['file']
#       f.save(f.filename)
#       return 'file uploaded successfully'


@blueprint.route('/coures_upload_action',methods=['POST'])
@login_required
def coures_upload_action():
    if request.method == 'POST':
        f = request.files['file']
        # f.save(f.filename)

        f.save(os.path.join("uploads", f.filename))
        return 'file uploaded successfully'
#     # return str(request.files['file'])

#     f = request.files['file']
#     f.save(secure_filename(f.filename))
#     return 'file uploaded successfully'

#     file=request.files["file"]
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#         # return redirect(url_for('download_file', name=filename))

#     return "str(request.form)"
#     order_id=str(request.form["id"])



#     params = {'role': "all"}

#     user_list=wcapi.get("customers",params=params)

#     # url="http://127.0.0.1/wordpress/wp-json/wp/v2/users"
#     # user_list=wc_oauth.get(url)

#     user_list=json.loads(user_list.text)

#     user_id=0
#     for user in user_list:
#         if (user["username"]==str(current_user)):
#             user_id=user["id"]
#             break

    
#     order_id=str(request.form["id"])

#     params = {'customer_id': user_id}

#     url=f'orders/{order_id}'
#     response=wcapi.put(url,params)


#     if(response.status_code==200):
#         pass

#     return redirect('/print_pending')



@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
