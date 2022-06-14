from flask import Flask, render_template, redirect, url_for, request, make_response, session
import requests

app = Flask(__name__)
app.secret_key = "abc" 

#base_url = 'https://thinkfotech02.herokuapp.com'
base_url = 'http://127.0.0.1:8000'

@app.route('/')
def homePage():
	if 'user' in session:
		userID = session['user']
		response = requests.get(base_url + '/user/' + userID)
		userDetails = response.json()
		response = requests.get(base_url + '/itemList/' + userID + '/oth')
		othItemList = response.json()
		response = requests.post(base_url + '/filterItemList',data={'userID' : userID})
		filterItemList = response.json()
		locationList = filterItemList['location']
		categoryList = filterItemList['category']
		response = requests.post(base_url + '/costEstimation/' + userID)
		costEstimation = response.json()
		userCart = costEstimation['userCart']
		return render_template('user_home.html', userDetails=userDetails, othItemList=othItemList, locationList=locationList, categoryList=categoryList, catID='nill', catName='nill', userCart=userCart)
	else:
		response = requests.get(base_url + '/itemList/admin/nil')
		itemList = response.json()
		response = requests.post(base_url + '/filterItemList',data={'userID' : 'user'})
		filterItemList = response.json()
		locationList = filterItemList['location']
		categoryList = filterItemList['category']
		return render_template('home.html', itemList=itemList, locationList=locationList, categoryList=categoryList, catID='nill', catName='nill')

@app.route('/home1', methods=['POST', 'GET'])
def filterHomePage():
	if request.method == 'GET':
		userInput = request.args.to_dict()
		if userInput['catID'] == 'rate':
			userInput['catName'] = userInput['minLimit'] + '-' + userInput['maxLimit']
		if 'user' in session:
			userID = session['user']
			userInput['userID'] = userID
			response = requests.get(base_url + '/user/' + userID)
			userDetails = response.json()
			response = requests.post(base_url + '/filterItem',data=userInput)
			if response.status_code != 400:
				othItemList = response.json()
			else:
				othItemList = {}
			response = requests.post(base_url + '/filterItemList',data={'userID' : userID})
			filterItemList = response.json()
			locationList = filterItemList['location']
			categoryList = filterItemList['category']
			response = requests.post(base_url + '/costEstimation/' + userID)
			costEstimation = response.json()
			userCart = costEstimation['userCart']
			return render_template('user_home.html', userDetails=userDetails, othItemList=othItemList, locationList=locationList, categoryList=categoryList, catID=userInput['catID'], catName=userInput['catName'], userCart=userCart)
		else:
			response = requests.post(base_url + '/filterItem',data=userInput)
			if response.status_code != 400:
				itemList = response.json()
			else:
				itemList = {}
			response = requests.post(base_url + '/filterItemList',data={'userID' : 'user'})
			filterItemList = response.json()
			locationList = filterItemList['location']
			categoryList = filterItemList['category']
			return render_template('home.html', itemList=itemList, locationList=locationList, categoryList=categoryList, catID=userInput['catID'], catName=userInput['catName'])

@app.route('/home2', methods=['POST', 'GET'])
def searchHomePage():
 if request.method == 'GET':
 	userInput = request.args.to_dict()
 	if 'user' in session:
 		userID = session['user']
 		userInput['userID'] = userID
 		response = requests.get(base_url + '/user/' + userID)
 		userDetails = response.json()
 		response = requests.post(base_url + '/searchItem',data=userInput)
 		if response.status_code != 400:
 			othItemList = response.json()
 		else:
 			othItemList = {}
 		response = requests.post(base_url + '/filterItemList',data={'userID' : userID})
 		filterItemList = response.json()
 		locationList = filterItemList['location']
 		categoryList = filterItemList['category']
 		response = requests.post(base_url + '/costEstimation/' + userID)
 		costEstimation = response.json()
 		userCart = costEstimation['userCart']
 		return render_template('user_home.html', userDetails=userDetails, othItemList=othItemList, locationList=locationList, categoryList=categoryList, catID=userInput['catID'], catName=userInput['catName'], userCart=userCart)
 	else:
 		response = requests.post(base_url + '/searchItem',data=userInput)
	 	if response.status_code != 400:
	 		itemList = response.json()
	 	else:
	 		itemList = {}
	 	response = requests.post(base_url + '/filterItemList',data={'userID' : 'user'})
	 	filterItemList = response.json()
	 	locationList = filterItemList['location']
	 	categoryList = filterItemList['category']
	 	return render_template('home.html', itemList=itemList, locationList=locationList, categoryList=categoryList, catID=userInput['catID'], catName=userInput['catName'])

