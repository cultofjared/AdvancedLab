import os
import shutil
from os import path, listdir
from doit.task import clean_targets
from copy import copy


DOIT_CONFIG = {'default_tasks': ['python_firststeps']}

NOTEBOOKS = [path.splitext(notebook)[0]
             for notebook in listdir('notebooks')
             if notebook[-6:] == '.ipynb']


def clean_latex():
    latex_cruft = ['Python-FirstSteps.out',
                   'Python-FirstSteps.fdb_latexmk',
                   'Python-FirstSteps.fls',
                   'Python-FirstSteps.log',
                   'Python-FirstSteps.pyg',
                   'Python-FirstSteps.aux']

    minted_dir = '_minted-Python-FirstSteps'

    for latex_file in latex_cruft:
        if path.isfile(latex_file):
            os.remove(latex_file)

    if path.isdir(minted_dir):
        shutil.rmtree(minted_dir)


def clean_python():
    cache_dir = '__pycache__'

    if path.isdir(cache_dir):
        shutil.rmtree('__pycache__')


def task_python_firststeps():
    """Creates python firststeps pdf"""
    return {
            'actions': [['latexmk', '-silent', 'Python-FirstSteps.tex'],
                        ['latexmk', '-c', 'Python-FirstSteps.tex']],
            'targets': ['Python-FirstSteps.pdf'],
            'file_dep': ['{0}.tex'.format(notebook)
                         for notebook in NOTEBOOKS] +
                         ['Python-FirstSteps.tex',
                          'tufte-handout-local.tex'],
            'clean': [clean_targets,
                      clean_latex]
            }


def task_convert_notebook():
    """Converts ipython notebook to inlineable .tex"""

    yield {
        'name': 'help_commands',
        'actions': [['jupyter', 'nbconvert',
                     '--to', 'latex',
                     '--template', 'notebooks/no_output.tplx',
                     'notebooks/help_commands.ipynb',
                     '--output', 'help_commands.tex']],

        'targets': ['help_commands.tex'],

        'file_dep': ['notebooks/help_commands.ipynb',
                     'notebooks/hide_warnings.tplx',
                     'notebooks/no_output.tplx'],

        'clean': [clean_targets,
                  clean_python]

        }

    normal_notebooks = copy(NOTEBOOKS)
    normal_notebooks.remove('help_commands')

    for notebook in normal_notebooks:
        datafile = 'notebooks/{0}.csv'.format(notebook)

        dependencies = ['notebooks/{0}.ipynb'.format(notebook),
                        'notebooks/hide_warnings.tplx']

        if path.isfile(datafile):
            dependencies += [datafile]

        yield {
            'name': notebook,
            'actions': [['jupyter', 'nbconvert',
                         '--to', 'latex',
                         '--template', 'notebooks/hide_warnings.tplx',
                         'notebooks/{0}.ipynb'.format(notebook),
                         '--output', '{0}.tex'.format(notebook)
                         ]],

            'targets': ['{0}.tex'.format(notebook)],

            'file_dep': dependencies,

            'clean': [clean_targets,
                      clean_python,
                      'rm -rf {0}_files'.format(notebook),
                      'rm -rf {0}_no_output_files'.format(notebook)]

        }
