#!/usr/bin/env python3

# Copyright (c) 2021 - 2021 TomTom N.V.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import click
import json
import logging

from .bitbucket import Bitbucket


@click.command()
@click.option(
    "--bitbucket-server",
    required=True,
    help="URL for the BitBucket server",
)
@click.option(
    "--username",
    required=True,
    prompt=True,
    help="Username associated with BitBucket",
)
@click.option(
    "--password",
    required=True,
    prompt=True,
    hide_input=True,
    help="Password associated with BitBucket",
)
@click.option(
    "--bitbucket-project",
    required=True,
    help="BitBucket project name",
)
@click.option(
    "--repository-slug",
    required=True,
    help="BitBucket repository slug name",
)
@click.option(
    "--commit-hash",
    required=True,
    help="Commit Hash to associate the Code Insights Report with",
)
@click.option(
    "--report-file",
    type=click.File("r", encoding="UTF-8", lazy=True),
    required=True,
    help="Code Insights Report identifier",
)
def report(
    bitbucket_server,
    username,
    password,
    bitbucket_project,
    repository_slug,
    commit_hash,
    report_file,
):
    logging.info("BitBucket Code Insight Reporter")

    _report = json.load(report_file)
    _report_id = _report["id"]

    bitbucket = Bitbucket(
        url=bitbucket_server,
        username=username,
        password=password,
    )

    try:
        bitbucket.delete_code_insights_report(
            project_key=bitbucket_project,
            repository_slug=repository_slug,
            commit_id=commit_hash,
            report_key=_report_id,
        )
    except:
        pass

    logging.debug(
        f"""\
Project: {bitbucket_project}
Repository: {repository_slug}
Commit Hash: {commit_hash}
Report: {json.dumps(_report["report"], indent=4, sort_keys=True)}"""
    )

    try:
        bitbucket.create_code_insights_report(
            project_key=bitbucket_project,
            repository_slug=repository_slug,
            commit_id=commit_hash,
            report_key=_report_id,
            report_title=_report["report"]["title"],
            **_report["report"],
        )
    except:
        print("ERR - Failed to create new Code Insight Report")
        return 1

    _annotations = _report.get("annotations", None)
    if not _annotations:
        return 0

    logging.debug(
        f"""\
Project: {bitbucket_project}
Repository: {repository_slug}
Commit Hash: {commit_hash}
Annotations: {json.dumps(_annotations, indent=4, sort_keys=True)}"""
    )

    bitbucket.add_code_insights_annotations_to_report(
        project_key=bitbucket_project,
        repository_slug=repository_slug,
        commit_id=commit_hash,
        report_key=_report_id,
        annotations=_annotations,
    )

    logging.info("Done...")

    return 0
