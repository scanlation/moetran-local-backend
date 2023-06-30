"""
本地文件存储相关方法
"""
import time
import os
import shutil
from flask import url_for
from app.utils.logging import logger

prefix_items = ["user_avatar", "team_avatar", "project", "thumbnail", "output"]

def checkDirName(staticPath, basePath, filePath=None):
  """
  用相对路径获取绝对路径
  """
  if staticPath[-1] != os.sep:
    staticPath = staticPath + os.sep
  path = os.path.abspath(os.path.join(staticPath, basePath))
  if filePath:
    path = os.path.abspath(os.path.join(staticPath, basePath, filePath))
  files_folder = path
  # 不存在文件夹自动创建
  if not os.path.isdir(files_folder):
    os.makedirs(files_folder)
  if filePath:
    return "{}/{}".format(basePath, filePath)
  else:
    return basePath

class LocalFile:
  def __init__(self, config=None):
    if config:
      self.init(config)
    else:
      self.base_folder = None
      for prefix in prefix_items:
        setattr(self, prefix + "_folder", None)


  def init(self, config):
    self.STATIC_PATH = config.get('STATIC_PATH', os.path.abspath(os.path.join(os.getcwd(), "storage")))
    if config["FILE_CACHE_TYPE"] == "local":
      self.scheme = config.get("FILE_SCHEME", "http")
      self.cache_type = config["FILE_CACHE_TYPE"]
      self.file_domain = config.get("FILE_DOMAIN", None)
      # 文件根目录
      base_folder = config.get("FILE_PREFIX", "files")
      self.base_folder = checkDirName(self.STATIC_PATH, base_folder)
      for prefix in prefix_items:
        value = config.get(prefix.upper() + "_PREFIX", prefix)
        dir_path = checkDirName(self.STATIC_PATH, base_folder, value)
        setattr(self, prefix + "_folder", dir_path)

  def getDirName(self, prefix):
    basePath = getattr(self, prefix + "_folder")
    return os.path.abspath(os.path.join(self.STATIC_PATH, basePath))

  def getPathType(self, name):
    if(name in prefix_items):
      return name
    else:
      return 'project'

  def upload(self, path_type, filename, file):
    """上传文件"""
    file_path = os.path.join(self.getDirName(path_type), filename)
    file.save(file_path)
  
  def is_exist(self, path_type, filename):
    """检查文件是否存在"""
    file_path = os.path.join(self.getDirName(path_type), filename)
    return os.path.isfile(file_path)

  def delete(self, path_type, filename):
    """（批量）删除文件"""
    # 如果给予列表，则批量删除
    if isinstance(filename, list):
      if len(filename) == 0:
        return
      for file in filename:
        return self.delete(path_type, file)
    else:
      file_path = os.path.join(self.getDirName(path_type), filename)
      if os.path.isfile(file_path):
        return os.remove(file_path)
      else:
        pass

  def download(self, path_type, filename, /, *, local_path=None):
    """没有下载文件功能，用复制功能替代"""
    file_path = os.path.join(self.getDirName(path_type), filename)
    if local_path:
      shutil.copy(file_path, local_path)
    else:
      return self.sign_url(path_type, filename)
  
  def open(self, path_type, filename):
    if not self.is_exist(path_type, filename):
      return False
    file_path = os.path.join(self.getDirName(path_type), filename)
    return open(file_path, 'r')
    

  def copy_file(self, path_type, filename, from_path):
    file_path = os.path.join(self.getDirName(path_type), filename)
    if not from_path:
      pass
    shutil.copy(from_path, file_path)

  def sign_url(self, path_type, filename, **kwargs):
    """ 生成文件地址 """
    file_domain = self.file_domain
    if not self.is_exist(path_type, filename):
      return False
    url = "{}/{}".format(getattr(self, path_type + "_folder"), filename)
    if file_domain is None:
      if url[0:3] == "../":
        url = url[3:]
      elif url[0:2] == "./":
        url = url[2:]
      url = url_for("index.storage", path=url, _external=True, _scheme=self.scheme)
    else:
      url = file_domain + url.replace(self.files_folder, "")
    return url
