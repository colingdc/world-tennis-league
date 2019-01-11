from flask import (render_template, request, jsonify,
                   current_app, redirect, url_for)


def unauthorized(e):
    if (request.accept_mimetypes.accept_json and
            not request.accept_mimetypes.accept_html):
        response = jsonify({'error': 'unauthorized'})
        response.status_code = 401
        return response
    current_app.logger.error('Unauthorized: %s', (request.path))
    return redirect(url_for("auth.login"))


def forbidden(e):
    if (request.accept_mimetypes.accept_json and
            not request.accept_mimetypes.accept_html):
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response
    current_app.logger.error('Unauthorized: %s', (request.path))
    return render_template('errors/403.html'), 403


def page_not_found(e):
    if (request.accept_mimetypes.accept_json and
            not request.accept_mimetypes.accept_html):
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    if not request.path.endswith("robots.txt"):
        current_app.logger.error('Page not found: %s', (request.path))
    return render_template('errors/404.html'), 404


def bad_request(e):
    if (request.accept_mimetypes.accept_json and
            not request.accept_mimetypes.accept_html):
        response = jsonify({'error': 'bad request'})
        response.status_code = 400
        return response
    current_app.logger.error('Bad request: %s', (request.path))
    return render_template('errors/400.html'), 400


def internal_server_error(e):
    if (request.accept_mimetypes.accept_json and
            not request.accept_mimetypes.accept_html):
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    current_app.logger.error('Server Error: {}, {}'.format(request.path, e))
    return render_template('errors/500.html'), 500


def unhandled_exception(e):
    if (request.accept_mimetypes.accept_json and
            not request.accept_mimetypes.accept_html):
        response = jsonify({'error': 'unhandled exception'})
        response.status_code = 500
        return response
    current_app.logger.error(
        'Unhandled exception: {}, {}'.format(request.path, e))
    return render_template('errors/500.html'), 500
