from app.services.oss import OSS
from app.services.local_file import LocalFile

""" 获取存储方案 """
class Storage:
  def __init__(self, config=None):
    if config:
      self.init(config)
    else:
      self.storageObject = None
      self.storageConfig = None

  def init(self, config):
    """配置初始化"""
    if config["FILE_CACHE_TYPE"] == "local":
      self.storageObject = LocalFile(config)
    else:
      self.storageObject = OSS(config)
    self.storageConfig = config

  def getStorageType(self):
    """返回存储方式"""
    return self.storageConfig["FILE_CACHE_TYPE"]
  
  def getPathType(self, name):
    """ 获取映射的路径 """
    # 不能改OSS区域代码所以临时添加的内容
    if self.getStorageType() == "oss":
      nameMap = {
        "project": self.storageConfig["OSS_FILE_PREFIX"],
        "thumbnail": self.storageConfig["OSS_FILE_PREFIX"],
        "user_avatar": self.storageConfig["OSS_USER_AVATAR_PREFIX"],
        "team_avatar": self.storageConfig["OSS_TEAM_AVATAR_PREFIX"],
        "output": self.storageConfig["OSS_OUTPUT_PREFIX"]
      }
      return nameMap.get(name, self.storageConfig["OSS_FILE_PREFIX"])
    else:
      return self.storageObject.getPathType(name)

  def upload(self, *args):
    """上传文件"""
    return self.storageObject.upload(*args)

  def download(self, path, filename, /, *args):
    """下载文件， 拷贝文件到另一个目录"""
    return self.storageObject.download(path, filename, *args)

  def is_exist(self, *args):
    """检查文件是否存在"""
    return self.storageObject.is_exist(*args)

  def delete(self, *args):
    """（批量）删除文件"""
    return self.storageObject.delete(*args)

  def sign_url(self, *args, **kwargs):
    """ 生成文件地址 """
    return self.storageObject.sign_url(*args, **kwargs)