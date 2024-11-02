import tkinter as tk
from tkinter import messagebox
import sqlite3
import re
import json
#--------------functions--------------------
def isEmpty(user,pas):
    if len(user)==0 or len(pas)==0:
        return True
    else:
        return False

def checkInfo(user,pas=False):
    if pas:
        sql=f'''SELECT * FROM users WHERE username="{user}" AND password="{pas}" '''
    else:
        sql = f'''SELECT * FROM users WHERE username="{user}" '''
    result=cnt.execute(sql)
    rows=result.fetchall()
    if len(rows)<1:
        return False
    else:
        return True

def login():
    global session
    user=txtUser.get()
    pas=txtPas.get()
    if isEmpty(user,pas):
        lblMsg.configure(text='empty fields error!!!',fg='red')
        return
    if checkInfo(user,pas):
        lblMsg.configure(text='Welcome To your Account!',fg='green')
        session=user
        txtUser.delete(0,'end')
        txtPas.delete(0,'end')
        txtUser.configure(state='disabled')
        txtPas.configure(state='disabled')
        btnLogin.configure(state='disabled')
        btnDel.configure(state='active')
        btnShop.configure(state='active')
        btnSearch.configure(state='active')
        if user == "admin":
            btnAdmin.configure(state="normal")
            btnDel.configure(state="disabled")
            btnFeedback.configure(state="disabled")
        else:
            btnAdmin.config(state="disabled")
            btnDel.config(state="normal")
            btnFeedback.configure(state="normal")
        with open('setting.json', 'r') as f:
            dct = json.load(f)
            grade = dct[user]
            if grade < 3:
                btnSpecial.configure(state='disabled')
            else:
                btnSpecial.configure(state='normal')
            if grade==0:
                btnMycart.configure(state='disabled')
            else:
                btnMycart.configure(state='normal')
    else:
        lblMsg.configure(text='Wrong Username Or Password', fg='red')


def signup():
    def signupValidate(user,pas,cpas):
        if user=='' or pas=='' or cpas=='':
            return False,'Empty Fields Error!'
        if pas!=cpas:
            return False,'password and confirmation mismatch!'
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$', pas):
            return False,'password Minimum eight chars,at least one letter and one number'
        if checkInfo(user):
            return False,'Username Already Exist!!'
        return  True,''

    def save2users(user,pas):
        try:
            sql=f'INSERT INTO users (username,password,grade) VALUES ("{user}","{pas}",0)'
            cnt.execute(sql)
            cnt.commit()
            return True
        except:
            return False

    def submit():
        user=txtUser.get()
        pas=txtPas.get()
        cpas=txtCpas.get()
        result,errorMSG=signupValidate(user,pas,cpas)
        if not result:
            lblMsg.configure(text=errorMSG,fg='red')
            return
        result=save2users(user,pas)
        if not result:
            lblMsg.configure(text='something went wrong during data base connection',fg='red')
            return
        lblMsg.configure(text='submit done successfully!',fg='green')
        txtUser.delete(0,'end')
        txtPas.delete(0,'end')
        txtCpas.delete(0,'end')
        txtUser.configure(state='disabled')
        txtPas.configure(state='disabled')
        txtCpas.configure(state='disabled')
        btnSubmit.configure(state='disabled')


    winSignup=tk.Toplevel(win)
    winSignup.title('Signup Panel')
    winSignup.geometry('300x300')
    lblUser = tk.Label(winSignup, text='Username:')
    lblUser.pack()
    txtUser = tk.Entry(winSignup)
    txtUser.pack()
    lblPas = tk.Label(winSignup, text='Password:')
    lblPas.pack()
    txtPas = tk.Entry(winSignup,show="*")
    txtPas.pack()
    lblCpas = tk.Label(winSignup, text='Password confirmation:')
    lblCpas.pack()
    txtCpas = tk.Entry(winSignup,show="*")
    txtCpas.pack()
    lblMsg = tk.Label(winSignup, text='')
    lblMsg.pack()
    btnSubmit = tk.Button(winSignup, text='Submit',command=submit)
    btnSubmit.pack()
    winSignup.mainloop()


def delAccount():
    global session
    result=messagebox.askyesno(title='confirm',message='Are you sure you want to delete this account?')
    if not result:
        lblMsg.configure(text='operation canceled by the user',fg='red')
        return
    result=delUser(session)
    if not result:
        lblMsg.configure(text='something went wrong during database connection',fg='red')
        return
    lblMsg.configure(text='account deleted successfully!',fg='green')
    btnDel.configure(state='disabled')
    btnLogin.configure(state='active')
    txtUser.configure(state='normal')
    txtPas.configure(state='normal')
    session=''

def delUser(user):
     try:
         sql=f'''DELETE FROM users WHERE username="{user}"'''
         cnt.execute(sql)
         cnt.commit()
         return True
     except:
         return False

