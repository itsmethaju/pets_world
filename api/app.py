from flask import Flask, request
from flask_restful import Resource, Api, abort, reqparse
from flask_cors import CORS
from firebase import Firebase
import werkzeug
from datetime import datetime
from pytz import timezone

app = Flask(__name__)
api = Api(app)
CORS(app)

config = {
  "apiKey": "AIzaSyCjM4iy43XcmqJXXm1vLSXiVDKcIJazMCM",
  "authDomain": "thinkfotechinnovations.firebaseapp.com",
  "databaseURL": "https://thinkfotechinnovations.firebaseio.com",
  "storageBucket": "thinkfotechinnovations.appspot.com",
}

firebase = Firebase(config)
db = firebase.database()
storage = firebase.storage()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

userRegParser = reqparse.RequestParser()
userRegParser.add_argument('name', type=str, help='name of the user required', required=True)
userRegParser.add_argument('mobileNumber', type=int, help='mobile number of user required', required=True)
userRegParser.add_argument('address', type=str, help='address of user required', required=True)
userRegParser.add_argument('city', type=str, help='city of user required', required=True)
userRegParser.add_argument('email', type=str, help='email of user required', required=True)
userRegParser.add_argument('password', type=str, help='password required', required=True)
userRegParser.add_argument('photo', type=werkzeug.datastructures.FileStorage, help='photo of user required', location='files')

userUpdateParser = reqparse.RequestParser()
userUpdateParser.add_argument('name', type=str)
userUpdateParser.add_argument('mobileNumber', type=int)
userUpdateParser.add_argument('address', type=str)
userUpdateParser.add_argument('city', type=str)
userUpdateParser.add_argument('email', type=str)
userUpdateParser.add_argument('password', type=str)
userUpdateParser.add_argument('photo', type=werkzeug.datastructures.FileStorage, location='files')

userLoginParser = reqparse.RequestParser()
userLoginParser.add_argument('email', type=str, help='email required', required=True)
userLoginParser.add_argument('password', type=str, help='password required', required=True)

adminLoginParser = reqparse.RequestParser()
adminLoginParser.add_argument('email', type=str, help='email required', required=True)
adminLoginParser.add_argument('password', type=str, help='password required', required=True)

catRegParser = reqparse.RequestParser()
catRegParser.add_argument('name', type=str, help='name of the category required', required=True)

itemRegParser = reqparse.RequestParser()
itemRegParser.add_argument('name', type=str, help='name of the item required', required=True)
itemRegParser.add_argument('catID', type=str, help='category ID required', required=True)
itemRegParser.add_argument('userID', type=str, help='user ID required', required=True)
itemRegParser.add_argument('rate', type=int, help='rate of the item required (must be integer)', required=True)
itemRegParser.add_argument('stock', type=int, help='stock of the item required (must be integer)', required=True)
itemRegParser.add_argument('description', type=str, help='description of item required', required=True)
itemRegParser.add_argument('photo', type=werkzeug.datastructures.FileStorage, help='photo of item required', location='files', action='append', required=True)

itemDataUpdateParser = reqparse.RequestParser()
itemDataUpdateParser.add_argument('name', type=str)
itemDataUpdateParser.add_argument('catID', type=str)
itemDataUpdateParser.add_argument('rate', type=int)
itemDataUpdateParser.add_argument('stock', type=int)
itemDataUpdateParser.add_argument('description', type=str)

itemImgUpdateParser = reqparse.RequestParser()
itemImgUpdateParser.add_argument('photo', type=werkzeug.datastructures.FileStorage, location='files', action='append')
itemImgUpdateParser.add_argument('imgName', type=str)

itemRatingParser = reqparse.RequestParser()
itemRatingParser.add_argument('userID', type=str, required=True, help='user id required')
itemRatingParser.add_argument('rating', type=int, required=True, help='rating requried (must be integer and between 0 and 5)')

itemCommentParser = reqparse.RequestParser()
itemCommentParser.add_argument('userID', type=str, required=True, help='user id required')
itemCommentParser.add_argument('comment', type=str, required=True, help='comment required')

commentUpdateParser = reqparse.RequestParser()
commentUpdateParser.add_argument('comment', type=str, required=True, help='comment required')

messageParser = reqparse.RequestParser()
messageParser.add_argument('sender', type=str, help='sender required', required=True)
messageParser.add_argument('receiver', type=str, help='receiver required', required=True)
messageParser.add_argument('action', type=str, help='action required', required=True)
messageParser.add_argument('message', type=str)
messageParser.add_argument('photo', type=werkzeug.datastructures.FileStorage, location='files', action='append')

filterItemParser = reqparse.RequestParser()
filterItemParser.add_argument('userID', type=str, required=True, help='user id required')

filterParser = reqparse.RequestParser()
filterParser.add_argument('userID', type=str, required=True, help='user id required')
filterParser.add_argument('catID', type=str, required=True, help='category id required')
filterParser.add_argument('catName', type=str, required=True, help='category name required')

searchParser = reqparse.RequestParser()
searchParser.add_argument('userID', type=str, required=True, help='user id required')
searchParser.add_argument('catID', type=str, required=True, help='category id required')
searchParser.add_argument('catName', type=str)
searchParser.add_argument('searchItem', type=str, required=True, help='search item required')

itemCartParser = reqparse.RequestParser()
itemCartParser.add_argument('itemID', type=str, required=True, help='item id required')
itemCartParser.add_argument('qty', type=int, required=True, help='quantity required')

itemCartUpdateParser = reqparse.RequestParser()
itemCartUpdateParser.add_argument('qty', type=int, required=True, help='quantity required')

def locationlist(itemlist):
	locationList = []
	for i in itemlist:
		locationList.append(itemlist[i]['sellerDetails']['city'].lower())
	locationList = set(locationList)
	locationList = list(locationList)
	return locationList

def categorylist(itemlist):
	tempCategorylist = []
	for i in itemlist:
		tempCategorylist.append(itemlist[i]['catID'])
	tempCategorylist = set(tempCategorylist)
	tempCategorylist = list(tempCategorylist)
	categoryList = db.child('PetsWorld').child('categoryList').get().val()
	if categoryList == None:
		categoryList = {}
	category_list = {}
	for i in tempCategorylist:
		if i == 'CATOTH':
			category_list[i] = {'name' : 'others'}
		else:
			category_list[i] = categoryList[i]
	return category_list

class UserReg(Resource):
	def post(self):
		args = userRegParser.parse_args()
		if args['photo']:
			if not allowed_file(args['photo'].filename):
				abort(400, message='unsupported file format')
		userCnt = db.child('PetsWorld').child('userCnt').get().val()
		if userCnt == None:
			userCnt = 0
		userCnt += 1
		db.child('PetsWorld').child('userCnt').set(userCnt)
		userID = 'USR' + str(100 + userCnt)
		if args['photo']:
			f = args['photo']
			del args['photo']
			storage.child('PetsWorld').child('userImage').child(userID).child('pic.jpg').put(f)		
		else:
			storage.child('PetsWorld').child('userImage').child(userID).child('pic.jpg').put('static/user.png')
		userList = db.child('PetsWorld').child('userList').get().val()
		if userList == None:
			userList = {}
		args['imgUrl'] = storage.child('PetsWorld').child('userImage').child(userID).child('pic.jpg').get_url(None)
		userList[userID] = args
		db.child('PetsWorld').child('userList').set(userList)
		return args

	def get(self):
		userList = db.child('PetsWorld').child('userList').get().val()
		if userList == None:
			userList = {}
		return userList

