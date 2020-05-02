import markdown
import datetime
from .models import Tags, EpistemicStates, DocTypes, DocStatuses


def read_file(filename):
    with open(f'./sample_md_articles/{filename}', 'r') as file:
        text = file.read()
        return text


# Is meant for unique db keys.
def db_id_for_meta_value(meta_value, db_object):
    existing = db_object.query.filter(db_object.name ==
                                      meta_value
                                      ).first()
# try/catch
    if existing is None:
        return 'Value \'' + meta_value + '\' not in database. Aborting.'

    print('Retrieved id for: ' + meta_value)
    return existing.id


def dict_from_md(filename):
    REQUIRED_META = {'slug', 'title', 'last_major_edit',
                     'importance', 'type',
                     'epistemic_state', 'status'}
    OPTIONAL_META = {'tags'}
    text = read_file(filename)
    md = markdown.Markdown(extensions=['meta'])
#  There's also convertFile, but it only outputs to files or stdout, so I went
#  manual
    html = md.convert(text)
    metadata = md.Meta
    tags = []
    prepared_dict = {}
# try/catch
# {*dict} fetches set of keys in dict. Weird but concise. Just get used to it.
    if(not ({*metadata} == REQUIRED_META or
       {*metadata} == REQUIRED_META | OPTIONAL_META)):
        print('Missing or wrong metadata.')
        return

    if 'tags' in metadata:
        tags_in_file = metadata.pop('tags')
        for name in tags_in_file:
            existing_in_db = Tags.query.filter(Tags.name == name).first()
            if existing_in_db:
                print('Tag \'' + name + '\' already exists.')
                tags.append(existing_in_db)
            else:
                tags.append(Tags(name=name, category=1))
                print('New domain tag \'' + name + '\' to be created.')
        print('Tags to be appended: ')
        for i in tags:
            print(i.name + ', ')

    prepared_dict['content'] = html
# Named 'tags_list' to mirror attribute of 'Articles' orm class
    prepared_dict['tags_list'] = tags
    for key in metadata:
        prepared_dict[key] = ''.join(metadata[key])
# convert date string to 'date' object
    prepared_dict['last_major_edit'] =\
        datetime.datetime.strptime(prepared_dict['last_major_edit'],
                                   "%d/%m/%Y").date()

    es_id = db_id_for_meta_value('epistemic_state', EpistemicStates)
    type_id = db_id_for_meta_value('type', DocTypes)
    status_id = db_id_for_meta_value('status', DocStatuses)

    del prepared_dict['epistemic_state']
    prepared_dict['epistemic_state_id'] = es_id
    del prepared_dict['type']
    prepared_dict['type_id'] = type_id
    del prepared_dict['status']
    prepared_dict['status_id'] = status_id

    return prepared_dict
