from setuptools import setup, find_packages  
  
setup(  
      name='potentiostat',   #名称  
      version='0.0.3',  #版本  
      description="This module implements the serial interface to the Rodeostat open source ", #描述  
      keywords='aptacam',  
      author='aptacam',  #作者  
      #author_email='', #作者邮箱  
      url='http://www.aptacam.com/', #作者链接  
      packages=find_packages(),
)  