class UserUpdate(Resource):
	def get(self, userID):
		userID = userID.upper()
		userList = db.child('PetsWorld').child('userList').get().val()
		if userList == None:
			userList = {}
		if userID in userList:
			userDetails = userList[userID]
		else:
			abort(400, message='user not found')
		return userDetails

	def put(self, userID):
		userID = userID.upper()
		args = userUpdateParser.parse_args()
		userList = db.child('PetsWorld').child('userList').get().val()
		if userList == None:
			userList = {}
		if userID in userList:
				if args['name']:
					userList[userID]['name'] = args['name']
				if args['mobileNumber']:
					userList[userID]['mobileNumber'] = args['mobileNumber']
				if args['address']:
					userList[userID]['address'] = args['address']
				if args['city']:
					userList[userID]['city'] = args['city']
				if args['email']:
					userList[userID]['email'] = args['email']
				if args['password']:
					userList[userID]['password'] = args['password']
				if args['photo']:
					storage.child('PetsWorld').child('userImage').child(userID).child('pic.jpg').put(args['photo'])
					userList[userID]['imgUrl'] = storage.child('PetsWorld').child('userImage').child(userID).child('pic.jpg').get_url(None)
				db.child('PetsWorld').child('userList').set(userList)
				userDetails= userList[userID]
		else:
			abort(400, message='user not found')
		return userDetails

	def delete(self, userID):
		userID = userID.upper()
		userList = db.child('PetsWorld').child('userList').get().val()
		if userList == None:
			userList = {}
		if userID in userList:
				del userList[userID]
				db.child('PetsWorld').child('userList').set(userList)
		else:
			abort(400, message='user not found')
		return userList

class UserLogin(Resource):
	def post(self):
		args = userLoginParser.parse_args()
		userList = db.child('PetsWorld').child('userList').get().val()
		if userList == None:
			userList = {}
		userID = ''
		for i in userList:
			if userList[i]['email'] == args['email'] and userList[i]['password'] == args['password']:
					userID = i
		return userID

class AdminLogin(Resource):
	def post(self):
		args = adminLoginParser.parse_args()
		adminPassword = db.child('PetsWorld').child('adminPassword').get().val()
		if adminPassword == None:
			adminPassword = 'admin123'
			db.child('PetsWorld').child('adminPassword').set(adminPassword)
		if 'admin@gmail.com' == args['email'] and adminPassword == args['password']:
			return 'admin'
		else:
			return ''

class CategoryReg(Resource):
	def post(self):
		args = catRegParser.parse_args()
		args['deleteStatus'] = 0
		catCnt = db.child('PetsWorld').child('catCnt').get().val()
		if catCnt == None:
			catCnt = 0
		catCnt += 1
		db.child('PetsWorld').child('catCnt').set(catCnt)
		catID = 'CAT' + str(100 + catCnt)
		categoryList = db.child('PetsWorld').child('categoryList').get().val()
		if categoryList == None:
			categoryList = {}
		categoryList[catID] = args
		db.child('PetsWorld').child('categoryList').set(categoryList)
		return args

	def get(self):
		categoryList = db.child('PetsWorld').child('categoryList').get().val()
		if categoryList == None:
			categoryList = {}
		categoryList['CATOTH'] = {'name':'others'}
		return categoryList

class CategoryUpdate(Resource):
	def get(self, catID):
		catID = catID.upper()
		categoryList = db.child('PetsWorld').child('categoryList').get().val()
		if categoryList == None:
			categoryList = {}
		if catID in categoryList:
			catDetails = categoryList[catID]
		else:
			abort(400, message='category not found')
		return catDetails

	def put(self, catID):
		catID = catID.upper()
		args = catRegParser.parse_args()
		categoryList = db.child('PetsWorld').child('categoryList').get().val()
		if categoryList == None:
			categoryList = {}
		if catID in categoryList:
				if args['name']:
					categoryList[catID]['name'] = args['name']
				db.child('PetsWorld').child('categoryList').set(categoryList)
				catDetails= categoryList[catID]
		else:
			abort(400, message='category not found')
		return catDetails

	def delete(self, catID):
		catID = catID.upper()
		categoryList = db.child('PetsWorld').child('categoryList').get().val()
		if categoryList == None:
			categoryList = {}
		if catID in categoryList:
			if categoryList[catID]['deleteStatus'] == 0:
				del categoryList[catID]
				db.child('PetsWorld').child('categoryList').set(categoryList)
			else:
				abort(400, message='category cant be deleted')
		else:
			abort(400, message='category not found')
		return categoryList

class ItemReg(Resource):
	def post(self):
		args = itemRegParser.parse_args()
		userID = args['userID'].upper()
		args['userID'] = userID
		userList = db.child('PetsWorld').child('userList').get().val()
		if userList == None:
			userList = {}
		if not userID in userList:
			abort(400, message='user not found')
		catID = args['catID'].upper()
		args['catID'] = catID
		categoryList = db.child('PetsWorld').child('categoryList').get().val()
		if categoryList == None:
			categoryList = {}
		if catID != 'CATOTH':
			if not catID in categoryList:
				abort(400, message='category not found')
		images = args['photo']
		del args['photo']
		for img in images:
			if not allowed_file(img.filename):
				abort(400, message='unsupported file format')
		itemCnt = db.child('PetsWorld').child('itemCnt').get().val()
		if itemCnt == None:
			itemCnt = 0
		itemCnt += 1
		db.child('PetsWorld').child('itemCnt').set(itemCnt)
		itemID = 'ITEM' + str(100 + itemCnt)
		args['imgList'] = []
		for img in images:
			imgCnt = db.child('PetsWorld').child('imgCnt').get().val()
			if imgCnt == None:
				imgCnt = 0
			imgCnt += 1
			db.child('PetsWorld').child('imgCnt').set(imgCnt)
			imgName = 'IMG' + str(100 + imgCnt) + '.jpg'
			storage.child('PetsWorld').child('itemImage').child(itemID).child(imgName).put(img)
			imgUrl = storage.child('PetsWorld').child('itemImage').child(itemID).child(imgName).get_url(None)
			args['imgList'].append({'imgName': imgName,'imgUrl' : imgUrl})
		args['totalRating'] = 0
		args['averageRating'] = 0
		args['ratedUserCnt'] = 0
		itemList = db.child('PetsWorld').child('itemList').get().val()
		if itemList == None:
			itemList = {}
		itemList[itemID] = args
		db.child('PetsWorld').child('itemList').set(itemList)
		if catID != 'CATOTH':
			categoryList[catID]['deleteStatus'] = 1
			db.child('PetsWorld').child('categoryList').set(categoryList)
		return args

