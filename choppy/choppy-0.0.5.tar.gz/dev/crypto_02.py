# Sat Jan  6 17:11:32 CST 2018

# def encrypt(key, fn, fnout):
#     algo = Fernet(key)
#     with open(fnout, 'wb') as outfile:
#         with open(fn, 'rb') as infile:
#             outfile.write(algo.encrypt(infile.read()))
#
#
# def decrypt(key, fn, fnout):
#     algo = Fernet(key)
#     with open(fnout, 'wb') as outfile:
#         with open(fn, 'rb') as infile:
#             outfile.write(algo.decrypt(infile.read()))
#
#
# def xxcrypt(crypt_algo, fp_out, fp_in):
#     with open(fp_out, 'wb') as outfile:
#         with open(fp_in, 'rb') as infile:
#             outfile.write(crypt_algo(infile.read()))
#
#
# def batch_encrypt(key, paths, outdir):
#     fp_out = lambda fp: os.path.join(outdir, os.path.basename(fp))
#     fernet = Fernet(key)
#     crypt_algo = fernet.encrypt
#     enc_paths = []
#     for fp in paths:
#         path = fp_out(fp)
#         xxcrypt(crypt_algo, path, fp)
#         enc_paths.append(path)
#
#     return enc_paths
#
#
# def batch_decrypt(key, paths, outdir):
#     fp_out = lambda fp: os.path.join(outdir, os.path.basename(fp))
#     tmp_paths = []
#
#     fernet = Fernet(key)
#     crypt_algo = fernet.decrypt
#     for fp in paths:
#         path = fp_out(fp)
#         xxcrypt(crypt_algo, path, fp)
#         tmp_paths.append(path)
#
#     return tmp_paths
# def apply_crypto(fernet_method, fp_in, fp_out):
#     with open(fp_out, 'wb') as outfile:
#         with open(fp_in, 'rb') as infile:
#             outfile.write(fernet_method(infile.read()))
#
#     return fp_out


# def batch(key, paths, outdir, encrypt=True):
#     get_path = lambda fp: os.path.join(outdir, os.path.basename(fp))
#     io_paths = tuple(zip(paths, map(get_path, paths)))
#
#     fernet = Fernet(key)
#     fernet_method = fernet.encrypt if encrypt else fernet.decrypt
#
#     outpaths = []
#
#     def apply_crypto(fps):
#         fp_in, fp_out = fps
#         with open(fp_out, 'wb') as outfile:
#             with open(fp_in, 'rb') as infile:
#                 outfile.write(fernet_method(infile.read()))
#
#         return fp_out
#
#     with futures.ProcessPoolExecutor() as pool:
#         for fp_out in pool.map(apply_crypto, io_paths):
#             outpaths.append(fp_out)
#
#     return outpaths
