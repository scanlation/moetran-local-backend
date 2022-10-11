from PIL import Image
import os

from app import celery, fileStorage

@celery.task(name="tasks.thumbnail_task", time_limit=35)
def thumbnail_task(path_type, filename):
  fileStorage.init(celery.conf.app_config)
  src = os.path.join(fileStorage.getDirName(path_type), filename)
  img = Image.open(src)
  base_width = 180
  base_height = 140
  width_percent = (base_width / float(img.size[0]))
  height = int(float(img.size[1]) * float(width_percent))
  resized = img.resize((base_width, height), Image.ANTIALIAS)
  if height > base_height:
      crop_height = int(float(height - base_height) / 2)
      resized = resized.crop((0, crop_height, base_width, crop_height + base_height))

  # resized.save(dest)
  fileStorage.upload('thumbnail', filename, resized)

def image_thumbnail(path_type, filename):
  if fileStorage.cache_type == 'local':
    thumbnail_task.delay(path_type, filename)

def remove_thumbnail(path_type, filenames):
  # 直接删除文件，不走任务
  if fileStorage.cache_type == 'local':
    fileStorage.delete('thumbnail', filenames)