class ItemDataUpdate(Resource):
	def get(self, itemID):
		itemID = itemID.upper()
		itemList = db.child('PetsWorld').child('itemList').get().val()
		if itemList == None:
			itemList = {}
		userList = db.child('PetsWorld').child('userList').get().val()
		if userList == None:
			userList = {}
		categoryList = db.child('PetsWorld').child('categoryList').get().val()
		if categoryList == None:
			categoryList = {}
		if itemID in itemList:
			itemDetails = itemList[itemID]
			if itemDetails['catID'] == 'CATOTH':
				itemDetails['categoryName'] = 'others'
			else:
				itemDetails['categoryName'] = categoryList[itemDetails['catID']]['name']
			itemDetails['sellerDetails'] = userList[itemDetails['userID']]
			itemDetails['averageRating'] = round(itemDetails['averageRating'])
		else:
			abort(400, message='item not found')
		return itemDetails

	def put(self, itemID):
		itemID = itemID.upper()
		args = itemDataUpdateParser.parse_args()
		itemList = db.child('PetsWorld').child('itemList').get().val()
		if itemList == None:
			itemList = {}
		categoryList = db.child('PetsWorld').child('categoryList').get().val()
		if categoryList == None:
			categoryList = {}
		if itemID in itemList:
				if args['name']:
					itemList[itemID]['name'] = args['name']
				if args['rate']:
					itemList[itemID]['rate'] = args['rate']
				if args['stock']:
					itemList[itemID]['stock'] = args['stock']
				if args['description']:
					itemList[itemID]['description'] = args['description']
				if args['catID']:
					catID = args['catID'].upper()
					if catID != 'CATOTH':
						if not catID in categoryList:
							abort(400, message='category doesnt exist')
					oldCatID = itemList[itemID]['catID']
					if oldCatID != catID:
						itemList[itemID]['catID'] = catID
						if catID != 'CATOTH':
							categoryList[catID]['deleteStatus'] = 1
							db.child('PetsWorld').child('categoryList').set(categoryList)
						if oldCatID != 'CATOTH':
							oldFlag = 0
							for i in itemList:
								if itemList[i]['catID'] == oldCatID:
									oldFlag = 1
									break
							if oldFlag == 0:
								categoryList[oldCatID]['deleteStatus'] = 0
								db.child('PetsWorld').child('categoryList').set(categoryList)
				db.child('PetsWorld').child('itemList').set(itemList)
				itemDetails= itemList[itemID]
		else:
			abort(400, message='item not found')
		return itemDetails

	def delete(self, itemID):
		itemID = itemID.upper()
		itemList = db.child('PetsWorld').child('itemList').get().val()
		if itemList == None:
			itemList = {}
		if not itemID in itemList:
			abort(400, message='item not found')
		categoryList = db.child('PetsWorld').child('categoryList').get().val()
		if categoryList == None:
			categoryList = {}
		catID = itemList[itemID]['catID']
		del itemList[itemID]
		db.child('PetsWorld').child('itemList').set(itemList)
		if catID != 'CATOTH':
			flag = 0
			for i in itemList:
				if itemList[i]['catID'] == catID:
					flag = 1
			if flag == 0:
				categoryList[catID]['deleteStatus'] = 0
				db.child('PetsWorld').child('categoryList').set(categoryList)
		return itemList

class ItemImgUpdate(Resource):
	def put(self,itemID):
		itemID = itemID.upper()
		args = itemImgUpdateParser.parse_args()
		if args['photo']:
			itemList = db.child('PetsWorld').child('itemList').get().val()
			if itemList == None:
				itemList = {}
			if itemID in itemList:
				images = args['photo']
				for img in images:
					if not allowed_file(img.filename):
						abort(400, message='unsupported file format')
				for img in images:
					imgCnt = db.child('PetsWorld').child('imgCnt').get().val()
					if imgCnt == None:
						imgCnt = 0
					imgCnt += 1
					db.child('PetsWorld').child('imgCnt').set(imgCnt)
					imgName = 'IMG' + str(100 + imgCnt) + '.jpg'
					storage.child('PetsWorld').child('itemImage').child(itemID).child(imgName).put(img)
					imgUrl = storage.child('PetsWorld').child('itemImage').child(itemID).child(imgName).get_url(None)
					itemList[itemID]['imgList'].append({'imgName' : imgName, 'imgUrl' : imgUrl})
				db.child('PetsWorld').child('itemList').set(itemList)
			else:
				abort(400, message='item not found')
		else:
			abort(400, message='photo required')
		return itemList[itemID]

	def delete(self,itemID):
		itemID = itemID.upper()
		itemList = db.child('PetsWorld').child('itemList').get().val()
		if itemList == None:
			itemList = {}
		args = itemImgUpdateParser.parse_args()
		if args['imgName']:
			imgName = args['imgName'].upper()
			if itemID in itemList:
				if len(itemList[itemID]['imgList']) > 1:
					flag = 0
					for i in itemList[itemID]['imgList']:
						if i['imgName'].upper() == imgName:
							flag = 1
							itemList[itemID]['imgList'].remove(i)
							db.child('PetsWorld').child('itemList').set(itemList)
					if flag == 0:
						abort(400, message='image not found')
				else:
					abort(400, message='minimum one image required')
			else:
				abort(400, message='item not found')
		else:
			abort(400, message='image name required')
		return itemList[itemID]

class ItemRating(Resource):
	def post(self, itemID):
		itemID = itemID.upper()
		args = itemRatingParser.parse_args()
		userID = args['userID'].upper()
		rating = args['rating']
		if rating < 0 or rating > 5:
			abort(400, message='rating should be between 0 and 5')
		itemList = db.child('PetsWorld').child('itemList').get().val()
		if itemList == None:
			itemList = {}
		if not itemID in itemList:
			abort(400, message='item not found')
		userList = db.child('PetsWorld').child('userList').get().val()
		if userList == None:
			userList = {}
		if not userID in userList:
			abort(400, message='user not found')
		else:
			if itemList[itemID]['userID'] == userID:
				abort(400, message='owner cant rate his own product')
		ratingList = db.child('PetsWorld').child('ratingList').get().val()
		if ratingList == None:
			ratingList = {}
		flag = 0
		for i in ratingList:
			if ratingList[i]['itemID'] == itemID:
				if ratingList[i]['userID'] == userID:
					flag = 1
					itemList[itemID]['totalRating'] = itemList[itemID]['totalRating'] - ratingList[i]['rating'] + rating
					ratingList[i]['rating'] = rating
					ratingID = i
					break
		if flag == 0:
			ratingCnt = db.child('PetsWorld').child('ratingCnt').get().val()
			if ratingCnt == None:
				ratingCnt = 0
			ratingCnt += 1
			db.child('PetsWorld').child('ratingCnt').set(ratingCnt)
			ratingID = 'RAT' + str(100 + ratingCnt)
			ratingList[ratingID] = {
				'itemID' : itemID,
				'userID'  : userID,
				'rating'  : rating
			}
			itemList[itemID]['totalRating'] = itemList[itemID]['totalRating'] + rating
			itemList[itemID]['ratedUserCnt'] = itemList[itemID]['ratedUserCnt'] + 1
		itemList[itemID]['averageRating'] = itemList[itemID]['totalRating'] / itemList[itemID]['ratedUserCnt']
		db.child('PetsWorld').child('ratingList').set(ratingList)
		db.child('PetsWorld').child('itemList').set(itemList)
		ratingList[ratingID]['totalRating'] = itemList[itemID]['totalRating']
		ratingList[ratingID]['ratedUserCnt'] = itemList[itemID]['ratedUserCnt']
		ratingList[ratingID]['averageRating'] = itemList[itemID]['averageRating']
		return ratingList[ratingID]

	def get(self, itemID):
		itemID = itemID.upper()
		itemList = db.child('PetsWorld').child('itemList').get().val()
		if itemList == None:
			itemList = {}
		if not itemID in itemList:
			abort(400, message='item not found')
		ratingList = db.child('PetsWorld').child('ratingList').get().val()
		if ratingList == None:
			ratingList = {}
		tempRatingList = {}
		for i in ratingList:
			if ratingList[i]['itemID'] == itemID:
				tempRatingList[i] = ratingList[i]
		return tempRatingList

