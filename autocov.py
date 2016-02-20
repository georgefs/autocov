#!/usr/bin/env python


import os
import json
from os import environ
import sys

__version__ = '2016.02.20'


def upload_cov(commit):
    os.system('coverage html')
    os.system('mkdir -p ../autocov')
    os.system('mv htmlcov ../autocov/%s' % commit)
    os.system('git checkout gh-pages')
    os.system('git add ../autocov/')
    os.system('git commit -m "auto cov %s"' % commit)
    os.system('git push')


def update_github_status(auth, repo, status):
    url = "https://api.github.com/repos/{}/{}/statuses/{}".format(
        repo['owner'],
        repo['repo'],
        repo['sha']
    )
    cmd = 'curl -u {}:{} -H "Content-Type: application/json" -X POST -d \'{}\' {}'.format(
        auth['user'],
        auth['token'],
        json.dumps(status),
        url
    )
    return os.system(cmd)


def auto_cov(user, token, cov_requirements=0):
    commit = environ['TRAVIS_COMMIT']
    owner, repo = environ['TRAVIS_REPO_SLUG'].split('/')

    upload_cov(commit)

    url = "http://%s.github.io/%s/autocov/%s/" % (owner, repo, commit)
    result = 30

    if result > cov_requirements:
        state = "success"
    else:
        state = "failure"

    status = {
        "state": state,
        "target_url": url,
        "description": "The current coverage is %s" % result,
        "context": "continuous-integration/autocov"
    }

    auth = {
        "user": user,
        "token": token
    }
    repo = {
        "repo": repo,
        "owner": owner,
        "sha": commit
    }
    update_github_status(auth, repo, status)


def docstring_summary(docstring):
    """Return summary of docstring."""
    return docstring.split('\n')[0] if docstring else ''


def create_parser():
    """Return command-line parser."""
    # Do import locally to be friendly to those who use autopep8 as a library
    # and are supporting Python 2.6.
    import argparse

    parser = argparse.ArgumentParser(description=docstring_summary(__doc__),
                                     prog='autocov')
    parser.add_argument('--user', help='the github user')
    parser.add_argument('--token', help='the github token')
    parser.add_argument(
        '--percent',
        type=int, help='the coverage percent requirement', default=0
    )
    return parser


def parse_args(arguments):
    """Parse command-line options."""
    parser = create_parser()
    args = parser.parse_args(arguments)
    return args


def main(argv=None):
    """Command-line entry."""
    if argv is None:
        argv = sys.argv

    args = parse_args(argv[1:])

    auto_cov(args.user, args.token, args.percent)

if __name__ == '__main__':
    sys.exit(main())