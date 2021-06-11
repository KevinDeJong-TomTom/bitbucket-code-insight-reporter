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
import os

from llvm_diagnostics import parser

LOGGER = logging.getLogger(__name__)


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
            if not workspace or workspace not in _data["filepath"]
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


@click.command()
@click.option(
    "--id",
    required=True,
    help="Unique identifier for the report",
)
@click.option(
    "--title",
    required=True,
    help="Humand readable title for the Code Insight report",
)
@click.option(
    "--details",
    help="Additional details to share withing the Code Insight report",
)
@click.option(
    "--reporter",
    help="Reference to the reporter of the Code Insight Report",
)
@click.option(
    "--link",
    help="Link towards an external report",
)
@click.option(
    "--logo-url",
    help="Link towards an image to be shown in the Code Insight report",
)
@click.option(
    "--workspace",
    help="Absolute path towards the root of the repository. This will be stripped from the file paths in the LLVM logging.",
)
@click.option(
    "--llvm-logging",
    required=True,
    help="Path pointing to logging file containing llvm diagnostics messages",
)
@click.option(
    "--output",
    required=True,
    type=click.File("w", encoding="UTF-8", lazy=True, atomic=True),
    help="Path towards the output file",
)
def generate(
    id,
    title,
    details,
    reporter,
    link,
    logo_url,
    workspace,
    llvm_logging,
    output,
):
    LOGGER.info("BitBucket Code Insight Generator")

    if not os.path.exists(llvm_logging):
        LOGGER.error("Specified input file does not exist!")
        return 1

    _report = {"id": id, "report": {}}

    if title:
        _report["report"]["title"] = title
    if details:
        _report["report"]["details"] = details
    if reporter:
        _report["report"]["reporter"] = reporter
    if link:
        _report["report"]["link"] = link
    if logo_url:
        _report["report"]["logo-url"] = logo_url

    _annotations = retrieve_annotations_from_file(llvm_logging, workspace)
    if _annotations:
        _report["annotations"] = _annotations

    _failure = len(_annotations) > 0
    _report["report"]["result"] = "FAIL" if _failure else "PASS"

    LOGGER.debug(f"Generating Report: {json.dumps(_report, indent=4, sort_keys=True)}")

    output.write(json.dumps(_report))
    LOGGER.info(f"Done...")

    return 0
