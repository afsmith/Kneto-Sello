
from tagging.models import Tag
from tagging import models

def to_autocomplete_format(db_row):
    return {u'id': db_row["pk"], u'value': db_row["name"]}

def bind_tags_with_file(file, tags_ids, new_tags_names):
    tags_ids = set(tags_ids).union(add_if_not_exists(new_tags_names))

    for tag_id in tags_ids:
        file.tag_set.add(Tag.objects.get(id=tag_id))

def add_if_not_exists(new_tags_names):
    result = []

    for new_tag_name in new_tags_names:
        result.append(add_if_not_exist(new_tag_name).id)
    return result

def add_if_not_exist(tag_name, is_default=False, type=models.TYPE_CUSTOM):
    tag_name = tag_name.upper()
    try:
        return Tag.objects.get(name=tag_name, is_default=is_default, type=type)
    except:
        return Tag.objects.create(name=tag_name, is_default=is_default, type=type)