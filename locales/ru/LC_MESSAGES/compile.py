import polib


po_path = 'locales/ru/LC_MESSAGES/messages.po'
mo_path = 'locales/ru/LC_MESSAGES/messages.mo'


po = polib.pofile(po_path)
po.save_as_mofile(mo_path)