@app.route('/admin')
def adminHomePage():
	if 'admin' in session:
		response = requests.get(base_url + '/itemList/ADMIN/nil')
		itemList = response.json()
		return render_template('admin_home.html', itemList=itemList)
	else:
		return render_template('login.html', session='admin')

@app.route('/othItemProfile/<itemID>')
def othItemProfile(itemID):
	if 'user' in session:
		userID = session['user']
		response = requests.get(base_url + '/user/' + userID)
		userDetails = response.json()
		response = requests.get(base_url + '/item/' + itemID)
		itemDetails = response.json()
		response = requests.get(base_url + '/user/' + itemDetails['userID'])
		othUserDetails = response.json()
		othID = itemDetails['userID']
		response = requests.post(base_url + '/costEstimation/' + userID)
		costEstimation = response.json()
		userCart = costEstimation['userCart']
		response = requests.get(base_url + '/othItemComment/' + userID + '/' + itemID)
		itemComment = response.json()
		return render_template('oth_item_profile.html', userID=userID, userDetails=userDetails, itemID=itemID, itemDetails=itemDetails, othUserDetails=othUserDetails, othID=othID, userCart=userCart, itemComment=itemComment)
	else:
		response = requests.get(base_url + '/item/' + itemID)
		itemDetails = response.json()
		response = requests.get(base_url + '/itemComment/' + itemID)
		itemComment = response.json()
		return render_template('general_item_profile.html', itemID=itemID, itemDetails=itemDetails, itemComment=itemComment)

@app.route('/loginPage/<itemID>')
def loginPage(itemID):
	return render_template('login.html', session='user', itemID=itemID)

@app.route('/addToCart', methods=['POST', 'GET'])
def addToCart():
	if request.method == 'POST':
		userInput = request.form.to_dict()
		if 'user' in session:
			userID = session['user']
			response = requests.post(base_url + '/itemCart/' + userID, data=userInput)
			return redirect(url_for('othItemProfile',itemID=userInput['itemID']))
		else:
			return redirect(url_for('loginPage',itemID=userInput['itemID']))

@app.route('/rateItem', methods=['POST', 'GET'])
def rateItem():
	if request.method == 'POST':
		userInput = request.form.to_dict()
		if 'user' in session:
			userID = session['user']
			response = requests.post(base_url + '/itemRating/' + userInput['itemID'], data={'userID' : userID, 'rating' : userInput['rating']})
			return redirect(url_for('othItemProfile',itemID=userInput['itemID']))

@app.route('/signup', methods=['POST', 'GET'])
def signup():
	if request.method == 'POST':
		userInput = request.form.to_dict()
		userImg = request.files['photo']
		if userImg:
			files = {'photo' : (userImg.filename, userImg, userImg.content_type)}	
			response = requests.post(base_url + '/user', data=userInput, files=files)
		else:
			response=requests.post(base_url + '/user', data=userInput)
		return redirect(url_for('homePage'))

@app.route('/login', methods=['POST', 'GET'])
def login():
	if request.method == 'POST':
		userInput = request.form.to_dict()
		if userInput['session'] == 'user':
			response = requests.post(base_url + '/userLogin', data=userInput)
			if response.json() != '':
				userID = response.json()
				session['user'] = userID
				if userInput['itemID'] == 'nill':
					return redirect(url_for('homePage'))
				else:
					response = requests.get(base_url + '/item/' + userInput['itemID'])
					itemDetails = response.json()
					if itemDetails['userID'] != userID: 
						return redirect(url_for('othItemProfile', itemID= userInput['itemID']))
					else:
						return redirect(url_for('homePage'))
			else:
				return redirect(url_for('loginPage', itemID=userInput['craftID']))
		elif userInput['session'] == 'admin':
			response = requests.post(base_url + '/adminLogin', data=userInput)
			if response.json() == 'admin':
				session['admin'] = response.json()
			return redirect(url_for('adminHomePage'))

@app.route('/logout')
def logout():
	if 'user' in session:
		session.pop('user', None)
	return redirect(url_for('homePage'))