class ItemComment(Resource):
	def post(self, itemID):
		itemID = itemID.upper()
		args = itemCommentParser.parse_args()
		userID = args['userID'].upper()
		comment = args['comment']
		itemList = db.child('PetsWorld').child('itemList').get().val()
		if itemList == None:
			itemList = {}
		if not itemID in itemList:
			abort(400, message='item not found')
		userList = db.child('PetsWorld').child('userList').get().val()
		if userList == None:
			userList = {}
		if not userID in userList:
			abort(400, message='user not found')
		else:
			if itemList[itemID]['userID'] == userID:
				abort(400, message='owner cant comment his own product')
		commentCnt = db.child('PetsWorld').child('commentCnt').get().val()
		if commentCnt == None:
			commentCnt = 0
		commentCnt += 1
		db.child('PetsWorld').child('commentCnt').set(commentCnt)
		commentID = 'CMNT' + str(100 + commentCnt)
		commentList = db.child('PetsWorld').child('commentList').get().val()
		if commentList == None:
			commentList = {}
		x = datetime.now(timezone("Asia/Kolkata"))
		date = x.strftime('%d/%m/%Y')
		time = x.strftime('%X')
		commentList[commentID] = {
			'itemID' : itemID,
			'userID'  : userID,
			'comment' : comment,
			'date'    : date,
			'time'    : time
		}
		db.child('PetsWorld').child('commentList').set(commentList)
		return commentList[commentID]

	def get(self, itemID):
		itemID = itemID.upper()
		itemList = db.child('PetsWorld').child('itemList').get().val()
		if itemList == None:
			itemList = {}
		userList = db.child('PetsWorld').child('userList').get().val()
		if userList == None:
			userList = {}
		if not itemID in itemList:
			abort(400, message='item not found')
		commentList = db.child('PetsWorld').child('commentList').get().val()
		if commentList == None:
			commentList = {}
		tempCommentList = {}
		for i in commentList:
			if commentList[i]['itemID'] == itemID:
				tempCommentList[i] = commentList[i]
				tempCommentList[i]['userDetails'] = userList[commentList[i]['userID']]
		return tempCommentList

class commentUpdate(Resource):
	def get(self, commentID):
		commentID = commentID.upper()
		commentList = db.child('PetsWorld').child('commentList').get().val()
		if commentList == None:
			commentList = {}
		if commentID in commentList:
			commentDetails = commentList[commentID]
		else:
			abort(400, message='comment not found')
		return commentDetails

	def put(self, commentID):
		commentID = commentID.upper()
		args = commentUpdateParser.parse_args()
		commentList = db.child('PetsWorld').child('commentList').get().val()
		if commentList == None:
			commentList = {}
		if commentID in commentList:
			commentList[commentID]['comment'] = args['comment']
			x = datetime.now(timezone("Asia/Kolkata"))
			date = x.strftime('%d/%m/%Y')
			time = x.strftime('%X')
			commentList[commentID]['date'] = date
			commentList[commentID]['time'] = time
			db.child('PetsWorld').child('commentList').set(commentList)
			commentDetails= commentList[commentID]
		else:
			abort(400, message='comment not found')
		return commentDetails

	def delete(self, commentID):
		commentID = commentID.upper()
		commentList = db.child('PetsWorld').child('commentList').get().val()
		if commentList == None:
			commentList = {}
		if commentID in commentList:
				del commentList[commentID]
				db.child('PetsWorld').child('commentList').set(commentList)
		else:
			abort(400, message='comment not found')
		return commentList

class Message(Resource):
	def post(self):
		args = messageParser.parse_args()
		sender = args['sender'].upper()
		receiver = args['receiver'].upper()
		args['sender'] = sender
		args['receiver'] = receiver
		userList = db.child('PetsWorld').child('userList').get().val()
		if userList == None:
			userList = {}
		if sender == receiver:
			abort(400, message='sender and receiver cannot be same') 
		if sender != 'ADMIN':
			if not sender in userList:
				abort(400, message='invalid sender')
		if receiver != 'ADMIN':
			if not receiver in userList:
				abort(400, message='invalid receiver')
		if args['action'] == 'send':
			if args['message'] or args['photo']:
				if args['photo']:
					images = args['photo']
					for img in images:
						if not allowed_file(img.filename):
							abort(400, message='unsupported file format')
					for img in images:
						imgCnt = db.child('PetsWorld').child('imgCnt').get().val()
						if imgCnt == None:
							imgCnt = 0
						imgCnt += 1
						db.child('PetsWorld').child('imgCnt').set(imgCnt)
						imgName = 'IMG' + str(100 + imgCnt)
						msgCnt = db.child('PetsWorld').child('msgCnt').get().val()
						if msgCnt == None:
							msgCnt = 0
						msgCnt += 1
						db.child('PetsWorld').child('msgCnt').set(msgCnt)
						msgID = 'MSG' + str(100 + msgCnt)
						storage.child('PetsWorld').child('msgImage').child(msgID).child(imgName).put(img)
						imgUrl = storage.child('PetsWorld').child('msgImage').child(msgID).child(imgName).get_url(None)
						msgList = db.child('PetsWorld').child('msgList').get().val()
						if msgList == None:
							msgList = {}
						msgList[msgID] = {
							'sender'   : sender,
							'receiver' : receiver,
							'type'     : 'img',
							'imgUrl'   : imgUrl
							}
						x = datetime.now(timezone("Asia/Kolkata"))
						msgList[msgID]['date'] = x.strftime('%d/%m/%Y')
						msgList[msgID]['time'] = x.strftime('%X')
						db.child('PetsWorld').child('msgList').set(msgList)
				if args['message']:
					msgCnt = db.child('PetsWorld').child('msgCnt').get().val()
					if msgCnt == None:
						msgCnt = 0
					msgCnt += 1
					db.child('PetsWorld').child('msgCnt').set(msgCnt)
					msgID = 'MSG' + str(100 + msgCnt)
					msgList = db.child('PetsWorld').child('msgList').get().val()
					if msgList == None:
						msgList = {}							
					msgList[msgID]= {
						'sender'   : sender,
						'receiver' : receiver,
						'type'     : 'text',
						'message'  : args['message']
						}
					x = datetime.now()
					x = datetime.now(timezone("Asia/Kolkata"))
					msgList[msgID]['date'] = x.strftime('%d/%m/%Y')
					msgList[msgID]['time'] = x.strftime('%X')
					db.child('PetsWorld').child('msgList').set(msgList)			
				return msgList
			else:
				abort(400, message='content required')
		elif args['action'] == 'get':
			msgList = db.child('PetsWorld').child('msgList').get().val()
			if msgList == None:
				msgList = {}
			tempMsgList = {}
			msgIDList = list(msgList.keys())
			msgIDList.reverse()
			for msgID in msgIDList:
				if msgList[msgID]['sender'] == sender or msgList[msgID]['receiver'] == sender:
					if msgList[msgID]['sender'] == receiver or msgList[msgID]['receiver'] == receiver:
						tempMsgList[msgID] = msgList[msgID]
			return tempMsgList
		else:
			abort(400, message='invalid action')

