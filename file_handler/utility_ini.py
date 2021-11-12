import configparser

def get_section_names( config_path ):
    section_names = list()

    fh = configparser.ConfigParser()
    fh.read( config_path )

    for sec_name in fh:
        if sec_name == 'DEFAULT':
            continue
        section_names.append(sec_name)

    return section_names