@app.route('/adminLogout')
def adminLogout():
	if 'admin' in session:
		session.pop('admin', None)
	return redirect(url_for('adminHomePage'))

@app.route('/profile/<flag>')
def profile(flag):
	if 'user' in session:
		if flag == 'own':
			userID = session['user']
		else:
			userID = flag
		response = requests.get(base_url + '/user/' + userID)
		userDetails = response.json()
		response = requests.post(base_url + '/costEstimation/' + userID)
		costEstimation = response.json()
		userCart = costEstimation['userCart']
		return render_template('user_profile.html', userDetails=userDetails, flag=flag, userCart=userCart)
	else:
		return redirect(url_for('homePage'))

@app.route('/editProfile')
def editProfile():
	if 'user' in session:
		userID = session['user']
		response = requests.get(base_url + '/user/' + userID)
		userDetails = response.json()
		response = requests.post(base_url + '/costEstimation/' + userID)
		costEstimation = response.json()
		userCart = costEstimation['userCart']
		return render_template('user_edit_profile.html', userDetails=userDetails, userCart=userCart)
	else:
		return redirect(url_for('homePage'))

@app.route('/updateProfile', methods=['POST','GET'])
def updateProfile():
	if 'user' in session:
		if request.method == 'POST':
			userID = session['user']
			userInput = request.form.to_dict()
			userImg = request.files['photo']
			if userImg:
				files = {'photo' : (userImg.filename, userImg, userImg.content_type)}	
				requests.put(base_url + '/user/' + userID, files=files)
			requests.put(base_url + '/user/' + userID, data=userInput)
			return redirect(url_for('profile', flag='own'))
	else:
		return redirect(url_for('homePage'))

@app.route('/userChat/<recID>')
def userChatPage(recID):
	if 'user' in session:
		userID = session['user']
		response = requests.get(base_url + '/user/' + userID)
		userDetails = response.json()
		if recID != 'admin':
			response = requests.get(base_url + '/user/' + recID)
			recDetails = response.json()
		else:
			recDetails = {}
		response = requests.post(base_url + '/message', data={'sender' : userID, 'receiver' : recID, 'action' : 'get'})
		msgList = response.json()
		response = requests.post(base_url + '/costEstimation/' + userID)
		costEstimation = response.json()
		userCart = costEstimation['userCart']
		return render_template('user_chat.html', userDetails=userDetails, recID=recID.upper(), recDetails=recDetails, msgList=msgList, session='user', userCart=userCart)
	else:
		return redirect(url_for('homePage'))

@app.route('/userInbox', methods=['POST', 'GET'])
def userInbox():
	if 'user' in session:
		userID = session['user']
		response = requests.get(base_url + '/user/' + userID)
		userDetails = response.json()
		response = requests.post(base_url + '/message/' + userID)
		msgList = response.json()
		response = requests.post(base_url + '/costEstimation/' + userID)
		costEstimation = response.json()
		userCart = costEstimation['userCart']
		return render_template('user_inbox.html', userDetails=userDetails, msgList=msgList, session='user', userCart=userCart)
	else:
		return redirect(url_for('homePage'))

@app.route('/userSendMessage', methods=['POST', 'GET'])
def userSendMessage():
	if 'user' in session:
		userID = session['user']
		if request.method == 'POST':
			userInput = request.form.to_dict()
			userInput['sender'] = userID
			requests.post(base_url + '/message', data=userInput)
			return redirect(url_for('userChatPage', recID=userInput['receiver']))
	else:
		return redirect(url_for('homePage'))

