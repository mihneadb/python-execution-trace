from setuptools import setup



setup(name='execution-trace',
      version='1.0.3',
      description="Trace the local context of a Python function's execution with just a decorator",
      url='http://github.com/mihneadb/python-execution-trace',
      author='Mihnea Dobrescu-Balaur',
      author_email='mihnea@linux.com',
      license='MIT',
      packages=['execution_trace',
                'execution_trace.viewer'],
      include_package_data=True,
      install_requires=[
            'voluptuous==0.8.10',
            'Flask==0.10.1',
      ],
      test_suite='nose.collector',
      tests_require=[
            'nose==1.3.7',
            'mock==1.3.0'
      ],
      scripts=[
            'bin/view_trace',
      ],
      zip_safe=False
)