class MessageInbox(Resource):
	def post(self,userID):
		userID = userID.upper()
		userList = db.child('PetsWorld').child('userList').get().val()
		if userList == None:
			userList = {}
		msgList = db.child('PetsWorld').child('msgList').get().val()
		if msgList == None:
			msgList = {}
		if userID != 'ADMIN':
			if not userID in userList:
				abort(400, message='user not found')
		msgIDList = list(msgList.keys())
		msgIDList.reverse()
		tempMsgList = {}
		for msg in msgIDList:
			if msgList[msg]['sender'] == userID or msgList[msg]['receiver'] == userID:
				if msgList[msg]['sender'] != userID:
					othUserID = msgList[msg]['sender']
				elif msgList[msg]['receiver'] != userID:
					othUserID = msgList[msg]['receiver']
				flag = 0
				for i in tempMsgList:
					if tempMsgList[i]['sender'] == othUserID or tempMsgList[i]['receiver'] == othUserID:
						flag = 1
						break
				if flag == 0:
					tempMsgList[msg] = msgList[msg]
					tempMsgList[msg]['othUserID'] = othUserID
					if othUserID != 'ADMIN':
						tempMsgList[msg]['userDetails'] = userList[othUserID]
		return tempMsgList

class ItemList(Resource):
	def get(self, userID, cat):
		userID = userID.upper()
		itemList = db.child('PetsWorld').child('itemList').get().val()
		if itemList == None:
			itemList = {}
		tempItemList = {}
		userList = db.child('PetsWorld').child('userList').get().val()
		if userList == None:
			userList = {}
		categoryList = db.child('PetsWorld').child('categoryList').get().val()
		if categoryList == None:
			categoryList = {}
		if userID == 'ADMIN':
			tempItemList = itemList
		else:
			if userID in userList:
				if cat == 'own':
					for i in itemList:
						if itemList[i]['userID'] == userID:
							tempItemList[i] = itemList[i]
				elif cat == 'oth':
					for i in itemList:
						if itemList[i]['userID'] != userID:
							if itemList[i]['stock'] > 0:
								tempItemList[i] = itemList[i]
				else:
					abort(400, message='invalid category')
			else:
				abort(400, message='invalid user')
		for i in tempItemList:
			if tempItemList[i]['catID'] == 'CATOTH':
				tempItemList[i]['categoryName'] = 'others'
			else:
				tempItemList[i]['categoryName'] = categoryList[tempItemList[i]['catID']]['name']
			tempItemList[i]['sellerDetails'] = userList[tempItemList[i]['userID']]
			tempItemList[i]['averageRating'] = round(tempItemList[i]['averageRating'])
		return tempItemList

class OthItemComment(Resource):
	def get(self, userID, itemID):
		userID = userID.upper()
		itemID = itemID.upper()
		itemList = db.child('PetsWorld').child('itemList').get().val()
		if itemList == None:
			itemList = {}
		commentList = db.child('PetsWorld').child('commentList').get().val()
		if commentList == None:
			commentList = {}
		tempCommentList = {}
		userList = db.child('PetsWorld').child('userList').get().val()
		if userList == None:
			userList = {}
		if userID in userList:
			if itemID in itemList:
				if itemList[itemID]['userID'] != userID:
					for i in commentList:
						if commentList[i]['itemID'] == itemID:
							if commentList[i]['userID'] == userID:
								tempCommentList[i] = commentList[i]
								tempCommentList[i]['userDetails'] = userList[commentList[i]['userID']]
					for i in commentList:
						if commentList[i]['itemID'] == itemID:
							if commentList[i]['userID'] != userID:
								tempCommentList[i] = commentList[i]
								tempCommentList[i]['userDetails'] = userList[commentList[i]['userID']]
				else:
					abort(400, message='item owner')
			else:
				abort(400, message='item not found')
		else:
			abort(400, message='invalid user')
		return tempCommentList

class FilterItemList(Resource):
	def post(self):
		args = filterItemParser.parse_args()
		userID = args['userID'].upper()
		itemList = db.child('PetsWorld').child('itemList').get().val()
		if itemList == None:
			itemList = {}
		userList = db.child('PetsWorld').child('userList').get().val()
		if userList == None:
			userList = {}
		tempItemList = {}
		if userID == 'USER':
			tempItemList = itemList
			for i in tempItemList:
				tempItemList[i]['sellerDetails'] = userList[tempItemList[i]['userID']]
		else:
			if userID in userList:
				for i in itemList:
					if itemList[i]['userID'] != userID:
						tempItemList[i] = itemList[i]
						tempItemList[i]['sellerDetails'] = userList[itemList[i]['userID']]
			else:
				abort(400, message='user not found')
		filterItemList = {}
		filterItemList['location'] = locationlist(tempItemList)
		filterItemList['category'] = categorylist(tempItemList)
		filterItemList['rating'] = [5,4,3,2,1,0]
		return filterItemList

class FilterItem(Resource):
	def post(self):
		args = filterParser.parse_args()
		userID = args['userID'].upper()
		itemList = db.child('PetsWorld').child('itemList').get().val()
		if itemList == None:
			itemList = {}
		categoryList = db.child('PetsWorld').child('categoryList').get().val()
		if categoryList == None:
			categoryList = {}
		userList = db.child('PetsWorld').child('userList').get().val()
		if userList == None:
			userList = {}
		tempItemList = {}
		if userID == 'USER':
			tempItemList = itemList
			for i in tempItemList:
				tempItemList[i]['sellerDetails'] = userList[tempItemList[i]['userID']]
		else:
			if userID in userList:
				for i in itemList:
					if itemList[i]['userID'] != userID:
						tempItemList[i] = itemList[i]
						tempItemList[i]['sellerDetails'] = userList[itemList[i]['userID']]
			else:
				abort(400, message='user not found')
		filterResult = {}
		if args['catID'] == 'location':
			locationList = locationlist(tempItemList)
			if args['catName'].lower() in locationList:
				for i in tempItemList:
					if tempItemList[i]['sellerDetails']['city'].lower() == args['catName'].lower():
						filterResult[i] = tempItemList[i]
			else:
				abort(400, message='invalid category name')
		elif args['catID'] == 'category':
			category_list = categorylist(tempItemList)
			if args['catName'].upper() in category_list:
				for i in tempItemList:
					if tempItemList[i]['catID'] == args['catName'].upper():
						filterResult[i] = tempItemList[i]
			else:
				abort(400, message='invalid category name')
		elif args['catID'] == 'rating':
			rating_list = [5,4,3,2,1,0]
			if int(args['catName']) in rating_list:
				for i in tempItemList:
					if round(tempItemList[i]['averageRating']) == int(args['catName']):
						filterResult[i] = tempItemList[i]
			else:
				abort(400, message='invalid category name')
		elif args['catID'] == 'rate':
			if args['catName'].count('-') == 1:
				minLimit = args['catName'].split('-')[0]
				maxLimit = args['catName'].split('-')[1]
				if minLimit.isnumeric() and maxLimit.isnumeric():
					minLimit = int(minLimit)
					maxLimit = int(maxLimit)
					if minLimit != maxLimit:
						if minLimit < maxLimit:
							for i in tempItemList:
								if tempItemList[i]['rate'] >= minLimit and tempItemList[i]['rate'] <= maxLimit:
									filterResult[i] = tempItemList[i]
						else:
							abort(400, message='minLimit should be less than maxLimit')
					else:
						abort(400, message='minLimit and maxLimit should not be equal')
				else:
					abort(400, message='limit should be a integer')
			else:
				abort(400, message='invalid format')
		else:
			abort(400, message='invalid category id')
		for i in filterResult:
			filterResult[i]['averageRating'] = round(filterResult[i]['averageRating'])
			if filterResult[i]['catID'] == 'CATOTH':
				filterResult[i]['categoryName'] = 'others'
			else:
				filterResult[i]['categoryName'] = categoryList[filterResult[i]['catID']]['name']
		return filterResult

