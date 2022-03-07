from webserver.api import api_bp
from flask import jsonify, request, url_for
from webserver.models import User
from webserver import db


@api_bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict(include_mail=True))


@api_bp.route('/users', methods=['GET'])
def get_users():
    # 从请求的查询字符串中提取page和per_page，如果它们没有被定义，则分别使用默认值1和6
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 6, type=int), 100)
    data = User.to_collection_dict(User.query, page, per_page, 'api.get_users')
    return jsonify(data)


@api_bp.route('/users/<int:id>/followers', methods=['GET'])
def get_followers(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 6, type=int), 100)
    data = User.to_collection_dict(user.followers, page, per_page, 'api.get_followers', id=id)
    return jsonify(data)


@api_bp.route('/users/<int:id>/followed', methods=['GET'])
def get_followed(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 6, type=int), 100)
    data = User.to_collection_dict(user.followers, page, per_page, 'api.get_followed', id=id)
    return jsonify(data)


@api_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    print(data)
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return 404
    if User.query.filter_by(username=data['username']).first():
        return 'please use a different username'
    if User.query.filter_by(email=data['email']).first():
        return 'please use a different email address'
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response


@api_bp.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json() or {}
    if 'username' in data and data['username'] != user.username and User.query.filter_by(username=data['username']).first():
        return 'please use a different username'
    if 'email' in data and data['email'] != user.email and User.query.filter_by(email=data['email']).first():
        return 'please use a different email address'
    user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(user.to_dict(include_mail=True))


