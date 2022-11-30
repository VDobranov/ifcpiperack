import ifcopenshell as ios
import ifcopenshell.util.element as element

path = '/Users/vdobranov/Yandex.Disk.localized/Python/Mac/ifcopenshell/new_model.ifc'
ifc = ios.open(path)

pts = ifc.by_type('IFCCARTESIANPOINT')

for main_pt in pts:
    pts_to_delete = []
    main_pt_attrs = main_pt.get_info()
    main_pt_id = main_pt.id()
    del main_pt_attrs['id']
    for pt in pts:
        pt_attrs = pt.get_info()
        del pt_attrs['id']
        if main_pt_attrs == pt_attrs:
            pts_to_delete.append(pt)

    if len(pts_to_delete) == 1:
        continue
    print(pts_to_delete)

    for d in pts_to_delete[1:]:
        toc = ifc.get_inverse(d)
        for t in toc:
            print(t.to_string())
            element.replace_attribute(t, d, main_pt)
        element.remove_deep(ifc,d)
            # t_attrs = t.get_info()
            # print(t_attrs)
            # for k, v in t_attrs:
            #     if v == d:
            #         v = main_pt
                # if v == f'#{d.id()}':
                #     v = f'#{main_pt_id}'


ifc.write(path)
