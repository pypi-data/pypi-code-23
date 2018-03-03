# -*- coding: utf-8 -*-
import os
import shutil


def rm_path(path):
    """ 安全删除文件或目录。 """
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


def mkdir_p(directory):
    """ 安全创建目录。 """
    if not os.path.exists(directory):
        os.makedirs(directory)


# Ref: https://github.com/qbox/ava/blob/dev/docker/scripts/README.md
MODEL_FILES = ("train.prototxt", "deploy.prototxt", "weight.caffemodel",
               "train.symbol.json", "deploy.symbol.json", "weight.params",)


def file_location(workdir, filetype):
    """ 按工作目录约定的文件组织结构查找配置或输入输出文件路径。

    1. 读文件：期望从 expect_fn 读文件，expect_fn 应当存在。
    2. 写文件：期望向 expect_fdir/filetype 写文件，expect_fdir 应当存在。
    3. 约定结构：
        https://github.com/qbox/ava/blob/dev/docker/scripts/README.md

    Args:
        workdir: 工作目录。
        filetype: （读写）文件名称或（读）匹配规则。

    Returns:
        文件路径。非预期情况返回 None，包括： 读文件不存在；非预期的文件名称或匹配规则。
    """
    expect_fn = None
    expect_fdir = None
    # 训练输出 - snapshot & upload trigger
    if filetype == "snapshot":
        expect_fdir = os.path.join(workdir, "run", "output")
    if filetype == "upload.run":
        expect_fdir = os.path.join(workdir, "run", "output")

    # 训练输出 - 日志
    if filetype.endswith(".log"):
        expect_fdir = os.path.join(workdir, "run", "logs")

    # 模型输入
    if filetype in MODEL_FILES:
        filedir = os.path.join(workdir, "model")
        for fn in os.listdir(filedir):
            if fn.endswith(filetype):
                expect_fn = os.path.join(filedir, fn)
                break

    # 训练生成的 fixed 模型
    if filetype == "fixed_train.prototxt" or filetype == "solver.prototxt":
        expect_fdir = os.path.join(workdir, "run", "prepared")
    if filetype == "fixed_train.symbol.json" or filetype == "solver.json":
        expect_fdir = os.path.join(workdir, "run", "prepared")

    # 训练注入的 ConfigMap
    if filetype.startswith("config"):
        expect_fdir = workdir

    # mean file
    if filetype.startswith("mean."):
        # 如果模型里面有，优先使用模型里的meanfile
        # 选择权交给 util 包的使用者？ TODO
        mean_file_in_model = os.path.join(workdir, "model", filetype)
        mean_file_in_data = os.path.join(workdir, "data", "train", filetype)
        if os.path.exists(mean_file_in_model):
            expect_fn = mean_file_in_model
        else:
            expect_fn = mean_file_in_data

    # 样本集
    if filetype == "train.rec":
        expect_fn = os.path.join(workdir, "data", "train", "cache", "data.rec")
    if filetype == "val.rec":
        expect_fn = os.path.join(workdir, "data", "val", "cache", "data.rec")

    if filetype == "train.lmdb":
        expect_fn = os.path.join(workdir, "data", "train", "cache")
    if filetype == "val.lmdb":
        expect_fn = os.path.join(workdir, "data", "val", "cache")

    if filetype == "train.roidb":
        expect_fn = os.path.join(
            workdir, "data", "train", "cache", "gt_roidb.pkl")
    if filetype == "val.roidb":
        expect_fn = os.path.join(
            workdir, "data", "val", "cache", "gt_roidb.pkl")

    if expect_fdir:
        mkdir_p(expect_fdir)
        return os.path.join(expect_fdir, filetype)

    if expect_fn and os.path.exists(expect_fn):
        return expect_fn

    return None
