class jbRouter(object):
    """
    A router to control all database operations on models in the
    jb application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read jb models go to jb_db.
        """
        if model._meta.app_label == 'jb':
            return 'jb_db'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write jb models go to jb_db.
        """
        if model._meta.app_label == 'jb':
            return 'jb_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the jb app is involved.
        """
        if obj1._meta.app_label == 'jb' or \
           obj2._meta.app_label == 'jb':
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the jb app only appears in the 'jb_db'
        database.
        """
        if app_label == 'jb':
            return db == 'jb_db'

        """
        Make sure the other apps don't migrate to 'jb_db'
        database.
        """
        if db == 'jb_db':
            return app_label == 'jb'

        return None