def getproducts():
    sql='''SELECT * FROM products'''
    result=cnt.execute(sql)
    rows=result.fetchall()
    return rows

def fetch(sql):
    result = cnt.execute(sql)
    rows = result.fetchall()
    if len(rows) > 0:
        return True
    else:
        return False

def idExist(pId):
     sql=f'''SELECT * FROM products WHERE id="{int(pId)}"'''
     return fetch(sql)

def enoughProducts(pid,num):
    sql=f'''SELECT * FROM products WHERE id="{int(pid)}" AND quantity>="{int(num)}"'''
    return fetch(sql)

def getId(user):
    sql = f'''SELECT id FROM users WHERE username = "{user}"'''
    result = cnt.execute(sql)
    rows = result.fetchall()
    return rows[0][0]

def shopPanel():
    def save2cart(pId,pNumber):
        try:
            global session
            id=getId(session)
            sql=f'''INSERT INTO cart (uid,pid,number) VALUES ({id},{int(pId)},{int(pNumber)})'''
            cnt.execute(sql)
            cnt.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def updateQNT(pId,pNumber):
        try:
            pNumber=int(pNumber)
            pId=int(pId)
            sql=f'''UPDATE products SET quantity=quantity-{pNumber} WHERE id={pId}'''
            cnt.execute(sql)
            cnt.commit()
            return True,''
        except Exception as e:
            return False,e

    def buy():
        pId=txtid.get()
        pNumber=txtqnt.get()
        if pId=='' or pNumber=='':
            lblMsg2.configure(text='Fill the blanks!',fg='red')
            return
        if (not pId.isdigit()) or (not pNumber.isdigit()):
            lblMsg2.configure(text='Invalid input!!',fg='red')
            return
        if not idExist(pId):
            lblMsg2.configure(text='Wrong product Id!',fg='red')
            return
        if not enoughProducts(pId,pNumber):
            lblMsg2.configure(text='Not Enough Products!',fg='red')
            return
        result, msg = updateQNT(pId, pNumber)
        if not result:
            lblMsg2.configure(text=f'ERROR while connecting database=>\n{msg}', fg='red')
            return
        result = save2cart(pId, pNumber)
        if not result:
            lblMsg2.configure(text='ERROR while connecting database', fg='red')
            return
        lblMsg2.configure(text='products saved to your cart', fg='green')
        txtid.delete(0, 'end')
        txtqnt.delete(0, 'end')
        lstBox.delete(0, 'end')
        for product in products:
            item = f'''Id={product[0]} , Name={product[1]} , Price={product[2]} , QNT={product[3]}'''
            lstBox.insert('end', item)
        if result:
            sql=f'''UPDATE users SET grade=grade+1 WHERE username="{session}"  '''
            cnt.execute(sql)
            cnt.commit()


    winShop=tk.Toplevel(win)
    winShop.title('Shop Panel')
    winShop.geometry('500x400')
    lstBox=tk.Listbox(winShop,width=50)
    lstBox.pack()
    lblid=tk.Label(winShop,text='Id:')
    lblid.pack()
    txtid=tk.Entry(winShop)
    txtid.pack()
    lblqnt=tk.Label(winShop,text='numbers:')
    lblqnt.pack()
    txtqnt=tk.Entry(winShop)
    txtqnt.pack()
    btnBuy=tk.Button(winShop,text='Buy!',command=buy)
    btnBuy.pack()
    lblMsg2=tk.Label(winShop,text='')
    lblMsg2.pack()
    products=getproducts()
    for product in products:
        item=f'''Id={product[0]} , Name={product[1]} , Price={product[2]} , QNT={product[3]}'''
        lstBox.insert('end',item)
    winShop.mainloop()



def checkGrade(user):
    with open('setting.json', 'r') as f:
        global grade
        info = json.load(f)
        k = list(info.keys())
        v = list(info.values())
        if user in k:
            i = k.index(user)
            grade = int(v[i])
            return grade

