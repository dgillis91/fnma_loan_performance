import os
import yaml

try:
    from sqlalchemy import create_engine, Column, Integer, String
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, reconstructor
    Base = declarative_base()
    HAVE_SQL_ALCHEMY = True
except:
    HAVE_SQL_ALCHEMY = False

class State(object):
    @classmethod
    def state(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    def __init__(self, path=None):
        self.path = path
        self.d = {}
        self.load()

    def __enter__(self):
        self.load()
        return self

    def __exit__(self, type, value, traceback):
        self.save()

    def __getitem__(self, key):
        try:
            return self.d[key]
        except KeyError:
            return None

    def __setitem__(self, key, value):
        self.d[key] = value 

    def save(self):
        with open(self.path, 'w') as f:
            f.write(yaml.dump(dict(self.d)))

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                self.d = yaml.safe_load(f.read().replace('\t', '    '))

    def cleanup(self):
        if os.path.exists(self.path):
            os.remove(self.path)

if HAVE_SQL_ALCHEMY:
    class DBState(State, Base):
        __tablename__ = 'state'

        # This module currently has a very simplistic schema - we use some arbitrary ID, and a textual data field. In this field, 
        # we store a structured text object with state attributes.
        id = Column(Integer, primary_key=True)
        data = Column(String)

        # The database session - singleton design
        session = None

        @classmethod
        def state(cls, url=None, *args, **kwargs):
            if not cls.session:
                engine = create_engine(url, echo=False)
                Base.metadata.create_all(engine)
                Session = sessionmaker(bind=engine)
                cls.session = Session()

            inst = cls.session.query(DBState).first()
            if inst:
                return inst
            else:
                return cls(*args, **kwargs)

            def __init__(self, *args, **kwargs):
                super(DBState, self).__init__(*args, **kwargs)
                self.d = {}
                self.data = '{}'

            def save(self):
                self.data = yaml.dump(self.d)
                self.session.add(self)
                self.session.commit()

            @reconstructor
            def load(self):
                if self.data:
                    self.d = yaml.safe_load(self.data)

            def cleanup(self):
                self.d = {}
                self.save()