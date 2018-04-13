class MirrorRouter:

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'sis_mirror':
            return 'cache'

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'sis_mirror' or\
            obj2._meta.app_label == 'sis_mirror':
            return True
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == "sis_mirror":
            return False
        return None