def showCart():
    def getMycart():
        global session
        id=getId(session)
        sql = f'''
                SELECT products.pname, products.price, cart.number 
                FROM products 
                INNER JOIN cart ON products.id = cart.pid
                WHERE cart.uid = {id}
                UNION
                SELECT special.pname, special.price, cart.number 
                FROM special 
                INNER JOIN cart ON special.id = cart.pid
                WHERE cart.uid = {id}
        '''
        result = cnt.execute(sql)
        rows = result.fetchall()
        return rows

    def total_price():
        total = 0
        for product in cart:
            price = product[1]
            quantity = product[2]
            total += price * quantity
        lblMsg5.configure(text=f'Total Price: {total}', fg='green')

    def discount():
        total = 0
        for product in cart:
            price = product[1]
            quantity = product[2]
            total += price * quantity
            discount_price = total * 0.9
            lblMsg5.configure(text=f'Discount has been applied. Total price = {discount_price}', fg='green')

    def Grade():
        try:
            sql = f'''SELECT * FROM users WHERE username="{session}"'''
            result = cnt.execute(sql)
            rows = result.fetchall()
            if len(rows) == 0:
                messagebox.showinfo(title='Error', message='User not found!')
                return False
            for row in rows:
                grade = row[3]
                messagebox.showinfo(title='User Grade', message=f'Grade:{int(grade)}')
        except Exception as e:
            messagebox.showinfo(title='Error', message=f'Error retrieving grade: {e}')
            return False


    winCart=tk.Toplevel(win)
    winCart.title('Cart Panel')
    winCart.geometry('600x600')
    lstbox2=tk.Listbox(winCart,width=80)
    lstbox2.pack()
    btnTotal=tk.Button(winCart,text='tap to see total price',command=total_price)
    btnTotal.pack()
    btnDiscount=tk.Button(winCart,text='tap to see total price with discount',command=discount,state='disabled')
    btnDiscount.pack()
    btnGrade=tk.Button(winCart,text='tap to see your grade',command=Grade)
    btnGrade.pack()
    lblMsg5 = tk.Label(winCart, text="")
    lblMsg5.pack()
    global session
    user=session
    checkGrade(user)
    if grade>5:
        btnDiscount.configure(state='active')
    cart=getMycart()
    for product in cart:
        text=f'name:{product[0]} number:{product[2]} total price={product[1] * product[2]}'
        lstbox2.insert(0,text)
    winCart.mainloop()

def search():
    def save2cart(pId,pNumber):
        try:
            global session
            id=getId(session)
            sql=f'''INSERT INTO cart (uid,pid,number) VALUES ({id},{int(pId)},{int(pNumber)})'''
            cnt.execute(sql)
            cnt.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def updateQNT(pId, pNumber):
        try:
            pNumber = int(pNumber)
            pId = int(pId)
            sql = f'''UPDATE products SET quantity=quantity-{pNumber} WHERE id={pId}'''
            cnt.execute(sql)
            cnt.commit()
            return True, ''
        except Exception as e:
            return False, e

    def buy(pId, pNumber, lblMsg):
        if pId == '' or pNumber == '':
            lblMsg.configure(text='Fill the blanks!', fg='red')
            return
        if (not pId.isdigit()) or (not pNumber.isdigit()):
            lblMsg.configure(text='Invalid input!!', fg='red')
            return
        if not idExist(pId):
            lblMsg.configure(text='Wrong product Id!', fg='red')
            return
        if not enoughProducts(pId, pNumber):
            lblMsg.configure(text='Not Enough Products!', fg='red')
            return
        result, msg = updateQNT(pId, pNumber)
        if not result:
            lblMsg.configure(text=f'ERROR while connecting database=>\n{msg}', fg='red')
            return
        result = save2cart(pId, pNumber)
        if not result:
            lblMsg.configure(text='ERROR while connecting database', fg='red')
            return
        lblMsg.configure(text='products saved to your cart', fg='green')
        if result:
            sql = f'''UPDATE users SET grade=grade+1 WHERE username="{session}"  '''
            cnt.execute(sql)
            cnt.commit()

    def searchProduct():
            Sname=txtSearch.get()
            pId=txtid.get()
            pNumber=txtqnt.get()
            if len(Sname)==0:
                lblMsg.configure(text='empty fields error!',fg='red')
                return
            if Sname.isdigit():
                lblMsg.configure(text='Invalid input!!',fg='red')
                return
            try:
                sql=f'''SELECT * FROM products WHERE pname LIKE ('%{Sname}%')'''
                result=cnt.execute(sql)
                rows = result.fetchall()
                if not rows:
                    lblMsg.configure(text="No products found!", fg='red')
                    return
                listbox.delete(0, tk.END)
                txtSearch.delete(0, tk.END)
                for row in rows:
                    listbox.insert(tk.END, row)
            except Exception as e:
                lblMsg.configure(text=f'Error: {e}', fg='red')


    winSearch=tk.Toplevel(win)
    winSearch.title('Search Panel')
    winSearch.geometry('400x400')
    lblMsg = tk.Label(winSearch, text='')
    lblMsg.pack()
    lblSearch = tk.Label(winSearch, text='Enter Product Name:')
    lblSearch.pack()
    txtSearch = tk.Entry(winSearch)
    txtSearch.pack()
    btnSearch=tk.Button(winSearch,text='Search!',command=searchProduct)
    btnSearch.pack()
    listbox = tk.Listbox(winSearch)
    listbox.pack()
    lblid = tk.Label(winSearch, text='Enter Product ID:')
    lblid.pack()
    txtid = tk.Entry(winSearch)
    txtid.pack()
    lblqnt=tk.Label(winSearch,text='Enter Product Number:')
    lblqnt.pack()
    txtqnt=tk.Entry(winSearch)
    txtqnt.pack()
    btnBuy=tk.Button(winSearch,text='Buy!')
    btnBuy.pack()