@app.route('/adminSendMessage', methods=['POST', 'GET'])
def adminSendMessage():
	if 'admin' in session:
		userID = 'ADMIN'
		if request.method == 'POST':
			userInput = request.form.to_dict()
			userInput['sender'] = userID
			requests.post(base_url + '/message', data=userInput)
			return redirect(url_for('adminChatPage', recID=userInput['receiver']))
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/adminInbox', methods=['POST', 'GET'])
def adminInbox():
	if 'admin' in session:
		userID = 'ADMIN'
		response = requests.post(base_url + '/message/' + userID)
		msgList = response.json()
		return render_template('user_inbox.html', msgList=msgList, session='admin')
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/adminChat/<recID>')
def adminChatPage(recID):
	if 'admin' in session:
		userID = 'ADMIN'
		response = requests.get(base_url + '/user/' + recID)
		recDetails = response.json()
		response = requests.post(base_url + '/message', data={'sender' : userID, 'receiver' : recID, 'action' : 'get'})
		msgList = response.json()
		return render_template('user_chat.html', recID=recID.upper(), recDetails=recDetails, msgList=msgList, session='admin')
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/userList')
def userList():
	if 'admin' in session:
		response=requests.get(base_url + '/user')
		userList = response.json()
		return render_template('admin_user_list.html', userList=userList)
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/addItem')
def addItem():
	if 'user' in session:
		userID = session['user']
		response = requests.get(base_url + '/user/' + userID)
		userDetails = response.json()
		response = requests.get(base_url + '/category')
		categoryList = response.json()
		response = requests.post(base_url + '/costEstimation/' + userID)
		costEstimation = response.json()
		userCart = costEstimation['userCart']
		return render_template('user_add_item.html', userDetails=userDetails, categoryList=categoryList, userCart=userCart)
	else:
		return redirect(url_for('homePage'))

@app.route('/itemReg', methods=['POST', 'GET'])
def itemReg():
	if 'user' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			userInput['userID'] = session['user']
			images = request.files.getlist('photo')
			mulFiles = []
			for img in images:
				mulFiles.append(('photo', (img.filename, img, img.content_type)))
			response = requests.post(base_url + '/item', data=userInput, files=mulFiles)
			return redirect(url_for('addItem'))
	else:
		return redirect(url_for('homePage'))

@app.route('/showItems')
def showItems():
	if 'user' in session:
		userID = session['user']
		response = requests.get(base_url + '/user/' + userID)
		userDetails = response.json()
		response = requests.get(base_url + '/itemList/' + userID + '/own')
		itemList = response.json()
		response = requests.post(base_url + '/costEstimation/' + userID)
		costEstimation = response.json()
		userCart = costEstimation['userCart']
		return render_template('user_show_items.html', userDetails=userDetails, itemList=itemList, userCart=userCart)
	else:
		return redirect(url_for('homePage'))

@app.route('/itemProfile/<itemID>')
def itemProfile(itemID):
	if 'user' in session:
		userID = session['user']
		response = requests.get(base_url + '/user/' + userID)
		userDetails = response.json()
		response = requests.get(base_url + '/item/' + itemID)
		itemDetails = response.json()
		response = requests.get(base_url + '/itemTransactionHistory/' + itemID)
		transHistory = response.json()
		response = requests.post(base_url + '/costEstimation/' + userID)
		costEstimation = response.json()
		userCart = costEstimation['userCart']
		response = requests.get(base_url + '/itemComment/' + itemID)
		itemComment = response.json()
		return render_template('item_profile.html', userDetails=userDetails, itemID=itemID, itemDetails=itemDetails, transHistory=transHistory, userCart=userCart, itemComment=itemComment)
	else:
		return redirect(url_for('homePage'))

@app.route('/deleteItem', methods=['POST', 'GET'])
def deleteItem():
	if 'user' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			requests.delete(base_url + '/item/' + userInput['itemID'])
			return redirect(url_for('showItems'))
	else:
		return redirect(url_for('homePage'))

@app.route('/adminDeleteItem', methods=['POST', 'GET'])
def adminDeleteItem():
	if 'admin' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			requests.delete(base_url + '/item/' + userInput['itemID'])
		return redirect(url_for('adminHomePage'))

@app.route('/editItemDetails/<itemID>')
def editItemDetails(itemID):
	if 'user' in session:
		userID = session['user']
		response = requests.get(base_url + '/user/' + userID)
		userDetails = response.json()
		response = requests.get(base_url + '/item/' + itemID)
		itemDetails = response.json()
		response = requests.get(base_url + '/category')
		categoryList = response.json()
		response = requests.post(base_url + '/costEstimation/' + userID)
		costEstimation = response.json()
		userCart = costEstimation['userCart']
		return render_template('user_edit_item.html', userDetails=userDetails, itemID=itemID, itemDetails=itemDetails, categoryList=categoryList, userCart=userCart)
	else:
		return redirect(url_for('homePage'))

@app.route('/updateItemData', methods=['POST', 'GET'])
def updateItemData():
	if 'user' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			requests.put(base_url + '/item/' + userInput['itemID'], data=userInput)
			return redirect(url_for('itemProfile', itemID=userInput['itemID']))
		else:
			return redirect(url_for('homePage'))

