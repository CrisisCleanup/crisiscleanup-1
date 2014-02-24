
import os, shutil, json
from glob import glob
from tempfile import mkdtemp, gettempdir

from fabric.api import env, task, local, abort
from fabric.colors import yellow
from fabric.utils import warn as raw_warn
from fabric.contrib.console import confirm

import yaml


# constants

ALLOWED_SDK_VERSIONS = {'1.8.8', '1.8.9'}
APP_YAML_FILENAME = 'app.yaml'
APP_YAML_TEMPLATE_FILENAME = 'app.yaml.template.yaml'
BUILD_DIR_PREFIX = 'ccbuild'


# find GAE SDK

POSSIBLE_SDK_DIRECTORIES = [
    '../google_appengine/',
    '../../google_appengine/',
    '../../../google_appengine/',
]

try:
    _sdk_path = (
        path for path in POSSIBLE_SDK_DIRECTORIES
        if os.path.exists(path)
        and os.path.exists(os.path.join(path, 'appcfg.py'))
    ).next()
    _sdk_path = os.path.join(*os.path.split(_sdk_path)[:-1])
except StopIteration:
    abort('GAE SDK directory not found - add it to POSSIBLE_SDK_DIRECTORIES')


# define env

env.master_branch = "master"
env.default_gae_app_version = "live"
env.sdk_path = os.path.realpath(_sdk_path)
env.appcfg = os.path.realpath(os.path.join(_sdk_path, 'appcfg.py'))
env.sdk_path = os.path.realpath(_sdk_path)


# define apps

MINI_YAML = """ 
- application: sandy-helping-hands
  secure: always
  allow_unclean_deploy: true
  sandbox: true
  overwrite:
    "assets/images/crisis-cleanup-logo-default.png" : "assets/images/crisis-cleanup-logo.png"


- application: crisis-cleanup-ph
  secure: always
  overwrite:
    "assets/images/crisis-cleanup-logo-default.png" : "assets/images/crisis-cleanup-logo.png"


- application: sandy-disaster-recovery
  secure: always
  overwrite:
    "assets/images/crisis-cleanup-logo-default.png" : "assets/images/crisis-cleanup-logo.png"

- application: crisiscleanup-demo
  secure: optional
  overwrite:
    "assets/images/crisis-cleanup-logo-default.png" : "assets/images/crisis-cleanup-logo.png"

- application: crisis-cleanup-au
  secure: always
  overwrite:
    "assets/images/crisis-cleanup-logo-au.png" : "assets/images/crisis-cleanup-logo.png"

- application: crisis-cleanup-au-demo
  secure: optional
  overwrite:
    "assets/images/crisis-cleanup-logo-au.png" : "assets/images/crisis-cleanup-logo.png"

- application: crisis-cleanup-in
  secure: always
  overwrite:
    "assets/images/crisis-cleanup-logo-in.png" : "assets/images/crisis-cleanup-logo.png"

- application: crisis-cleanup-in-demo
  secure: optional
  overwrite:
    "assets/images/crisis-cleanup-logo-in.png" : "assets/images/crisis-cleanup-logo.png"
"""

APPS = {
    d['application']:d for d in yaml.load(MINI_YAML)
}

LOCAL_APP = {
    'application': 'local',
    'secure': 'optional'
}


# functions

def warn(msg):
    return raw_warn(yellow(msg))


def warn_or_abort(app_defn, message):
    if app_defn.get('allow_unclean_deploy', False):
        warn(message)
    else:
        abort(message)


def sdk_version_ok():
    " Check that the SDK is the specified version. "
    try:
        sdk_version_d = yaml.load(open(os.path.join(env.sdk_path, 'VERSION')))
        current_sdk_version = sdk_version_d['release']
    except:
        current_sdk_version = None
    if current_sdk_version not in ALLOWED_SDK_VERSIONS:
        abort("Local SDK version is %s - one of %s is required" % (
            current_sdk_version, ALLOWED_SDK_VERSIONS))
    return True


def app_yaml_template_present():
    " Check that the app.yaml template is present. "
    if APP_YAML_TEMPLATE_FILENAME not in os.listdir('.'):
        abort("%s not found" % APP_YAML_TEMPLATE_FILENAME)
    return True