def specialOffer():
    def addToCart():
        buySpecial(txtSpecialid.get(), txtSpecialqnt.get(), lblMsg3)

    def save2cart(pId,pNumber):
        try:
            global session
            id=getId(session)
            sql=f'''INSERT INTO cart (uid,pid,number) VALUES ({id},{int(pId)},{int(pNumber)})'''
            cnt.execute(sql)
            cnt.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def specialidExist(pId):
        sql = f'''SELECT * FROM special WHERE id="{int(pId)}"'''
        return fetch(sql)

    def enoughProducts(pid, num):
        sql = f'''SELECT * FROM special WHERE id="{int(pid)}" AND quantity>="{int(num)}"'''
        return fetch(sql)

    def updateQNT(pId, pNumber):
        try:
            pNumber = int(pNumber)
            pId = int(pId)
            sql = f'''UPDATE special SET quantity=quantity-{pNumber} WHERE id={pId}'''
            cnt.execute(sql)
            cnt.commit()
            return True, ''
        except Exception as e:
            return False, e

    def buySpecial(pId, pNumber, lblMsg3):
        if pId == '' or pNumber == '':
            lblMsg3.configure(text='Fill the blanks!', fg='red')
            return
        if (not pId.isdigit()) or (not pNumber.isdigit()):
            lblMsg3.configure(text='Invalid input!!', fg='red')
            return
        if not specialidExist(pId):
            lblMsg3.configure(text='Wrong special product Id!', fg='red')
            return
        if not enoughProducts(pId, pNumber):
            lblMsg3.configure(text='Not Enough special Products!', fg='red')
            return
        result, msg = updateQNT(pId, pNumber)
        if not result:
            lblMsg3.configure(text=f'ERROR while connecting database=>\n{msg}', fg='red')
            return
        result = save2cart(pId, pNumber)
        if not result:
            lblMsg3.configure(text='ERROR while connecting database', fg='red')
            return
        lblMsg3.configure(text='special products saved to your cart', fg='green')
        if result:
            sql = f'''UPDATE users SET grade=grade+2 WHERE username="{session}"  '''
            cnt.execute(sql)
            cnt.commit()
    
    def getSpecialproducts():
        sql = '''SELECT * FROM special'''
        result = cnt.execute(sql)
        rows = result.fetchall()
        return rows


    winSpecial=tk.Toplevel(win)
    winSpecial.title('Special Offers')
    winSpecial.geometry('700x700')
    lblMsg3 = tk.Label(winSpecial, text='')
    lblMsg3.pack()
    lstbox2=tk.Listbox(winSpecial,width=80)
    lstbox2.pack()
    lblSpecialid=tk.Label(winSpecial,text='Enter Special Offer ID:')
    lblSpecialid.pack()
    txtSpecialid=tk.Entry(winSpecial)
    txtSpecialid.pack()
    lblSpecialqnt=tk.Label(winSpecial,text='Enter Special Offer numbers:')
    lblSpecialqnt.pack()
    txtSpecialqnt=tk.Entry(winSpecial)
    txtSpecialqnt.pack()
    btnSpecial=tk.Button(winSpecial,text='add to cart!',command=addToCart)
    btnSpecial.pack()
    special=getSpecialproducts()
    for product in special:
        item=f'''Id={product[0]} , Name={product[1]} , Price={product[2]} , QNT={product[3]}'''
        lstbox2.insert('end',item)
    winSpecial.mainloop()