class SearchItem(Resource):
	def post(self):
		args = searchParser.parse_args()
		userID = args['userID'].upper()
		itemList = db.child('PetsWorld').child('itemList').get().val()
		if itemList == None:
			itemList = {}
		categoryList = db.child('PetsWorld').child('categoryList').get().val()
		if categoryList == None:
			categoryList = {}
		userList = db.child('PetsWorld').child('userList').get().val()
		if userList == None:
			userList = {}
		tempItemList = {}
		if userID == 'USER':
			tempItemList = itemList
			for i in tempItemList:
				tempItemList[i]['sellerDetails'] = userList[tempItemList[i]['userID']]
		else:
			if userID in userList:
				for i in itemList:
					if itemList[i]['userID'] != userID:
						tempItemList[i] = itemList[i]
						tempItemList[i]['sellerDetails'] = userList[itemList[i]['userID']]
			else:
				abort(400, message='user not found')
		searchResult = {}
		if args['searchItem'] == '':
			abort(400, message='search item should not be empty')
		else:
			searchItem = args['searchItem'].lower()
		filterResult = {}
		if args['catID'] == 'nill':
			for i in tempItemList:
				itemName = tempItemList[i]['name'].lower()
				if itemName.startswith(searchItem):
					searchResult[i] = tempItemList[i]
		elif args['catID'] == 'location':
			if args['catName']:
				locationList = locationlist(tempItemList)
				if args['catName'].lower() in locationList:
					for i in tempItemList:
						if tempItemList[i]['sellerDetails']['city'].lower() == args['catName'].lower():
							filterResult[i] = tempItemList[i]
					for i in filterResult:
						itemName = filterResult[i]['name'].lower()
						if itemName.startswith(searchItem):
							searchResult[i] = filterResult[i]
				else:
					abort(400, message='invalid category name')
			else:
				abort(400, message='category name required')
		elif args['catID'] == 'category':
			if args['catName']:
				category_list = categorylist(tempItemList)
				if args['catName'].upper() in category_list:
					for i in tempItemList:
						if tempItemList[i]['catID'] == args['catName'].upper():
							filterResult[i] = tempItemList[i]
					for i in filterResult:
						itemName = filterResult[i]['name'].lower()
						if itemName.startswith(searchItem):
							searchResult[i] = filterResult[i]
				else:
					abort(400, message='invalid category name')
			else:
				abort(400, message='category name required')
		elif args['catID'] == 'rating':
			if args['catName']:
				rating_list = [5,4,3,2,1,0]
				if int(args['catName']) in rating_list:
					for i in tempItemList:
						if round(tempItemList[i]['averageRating']) == int(args['catName']):
							filterResult[i] = tempItemList[i]
					for i in filterResult:
						itemName = filterResult[i]['name'].lower()
						if itemName.startswith(searchItem):
							searchResult[i] = filterResult[i]
				else:
					abort(400, message='invalid category name')
			else:
				abort(400, message='category name required')
		elif args['catID'] == 'rate':
			if args['catName']:
				if args['catName'].count('-') == 1:
					minLimit = args['catName'].split('-')[0]
					maxLimit = args['catName'].split('-')[1]
					if minLimit.isnumeric() and maxLimit.isnumeric():
						minLimit = int(minLimit)
						maxLimit = int(maxLimit)
						if minLimit != maxLimit:
							if minLimit < maxLimit:
								for i in tempItemList:
									if tempItemList[i]['rate'] >= minLimit and tempItemList[i]['rate'] <= maxLimit:
										filterResult[i] = tempItemList[i]
								for i in filterResult:
									itemName = filterResult[i]['name'].lower()
									if itemName.startswith(searchItem):
										searchResult[i] = filterResult[i]
							else:
								abort(400, message='minLimit should be less than maxLimit')
						else:
							abort(400, message='minLimit and maxLimit should not be equal')
					else:
						abort(400, message='limit should be a integer')
				else:
					abort(400, message='invalid format')
			else:
				abort(400, message='category name required')
		else:
			abort(400, message= 'invalid category')
		for i in searchResult:
			searchResult[i]['averageRating'] = round(searchResult[i]['averageRating'])
			if searchResult[i]['catID'] == 'CATOTH':
				searchResult[i]['categoryName'] = 'others'
			else:
				searchResult[i]['categoryName'] = categoryList[searchResult[i]['catID']]['name']
		return searchResult

class ItemCart(Resource):
	def post(self, userID):
		userID = userID.upper()
		args = itemCartParser.parse_args()
		itemID = args['itemID'].upper()
		itemList = db.child('PetsWorld').child('itemList').get().val()
		if itemList == None:
			itemList = {}
		userList = db.child('PetsWorld').child('userList').get().val()
		if userList == None:
			userList = {}
		itemCart = db.child('PetsWorld').child('itemCart').get().val()
		if itemCart == None:
			itemCart = {}
		if not userID in userList:
			abort(400, message='user not found')
		if not itemID in itemList:
			abort(400, message='item not found')
		if itemList[itemID]['userID'] == userID:
			abort(400, message='item owner')
		if userID in itemCart:
			if itemID in itemCart[userID]:
				itemCart[userID][itemID]['qty'] = itemCart[userID][itemID]['qty'] + args['qty']
			else:
				itemCart[userID][itemID] = { 'qty' : args['qty'] }
		else:
			itemCart[userID] = {
				itemID : { 'qty' : args['qty'] }
				} 
		db.child('PetsWorld').child('itemCart').set(itemCart)
		return itemCart[userID]

	def get(self, userID):
		userID = userID.upper()
		userList = db.child('PetsWorld').child('userList').get().val()
		if userList == None:
			userList = {}
		categoryList = db.child('PetsWorld').child('categoryList').get().val()
		if categoryList == None:
			categoryList = {}
		itemList = db.child('PetsWorld').child('itemList').get().val()
		if itemList == None:
			itemList = {}
		itemCart = db.child('PetsWorld').child('itemCart').get().val()
		if itemCart == None:
			itemCart = {}
		if not userID in userList:
			abort(400, message='user not found')
		userCart = {}
		if userID in itemCart:
			userCart = itemCart[userID]
			for i in userCart:
				userCart[i]['itemDetails'] = itemList[i]
				userCart[i]['itemDetails']['averageRating'] = round(userCart[i]['itemDetails']['averageRating'])
				if userCart[i]['itemDetails']['catID'] == 'CATOTH':
					userCart[i]['itemDetails']['categoryName'] = 'others'
				else:
					userCart[i]['itemDetails']['categoryName'] = categoryList[userCart[i]['itemDetails']['catID']]['name']
				userCart[i]['sellerDetails'] = userList[userCart[i]['itemDetails']['userID']]
		return userCart

