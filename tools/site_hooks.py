# SPDX-License-Identifier: GPL-3.0-only
"""Point staged aliases at canonical GitHub sources; hide generated edit links."""


def on_page_context(context, page, config, nav):
    canonical = page.meta.get('edit_uri')
    if canonical == '':
        page.edit_url = None
    elif canonical is not None:
        page.edit_url = config['repo_url'].rstrip('/') + '/edit/main/' + canonical
    return context