def Feedback():
    def saveFeedback(session,product, feedback):
        try:
            sql =f'''INSERT INTO feedback (user_id,product, feedback) VALUES ('{session}', '{product}', '{feedback}')'''
            cnt.execute(sql)
            cnt.commit()
        except Exception as e:
            lblMsg4.configure(text=f'Error saving feedback: {e}', fg='red')
            return False
        return True

    def productExist(product):
        sql = f'''SELECT * FROM products WHERE pname="{product}"'''
        result=cnt.execute(sql)
        rows = result.fetchall()
        return rows

    def getFeedback():
        product=txtproduct.get()
        feedback=txtFeedback.get()
        if len(product) == 0 or len(feedback) == 0:
            lblMsg4.configure(text='Empty fields error!', fg='red')
            return
        result=productExist(product)
        if not result:
            lblMsg4.configure(text='Product not found!',fg='red')
        else:
            if saveFeedback(session,product, feedback):
              lblMsg4.configure(text='Feedback has been applied',fg='green')
              tpl=()
              sql='''SELECT * FROM feedback '''
              result=cnt.execute(sql)
              columns = result.fetchall()
              tpl=tuple(columns)
              with open('feedback.json', 'w') as f:
                  json.dump(tpl, f)
              txtproduct.delete(0, tk.END)
              txtFeedback.delete(0, tk.END)


    winFeedback=tk.Toplevel(win)
    winFeedback.title('Feedback')
    winFeedback.geometry('400x400')
    lblMsg4 = tk.Label(winFeedback, text='')
    lblMsg4.pack()
    lblproduct=tk.Label(winFeedback,text='product name:')
    lblproduct.pack()
    txtproduct=tk.Entry(winFeedback)
    txtproduct.pack()
    lblFeedback=tk.Label(winFeedback,text='your feedback:')
    lblFeedback.pack()
    txtFeedback=tk.Entry(winFeedback)
    txtFeedback.pack()
    btnFeedback=tk.Button(winFeedback,text='Done!',command=getFeedback)
    btnFeedback.pack()
    winFeedback.mainloop()