@app.route('/deleteItemImg', methods=['POST', 'GET'])
def deleteItemImg():
	if 'user' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			requests.delete(base_url + '/itemImg/' + userInput['itemID'], data=userInput)
			return redirect(url_for('editItemDetails', itemID=userInput['itemID']))
		else:
			return redirect(url_for('homePage'))

@app.route('/addItemImg', methods=['POST', 'GET'])
def addItemImg():
	if 'user' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			images = request.files.getlist('photo')
			mulFiles = []
			for img in images:
				mulFiles.append(('photo', (img.filename, img, img.content_type)))
			requests.put(base_url + '/itemImg/' + userInput['itemID'], files=mulFiles)
			return redirect(url_for('editItemDetails', itemID=userInput['itemID']))
		else:
			return redirect(url_for('homePage'))

@app.route('/userHistory')
def userHistory():
	if 'user' in session:
		userID = session['user']
		response = requests.get(base_url + '/user/' + userID)
		userDetails = response.json()
		response = requests.get(base_url + '/transactionHistory/' + userID + '/all')
		allTransHistory = response.json()
		response = requests.get(base_url + '/transactionHistory/' + userID + '/sell')
		sellTransHistory = response.json()
		response = requests.get(base_url + '/transactionHistory/' + userID + '/buy')
		buyTransHistory = response.json()
		response = requests.post(base_url + '/costEstimation/' + userID)
		costEstimation = response.json()
		userCart = costEstimation['userCart']
		return render_template('user_history.html', userDetails=userDetails,allTransHistory=allTransHistory, sellTransHistory=sellTransHistory, buyTransHistory=buyTransHistory, userCart=userCart)
	else:
		return redirect(url_for('homePage'))

@app.route('/adminHistory')
def adminHistory():
	if 'admin' in session:
		response = requests.get(base_url + '/transactionHistory')
		transHistory = response.json()
		return render_template('admin_history.html', transHistory=transHistory)
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/adminTransDetails/<transID>')
def adminTransDetails(transID):
	if 'admin' in session:
		response = requests.get(base_url + '/transDetails/' + transID)
		transDetails = response.json()
		return render_template('trans_details.html', transDetails=transDetails, session='admin')
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/userTransDetails/<transID>')
def userTransDetails(transID):
	if 'user' in session:
		userID = session['user']
		response = requests.get(base_url + '/user/' + userID)
		userDetails = response.json()
		response = requests.get(base_url + '/transDetails/' + transID)
		transDetails = response.json()
		response = requests.post(base_url + '/costEstimation/' + userID)
		costEstimation = response.json()
		userCart = costEstimation['userCart']
		return render_template('trans_details.html', userID=userID, userDetails=userDetails, transDetails=transDetails, session='user', userCart=userCart)
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/adminItemProfile/<itemID>')
def adminItemProfile(itemID):
	if 'admin' in session:
		response = requests.get(base_url + '/item/' + itemID)
		itemDetails = response.json()
		response = requests.get(base_url + '/user/' + itemDetails['userID'])
		sellerDetails = response.json()
		response = requests.get(base_url + '/itemTransactionHistory/' + itemID)
		transHistory = response.json()
		response = requests.get(base_url + '/itemComment/' + itemID)
		itemComment = response.json()
		return render_template('admin_item_profile.html', itemID=itemID, itemDetails=itemDetails, sellerDetails=sellerDetails, transHistory=transHistory, itemComment=itemComment)
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/adminUserProfile/<userID>')
def adminUserProfile(userID):
	if 'admin' in session:
		response = requests.get(base_url + '/user/' + userID)
		userDetails = response.json()
		response = requests.get(base_url + '/transactionHistory/' + userID + '/all')
		transHistory = response.json()
		response = requests.get(base_url + '/itemList/' + userID + '/own')
		itemList = response.json()
		response = requests.post(base_url + '/costEstimation/' + userID)
		costEstimation = response.json()
		userCart = costEstimation['userCart']
		grandTotal = costEstimation['grandTotal']
		return render_template('admin_user_profile.html', userID=userID, userDetails=userDetails, transHistory=transHistory, itemList=itemList, userCart=userCart, grandTotal=grandTotal)
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/category')
def viewCategory():
	if 'admin' in session:
		response = requests.get(base_url + '/category', timeout=5)
		categoryList = response.json()
		return render_template('category_list.html', categoryList=categoryList)
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/updateCategory', methods=['POST', 'GET'])
def updateCategory():
	if 'admin' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			response = requests.put(base_url + '/category/' + userInput['catID'], data={'name':userInput['name']})
			return redirect(url_for('viewCategory'))
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/deleteCategory', methods=['POST', 'GET'])
def deleteCategory():
	if 'admin' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			response = requests.delete(base_url + '/category/' + userInput['catID'] )
			return redirect(url_for('viewCategory'))
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/addCategory', methods=['POST', 'GET'])
def addCategory():
	if 'admin' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			response = requests.post(base_url + '/category', data={'name':userInput['name']})
			return redirect(url_for('viewCategory'))
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/detailedCart')
def detailedCart():
	if 'user' in session:
		userID = session['user']
		response = requests.get(base_url + '/user/' + userID)
		userDetails = response.json()
		response = requests.post(base_url + '/costEstimation/' + userID)
		costEstimation = response.json()
		userCart = costEstimation['userCart']
		grandTotal = costEstimation['grandTotal']
		return render_template('detailed_cart.html', userDetails=userDetails, userCart=userCart, grandTotal=grandTotal)
	else:
		return redirect(url_for('homePage'))

