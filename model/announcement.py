from datetime import datetime
from flask import Blueprint, request

from mongo import *
from .auth import *
from .utils import *

__all__ = ['ann_api']

ann_api = Blueprint('ann_api', __name__)


@ann_api.route('/', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
def anncmnt(user):
    @Request.json('course_name')
    def get_anns(course_name):
        # Get an announcement list
        try:
            anns = Announcement.ann_list(user.obj, course_name or 'Public')
        except (DoesNotExist, ValidationError):
            return HTTPError('Cannot Access a Announcement', 403)
        if anns is None:
            return HTTPError('Announcement Not Found', 404)
        data = [{
            'annId': str(an.id),
            'title': an.title,
            'createTime': int(an.create_time.timestamp()),
            'updateTime': int(an.update_time.timestamp()),
            'creater': an.creater.username,
            'updater': an.updater.username,
            'markdown': an.markdown
        } for an in anns]
        return HTTPResponse('Announcement List', data=data)

    @Request.json('title', 'markdown', 'course_name')
    def create(title, markdown, course_name):
        # Create a new announcement
        try:
            ann = Announcement.new_ann(course_name or 'Public', title,
                                         user.obj, markdown)
        except ValidationError as ve:
            return HTTPError('Failed to Create Announcement',
                             400,
                             data=ve.to_dict())
        if ann is None:
            return HTTPError('Failed to Create Announcement', 403)
        data = {
            'annId': str(ann.id),
            'createTime': int(ann.create_time.timestamp())
        }
        return HTTPResponse('Announcement Created', data=data)

    @Request.json('ann_id', 'title', 'markdown')
    def update(ann_id, title, markdown):
        # Update an announcement
        ann = Announcement(ann_id)
        if not ann:
            return HTTPError('Announcement Not Found', 404)
        course = ann.course
        if user.role != 0 and user != course.teacher and user not in course.tas:
            return HTTPError('Failed to Update Announcement', 403)
        try:
            ann.update(title=title,
                        markdown=markdown,
                        update_time=datetime.utcnow(),
                        updater=user.obj)
        except ValidationError as ve:
            return HTTPError('Failed to Update Announcement',
                             400,
                             data=ve.to_dict())
        return HTTPResponse('Updated')

    @Request.json('ann_id')
    def delete(ann_id):
        # Delete an announcement
        ann = Announcement(ann_id)
        if not ann:
            return HTTPError('Announcement Not Found', 404)
        course = ann.course
        if user.role != 0 and user != course.teacher and user.obj not in course.tas:
            return HTTPError('Failed to Delete Announcement', 403)
        ann.update(status=1)
        return HTTPResponse('Deleted')

    methods = {
        'GET': get_anns,
        'POST': create,
        'PUT': update,
        'DELETE': delete
    }

    return methods[request.method]()
