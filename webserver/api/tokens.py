from flask import jsonify, g
from webserver import db
from webserver.api import api_bp
from webserver.api.auth import basic_auth, token_auth


# @basic_auth.login_required装饰器将指示Flask-HTTPAuth验证身份（通过自定义的验证函数）
@api_bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = g.current_user.get_token()
    db.session.commit()
    return jsonify({'token': token})


@api_bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    g.current_user.revoke_token()
    db.session.commit()
    return '', 204