class ItemCartUpdate(Resource):
	def get(self, userID, itemID):
		userID = userID.upper()
		itemID = itemID.upper()
		userList = db.child('PetsWorld').child('userList').get().val()
		if userList == None:
			userList = {}
		categoryList = db.child('PetsWorld').child('categoryList').get().val()
		if categoryList == None:
			categoryList = {}
		itemList = db.child('PetsWorld').child('itemList').get().val()
		if itemList == None:
			itemList = {}
		itemCart = db.child('PetsWorld').child('itemCart').get().val()
		if itemCart == None:
			itemCart = {}
		if not userID in userList:
			abort(400, message='user not found')
		if not itemID in itemList:
			abort(400, message='item not found')
		cartItem = {}
		if userID in itemCart:
			userCart = itemCart[userID]
			if itemID in userCart:
				cartItem = userCart[itemID]
				cartItem['itemDetails'] = itemList[itemID]
				cartItem['itemDetails']['averageRating'] = round(cartItem['itemDetails']['averageRating'])
				if cartItem['itemDetails']['catID'] == 'CATOTH':
					cartItem['itemDetails']['categoryName'] = 'others'
				else:
					cartItem['itemDetails']['categoryName'] = categoryList[cartItem['itemDetails']['catID']]['name']
				cartItem['sellerDeatials'] = userList[cartItem['itemDetails']['userID']]
		return cartItem

	def put(self, userID, itemID):
		userID = userID.upper()
		itemID = itemID.upper()
		args = itemCartUpdateParser.parse_args()
		userList = db.child('PetsWorld').child('userList').get().val()
		if userList == None:
			userList = {}
		categoryList = db.child('PetsWorld').child('categoryList').get().val()
		if categoryList == None:
			categoryList = {}
		itemList = db.child('PetsWorld').child('itemList').get().val()
		if itemList == None:
			itemList = {}
		itemCart = db.child('PetsWorld').child('itemCart').get().val()
		if itemCart == None:
			itemCart = {}
		if not userID in userList:
			abort(400, message='user not found')
		if not itemID in itemList:
			abort(400, message='item not found')
		flag = 0
		if userID in itemCart:
			userCart = itemCart[userID]
			if itemID in userCart:
				flag = 1
				itemCart[userID][itemID]['qty'] = args['qty']
				cartItem = itemCart[userID][itemID]
				db.child('PetsWorld').child('itemCart').set(itemCart)
				cartItem['itemDetails'] = itemList[itemID]
				cartItem['itemDetails']['averageRating'] = round(cartItem['itemDetails']['averageRating'])
				if cartItem['itemDetails']['catID'] == 'CATOTH':
					cartItem['itemDetails']['categoryName'] = 'others'
				else:
					cartItem['itemDetails']['categoryName'] = categoryList[cartItem['itemDetails']['catID']]['name']
				cartItem['sellerDeatials'] = userList[cartItem['itemDetails']['userID']]
		if flag == 0:
			abort(400, message='item not found')
		return cartItem

	def delete(self, userID, itemID):
		userID = userID.upper()
		itemID = itemID.upper()
		userList = db.child('PetsWorld').child('userList').get().val()
		if userList == None:
			userList = {}
		categoryList = db.child('PetsWorld').child('categoryList').get().val()
		if categoryList == None:
			categoryList = {}
		itemList = db.child('PetsWorld').child('itemList').get().val()
		if itemList == None:
			itemList = {}
		itemCart = db.child('PetsWorld').child('itemCart').get().val()
		if itemCart == None:
			itemCart = {}
		if not userID in userList:
			abort(400, message='user not found')
		if not itemID in itemList:
			abort(400, message='item not found')
		flag = 0
		if userID in itemCart:
			userCart = itemCart[userID]
			if itemID in userCart:
				flag = 1
				del itemCart[userID][itemID]
				itemCart = db.child('PetsWorld').child('itemCart').set(itemCart)
		if flag == 0:
			abort(400, message='item not found')
		userCart = {}
		if userID in itemCart:
			userCart = itemCart[userID]
			for i in userCart:
				userCart[i]['itemDetails'] = itemList[i]
				userCart[i]['itemDetails']['averageRating'] = round(userCart[i]['itemDetails']['averageRating'])
				if userCart[i]['itemDetails']['catID'] == 'CATOTH':
					userCart[i]['itemDetails']['categoryName'] = 'others'
				else:
					userCart[i]['itemDetails']['categoryName'] = categoryList[userCart[i]['itemDetails']['catID']]['name']
				userCart[i]['sellerDeatials'] = userList[userCart[i]['itemDetails']['userID']]
		return userCart

class CostEstimation(Resource):
	def post(self, userID):
		userID = userID.upper()
		userList = db.child('PetsWorld').child('userList').get().val()
		if userList == None:
			userList = {}
		categoryList = db.child('PetsWorld').child('categoryList').get().val()
		if categoryList == None:
			categoryList = {}
		itemList = db.child('PetsWorld').child('itemList').get().val()
		if itemList == None:
			itemList = {}
		itemCart = db.child('PetsWorld').child('itemCart').get().val()
		if itemCart == None:
			itemCart = {}
		if not userID in userList:
			abort(400, message= 'user not found')
		userCart = {}
		grandTotal = 0
		if userID in itemCart:
			userCart = itemCart[userID]
			for i in userCart:
				userCart[i]['itemDetails'] = itemList[i]
				userCart[i]['itemDetails']['averageRating'] = round(userCart[i]['itemDetails']['averageRating'])
				if userCart[i]['itemDetails']['catID'] == 'CATOTH':
					userCart[i]['itemDetails']['categoryName'] = 'others'
				else:
					userCart[i]['itemDetails']['categoryName'] = categoryList[userCart[i]['itemDetails']['catID']]['name']
				userCart[i]['sellerDetails'] = userList[userCart[i]['itemDetails']['userID']]
				if userCart[i]['qty'] <= itemList[i]['stock']:
					userCart[i]['stockStatus'] = 'available'
					userCart[i]['totalPrice'] = itemList[i]['rate'] * userCart[i]['qty']
					grandTotal = grandTotal + userCart[i]['totalPrice']
				else:
					userCart[i]['totalPrice'] = itemList[i]['rate'] * userCart[i]['qty']
					userCart[i]['stockStatus'] = 'not available'
		cart = {
			'userCart'   : userCart,
			'grandTotal' : grandTotal
		}
		return cart