def admin():
    def newProducts():
        def AddToShopPanel():
            pname=txtproduct.get()
            price=txtprice.get()
            quantity=txtqnt.get()
            if (not price.isdigit()) or (not quantity.isdigit()):
                lblMsg7.configure(text='Please enter valid price and/or quantity!',fg='red')
                return False
            if pname=='' or price=='' or quantity=='':
                lblMsg7.configure(text='Please Fill the blanks!',fg='red')
                return False
            else:
                try:
                    sql = f'''INSERT INTO products (pname, price, quantity, date)
                             VALUES ('{pname}', {price}, {quantity}, 0)'''
                    cnt.execute(sql)
                    cnt.commit()
                    lblMsg7.configure(text='Product added!',fg='green')
                except Exception as e:
                    lblMsg7.configure(text=f'Error saving products: {e}', fg='red')
        winNewProducts=tk.Toplevel(winAdmin)
        winNewProducts.title('New Products')
        winNewProducts.geometry('400x400')
        lblproduct = tk.Label(winNewProducts, text='product name:')
        lblproduct.pack()
        txtproduct = tk.Entry(winNewProducts)
        txtproduct.pack()
        lblprice = tk.Label(winNewProducts, text='product price:')
        lblprice.pack()
        txtprice = tk.Entry(winNewProducts)
        txtprice.pack()
        lblqnt = tk.Label(winNewProducts, text='product quantity:')
        lblqnt.pack()
        txtqnt = tk.Entry(winNewProducts)
        txtqnt.pack()
        lblMsg7=tk.Label(winNewProducts, text='')
        lblMsg7.pack()
        btnDone=tk.Button(winNewProducts,text='Done!',command=AddToShopPanel)
        btnDone.pack()
        winNewProducts.mainloop()

    def removeProduct():
        def deleteProduct():
            productId=txtproductid.get()
            if len(productId)==0:
                lblMsg7.configure(text='Empty fields Error!',fg='red')
                return False
            if not productId.isdigit():
                lblMsg7.configure(text='Please enter valid product id!',fg='red')
                return False
            else:
                result=messagebox.askokcancel('Remove product', 'Are you sure you want to delete this product?')
                if result:
                    try:
                        sql=f'''DELETE FROM products WHERE id={int(productId)}'''
                        cnt.execute(sql)
                        cnt.commit()
                        lblMsg7.configure(text='Product has been deleted!',fg='green')
                    except Exception as e:
                        lblMsg7.configure(text=f'Error deleting products: {e}', fg='red')
                        return False

        winRemoveProduct = tk.Toplevel(winAdmin)
        winRemoveProduct.title('Remove Products')
        winRemoveProduct.geometry('400x400')
        lblproductid = tk.Label(winRemoveProduct, text='product ID:')
        lblproductid.pack()
        txtproductid = tk.Entry(winRemoveProduct)
        txtproductid.pack()
        btnDelete=tk.Button(winRemoveProduct,text='Delete',command=deleteProduct)
        btnDelete.pack()
        lblMsg7=tk.Label(winRemoveProduct, text='')
        lblMsg7.pack()
        winRemoveProduct.mainloop()


    def updateProducts():
        def update():
            Id=txtproductId.get()
            product=txtproduct.get()
            price=txtprice.get()
            quantity=txtqnt.get()
            if (not price.isdigit()) or (not quantity.isdigit()):
                lblMsg9.configure(text='Please enter valid price and/or quantity!',fg='red')
                return False
            if product=='' or price=='' or quantity=='':
                lblMsg9.configure(text='Please Fill the blanks!',fg='red')
                return False
            else:
                result = messagebox.askokcancel('Update Product', 'Are you sure you want to update this product?')
                if result:
                    try:
                        sql=f'''UPDATE products SET pname='{product}' ,price={int(price)}, quantity={int(quantity)} WHERE id={int(Id)}'''
                        cnt.execute(sql)
                        cnt.commit()
                        lblMsg9.configure(text='Product has been updated!',fg='green')
                    except Exception as e:
                        lblMsg9.configure(text=f'Error updating products: {e}', fg='red')
                        return False


        winUpdate=tk.Toplevel(winAdmin)
        winUpdate.title('New Products')
        winUpdate.geometry('400x400')
        lblproductId=tk.Label(winUpdate, text='product ID:')
        lblproductId.pack()
        txtproductId = tk.Entry(winUpdate)
        txtproductId.pack()
        lblproduct = tk.Label(winUpdate, text='product name:')
        lblproduct.pack()
        txtproduct = tk.Entry(winUpdate)
        txtproduct.pack()
        lblprice = tk.Label(winUpdate, text='product price:')
        lblprice.pack()
        txtprice = tk.Entry(winUpdate)
        txtprice.pack()
        lblqnt = tk.Label(winUpdate, text='product quantity:')
        lblqnt.pack()
        txtqnt = tk.Entry(winUpdate)
        txtqnt.pack()
        lblMsg9=tk.Label(winUpdate, text='')
        lblMsg9.pack()
        btnDone=tk.Button(winUpdate,text='Update!',command=update)
        btnDone.pack()
        winUpdate.mainloop()


    def ViewFeedback():
        def getFeedback():
            sql='''SELECT * FROM feedback '''
            result=cnt.execute(sql)
            rows = result.fetchall()
            return rows
        winViewFeedback = tk.Toplevel(winAdmin)
        winViewFeedback.title('View Feedbacks')
        winViewFeedback.geometry('800x400')
        lstbox=tk.Listbox(winViewFeedback,width=80)
        lstbox.pack()
        lblMsg8 = tk.Label(winViewFeedback, text='')
        lblMsg8.pack()
        feedbacks = getFeedback()
        for feedback in feedbacks:
            text = f'user_id:{feedback[0]} username:{feedback[1]} product:{feedback[2]} feedback:{feedback[3]} '
            lstbox.insert(0, text)
        winViewFeedback.mainloop()


    def newOffers():
        def AddToSpecialOffer():
            pname = txtproduct.get()
            price = txtprice.get()
            quantity = txtqnt.get()
            if (not price.isdigit()) or (not quantity.isdigit()):
                lblMsg7.configure(text='Please enter valid price and/or quantity!', fg='red')
                return False
            if pname == '' or price == '' or quantity == '':
                lblMsg7.configure(text='Please Fill the blanks!', fg='red')
                return False
            else:
                try:
                    sql = f'''INSERT INTO special (pname, price, quantity, date)
                             VALUES ('{pname}', {price}, {quantity}, 0)'''
                    cnt.execute(sql)
                    cnt.commit()
                    lblMsg7.configure(text=' New Special Offer added!', fg='green')
                except Exception as e:
                    lblMsg7.configure(text=f'Error saving products: {e}', fg='red')


        winNewOffers=tk.Toplevel(winAdmin)
        winNewOffers.title('Add New Special Offers')
        winNewOffers.geometry('500x500')
        lblproduct = tk.Label(winNewOffers, text='Special Offer name:')
        lblproduct.pack()
        txtproduct = tk.Entry(winNewOffers)
        txtproduct.pack()
        lblprice = tk.Label(winNewOffers, text='Special Offer price:')
        lblprice.pack()
        txtprice = tk.Entry(winNewOffers)
        txtprice.pack()
        lblqnt = tk.Label(winNewOffers, text='Special Offer quantity:')
        lblqnt.pack()
        txtqnt = tk.Entry(winNewOffers)
        txtqnt.pack()
        lblMsg7=tk.Label(winNewOffers, text='')
        lblMsg7.pack()
        btnDone=tk.Button(winNewOffers,text='Done!',command=AddToSpecialOffer)
        btnDone.pack()
        winNewOffers.mainloop()

    def updateOffers():
        def Update():
            Id=txtSproductId.get()
            product=txtSproduct.get()
            price=txtSprice.get()
            quantity=txtSqnt.get()
            if (not price.isdigit()) or (not quantity.isdigit()):
                lblMsgS.configure(text='Please enter valid price and/or quantity!',fg='red')
                return False
            if product=='' or price=='' or quantity=='':
                lblMsgS.configure(text='Please Fill the blanks!',fg='red')
                return False
            else:
                result = messagebox.askyesno(title='Update Product', message='Are you sure you want to update this Offer?')
                if result:
                    try:
                        sql=f'''UPDATE special SET pname='{product}' ,price={int(price)}, quantity={int(quantity)} WHERE id={int(Id)}'''
                        cnt.execute(sql)
                        cnt.commit()
                        lblMsgS.configure(text='Offer has been updated!',fg='green')
                    except Exception as e:
                        lblMsgS.configure(text=f'Error updating Offers: {e}', fg='red')
                        return False

        winUpdateS=tk.Toplevel(winAdmin)
        winUpdateS.title('New Products')
        winUpdateS.geometry('600x600')
        lblSproductId=tk.Label(winUpdateS, text='Special Offer ID:')
        lblSproductId.pack()
        txtSproductId = tk.Entry(winUpdateS)
        txtSproductId.pack()
        lblSproduct = tk.Label(winUpdateS, text='Offer name:')
        lblSproduct.pack()
        txtSproduct = tk.Entry(winUpdateS)
        txtSproduct.pack()
        lblSprice = tk.Label(winUpdateS, text='Offer price:')
        lblSprice.pack()
        txtSprice = tk.Entry(winUpdateS)
        txtSprice.pack()
        lblSqnt = tk.Label(winUpdateS, text='Offer quantity:')
        lblSqnt.pack()
        txtSqnt = tk.Entry(winUpdateS)
        txtSqnt.pack()
        lblMsgS=tk.Label(winUpdateS, text='')
        lblMsgS.pack()
        btnSDone=tk.Button(winUpdateS,text='Update!',command=Update)
        btnSDone.pack()
        winUpdateS.mainloop()


    def removeOffers():
        def RemoveFromSpecialOffer():
            OfferId=txtOfferid.get()
            if len(OfferId)==0:
                lblMsg8.configure(text='Empty fields Error!',fg='red')
                return False
            if not OfferId.isdigit():
                lblMsg8.configure(text='Please enter valid Special Offer id!',fg='red')
                return False
            else:
                result=messagebox.askyesno(title='Remove product', message= 'Are you sure you want to delete this offer?')
                if result:
                    try:
                        sql=f'''DELETE FROM special WHERE id={int(OfferId)}'''
                        cnt.execute(sql)
                        cnt.commit()
                        lblMsg8.configure(text='Offer has been deleted!',fg='green')
                    except Exception as e:
                        lblMsg8.configure(text=f'Error deleting Offers: {e}', fg='red')
                        return False

        winRemoveSpecialOffer = tk.Toplevel(winAdmin)
        winRemoveSpecialOffer.title('Remove Special Offer')
        winRemoveSpecialOffer.geometry('400x400')
        lblOfferid = tk.Label(winRemoveSpecialOffer, text='Special Offer ID:')
        lblOfferid.pack()
        txtOfferid = tk.Entry(winRemoveSpecialOffer)
        txtOfferid.pack()
        btnDelete = tk.Button(winRemoveSpecialOffer, text='Delete', command=RemoveFromSpecialOffer)
        btnDelete.pack()
        lblMsg8 = tk.Label(winRemoveSpecialOffer, text='')
        lblMsg8.pack()
        winRemoveSpecialOffer.mainloop()


    def SearchGrade():
        global session
        def Search():
            user=txtSearch.get()
            if len(user)==0:
                lblMsgG.configure(text='Empty fields Error!',fg='red')
                return False
            if user.isdigit():
                lblMsgG.configure(text='Please enter valid Username!',fg='red')
                return False
            else:
                try:
                    sql=f'''SELECT * FROM users WHERE username="{user}"'''
                    result=cnt.execute(sql)
                    rows=result.fetchall()
                    for row in rows:
                        if len(rows)==0:
                            lblMsgG.configure(text='Empty fields Error!',fg='red')
                            return False
                        else:
                              grade = row[3]
                              messagebox.showinfo(title='User Grade', message=f'Grade:{int(grade)}')
                              txtSearch.delete(0, tk.END)
                except Exception as e:
                    lblMsgG.configure(text=f'Error searching Grade: {e}', fg='red')
                    return False

        winSearchGrade = tk.Toplevel(winAdmin)
        winSearchGrade.title('Search Grade Based On Username')
        winSearchGrade.geometry('400x400')
        lblSearch = tk.Label(winSearchGrade, text='Username:')
        lblSearch.pack()
        txtSearch = tk.Entry(winSearchGrade)
        txtSearch.pack()
        btnSearch = tk.Button(winSearchGrade, text='Search.', command=Search)
        btnSearch.pack()
        lblMsgG = tk.Label(winSearchGrade, text='')
        lblMsgG.pack()
        winSearchGrade.mainloop()


    winAdmin=tk.Toplevel(win)
    winAdmin.title('Admin Panel')
    winAdmin.geometry('400x400')
    lblMsg6 = tk.Label(winAdmin, text='')
    lblMsg6.pack()
    btnNewproducts=tk.Button(winAdmin,text='Add New Products.',command=newProducts)
    btnNewproducts.pack()
    btnUpdateProduct=tk.Button(winAdmin,text='Update Products.',command=updateProducts)
    btnUpdateProduct.pack()
    btnRemoveproducts=tk.Button(winAdmin,text='Remove Products.',command=removeProduct)
    btnRemoveproducts.pack()
    btnFeedbackSee=tk.Button(winAdmin,text='View Feedbacks.',command=ViewFeedback)
    btnFeedbackSee.pack()
    btnNewOffers=tk.Button(winAdmin,text='Add New Special Offers.',command=newOffers)
    btnNewOffers.pack()
    btnUpdateProduct=tk.Button(winAdmin,text='Update Special Offers.',command=updateOffers)
    btnUpdateProduct.pack()
    btnRemoveOffers=tk.Button(winAdmin,text='Remove Special Offers.',command=removeOffers)
    btnRemoveOffers.pack()
    btnSearchGrade=tk.Button(winAdmin,text='Search Grade.',command=SearchGrade)
    btnSearchGrade.pack()
    winAdmin.mainloop()


