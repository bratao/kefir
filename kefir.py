class Kefir:
    
    def __init__(self, session=None, objects={}, rels=[], shorcuts={}, ignore=[]):
        self.session = session  # SQLAlhcemy session
        self.objects = objects # tablename -> Class; {'users':User} for example. this is needed for relations
        self.rels = rels # some relations of tables. Example: rels={'users':['orders']}. users table is main in rels with orders
        self.shorcuts = shorcuts  # shorcuts for change table name in converted object
        self.ignore = ignore  # Table for ignoring
    
    def _is_custom_class(self, obj):
         return not (
             isinstance(obj, int) or \
             isinstance(obj, str) or \
             isinstance(obj, bool) or \
             isinstance(obj, dict) or \
             isinstance(obj, float)
        )
    
    def _is_foreign_key(self, table, col):
        dct = {}
        for i in table.columns:
            rels = []
            if i.foreign_keys:
                for j in i.foreign_keys:
                    rels.append((j._column_tokens[1], j._column_tokens[2]))
                    
            dct[i.name] = rels

        return dct[col]
    
    def dump(self, obj):
        if isinstance(obj , list):
            lst = []
            for i in obj:
                lst.append(self.dump(i))
            return lst
        else:
            obj_type = 'class'
            if "<class 'sqlalchemy.ext.declarative.api.Model'>" in list(map(str, type(obj).mro())): #looks bad :[
                obj_type = 'model'
            
            if obj_type == 'class':
                dct = {}
                try:
                    obj.__slots__
                    has_slots = True
                except AttributeError:
                    has_slots = False
                if has_slots:
                    for key in obj.__slots__:
                        if self._is_custom_class(getattr(obj, key)):
                            dct[key] = self.dump(getattr(obj, key))
                        else:
                            dct[key] = getattr(obj, key)
                else:
                    for key, value in obj.__dict__.items():
                        if not key.startswith('_'):
                            if self._is_custom_class(value):
                                dct[key] = self.dump(value)
                            else:
                                dct[key] = value
                return dct
            elif obj_type == 'model':
                dct = {}
                done = []
                table = obj.metadata.tables[obj.__tablename__]
                cols = [str(col[len(obj.__tablename__)+1:]) for col in list(map(str, table.columns))]
                for col in cols:
                    if self._is_foreign_key(table, col):
                        for i in  self._is_foreign_key(table, col):
                           if i[0] not in self.ignore:
                               sql = 'SELECT * FROM '+ i[0]  + ' WHERE ' + i[1] + ' = ' + '"' + str(getattr(obj, col)) + '"' + ';'
                               data = self.session.execute(sql).cursor.fetchall()
                               cols = self.session.execute(sql).__dict__['_metadata'].keys
                               if len(data) == 1:
                                   dct[self.shorcuts.get(i[0], i[0])] = dict(zip(cols, data[0]))                                
                               else:
                                   dct[self.shorcuts.get(i[0], i[0])] = [dict(zip(cols, i)) for i in data]

                    dct[col] = getattr(obj, col)
                if self.rels.get(obj.__tablename__):
                    for i in self.rels[obj.__tablename__]:
                        obj_arg = list(obj.__dict__['_sa_instance_state'].__dict__ \
                                                                    ['manager'].__dict__['local_attrs'][i].__dict__\
                                                                    [ 'comparator'].__dict__['_parententity'].__dict__ \
                                                                    ['_init_properties'][i].__dict__ \
                                                                    ['synchronize_pairs'][0][1].__dict__ \
                                                                    ['foreign_keys'])[0].__dict__[ '_column_tokens'][2]
                        
                        rel_obj_arg = list(obj.__dict__['_sa_instance_state'].__dict__['manager'].__dict__ \
                                      ['local_attrs'][i].__dict__[ 'comparator'].__dict__ \
                                      ['_parententity'].__dict__['_init_properties'][i].__dict__ \
                                      ['synchronize_pairs'][0][1].__dict__['foreign_keys'])[0].__dict__ \
                                      ['parent'].__dict__[ '_key_label'][len(i)+1:]
                        sql = 'SELECT * FROM ' + i + ' WHERE ' + rel_obj_arg + ' = ' + '"' + str(getattr(obj, obj_arg)) + '"' + ';'
                        data = self.session.execute(sql).fetchall()
                        cols = self.session.execute(sql).__dict__['_metadata'].keys
                        if len(data) == 1:
                            dct[self.shorcuts.get(i, i)] = dict(zip(cols, data))
                        else:
                            dct[self.shorcuts.get(i, i)] = [dict(zip(cols, i)) for i in data]
                return dct
