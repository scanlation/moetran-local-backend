"""
本地文件存储相关方法
"""
import time
import os
from flask import url_for

prefix_items = ["user_avatar", "team_avatar", "project", "thumbnail"]

def getDirName(basePath, filePath=None):
  """
  用相对路径获取绝对路径
  """
  path = basePath
  if filePath:
    path = "./app/static/" + basePath + filePath
  files_folder = os.path.dirname(path)
  # 不存在文件夹自动创建
  if not os.path.isdir(files_folder):
      os.makedirs(files_folder)
  return files_folder.replace("./app/static/", "")

class LocalFile:
  def __init__(self, config=None):
    if config and config["FILE_CACHE_TYPE"] == "local":
      self.init(config)
    else:
      self.base_folder = None
      for prefix in prefix_items:
        setattr(self, prefix + "_folder", None)


  def init(self, config):
    if config["FILE_CACHE_TYPE"] == "local":
      self.file_domain = config.get("FILE_DOMAIN", None)
      # 文件根目录
      base_folder = config.get("FILE_PREFIX", "files/")
      self.base_folder = getDirName(base_folder)
      for prefix in prefix_items:
        value = config.get(prefix.upper() + "_PREFIX", prefix + "/")
        dir_path = getDirName(base_folder, value)
        setattr(self, prefix + "_folder", dir_path)

  def upload(self, path_type, filename, file):
    """上传文件"""
    file_path = "./app/static/{}/{}".format(getattr(self, path_type + "_folder"), filename)
    file.save(file_path)
  
  def is_exist(self, path_type, filename):
    """检查文件是否存在"""
    file_path = "./app/static/{}/{}".format(getattr(self, path_type + "_folder"), filename)
    return os.path.exists(file_path)
  def delete(self, path_type, filename):
    """删除文件"""
    file_path = "./app/static/{}/{}".format(getattr(self, path_type + "_folder"), filename)
    return os.remove(file_path)


  def sign_url(self, path_type, filename):
    file_domain = self.file_domain
    url = "{}/{}".format(getattr(self, path_type + "_folder"), filename)
    if file_domain is None:
      if url[0:3] == "../":
        url = url[3:]
      elif url[0:2] == "./":
        url = url[2:]
      url = url_for("static", filename=url, _external=True)
    else:
      url = file_domain + url.replace(self.files_folder, "")
    return url