#-------------- database codes ---------------
cnt=sqlite3.connect('shop.db')
# sql='''CREATE TABLE users (
#         id INTEGER PRIMARY KEY,
#         username VARCHAR(30) NOT NULL,
#         password VARCHAR(30) NOT NULL,
#         grade INTEGER NOT NULL)'''
# cnt.execute(sql)

# sql='''INSERT INTO users (username,password,grade)
#         VALUES('admin','123456789',0)'''
# cnt.execute(sql)
# cnt.commit()


# sql='''CREATE TABLE products (
#        id INTEGER PRIMARY KEY,
#        pname VARCHAR(50) NOT NULL,
#        price REAL NOT NULL,
#        quantity INTEGER NOT NULL,
#        date VARCHAR )'''
# cnt.execute(sql)
# cnt.commit()

# sql='''INSERT INTO products (pname,price,quantity,date)
#          VALUES('tee',30000,300,0)'''
# cnt.execute(sql)
# cnt.commit()


# sql='''CREATE TABLE cart (
#        id INTEGER PRIMARY KEY,
#        uid quantity INTEGER NOT NULL,
#        pid INTEGER NOT NULL,
#        number INTEGER NOT NULL)'''
# cnt.execute(sql)
# cnt.commit()


# sql = '''CREATE TABLE special(
#        id INTEGER PRIMARY KEY,
#        pname VARCHAR(50) NOT NULL,
#        price REAL NOT NULL,
#        quantity INTEGER NOT NULL,
#        date VARCHAR)'''
# cnt.execute(sql)
# cnt.commit()

