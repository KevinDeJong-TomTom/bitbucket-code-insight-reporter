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
import os

from . import bitbucket
from llvm_diagnostics import parser


def get_severity_for_level(level):
    if level == "error":
        return "HIGH"

    if level == "warning":
        return "MEDIUM"

    return "LOW"


def retrieve_annotations_from_file(path, workspace):
    _annotations = []
    for diag_msg in parser.diagnostics_messages_from_file(path):
        _data = json.loads(diag_msg.to_json())
        _filepath = (
            _data["filepath"]
            if not workspace
            else _data["filepath"].replace(workspace, "").lstrip(os.path.sep)
        )
        _annotations.append(
            {
                "path": _filepath,
                "line": _data["line"],
                "message": _data["message"],
                "severity": get_severity_for_level(_data["level"]),
            }
        )

    return _annotations


def add_impact_report(report, impact, count):
    if count > 0:
        report["data"].append(
            {"title": f"{impact} Impact", "type": "NUMBER", "value": count}
        )


def get_count_per_impact(annotations, impact):
    return len([item for item in annotations if item["severity"] == impact])


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
    "--llvm-logging",
    required=True,
    help="Path pointing to logging file containing llvm diagnostics messages",
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
def main(
    bitbucket_server,
    username,
    password,
    bitbucket_project,
    repository_slug,
    commit_hash,
    report_file,
    llvm_logging,
):
    print(
        """\
===============================
BitBucket Code Insight Reporter
==============================="""
    )

    if not os.path.exists(llvm_logging):
        print("ERR - Specified input file does not exist!")
        return 1

    _report = json.load(report_file)
    _report["data"] = []
    _report_id = _report["id"]

    _annotations = retrieve_annotations_from_file(llvm_logging, _report["workspace"])
    _failure = len(_annotations) > 0

    if _failure:
        _report["result"] = "FAIL"
        add_impact_report(_report, "High", get_count_per_impact(_annotations, "HIGH"))
        add_impact_report(
            _report, "Medium", get_count_per_impact(_annotations, "MEDIUM")
        )
        add_impact_report(_report, "Low", get_count_per_impact(_annotations, "LOW"))

    bb = bitbucket.Bitbucket(
        url=bitbucket_server,
        username=username,
        password=password,
    )

    try:
        bb.delete_code_insights_report(
            project_key=bitbucket_project,
            repository_slug=repository_slug,
            commit_id=commit_hash,
            report_key=_report_id,
        )
    except:
        pass

    print(
        f"""\

REPORT REPORT REPORT REPORT REP
-------------------------------
Project: {bitbucket_project}
Repository: {repository_slug}
Commit Hash: {commit_hash}
Report: {json.dumps(_report, indent=4, sort_keys=True)}"""
    )

    try:
        bb.create_code_insights_report(
            project_key=bitbucket_project,
            repository_slug=repository_slug,
            commit_id=commit_hash,
            report_key=_report_id,
            report_title=_report["title"],
            **_report,
        )
    except:
        print("ERR - Failed to create new Code Insight Report")
        return 1

    if not _annotations:
        return 0

    print(
        f"""\

ANNOTATIONS ANNOTATIONS ANNOTAT
-------------------------------
Project: {bitbucket_project}
Repository: {repository_slug}
Commit Hash: {commit_hash}
Annotations: {json.dumps(_annotations, indent=4, sort_keys=True)}"""
    )

    bb.add_code_insights_annotations_to_report(
        project_key=bitbucket_project,
        repository_slug=repository_slug,
        commit_id=commit_hash,
        report_key=_report_id,
        annotations=_annotations,
    )

    print("============= DONE =============")

    return 0
