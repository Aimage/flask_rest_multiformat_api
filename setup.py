from setuptools import setup, find_packages


setup(name='Flask-REST-multiformat-api',
      version='0.1',
      description='Flask extension to create REST api using different \
                      kind of format like JSONAPI 1.0',
      url='https://github.com/Aimage/flask_rest_multiformat_api',
      author='RAKOTOSON Ainanirina Jean',
      author_email='rainanirina@gmail.com',
      license='MIT',
      packages=find_packages(exclude=['tests']),
      zip_safe=False
      )