def working_directory_clean(app_defn):
    """
    Check that the working directory is clean.

    Warn only; deployment is from a git commit.
    """
    git_status = local("git status", capture=True)
    if "working directory clean" not in git_status:
        if app_defn.get('allow_unclean_deploy', False):
            warn("Working directory not clean (ignoring for %s)" % app_defn['application'])
        else:
            warn("Working directory not clean - modified files will not be deployed to %s" % app_defn['application'])
    return True


def get_current_branch():
    return local("git rev-parse --abbrev-ref HEAD", capture=True)


def on_master_branch(app_defn):
    " Check master branch is checked out. "
    checked_out_branch = get_current_branch()
    if checked_out_branch != env.master_branch:
        if app_defn.get('allow_unclean_deploy', False):
            warn("Branch is %s (ignoring for %s)" % (checked_out_branch, app_defn['application']))
        else:
            abort("%s branch must be checked out to deploy to %s" % (
                env.master_branch, app_defn['application']))
    return True


def current_branch_pushed_to_remote(app_defn):
    " Check that the current branch is pushed to origin. "
    current_branch = get_current_branch()
    local_ref = local("git rev-parse %s" % current_branch, capture=True)
    origin_ref = local("git rev-parse origin/%s" % current_branch, capture=True)
    if local_ref != origin_ref:
        if app_defn.get('allow_unclean_deploy', False):
            warn("%s and origin/%s differ (ignoring for %s)" % (
                current_branch, current_branch, app_defn['application']))
        else:
            abort("%s must be pushed to origin to deploy to %s" % (
                current_branch, app_defn['application']))
    return True


def check_specified_commitish_pushed_to_remote(app_defn, tag):
    " Check the specified commit on the current branch has been pushed to origin. "
    current_branch = get_current_branch()
    containing_branches = local("git branch -a --contains %s" % tag, capture=True)
    if 'origin/%s' % current_branch not in containing_branches:
        if app_defn.get('allow_unclean_deploy', False):
            warn("%s has not been pushed to origin/%s (ignoring for %s)" % (
                tag, current_branch, app_defn['application']))
        else:
            abort("%s must be pushed to origin/%s to deploy to %s" % (
                tag, current_branch, app_defn['application']))

    return True


def ok_to_deploy(app_defn, tag):
    return (
        sdk_version_ok() and
        app_yaml_template_present() and
        working_directory_clean(app_defn) and
        on_master_branch(app_defn) and
        check_specified_commitish_pushed_to_remote(app_defn, tag)
    )


def write_app_yaml(app_defn, gae_app_version=None, preamble=None):
    # set default preamble and GAE app version
    if preamble is None:
        preamble = "\n# *** AUTOMATICALLY GENERATED BY FABRIC ***\n"
    if gae_app_version is None:
        gae_app_version = 'default'

    # open template
    with open(APP_YAML_TEMPLATE_FILENAME)as app_yaml_template_fd:
        yaml = app_yaml_template_fd.read()

        # replace placeholders
        placeholder_replacements = app_defn.items() + [('version', gae_app_version)]
        for key, val in placeholder_replacements:
            placeholder_name = ("$%s_PLACEHOLDER" % key).upper()
            if placeholder_name in yaml:
                yaml = yaml.replace(placeholder_name, unicode(val))

    # write app.yaml
    with open(APP_YAML_FILENAME, 'w') as app_yaml_fd:
        app_yaml_fd.write(preamble)
        app_yaml_fd.write(yaml)


def delete_app_yaml():
    os.remove(APP_YAML_FILENAME)


def perform_overwrites(app_defn):
    for src, dest in app_defn.get('overwrite', {}).items():
        print "Copying %s to %s ..." % (src, dest)
        shutil.copyfile(src, dest)


def write_deployment_version(app_defn, tag, commit):
    with open('version.json', 'w') as version_json_fd:
        version_d = {
            'application': app_defn['application'],
            'tag': tag,
            'commit': commit,
        }
        json.dump(version_d, version_json_fd)


def update():
    " Update GAE from working dir. "
    local("%(appcfg)s --oauth2 update . " % env)


def get_app_definitions(app_names_or_all):
    if app_names_or_all == ['all']:
        return [defn for name,defn in APPS.items() if not defn.get('sandbox')]
    else:
        try:
            return [APPS[name] for name in app_names_or_all]
        except KeyError, e:
            abort("'%s' is not a known application." % e.message)


@task
def list():
    " List known application names. "
    for name in APPS:
        print name


