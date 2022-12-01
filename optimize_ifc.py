import ifcopenshell as ios
from toposort import toposort_flatten as toposort

# path = '/Users/vdobranov/Yandex.Disk.localized/Python/Mac/ifcopenshell/new_model.ifc'

# path = 'C:\\Users\\DobranovVY\\Downloads\\new_model.ifc'
path = '/Users/vdobranov/Yandex.Disk.localized/Python/Mac/ifcopenshell/new_model.ifc'
path_opt = path.replace('.ifc', '_optimized.ifc')

f = ios.open(path)
g = ios.file(schema=f.schema)


def generate_instances_and_references():
    """
    Generator which yields an entity id and 
    the set of all of its references contained in its attributes. 
    """
    for inst in f:
        yield inst.id(), set(i.id() for i in f.traverse(inst)[1:] if i.id())


instance_mapping = {}


def map_value(v):
    """
    Recursive function which replicates an entity instance, with 
    its attributes, mapping references to already registered
    instances. Indeed, because of the toposort we know that 
    forward attribute value instances are mapped before the instances
    that reference them.
    """
    if isinstance(v, (list, tuple)):
        # lists are recursively traversed
        return type(v)(map(map_value, v))
    elif isinstance(v, ios.entity_instance):
        if v.id() == 0:
            # express simple types are not part of the toposort and just copied
            return g.create_entity(v.is_a(), v[0])

        return instance_mapping[v]
    else:
        # a plain python value can just be returned
        return v


info_to_id = {}
stop = False

for id in toposort(dict(generate_instances_and_references())):
    inst = f[id]
    if inst.id() == 22: 
        stop = True
    print(inst[0])
    info = inst.get_info(include_identifier=False,
                         recursive=True, return_type=frozenset)
    if info in info_to_id:
        mapped = instance_mapping[inst] = instance_mapping[f[info_to_id[info]]]
    else:
        info_to_id[info] = id
        # if there is an error at this place then the model has some discrepancies - there is unset non-optional attributes!
        instance_mapping[inst] = g.create_entity(
            inst.is_a(),
            *map(map_value, inst)
        )
g.write(path_opt)