@app.route('/updateCartItem', methods=['POST', 'GET'])
def updateCartItem():
	if 'user' in session:
		if request.method == 'POST':
			userID = session['user']
			userInput = request.form.to_dict()
			response = requests.put(base_url + '/itemCartUpdate/' + userID + '/' + userInput['itemID'], data=userInput)
			return redirect(url_for('detailedCart'))
	else:
		return redirect(url_for('homePage'))

@app.route('/deleteCartItem', methods=['POST', 'GET'])
def deleteCartItem():
	if 'user' in session:
		if request.method == 'POST':
			userID = session['user']
			userInput = request.form.to_dict()
			response = requests.delete(base_url + '/itemCartUpdate/' + userID + '/' + userInput['itemID'])
			return redirect(url_for('detailedCart'))
	else:
		return redirect(url_for('homePage'))

@app.route('/purchaseDetails')
def purchaseDetails():
	if 'user' in session:
		userID = session['user']
		response = requests.get(base_url + '/user/' + userID)
		userDetails = response.json()
		response = requests.post(base_url + '/costEstimation/' + userID)
		costEstimation = response.json()
		userCart = costEstimation['userCart']
		grandTotal = costEstimation['grandTotal']
		return render_template('purchase_details.html', userDetails=userDetails, userCart=userCart, grandTotal=grandTotal)
	else:
		return redirect(url_for('homePage'))

@app.route('/purchaseItem', methods=['POST', 'GET'])
def purchaseItem():
	if 'user' in session:
		if request.method == 'POST':
			userID = session['user']
			response = requests.post(base_url + '/purchaseItem/' + userID)
			return redirect(url_for('userHistory'))
	else:
		return redirect(url_for('homePage'))

@app.route('/postComment', methods=['POST', 'GET'])
def postComment():
	if 'user' in session:
		if request.method == 'POST':
			userID = session['user']
			userInput = request.form.to_dict()
			response = requests.post(base_url + '/itemComment/' + userInput['itemID'], data=userInput)
			return redirect(url_for('othItemProfile', itemID=userInput['itemID']))
	else:
		return redirect(url_for('homePage'))

@app.route('/deleteComment', methods=['POST', 'GET'])
def deleteComment():
	if 'user' in session:
		if request.method == 'POST':
			userID = session['user']
			userInput = request.form.to_dict()
			response = requests.delete(base_url + '/comment/' + userInput['commentID'])
			return redirect(url_for('othItemProfile', itemID=userInput['itemID']))
	else:
		return redirect(url_for('homePage'))

@app.route('/adminDeleteComment', methods=['POST', 'GET'])
def adminDeleteComment():
	if 'user' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			response = requests.delete(base_url + '/comment/' + userInput['commentID'])
			return redirect(url_for('adminItemProfile', itemID=userInput['itemID']))
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/updateComment', methods=['POST', 'GET'])
def updateComment():
	if 'user' in session:
		if request.method == 'POST':
			userID = session['user']
			userInput = request.form.to_dict()
			response = requests.put(base_url + '/comment/' + userInput['commentID'], data={'comment' : userInput['comment']})
			return redirect(url_for('othItemProfile', itemID=userInput['itemID']))
	else:
		return redirect(url_for('homePage'))

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')