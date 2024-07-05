from setuptools import setup, find_packages

setup(
    name='CNLWizard',
    version='1.0.0',
    description='',
    url='https://github.com/dodaro/CNLWizard',
    license='MIT License',
    author='Carmine Dodaro',
    author_email='carmine.dodaro@unical.it',
    maintainer='Simone Caruso',
    maintainer_email='simone.caruso@edu.unige.it',
    package_dir={'': 'src'},
    packages=find_packages('src', exclude=['tests*']),
    package_data={'CNLWizard': ['components.yaml']},
    entry_points={
        'console_scripts': ['CNLWizard = main:main'],
    },
    install_requires=['lark'],
    python_requires=">=3.10"
)