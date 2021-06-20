from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import shutil

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pxhvltkppvygwu:040a51f1444c8cf0a3bcb5a19c79d649ed618388a9ff5aafb55c1ba96d927671@ec2-174-129-225-160.compute-1.amazonaws.com:5432/d47blt1hbc4qjj'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cat.db'
db = SQLAlchemy(app)

class TournamentTable(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	path = db.Column(db.String, nullable=False)
	ranking = db.Column(db.Integer, default=0)

	def __repr__(self):
		return '<TournamentTable(id: %d, path: %s, ranking: %d)>' % (self.id, self.path, self.ranking)

def make_response(data={}, status=200):
    '''
        - Make a resionable response with header
        - status default is 200 mean ok
    '''
    res = jsonify(data)
    res.headers.add('Access-Control-Allow-Origin', '*')
    res.headers.add('Content-Type', 'application/json')
    res.headers.add('Accept', 'application/json')
    return res

@app.route('/')
def index():
	data = dict(data='this is cat-mash page')
	return make_response(data)

@app.route('/get-tournament')
def get_tournament():
	'''
		lấy hai ảnh mèo có ranking thấp nhất để đọ 
	'''
	data = TournamentTable.query.order_by(TournamentTable.ranking.asc()).limit(2).all()
	data = [dict(id=datum.id, path=datum.path) for datum in data]
	ret = dict(data=data)
	return make_response(ret)

@app.route('/vote/<int:cat_id>')
def vote(cat_id):
	'''
	vote với id tương ứng
	'''
	data = TournamentTable.query.filter(TournamentTable.id == cat_id).first()
	data.ranking += 1
	db.session.commit()
	ret = dict(data=f'vote done, ranking of {data.id} change from {data.ranking - 1} to {data.ranking}')
	return make_response(ret)

@app.route('/get-leaderboard')
def get_leaderboard():
	'''
		trả về bảng phong thần 
	'''
	data = TournamentTable.query.order_by(TournamentTable.ranking.desc()).limit(10).all()
	data = [dict(id=datum.id, path=datum.path, ranking=datum.ranking) for datum in data]
	ret = dict(data=data)
	return make_response(ret)

@app.route('/init-db/<key>')
def init_db(key):
	'''
		thực hiện gán ảnh với id vào db và reset ranking 
	'''
	if key == 'tuanio':

		# assign image
		# img_id = 1
		# for source, dirs, files in os.walk('images'):
		# 	for file in files:
		# 		filename = os.path.join(source, file)
		# 		file_ext = filename.rsplit('.', 1)[-1]
		# 		if file_ext == 'txt':
		# 			continue
		# 		new_filename = os.path.join(source, f'{img_id}.{file_ext}')
		# 		os.rename(filename, new_filename)
		# 		img_id += 1
		# end assign image
		db.drop_all()
		db.create_all()

		for source, dirs, files in os.walk('images'):
			for file in files:
				filename = os.path.join(source, file)
				if 'jpg' not in filename and 'jpeg' not in filename:
					os.remove(filename)
				img_id = file.split('.')[0]
				ins = TournamentTable(path=filename, ranking=0)
				db.session.add(ins)
		db.session.commit()
		return make_response({'data': 'init db successfully'})
	return make_response({'data': 'route not found'})

if __name__ == '__main__':
	app.run(debug=True)