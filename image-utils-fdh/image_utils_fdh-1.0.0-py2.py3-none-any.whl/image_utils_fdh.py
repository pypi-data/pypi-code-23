import os

from PIL import Image


def manipulate_and_save(src_img_path, pil_manip_funcs, output_path, output_file_format="jpeg"):
    """
    Uses function composition.  pil_manip_funcs is a list of functions.  Each function should
    be expecting a only pil object to be passed into it and should return that manipulated
    pil object.  If other parameters are needed for your manipulation function then I
    recommend using the functools partial function tool.
    """
    if len(pil_manip_funcs) == 0:
        raise Exception("Expecting at least one image manipulation function")
    pil_img = Image.open(src_img_path)
    for pil_manip_func in pil_manip_funcs:
        pil_img = pil_manip_func(pil_img)
    output_dir_path = output_path[:output_path.rfind('/')]
    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)
    pil_img.save(output_path, output_file_format, quality=100)


def down_scale(max_width, pil_obj):
    src_w, src_h = pil_obj.size
    # max_width = 720
    # final_img = pg_img
    if src_w > max_width:
        pil_obj.thumbnail((max_width, max_width), Image.ANTIALIAS)
    # tmp_local_img_path = tmp_dir_path + "/pdf_img_" + str(uuid.uuid1()) + ".jpg"
    # final_img.save(tmp_local_img_path)
    return pil_obj