# sql='''INSERT INTO special (pname, price, quantity, date)
#         VALUES ('lasagna + hot dog + orange juice',300000, 35 ,0)'''
# cnt.execute(sql)
# cnt.commit()
#

# sql='''CREATE TABLE feedback(
#     id INTEGER PRIMARY KEY,
#     user_id INTEGER,
#     product VARCHAR(50),
#     feedback TEXT)'''
# cnt.execute(sql)
# cnt.commit()


dct = {}
sql = '''SELECT * FROM users'''
result = cnt.execute(sql)
columns = result.fetchall()
for column in columns:
    dct[column[1]] = column[3]
cnt.commit()
with open('setting.json', 'w') as f:
    json.dump(dct, f)

#---------------- main -----------------------

session=''
win=tk.Tk()
win.title('Shop Project')
win.geometry('400x400')
lblUser=tk.Label(win,text='Username:')
lblUser.pack()
txtUser=tk.Entry(win)
txtUser.pack()
lblPas=tk.Label(win,text='Password:')
lblPas.pack()
txtPas=tk.Entry(win,show="*")
txtPas.pack()
lblMsg=tk.Label(win,text='')
lblMsg.pack()
btnLogin=tk.Button(win,text='Login',command=login)
btnLogin.pack()
btnSignup=tk.Button(win,text='Signup',command=signup)
btnSignup.pack()
btnDel=tk.Button(win,text='Delete Account',state='disabled',command=delAccount)
btnDel.pack()
btnShop=tk.Button(win,text='Shop Panel',state='disabled',command=shopPanel)
btnShop.pack()
btnMycart=tk.Button(win,text='My Cart',state='disabled',command=showCart)
btnMycart.pack()
btnSearch=tk.Button(win, text='Search', state='disabled', command=search)
btnSearch.pack()
btnSpecial=tk.Button(win,text='Special Offers',state='disabled',command=specialOffer)
btnSpecial.pack()
btnFeedback=tk.Button(win,text='Feedback',state='disabled',command=Feedback)
btnFeedback.pack()
btnAdmin=tk.Button(win,text='admin',state='disabled',command=admin)
btnAdmin.pack()
win.mainloop()