class PurchaseItem(Resource):
	def post(self, userID):
		userID = userID.upper()
		userList = db.child('PetsWorld').child('userList').get().val()
		if userList == None:
			userList = {}
		categoryList = db.child('PetsWorld').child('categoryList').get().val()
		if categoryList == None:
			categoryList = {}
		itemList = db.child('PetsWorld').child('itemList').get().val()
		if itemList == None:
			itemList = {}
		itemCart = db.child('PetsWorld').child('itemCart').get().val()
		if itemCart == None:
			itemCart = {}
		tempItemCart = itemCart.copy()
		if not userID in userList:
			abort(400, message= 'user not found')
		if not userID in tempItemCart:
			abort(400, message= 'empty cart, cant purchase. please add items to cart')
		else:
			userCart = tempItemCart[userID]
			tempUserCart = userCart.copy()
		purchaseCnt = db.child('PetsWorld').child('purchaseCnt').get().val()
		if purchaseCnt == None:
			purchaseCnt = 0
		purchaseCnt += 1
		db.child('PetsWorld').child('purchaseCnt').set(purchaseCnt)
		purchsID = 'PURCHS' + str(100 + purchaseCnt)
		sampleHistroy = {}
		for i in tempUserCart:
			if tempUserCart[i]['qty'] <= itemList[i]['stock']:
				transDetails = {}
				transactionCnt = db.child('PetsWorld').child('transactionCnt').get().val()
				if transactionCnt == None:
					transactionCnt = 0
				transactionCnt += 1
				db.child('PetsWorld').child('transactionCnt').set(transactionCnt)
				transID = 'TRANS' + str(100 + transactionCnt)
				x = datetime.now(timezone("Asia/Kolkata"))
				date = x.strftime('%d/%m/%Y')
				time = x.strftime('%X')
				transDetails = {
					'purchsID'      : purchsID,
					'itemID'       : i,
					'qty'           : tempUserCart[i]['qty'],
					'totalPrice'    : tempUserCart[i]['qty'] * itemList[i]['rate'],
					'date'          : date,
					'time'          : time,
					'itemDetails'   : itemList[i],
					'sellerID'      : itemList[i]['userID'],
					'sellerDetails' : userList[itemList[i]['userID']],
					'buyerID'       : userID,
					'buyerDetails'  : userList[userID]
				}
				transDetails['itemDetails']['averageRating'] = round(transDetails['itemDetails']['averageRating'])
				if transDetails['itemDetails']['catID'] == 'CATOTH':
					transDetails['itemDetails']['categoryName'] = 'others'
				else:
					transDetails['itemDetails']['categoryName'] = categoryList[transDetails['itemDetails']['catID']]['name']
				transactionHistory = db.child('PetsWorld').child('transactionHistory').get().val()
				if transactionHistory == None:
					transactionHistory = {}
				transactionHistory[transID] = transDetails
				sampleHistroy[transID] = transDetails
				db.child('PetsWorld').child('transactionHistory').set(transactionHistory)
				itemList[i]['stock'] = itemList[i]['stock'] - tempUserCart[i]['qty']
				db.child('PetsWorld').child('itemList').set(itemList)
				del itemCart[userID][i]
		db.child('PetsWorld').child('itemCart').set(itemCart)
		return sampleHistroy

class TransactionHistory(Resource):
	def get(self):
		transactionHistory = db.child('PetsWorld').child('transactionHistory').get().val()
		if transactionHistory == None:
			transactionHistory = {}
		transKey = list(transactionHistory.keys())
		transKey.reverse()
		transHistory = {}
		for i in transKey:
			transHistory[i] = transactionHistory[i]
		return transHistory

class PurchaseHistory(Resource):
	def get(self, purchsID):
		purchsID = purchsID.upper()
		purchaseHistory = {}
		transactionHistory = db.child('PetsWorld').child('transactionHistory').get().val()
		if transactionHistory == None:
			transactionHistory = {}
		for i in transactionHistory:
			if transactionHistory[i]['purchsID'] == purchsID:
				purchaseHistory[i] = transactionHistory[i]
		return purchaseHistory

class TransactionDetails(Resource):
	def get(self, transID):
		transID = transID.upper()
		transDetails = {}
		transactionHistory = db.child('PetsWorld').child('transactionHistory').get().val()
		if transactionHistory == None:
			transactionHistory = {}
		if transID in transactionHistory:
			transDetails = transactionHistory[transID]
		else:
			abort(400, message='transaction not found')
		return transDetails

class UserTransactionHistory(Resource):
	def get(self, userID, cat):
		userID = userID.upper()
		userList = db.child('PetsWorld').child('userList').get().val()
		if userList == None:
			userList = {}
		if not userID in userList:
			abort(400, message='user not found')
		transactionHistory = db.child('PetsWorld').child('transactionHistory').get().val()
		if transactionHistory == None:
			transactionHistory = {}
		tempTransactionHistory = {}
		for i in transactionHistory:
			if cat == 'all':
				if transactionHistory[i]['sellerID'] == userID or transactionHistory[i]['buyerID'] == userID:
					tempTransactionHistory[i] = transactionHistory[i]
			elif cat == 'sell':
				if transactionHistory[i]['sellerID'] == userID:
					tempTransactionHistory[i] = transactionHistory[i]
			elif cat == 'buy':
				if transactionHistory[i]['buyerID'] == userID:
					tempTransactionHistory[i] = transactionHistory[i]
			else:
				abort(400, message='invalid category')
		transKey = list(tempTransactionHistory.keys())
		transKey.reverse()
		transHistory = {}
		for i in transKey:
			transHistory[i] = tempTransactionHistory[i]
		return transHistory

class ItemTransactionHistory(Resource):
	def get(self, itemID):
		itemID = itemID.upper()
		itemList = db.child('PetsWorld').child('itemList').get().val()
		if itemList == None:
			itemList = {}
		if not itemID in itemList:
			abort(400, message='item not found')
		transactionHistory = db.child('PetsWorld').child('transactionHistory').get().val()
		if transactionHistory == None:
			transactionHistory = {}
		tempTransactionHistory = {}
		for i in transactionHistory:
			if transactionHistory[i]['itemID'] == itemID:
				tempTransactionHistory[i] = transactionHistory[i]
		transKey = list(tempTransactionHistory.keys())
		transKey.reverse()
		transHistory = {}
		for i in transKey:
			transHistory[i] = tempTransactionHistory[i]
		return transHistory

api.add_resource(UserReg, '/user')
api.add_resource(UserUpdate, '/user/<userID>')
api.add_resource(UserLogin, '/userLogin')
api.add_resource(AdminLogin, '/adminLogin')
api.add_resource(CategoryReg, '/category')
api.add_resource(CategoryUpdate, '/category/<catID>')
api.add_resource(ItemReg, '/item')
api.add_resource(ItemDataUpdate, '/item/<itemID>')
api.add_resource(ItemImgUpdate, '/itemImg/<itemID>')
api.add_resource(ItemRating, '/itemRating/<itemID>')
api.add_resource(ItemComment, '/itemComment/<itemID>')
api.add_resource(commentUpdate, '/comment/<commentID>')
api.add_resource(Message, '/message')
api.add_resource(MessageInbox, '/message/<userID>')
api.add_resource(ItemList, '/itemList/<userID>/<cat>')
api.add_resource(OthItemComment, '/othItemComment/<userID>/<itemID>')
api.add_resource(FilterItemList, '/filterItemList')
api.add_resource(FilterItem, '/filterItem')
api.add_resource(SearchItem, '/searchItem')
api.add_resource(ItemCart, '/itemCart/<userID>')
api.add_resource(ItemCartUpdate, '/itemCartUpdate/<userID>/<itemID>')
api.add_resource(CostEstimation, '/costEstimation/<userID>')
api.add_resource(PurchaseItem, '/purchaseItem/<userID>')
api.add_resource(TransactionHistory, '/transactionHistory')
api.add_resource(PurchaseHistory, '/purchaseHistory/<purchsID>')
api.add_resource(TransactionDetails, '/transDetails/<transID>')
api.add_resource(UserTransactionHistory, '/transactionHistory/<userID>/<cat>')
api.add_resource(ItemTransactionHistory, '/itemTransactionHistory/<itemID>')

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=8000)