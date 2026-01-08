"""
自定义异常类
统一管理业务异常
"""


class ServiceException(Exception):
    """服务层基础异常"""

    pass


class UserServiceException(ServiceException):
    """用户服务异常"""

    pass


class EmailServiceException(ServiceException):
    """邮件服务异常"""

    pass


class DatabaseException(ServiceException):
    """数据库操作异常"""

    pass


class ValidationException(ServiceException):
    """数据验证异常"""

    pass