@task
def clear_build_dirs():
    " Remove old build directories. "
    for path in glob(os.path.join(gettempdir(), '%s*' % BUILD_DIR_PREFIX)):
        if os.path.isdir(path):
            print "Removing old tmp build dir: %s" % path
            shutil.rmtree(path)


@task
def check(apps, tag='HEAD'):
    """
    Check if it is ok to deploy to apps
    """
    app_defns = get_app_definitions(apps.split(';'))
    for app_defn in app_defns:
        ok_to_deploy(app_defn, tag)


@task
def vacuum_indexes(apps):
    """
    Vacuum indexes for apps.
    """
    app_defns = get_app_definitions(apps.split(';'))
    for app_defn in app_defns:
        local("%(appcfg)s --oauth2 -A %(application)s vacuum_indexes ." % (
            dict(env.items() + app_defn.items()))
        )


@task
def deploy(apps, tag='HEAD', version=None):
    """
    Deploy to one or more applications
    (semicolon-separated values or 'all').
    """
    # get app definitions
    app_defns = get_app_definitions(apps.split(';'))

    # before doing anything, check if *all* apps are ok to deploy to
    for app_defn in app_defns:
        ok_to_deploy(app_defn, tag)

    # check/rewrite tag
    available_tags = local('git tag -l', capture=True).splitlines()
    if tag == 'HEAD':
        # rewrite HEAD to a tag if available
        head_tags = local('git tag -l --contains=HEAD', capture=True)
        if head_tags:
            tag = head_tags.splitlines()[0]
        else:
            warn("HEAD is not tagged with a version.")
    elif tag not in available_tags:
        abort("Unknown tag '%s'" % tag)

    # get commit hash
    commit = local('git rev-parse %s' % tag, capture=True)

    # decide GAE app version to use
    if version:
        gae_app_version = version
    else:
        current_branch = get_current_branch()
        if current_branch == env.master_branch:
            gae_app_version = env.default_gae_app_version
        else:
            gae_app_version = current_branch

    # state options
    print "\nSelected deployment options:\n"
    print "Tag:             %s" % tag
    print "GAE app version: %s" % gae_app_version
    print "Apps:            %s" % ', '.join(
        app_defn['application'] for app_defn in app_defns
    )
    print

    # if deploying to all, check
    if apps == 'all':
        if not confirm("Deploy to ALL apps, excluding sandbox? Are you sure?", default=False):
            abort("Deploy to all except sandbox unconfirmed")

    # clear old build dirs
    clear_build_dirs()

    # build to deployment, using git archive
    build_dir = mkdtemp(prefix=BUILD_DIR_PREFIX)
    print "Building to %s ..." % build_dir
    local("git archive %s | tar -x -C %s" % (tag, build_dir))
    print "Changing pwd to %s ..." % build_dir
    os.chdir(build_dir)

    # deploy to all specified apps
    for app_defn in app_defns:
        print "\nDeploying to %s...\n" % app_defn['application']
        print "Writing app.yaml..."
        write_app_yaml(app_defn, gae_app_version=gae_app_version)
        perform_overwrites(app_defn)
        write_deployment_version(app_defn, tag, commit)
        print "Starting GAE update..."
        update()  # call GAE appcfg
        delete_app_yaml()

    # output success message
    print "\nSuccessfully deployed to %s." % ', '.join(
        app_defn['application'] for app_defn in app_defns
    )


@task
def write_local_app_yaml():
    " Write out app.yaml for local dev use. "
    write_app_yaml(
        LOCAL_APP,
        preamble=(
            "\n# ** GENERATED BY FABRIC FOR LOCAL USE ONLY **\n" + 
            "#\n" + 
            "# (edit %s instead)\n\n" % APP_YAML_TEMPLATE_FILENAME
        )
    )


@task
def dev():
    " Start development server. "
    sdk_version_ok()
    write_local_app_yaml()
    local(
        "%s --require_indexes=true --show_mail_body=true ." %
        os.path.join(env.sdk_path, 'dev_appserver.py')
    )


@task
def local_shell():
    " Start a local shell ."
    sdk_version_ok()
    print "\nEnter a fake email address and password.\n"
    local(
        "%s -s localhost:8080" % os.path.join(env.sdk_path, 'remote_api_shell.py')
    )


@task
def remote_shell(app):
    sdk_version_ok()
    print "\nGenerate a app-specific password via https://www.google.com/settings/security\n"
    local(
        "%s --secure %s" % (
            os.path.join(env.sdk_path, 'remote_api_shell.py'),
            app
        )
    )
