# -*- coding: utf-8 -*-

from ava.utils.error import TrainConfigError


class TrainConfig(object):
    """训练监控配置"""

    def __init__(self,
                 job_type=None,
                 job_id=None,
                 training_ins_id=None,
                 training_sample_num=None,
                 batch_size=None,
                 val_batch_size=None,
                 batch_num_of_epoch=None,
                 ):
        """初始化监控配置

        Args:
                job_id:                 任务ID
                training_ins_id:        训练实例ID （一个任务ID对应多个训练实例ID）
                training_sample_num:    用于训练的样本数
                batch_size:             每次训练迭代包含 x 个样本
                val_batch_size:         每次验证评估迭代包含 x 个样本
                batch_num_of_epoch:     一个 epoch 中包含多少个 batch

        Raises:
                TrainConfigError
        """
        self.job_type = job_type or ''
        self.job_id = job_id or ''
        self.training_ins_id = training_ins_id or ''
        self.training_sample_num = training_sample_num or 0
        self.batch_size = batch_size or 0
        self.val_batch_size = val_batch_size or 0
        self.batch_num_of_epoch = batch_num_of_epoch or 0
        # TODO 后续随着监控项的完善，再进行扩充
